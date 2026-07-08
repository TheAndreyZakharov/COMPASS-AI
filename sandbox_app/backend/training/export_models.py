from __future__ import annotations

import json
import shutil
from copy import deepcopy
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sandbox_app.backend.inference.model_loader import (
    LoadedSandboxModel,
    ModelLoadError,
    list_available_models,
    load_model,
    load_validation_frame,
)
from sandbox_app.backend.inference.onnx_runtime import (
    OnnxRuntimeError,
    run_onnx_predictions,
)


class ModelExportError(RuntimeError):
    """Raised when model export or validation fails."""


@dataclass(frozen=True)
class ModelExportConfig:
    session_id: str
    model_name: str
    export_onnx: bool = False
    sample_size: int = 100


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def to_json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): to_json_safe(item) for key, item in value.items()}

    if isinstance(value, list):
        return [to_json_safe(item) for item in value]

    if isinstance(value, tuple):
        return [to_json_safe(item) for item in value]

    if isinstance(value, np.integer):
        return int(value)

    if isinstance(value, np.floating):
        result = float(value)
        if np.isnan(result) or np.isinf(result):
            return None
        return result

    if isinstance(value, np.ndarray):
        return to_json_safe(value.tolist())

    if isinstance(value, Path):
        return str(value)

    return value


