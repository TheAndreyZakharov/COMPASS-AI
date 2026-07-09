from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sandbox_app.backend.core.paths import PATHS
from sandbox_app.backend.training.train_session import TRAINING_SESSIONS_DIR
from sklearn.preprocessing import StandardScaler


class ModelLoadError(RuntimeError):
    """Raised when a saved sandbox model cannot be loaded."""


@dataclass
class LoadedSandboxModel:
    model_name: str
    model_dir: Path
    artifact_path: Path
    artifact_format: str
    feature_names: list[str]
    metadata: dict[str, Any]
    model: Any

    def align_features(self, features: pd.DataFrame) -> pd.DataFrame:
        aligned = features.copy()

        for feature_name in self.feature_names:
            if feature_name not in aligned.columns:
                aligned[feature_name] = 0.0

        aligned = aligned[self.feature_names]
        return aligned.fillna(0.0).astype(float)

    def predict_scores(self, features: pd.DataFrame) -> np.ndarray:
        aligned = self.align_features(features)

        if self.artifact_format == "pt":
            return predict_torch_scores(self.model, aligned)

        if hasattr(self.model, "predict_score"):
            scores = self.model.predict_score(aligned)
            return np.clip(np.asarray(scores, dtype=float), 0.0, 1.0)

        if hasattr(self.model, "predict_proba"):
            probabilities = self.model.predict_proba(aligned)
            if probabilities.shape[1] == 1:
                return np.clip(np.asarray(probabilities[:, 0], dtype=float), 0.0, 1.0)
            return np.clip(np.asarray(probabilities[:, 1], dtype=float), 0.0, 1.0)

        if hasattr(self.model, "decision_function"):
            decision = np.asarray(self.model.decision_function(aligned), dtype=float)
            return np.clip(1.0 / (1.0 + np.exp(-decision)), 0.0, 1.0)

        if hasattr(self.model, "predict"):
            predictions = np.asarray(self.model.predict(aligned), dtype=float)
            return np.clip(predictions, 0.0, 1.0)

        raise ModelLoadError(f"Model does not support inference: {self.model_name}")


@dataclass
class TorchLoadedModel:
    model: Any
    scaler: StandardScaler
    feature_names: list[str]

    def predict_score(self, features: pd.DataFrame) -> np.ndarray:
        return predict_torch_scores(self, features)


def read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ModelLoadError(f"Could not read JSON file: {path}") from exc

    if not isinstance(payload, dict):
        raise ModelLoadError(f"JSON file must contain an object: {path}")

    return payload


