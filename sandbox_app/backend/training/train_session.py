from __future__ import annotations

import csv
import json
import secrets
import shutil
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sandbox_app.backend.core.paths import PATHS
from sandbox_app.backend.features.build_features import (
    FeatureBuildConfig,
    FeatureBuildError,
    build_features_for_dataset,
    read_feature_metadata,
)
from sandbox_app.backend.training.baseline import train_baseline_model
from sandbox_app.backend.training.evaluate import comparison_row, evaluate_by_split
from sandbox_app.backend.training.sklearn_models import (
    SKLEARN_MODEL_NAMES,
    save_sklearn_model,
    sklearn_positive_scores,
    train_sklearn_model,
)
from sandbox_app.backend.training.torch_model import TorchTrainingError, train_torch_mlp

SANDBOX_ROOT = Path(__file__).resolve().parents[2]
TRAINING_SESSIONS_DIR = getattr(
    PATHS,
    "training_sessions_dir",
    SANDBOX_ROOT / "training_sessions",
)

SUPPORTED_MODELS = {
    "baseline_rule_based",
    "sgd_classifier",
    "logistic_regression",
    "random_forest",
    "hist_gradient_boosting",
    "torch_mlp",
}

TARGET_MODES = {"quality", "speed", "balanced", "learning", "risk_aware"}


class TrainingSessionError(RuntimeError):
    """Raised when a training session fails."""


@dataclass(frozen=True)
class SplitConfig:
    train_size: float = 0.7
    validation_size: float = 0.15
    test_size: float = 0.15


@dataclass(frozen=True)
class TrainingSessionConfig:
    dataset_id: str
    dataset_kind: str = "generated"
    target_mode: str = "balanced"
    model_names: list[str] = field(default_factory=lambda: ["baseline_rule_based"])
    seed: int = 42
    split: SplitConfig = field(default_factory=SplitConfig)
    model_params: dict[str, dict[str, Any]] = field(default_factory=dict)
    auto_build_features: bool = True
    overwrite_features: bool = False
    max_pairs: int | None = None


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def new_session_id() -> str:
    timestamp = datetime.now(UTC).strftime("%Y-%m-%d_%H-%M-%S")
    short_id = secrets.token_hex(3)
    return f"{timestamp}_{short_id}"


def dataset_dir(dataset_kind: str, dataset_id: str) -> Path:
    root = PATHS.data_dir / dataset_kind
    path = root / dataset_id

    if not path.exists():
        raise TrainingSessionError(f"Dataset not found: {path}")

    return path