def read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ModelExportError(f"Could not read JSON file: {path}") from exc

    if not isinstance(payload, dict):
        raise ModelExportError(f"JSON file must contain an object: {path}")

    return payload


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    safe_payload = to_json_safe(payload)
    path.write_text(
        json.dumps(safe_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def mean_abs_diff(left: np.ndarray, right: np.ndarray) -> float:
    if len(left) != len(right):
        raise ModelExportError("Prediction arrays have different lengths")

    return float(np.mean(np.abs(left.astype(float) - right.astype(float))))


def validation_status(native_diff: float, onnx_result: dict[str, Any] | None) -> str:
    native_ok = native_diff <= 1e-6

    if onnx_result is None:
        return "validated" if native_ok else "failed"

    onnx_status = onnx_result.get("status")
    if onnx_status in {"skipped", "not_supported", "not_requested"}:
        return "validated" if native_ok else "failed"

    onnx_ok = onnx_status == "validated"
    return "validated" if native_ok and onnx_ok else "failed"


def native_copy_path(model: LoadedSandboxModel) -> Path:
    return model.model_dir / f"model.{model.artifact_format}"


def ensure_native_artifact(model: LoadedSandboxModel) -> Path:
    target_path = native_copy_path(model)

    if model.artifact_path.resolve() != target_path.resolve():
        shutil.copy2(model.artifact_path, target_path)

    if not target_path.exists():
        raise ModelExportError(f"Native artifact was not saved: {target_path}")

    return target_path


def export_sklearn_to_onnx(
    model: LoadedSandboxModel,
    feature_frame: pd.DataFrame,
) -> dict[str, Any]:
    if model.model_name == "baseline_rule_based":
        return {
            "status": "not_supported",
            "reason": "Custom rule-based baseline is not converted to ONNX",
        }

    try:
        from skl2onnx import convert_sklearn
        from skl2onnx.common.data_types import FloatTensorType
    except ImportError:
        return {
            "status": "skipped",
            "reason": "skl2onnx is not installed",
        }

    matrix = model.align_features(feature_frame).to_numpy(dtype=np.float32)
    onnx_path = model.model_dir / "model.onnx"

    try:
        initial_type = [("input", FloatTensorType([None, len(model.feature_names)]))]
        converted = convert_sklearn(
            model.model,
            initial_types=initial_type,
            options={id(model.model): {"zipmap": False}},
        )
    except Exception:
        try:
            initial_type = [("input", FloatTensorType([None, len(model.feature_names)]))]
            converted = convert_sklearn(model.model, initial_types=initial_type)
        except Exception as exc:
            return {
                "status": "failed",
                "reason": f"sklearn to ONNX conversion failed: {exc}",
            }

    onnx_path.write_bytes(converted.SerializeToString())

    try:
        onnx_scores = run_onnx_predictions(onnx_path, matrix)
        native_scores = model.predict_scores(feature_frame)
        diff = mean_abs_diff(native_scores, onnx_scores)
    except (OnnxRuntimeError, ModelLoadError, ModelExportError) as exc:
        return {
            "status": "failed",
            "path": str(onnx_path),
            "reason": str(exc),
        }

    return {
        "status": "validated" if diff <= 1e-5 else "failed",
        "path": str(onnx_path),
        "mean_abs_diff_vs_native": diff,
    }


def torch_scaled_matrix(
    model: LoadedSandboxModel,
    feature_frame: pd.DataFrame,
) -> np.ndarray:
    scaler = getattr(model.model, "scaler", None)

    if scaler is None:
        raise ModelExportError("Loaded PyTorch model does not contain scaler")

    aligned = model.align_features(feature_frame)
    return scaler.transform(aligned).astype(np.float32)


def export_torch_to_onnx(
    model: LoadedSandboxModel,
    feature_frame: pd.DataFrame,
) -> dict[str, Any]:
    try:
        import torch
    except ImportError:
        return {
            "status": "skipped",
            "reason": "PyTorch is not installed",
        }

    torch_model = getattr(model.model, "model", None)
    if torch_model is None:
        return {
            "status": "failed",
            "reason": "Loaded PyTorch model is invalid",
        }

    onnx_path = model.model_dir / "model.onnx"

    try:
        matrix = torch_scaled_matrix(model, feature_frame)
        input_tensor = torch.tensor(matrix, dtype=torch.float32)
        torch_model.eval()
        torch.onnx.export(
            torch_model,
            input_tensor,
            str(onnx_path),
            input_names=["input"],
            output_names=["logits"],
            dynamic_axes={
                "input": {0: "batch_size"},
                "logits": {0: "batch_size"},
            },
            opset_version=17,
        )
    except Exception as exc:
        return {
            "status": "failed",
            "reason": f"PyTorch to ONNX conversion failed: {exc}",
        }

    try:
        onnx_scores = run_onnx_predictions(
            onnx_path,
            matrix,
            output_is_logits=True,
        )
        native_scores = model.predict_scores(feature_frame)
        diff = mean_abs_diff(native_scores, onnx_scores)
    except (OnnxRuntimeError, ModelLoadError, ModelExportError) as exc:
        return {
            "status": "failed",
            "path": str(onnx_path),
            "reason": str(exc),
        }

    return {
        "status": "validated" if diff <= 1e-5 else "failed",
        "path": str(onnx_path),
        "mean_abs_diff_vs_native": diff,
    }


def export_optional_onnx(
    model: LoadedSandboxModel,
    feature_frame: pd.DataFrame,
    export_onnx: bool,
) -> dict[str, Any]:
    if not export_onnx:
        return {
            "status": "not_requested",
        }

    if model.artifact_format == "joblib":
        return export_sklearn_to_onnx(model, feature_frame)

    if model.artifact_format == "pt":
        return export_torch_to_onnx(model, feature_frame)

    return {
        "status": "not_supported",
        "reason": f"Unsupported artifact format: {model.artifact_format}",
    }


def validate_native_inference(
    model: LoadedSandboxModel,
    sample_size: int,
) -> tuple[dict[str, Any], pd.DataFrame]:
    feature_frame, saved_predictions = load_validation_frame(model, sample_size)
    native_scores = model.predict_scores(feature_frame)
    saved_scores = saved_predictions["predicted_score"].astype(float).to_numpy()
    diff = mean_abs_diff(native_scores, saved_scores)

    validation = {
        "status": "validated" if diff <= 1e-6 else "failed",
        "sample_size": len(feature_frame),
        "mean_abs_diff_vs_saved_predictions": diff,
        "max_abs_diff_vs_saved_predictions": float(
            np.max(np.abs(native_scores - saved_scores))
        ),
    }

    return validation, feature_frame


def validation_snapshot(validation: dict[str, Any]) -> dict[str, Any]:
    snapshot = deepcopy(validation)
    snapshot.pop("model_metadata", None)
    return to_json_safe(snapshot)


def update_model_metadata(
    model: LoadedSandboxModel,
    native_path: Path,
    validation: dict[str, Any],
) -> dict[str, Any]:
    metadata_path = model.model_dir / "model_metadata.json"
    metadata = dict(model.metadata)
    metadata["artifact_path"] = str(native_path)
    metadata["artifact_format"] = model.artifact_format
    metadata["last_export_validation"] = validation_snapshot(validation)
    metadata["updated_at"] = utc_now_iso()

    onnx_path = validation.get("onnx", {}).get("path")
    if onnx_path:
        metadata["onnx_path"] = str(onnx_path)

    safe_metadata = to_json_safe(metadata)
    write_json(metadata_path, safe_metadata)
    return safe_metadata


def export_and_validate_model(config: ModelExportConfig) -> dict[str, Any]:
    if config.sample_size < 1:
        raise ModelExportError("sample_size must be positive")

    try:
        model = load_model(config.session_id, config.model_name)
        native_path = ensure_native_artifact(model)
        native_validation, feature_frame = validate_native_inference(
            model,
            sample_size=config.sample_size,
        )
        onnx_result = export_optional_onnx(
            model,
            feature_frame=feature_frame,
            export_onnx=config.export_onnx,
        )
    except ModelLoadError as exc:
        raise ModelExportError(str(exc)) from exc

    validation = {
        "status": validation_status(
            native_validation["mean_abs_diff_vs_saved_predictions"],
            onnx_result,
        ),
        "validated_at": utc_now_iso(),
        "session_id": config.session_id,
        "model_name": config.model_name,
        "native": {
            "status": native_validation["status"],
            "artifact_format": model.artifact_format,
            "artifact_path": str(native_path),
            "sample_size": native_validation["sample_size"],
            "mean_abs_diff_vs_saved_predictions": (
                native_validation["mean_abs_diff_vs_saved_predictions"]
            ),
            "max_abs_diff_vs_saved_predictions": (
                native_validation["max_abs_diff_vs_saved_predictions"]
            ),
        },
        "onnx": onnx_result,
    }

    metadata = update_model_metadata(model, native_path, validation)
    validation["metadata_path"] = str(model.model_dir / "model_metadata.json")
    validation["model_metadata"] = metadata

    safe_validation = to_json_safe(validation)
    write_json(model.model_dir / "export_validation.json", safe_validation)

    return safe_validation


def read_export_validation(session_id: str, model_name: str) -> dict[str, Any]:
    model_dir = load_model(session_id, model_name).model_dir
    validation_path = model_dir / "export_validation.json"

    if not validation_path.exists():
        raise ModelExportError(f"export_validation.json not found: {model_dir}")

    return read_json(validation_path)


def read_model_metadata(session_id: str, model_name: str) -> dict[str, Any]:
    model_dir = load_model(session_id, model_name).model_dir
    metadata_path = model_dir / "model_metadata.json"

    if not metadata_path.exists():
        raise ModelExportError(f"model_metadata.json not found: {model_dir}")

    return read_json(metadata_path)


def predict_with_saved_model(
    session_id: str,
    model_name: str,
    records: list[dict[str, Any]],
) -> dict[str, Any]:
    if not records:
        raise ModelExportError("records must not be empty")

    try:
        model = load_model(session_id, model_name)
        frame = pd.DataFrame(records)
        scores = model.predict_scores(frame)
    except ModelLoadError as exc:
        raise ModelExportError(str(exc)) from exc

    return {
        "session_id": session_id,
        "model_name": model_name,
        "scores": scores.tolist(),
        "rows": len(records),
    }


def list_models_for_api() -> dict[str, Any]:
    return list_available_models()


def save_joblib_copy(model: LoadedSandboxModel, target_path: Path) -> None:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model.model, target_path)