def build_torch_mlp(input_dim: int, hidden_size: int, dropout: float):
    try:
        from torch import nn
    except ImportError as exc:
        raise ModelLoadError("PyTorch is not installed") from exc

    second_layer_size = max(4, hidden_size // 2)

    return nn.Sequential(
        nn.Linear(input_dim, hidden_size),
        nn.ReLU(),
        nn.Dropout(dropout),
        nn.Linear(hidden_size, second_layer_size),
        nn.ReLU(),
        nn.Linear(second_layer_size, 1),
    )


def load_torch_model(artifact_path: Path) -> TorchLoadedModel:
    try:
        import torch
    except ImportError as exc:
        raise ModelLoadError("PyTorch is not installed") from exc

    try:
        checkpoint = torch.load(artifact_path, map_location="cpu")
    except Exception as exc:
        raise ModelLoadError(f"Could not load PyTorch artifact: {artifact_path}") from exc

    feature_names = list(checkpoint.get("feature_names") or [])
    if not feature_names:
        raise ModelLoadError("PyTorch artifact does not contain feature_names")

    config = checkpoint.get("config") or {}
    hidden_size = int(config.get("hidden_size", 64))
    dropout = float(config.get("dropout", 0.0))

    model = build_torch_mlp(
        input_dim=len(feature_names),
        hidden_size=hidden_size,
        dropout=dropout,
    )
    model.load_state_dict(checkpoint["state_dict"])
    model.eval()

    scaler = StandardScaler()
    scaler.mean_ = np.asarray(checkpoint["scaler_mean"], dtype=float)
    scaler.scale_ = np.asarray(checkpoint["scaler_scale"], dtype=float)
    scaler.var_ = scaler.scale_**2
    scaler.n_features_in_ = len(feature_names)
    scaler.feature_names_in_ = np.asarray(feature_names, dtype=object)

    return TorchLoadedModel(model=model, scaler=scaler, feature_names=feature_names)


def predict_torch_scores(model: Any, features: pd.DataFrame) -> np.ndarray:
    try:
        import torch
    except ImportError as exc:
        raise ModelLoadError("PyTorch is not installed") from exc

    feature_names = list(getattr(model, "feature_names", []))
    scaler = getattr(model, "scaler", None)
    torch_model = getattr(model, "model", None)

    if not feature_names or scaler is None or torch_model is None:
        raise ModelLoadError("Invalid loaded PyTorch model")

    aligned = features.copy()

    for feature_name in feature_names:
        if feature_name not in aligned.columns:
            aligned[feature_name] = 0.0

    matrix = scaler.transform(aligned[feature_names].fillna(0.0).astype(float))
    tensor = torch.tensor(matrix, dtype=torch.float32)

    torch_model.eval()
    with torch.no_grad():
        logits = torch_model(tensor).reshape(-1)
        scores = torch.sigmoid(logits).cpu().numpy()

    return np.clip(scores, 0.0, 1.0)


def model_dir_for(session_id: str, model_name: str) -> Path:
    model_dir = TRAINING_SESSIONS_DIR / session_id / "models" / model_name

    if not model_dir.exists():
        raise ModelLoadError(f"Model artifact not found: {session_id}/{model_name}")

    return model_dir


def load_model_from_dir(model_dir: Path) -> LoadedSandboxModel:
    metadata_path = model_dir / "model_metadata.json"

    if not metadata_path.exists():
        raise ModelLoadError(f"model_metadata.json not found: {model_dir}")

    metadata = read_json(metadata_path)
    model_name = str(metadata.get("model_name") or model_dir.name)
    artifact_format = str(metadata.get("artifact_format") or "")
    feature_names = list(metadata.get("feature_names") or [])

    if not feature_names:
        raise ModelLoadError(f"feature_names are missing for model: {model_name}")

    artifact_path = Path(str(metadata.get("artifact_path") or ""))
    if not artifact_path.exists():
        artifact_path = model_dir / f"model.{artifact_format}"

    if not artifact_path.exists():
        raise ModelLoadError(f"Model artifact not found: {artifact_path}")

    if artifact_format == "pt":
        model = load_torch_model(artifact_path)
    elif artifact_format == "joblib":
        try:
            model = joblib.load(artifact_path)
        except Exception as exc:
            raise ModelLoadError(f"Could not load joblib artifact: {artifact_path}") from exc
    else:
        raise ModelLoadError(f"Unsupported artifact format: {artifact_format}")

    return LoadedSandboxModel(
        model_name=model_name,
        model_dir=model_dir,
        artifact_path=artifact_path,
        artifact_format=artifact_format,
        feature_names=feature_names,
        metadata=metadata,
        model=model,
    )


def load_model(session_id: str, model_name: str) -> LoadedSandboxModel:
    return load_model_from_dir(model_dir_for(session_id, model_name))


def dataset_features_path(metadata: dict[str, Any]) -> Path:
    dataset_id = str(metadata.get("dataset_id") or "")
    dataset_kind = str(metadata.get("dataset_kind") or "generated")

    if not dataset_id:
        raise ModelLoadError("dataset_id is missing in model metadata")

    path = PATHS.data_dir / dataset_kind / dataset_id / "features" / "features.parquet"

    if not path.exists():
        raise ModelLoadError(f"features.parquet not found: {path}")

    return path


def load_model_features(metadata: dict[str, Any]) -> pd.DataFrame:
    return pd.read_parquet(dataset_features_path(metadata))


def load_saved_predictions(model_dir: Path) -> pd.DataFrame:
    predictions_path = model_dir / "predictions.parquet"

    if not predictions_path.exists():
        raise ModelLoadError(f"predictions.parquet not found: {model_dir}")

    return pd.read_parquet(predictions_path)


def load_validation_frame(
    loaded_model: LoadedSandboxModel,
    sample_size: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    features = load_model_features(loaded_model.metadata)
    predictions = load_saved_predictions(loaded_model.model_dir)

    if "pair_id" not in features.columns or "pair_id" not in predictions.columns:
        raise ModelLoadError("features and predictions must contain pair_id")

    joined = features.merge(
        predictions[["pair_id", "predicted_score"]],
        on="pair_id",
        how="inner",
    )

    if joined.empty:
        raise ModelLoadError("No overlapping pair_id rows for validation")

    joined = joined.head(sample_size)
    saved_predictions = joined[["pair_id", "predicted_score"]].copy()
    feature_frame = joined.drop(columns=["predicted_score"])

    return feature_frame, saved_predictions


def list_available_models() -> dict[str, Any]:
    TRAINING_SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    models: list[dict[str, Any]] = []

    for session_dir in sorted(TRAINING_SESSIONS_DIR.iterdir(), reverse=True):
        models_dir = session_dir / "models"
        if not models_dir.exists():
            continue

        for model_dir in sorted(path for path in models_dir.iterdir() if path.is_dir()):
            metadata_path = model_dir / "model_metadata.json"
            validation_path = model_dir / "export_validation.json"

            metadata = read_json(metadata_path) if metadata_path.exists() else {}
            validation = read_json(validation_path) if validation_path.exists() else {}

            models.append(
                {
                    "session_id": session_dir.name,
                    "model_name": model_dir.name,
                    "artifact_format": metadata.get("artifact_format"),
                    "dataset_id": metadata.get("dataset_id"),
                    "dataset_kind": metadata.get("dataset_kind"),
                    "target_mode": metadata.get("target_mode"),
                    "feature_count": metadata.get("feature_count"),
                    "export_validation_status": validation.get("status"),
                    "model_dir": str(model_dir),
                    "artifact_path": metadata.get("artifact_path"),
                    "onnx_path": metadata.get("onnx_path"),
                }
            )

    return {
        "models": models,
        "total": len(models),
        "training_sessions_dir": str(TRAINING_SESSIONS_DIR),
    }

def load_sandbox_model(session_id: str, model_name: str) -> LoadedSandboxModel:
    return load_model(session_id, model_name)