def features_dir(dataset_kind: str, dataset_id: str) -> Path:
    return dataset_dir(dataset_kind, dataset_id) / "features"


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise TrainingSessionError(f"Could not read JSON file: {path}") from exc

    if not isinstance(payload, dict):
        raise TrainingSessionError(f"JSON file must contain an object: {path}")

    return payload


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = sorted({field_name for row in rows for field_name in row})
    with path.open("w", encoding="utf-8", newline="") as file_obj:
        writer = csv.DictWriter(file_obj, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def ensure_features(config: TrainingSessionConfig) -> dict[str, Any]:
    try:
        return read_feature_metadata(config.dataset_id, config.dataset_kind)
    except FeatureBuildError:
        if not config.auto_build_features:
            raise TrainingSessionError("Features were not built for this dataset") from None

    result = build_features_for_dataset(
        FeatureBuildConfig(
            dataset_id=config.dataset_id,
            dataset_kind=config.dataset_kind,
            target_mode=config.target_mode,
            overwrite=config.overwrite_features,
            max_pairs=config.max_pairs,
        )
    )
    return result["metadata"]


def read_training_frames(
    dataset_kind: str,
    dataset_id: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    root = features_dir(dataset_kind, dataset_id)
    features_path = root / "features.parquet"
    targets_path = root / "targets.parquet"

    if not features_path.exists() or not targets_path.exists():
        raise TrainingSessionError("features.parquet or targets.parquet was not found")

    features = pd.read_parquet(features_path)
    targets = pd.read_parquet(targets_path)

    if "pair_id" not in features.columns or "pair_id" not in targets.columns:
        raise TrainingSessionError("features and targets must contain pair_id")

    return features, targets


def normalize_split_config(split: SplitConfig) -> SplitConfig:
    total = split.train_size + split.validation_size + split.test_size

    if total <= 0:
        raise TrainingSessionError("Split sizes must be positive")

    return SplitConfig(
        train_size=split.train_size / total,
        validation_size=split.validation_size / total,
        test_size=split.test_size / total,
    )


def assign_splits(
    frame: pd.DataFrame,
    split: SplitConfig,
    seed: int,
) -> pd.Series:
    if "split" in frame.columns and frame["split"].notna().any():
        normalized = frame["split"].fillna("train").astype(str)
        return normalized.replace({"val": "validation", "dev": "validation"})

    split = normalize_split_config(split)
    rng = np.random.default_rng(seed)
    values = rng.random(len(frame))

    train_limit = split.train_size
    validation_limit = split.train_size + split.validation_size

    result = np.where(
        values < train_limit,
        "train",
        np.where(values < validation_limit, "validation", "test"),
    )

    return pd.Series(result, index=frame.index)


def merged_training_frame(
    features: pd.DataFrame,
    targets: pd.DataFrame,
    config: TrainingSessionConfig,
) -> tuple[pd.DataFrame, list[str]]:
    merged = features.merge(targets, on="pair_id", suffixes=("", "_target"))

    if merged.empty:
        raise TrainingSessionError("No rows after merging features and targets")

    merged["split"] = assign_splits(merged, config.split, config.seed)

    if "label" not in merged.columns:
        raise TrainingSessionError("targets must contain label")

    feature_columns = [
        column
        for column in features.columns
        if column != "pair_id" and pd.api.types.is_numeric_dtype(features[column])
    ]

    if not feature_columns:
        raise TrainingSessionError("No numeric feature columns found")

    merged[feature_columns] = merged[feature_columns].fillna(0.0).astype(float)
    merged["label"] = merged["label"].fillna(0).astype(int)

    if "target_score" not in merged.columns:
        merged["target_score"] = merged["label"].astype(float)

    for column in ("task_id", "employee_id"):
        if column not in merged.columns:
            merged[column] = ""

    return merged, feature_columns


def training_subset(frame: pd.DataFrame) -> pd.DataFrame:
    train_frame = frame[frame["split"] == "train"]

    if train_frame["label"].nunique() >= 2:
        return train_frame

    fallback = frame[frame["label"].notna()]
    if fallback["label"].nunique() >= 2:
        return fallback

    raise TrainingSessionError("Training labels must contain at least two classes")


def prediction_frame(
    model_name: str,
    frame: pd.DataFrame,
    feature_columns: list[str],
    scores: np.ndarray,
) -> pd.DataFrame:
    columns = [
        "pair_id",
        "task_id",
        "employee_id",
        "split",
        "label",
        "target_score",
    ]
    available_columns = [column for column in columns if column in frame.columns]
    predictions = frame[available_columns].copy()
    predictions["model_name"] = model_name
    predictions["predicted_score"] = np.clip(scores, 0.0, 1.0)
    predictions["predicted_label"] = (predictions["predicted_score"] >= 0.5).astype(int)
    predictions["feature_count"] = len(feature_columns)
    return predictions


def validate_models(model_names: list[str]) -> list[str]:
    if not model_names:
        raise TrainingSessionError("At least one model is required")

    invalid = sorted(set(model_names) - SUPPORTED_MODELS)
    if invalid:
        allowed = ", ".join(sorted(SUPPORTED_MODELS))
        raise TrainingSessionError(f"Unsupported models {invalid}. Allowed: {allowed}")

    return model_names


def artifact_format_for_model(model_name: str) -> str:
    if model_name == "torch_mlp":
        return "pt"
    return "joblib"


def artifact_filename_for_model(model_name: str) -> str:
    return f"model.{artifact_format_for_model(model_name)}"


def build_model_metadata(
    *,
    model_name: str,
    artifact_path: Path,
    predictions_path: Path,
    metrics_path: Path,
    feature_columns: list[str],
    train_rows: int,
    prediction_rows: int,
    config: TrainingSessionConfig,
) -> dict[str, Any]:
    return {
        "model_name": model_name,
        "artifact_format": artifact_format_for_model(model_name),
        "artifact_path": str(artifact_path),
        "predictions_path": str(predictions_path),
        "metrics_path": str(metrics_path),
        "created_at": utc_now_iso(),
        "dataset_id": config.dataset_id,
        "dataset_kind": config.dataset_kind,
        "target_mode": config.target_mode,
        "seed": config.seed,
        "feature_count": len(feature_columns),
        "feature_names": feature_columns,
        "train_rows": train_rows,
        "prediction_rows": prediction_rows,
        "model_params": config.model_params.get(model_name, {}),
        "export_formats": {
            "native": artifact_format_for_model(model_name),
            "onnx": "optional_future_export",
        },
    }


def validate_export_files(
    *,
    artifact_path: Path,
    predictions_path: Path,
    metrics_path: Path,
    model_metadata_path: Path,
    expected_prediction_rows: int,
) -> dict[str, Any]:
    checks: dict[str, Any] = {
        "artifact_exists": artifact_path.exists(),
        "predictions_exists": predictions_path.exists(),
        "metrics_exists": metrics_path.exists(),
        "model_metadata_exists": model_metadata_path.exists(),
        "predictions_readable": False,
        "metrics_readable": False,
        "prediction_rows_match": False,
    }

    if predictions_path.exists():
        try:
            predictions = pd.read_parquet(predictions_path)
            checks["predictions_readable"] = True
            checks["prediction_rows"] = len(predictions)
            checks["prediction_rows_match"] = len(predictions) == expected_prediction_rows
        except Exception as exc:
            checks["predictions_error"] = str(exc)

    if metrics_path.exists():
        try:
            metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
            checks["metrics_readable"] = isinstance(metrics, dict)
        except (OSError, json.JSONDecodeError) as exc:
            checks["metrics_error"] = str(exc)

    status = "validated" if all(
        checks[name]
        for name in (
            "artifact_exists",
            "predictions_exists",
            "metrics_exists",
            "model_metadata_exists",
            "predictions_readable",
            "metrics_readable",
            "prediction_rows_match",
        )
    ) else "failed"

    return {
        "status": status,
        "validated_at": utc_now_iso(),
        "checks": checks,
    }


def train_single_model(
    model_name: str,
    train_frame: pd.DataFrame,
    full_frame: pd.DataFrame,
    feature_columns: list[str],
    config: TrainingSessionConfig,
    model_dir: Path,
) -> dict[str, Any]:
    x_train = train_frame[feature_columns]
    y_train = train_frame["label"]
    x_full = full_frame[feature_columns]
    params = config.model_params.get(model_name, {})

    artifact_path = model_dir / artifact_filename_for_model(model_name)

    if model_name == "baseline_rule_based":
        model = train_baseline_model(x_train, y_train, params)
        scores = model.predict_score(x_full)
        model.save(artifact_path)
    elif model_name in SKLEARN_MODEL_NAMES:
        model = train_sklearn_model(model_name, x_train, y_train, config.seed, params)
        scores = sklearn_positive_scores(model, x_full)
        save_sklearn_model(model, artifact_path)
    elif model_name == "torch_mlp":
        model = train_torch_mlp(x_train, y_train, config.seed, params)
        scores = model.predict_score(x_full)
        model.save(artifact_path)
    else:
        raise TrainingSessionError(f"Unsupported model: {model_name}")

    model_dir.mkdir(parents=True, exist_ok=True)

    predictions = prediction_frame(model_name, full_frame, feature_columns, scores)
    metrics_by_split = evaluate_by_split(predictions)

    predictions_path = model_dir / "predictions.parquet"
    metrics_path = model_dir / "metrics.json"
    model_metadata_path = model_dir / "model_metadata.json"
    export_validation_path = model_dir / "export_validation.json"

    predictions.to_parquet(predictions_path, index=False)
    write_json(metrics_path, metrics_by_split)

    model_metadata = build_model_metadata(
        model_name=model_name,
        artifact_path=artifact_path,
        predictions_path=predictions_path,
        metrics_path=metrics_path,
        feature_columns=feature_columns,
        train_rows=len(train_frame),
        prediction_rows=len(full_frame),
        config=config,
    )
    write_json(model_metadata_path, model_metadata)

    export_validation = validate_export_files(
        artifact_path=artifact_path,
        predictions_path=predictions_path,
        metrics_path=metrics_path,
        model_metadata_path=model_metadata_path,
        expected_prediction_rows=len(full_frame),
    )
    write_json(export_validation_path, export_validation)

    return {
        "model_name": model_name,
        "status": "trained",
        "artifact_path": str(artifact_path),
        "predictions_path": str(predictions_path),
        "metrics_path": str(metrics_path),
        "model_metadata_path": str(model_metadata_path),
        "export_validation_path": str(export_validation_path),
        "metrics": metrics_by_split,
        "model_metadata": model_metadata,
        "export_validation": export_validation,
    }


def session_config_payload(config: TrainingSessionConfig) -> dict[str, Any]:
    return {
        "dataset_id": config.dataset_id,
        "dataset_kind": config.dataset_kind,
        "target_mode": config.target_mode,
        "model_names": config.model_names,
        "seed": config.seed,
        "split": {
            "train_size": config.split.train_size,
            "validation_size": config.split.validation_size,
            "test_size": config.split.test_size,
        },
        "model_params": config.model_params,
        "auto_build_features": config.auto_build_features,
        "overwrite_features": config.overwrite_features,
        "max_pairs": config.max_pairs,
    }


def copy_dataset_metadata(config: TrainingSessionConfig, session_dir: Path) -> dict[str, Any]:
    source_path = dataset_dir(config.dataset_kind, config.dataset_id) / "dataset_metadata.json"
    target_path = session_dir / "dataset_metadata.json"

    if source_path.exists():
        shutil.copy2(source_path, target_path)
        return read_json(target_path)

    fallback = {
        "dataset_id": config.dataset_id,
        "dataset_kind": config.dataset_kind,
        "warning": "dataset_metadata.json was not found in source dataset",
    }
    write_json(target_path, fallback)
    return fallback


def collect_model_artifacts(session_dir: Path) -> list[dict[str, Any]]:
    models_dir = session_dir / "models"
    artifacts: list[dict[str, Any]] = []

    if not models_dir.exists():
        return artifacts

    for model_dir in sorted(path for path in models_dir.iterdir() if path.is_dir()):
        metadata_path = model_dir / "model_metadata.json"
        validation_path = model_dir / "export_validation.json"
        metrics_path = model_dir / "metrics.json"

        metadata = read_json(metadata_path) if metadata_path.exists() else {}
        validation = read_json(validation_path) if validation_path.exists() else {}
        metrics = read_json(metrics_path) if metrics_path.exists() else {}

        artifacts.append(
            {
                "model_name": model_dir.name,
                "model_dir": str(model_dir),
                "metadata": metadata,
                "export_validation": validation,
                "metrics": metrics,
                "files": sorted(path.name for path in model_dir.iterdir() if path.is_file()),
            }
        )

    return artifacts


def run_training_session(config: TrainingSessionConfig) -> dict[str, Any]:
    validate_models(config.model_names)

    session_id = new_session_id()
    session_dir = TRAINING_SESSIONS_DIR / session_id

    if session_dir.exists():
        shutil.rmtree(session_dir)

    session_dir.mkdir(parents=True, exist_ok=True)

    started_at = utc_now_iso()
    feature_metadata = ensure_features(config)
    dataset_metadata = copy_dataset_metadata(config, session_dir)
    features, targets = read_training_frames(config.dataset_kind, config.dataset_id)
    frame, feature_columns = merged_training_frame(features, targets, config)

    if config.max_pairs is not None:
        frame = frame.head(config.max_pairs)

    train_frame = training_subset(frame)

    model_results: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []

    for model_name in config.model_names:
        model_dir = session_dir / "models" / model_name

        try:
            model_results.append(
                train_single_model(
                    model_name=model_name,
                    train_frame=train_frame,
                    full_frame=frame,
                    feature_columns=feature_columns,
                    config=config,
                    model_dir=model_dir,
                )
            )
        except (TrainingSessionError, TorchTrainingError, ValueError) as exc:
            failures.append({"model_name": model_name, "error": str(exc)})

    if not model_results:
        raise TrainingSessionError(f"No models were trained: {failures}")

    comparison_rows = [
        comparison_row(result["model_name"], result["metrics"])
        for result in model_results
    ]

    comparison_json_path = session_dir / "comparison_metrics.json"
    comparison_csv_path = session_dir / "comparison_metrics.csv"

    write_json(comparison_json_path, comparison_rows)
    write_csv(comparison_csv_path, comparison_rows)

    write_json(session_dir / "session_config.json", session_config_payload(config))
    write_json(session_dir / "feature_metadata.json", feature_metadata)

    session_summary = {
        "session_id": session_id,
        "status": "completed" if not failures else "completed_with_failures",
        "started_at": started_at,
        "completed_at": utc_now_iso(),
        "dataset_id": config.dataset_id,
        "dataset_kind": config.dataset_kind,
        "target_mode": config.target_mode,
        "feature_count": len(feature_columns),
        "rows": len(frame),
        "train_rows": len(train_frame),
        "trained_models": [result["model_name"] for result in model_results],
        "failed_models": failures,
        "comparison_metrics": comparison_rows,
        "dataset_metadata_available": bool(dataset_metadata),
        "feature_metadata_available": bool(feature_metadata),
        "paths": {
            "session_dir": str(session_dir),
            "comparison_metrics_json": str(comparison_json_path),
            "comparison_metrics_csv": str(comparison_csv_path),
            "session_config": str(session_dir / "session_config.json"),
            "dataset_metadata": str(session_dir / "dataset_metadata.json"),
            "feature_metadata": str(session_dir / "feature_metadata.json"),
            "session_summary": str(session_dir / "session_summary.json"),
        },
    }

    write_json(session_dir / "session_summary.json", session_summary)

    return {
        "status": session_summary["status"],
        "session_id": session_id,
        "session_dir": str(session_dir),
        "summary": session_summary,
        "models": model_results,
        "failures": failures,
        "artifacts": collect_model_artifacts(session_dir),
    }


def read_training_session(session_id: str) -> dict[str, Any]:
    session_dir = TRAINING_SESSIONS_DIR / session_id
    summary_path = session_dir / "session_summary.json"

    if not summary_path.exists():
        raise TrainingSessionError(f"Training session not found: {session_id}")

    config_path = session_dir / "session_config.json"
    comparison_path = session_dir / "comparison_metrics.json"
    dataset_metadata_path = session_dir / "dataset_metadata.json"
    feature_metadata_path = session_dir / "feature_metadata.json"

    return {
        "session_id": session_id,
        "session_dir": str(session_dir),
        "summary": read_json(summary_path),
        "config": read_json(config_path),
        "dataset_metadata": read_json(dataset_metadata_path),
        "feature_metadata": read_json(feature_metadata_path),
        "comparison_metrics": json.loads(comparison_path.read_text(encoding="utf-8")),
        "artifacts": collect_model_artifacts(session_dir),
    }


def read_training_model_artifact(session_id: str, model_name: str) -> dict[str, Any]:
    session_dir = TRAINING_SESSIONS_DIR / session_id
    model_dir = session_dir / "models" / model_name

    if not model_dir.exists():
        raise TrainingSessionError(f"Model artifact not found: {session_id}/{model_name}")

    metadata_path = model_dir / "model_metadata.json"
    validation_path = model_dir / "export_validation.json"
    metrics_path = model_dir / "metrics.json"
    predictions_path = model_dir / "predictions.parquet"

    predictions_preview: list[dict[str, Any]] = []
    prediction_rows = 0

    if predictions_path.exists():
        predictions = pd.read_parquet(predictions_path)
        prediction_rows = len(predictions)
        predictions_preview = predictions.head(20).to_dict(orient="records")

    return {
        "session_id": session_id,
        "model_name": model_name,
        "model_dir": str(model_dir),
        "metadata": read_json(metadata_path),
        "export_validation": read_json(validation_path),
        "metrics": read_json(metrics_path),
        "prediction_rows": prediction_rows,
        "predictions_preview": predictions_preview,
        "files": sorted(path.name for path in model_dir.iterdir() if path.is_file()),
    }


def list_training_sessions() -> dict[str, Any]:
    TRAINING_SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    sessions: list[dict[str, Any]] = []

    for path in sorted(TRAINING_SESSIONS_DIR.iterdir(), reverse=True):
        if not path.is_dir():
            continue

        summary_path = path / "session_summary.json"
        if not summary_path.exists():
            continue

        try:
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue

        sessions.append(
            {
                "session_id": path.name,
                "status": summary.get("status"),
                "dataset_id": summary.get("dataset_id"),
                "dataset_kind": summary.get("dataset_kind"),
                "target_mode": summary.get("target_mode"),
                "feature_count": summary.get("feature_count"),
                "rows": summary.get("rows"),
                "trained_models": summary.get("trained_models", []),
                "failed_models": summary.get("failed_models", []),
                "completed_at": summary.get("completed_at"),
                "session_dir": str(path),
            }
        )

    return {
        "sessions": sessions,
        "total": len(sessions),
        "training_sessions_dir": str(TRAINING_SESSIONS_DIR),
    }