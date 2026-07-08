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
        normalized = normalized.replace({"val": "validation", "dev": "validation"})
        return normalized

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


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = sorted({field_name for row in rows for field_name in row})
    with path.open("w", encoding="utf-8", newline="") as file_obj:
        writer = csv.DictWriter(file_obj, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def validate_models(model_names: list[str]) -> list[str]:
    if not model_names:
        raise TrainingSessionError("At least one model is required")

    invalid = sorted(set(model_names) - SUPPORTED_MODELS)
    if invalid:
        allowed = ", ".join(sorted(SUPPORTED_MODELS))
        raise TrainingSessionError(f"Unsupported models {invalid}. Allowed: {allowed}")

    return model_names


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

    if model_name == "baseline_rule_based":
        model = train_baseline_model(x_train, y_train, params)
        scores = model.predict_score(x_full)
        artifact_path = model_dir / "model.joblib"
        model.save(artifact_path)
    elif model_name in SKLEARN_MODEL_NAMES:
        model = train_sklearn_model(model_name, x_train, y_train, config.seed, params)
        scores = sklearn_positive_scores(model, x_full)
        artifact_path = model_dir / "model.joblib"
        save_sklearn_model(model, artifact_path)
    elif model_name == "torch_mlp":
        model = train_torch_mlp(x_train, y_train, config.seed, params)
        scores = model.predict_score(x_full)
        artifact_path = model_dir / "model.pt"
        model.save(artifact_path)
    else:
        raise TrainingSessionError(f"Unsupported model: {model_name}")

    predictions = prediction_frame(model_name, full_frame, feature_columns, scores)
    metrics_by_split = evaluate_by_split(predictions)

    predictions_path = model_dir / "predictions.parquet"
    metrics_path = model_dir / "metrics.json"

    model_dir.mkdir(parents=True, exist_ok=True)
    predictions.to_parquet(predictions_path, index=False)
    write_json(metrics_path, metrics_by_split)

    return {
        "model_name": model_name,
        "status": "trained",
        "artifact_path": str(artifact_path),
        "predictions_path": str(predictions_path),
        "metrics_path": str(metrics_path),
        "metrics": metrics_by_split,
    }


def run_training_session(config: TrainingSessionConfig) -> dict[str, Any]:
    validate_models(config.model_names)

    session_id = new_session_id()
    session_dir = TRAINING_SESSIONS_DIR / session_id

    if session_dir.exists():
        shutil.rmtree(session_dir)

    session_dir.mkdir(parents=True, exist_ok=True)

    started_at = utc_now_iso()
    feature_metadata = ensure_features(config)
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

    session_config = {
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
        "trained_models": [result["model_name"] for result in model_results],
        "failed_models": failures,
        "comparison_metrics": comparison_rows,
        "paths": {
            "session_dir": str(session_dir),
            "comparison_metrics_json": str(comparison_json_path),
            "comparison_metrics_csv": str(comparison_csv_path),
        },
    }

    write_json(session_dir / "session_config.json", session_config)
    write_json(session_dir / "feature_metadata.json", feature_metadata)
    write_json(session_dir / "session_summary.json", session_summary)

    dataset_metadata_path = (
        dataset_dir(config.dataset_kind, config.dataset_id) / "dataset_metadata.json"
    )
    if dataset_metadata_path.exists():
        shutil.copy2(dataset_metadata_path, session_dir / "dataset_metadata.json")

    return {
        "status": session_summary["status"],
        "session_id": session_id,
        "session_dir": str(session_dir),
        "summary": session_summary,
        "models": model_results,
        "failures": failures,
    }


def read_training_session(session_id: str) -> dict[str, Any]:
    session_dir = TRAINING_SESSIONS_DIR / session_id
    summary_path = session_dir / "session_summary.json"

    if not summary_path.exists():
        raise TrainingSessionError(f"Training session not found: {session_id}")

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    config_path = session_dir / "session_config.json"
    comparison_path = session_dir / "comparison_metrics.json"

    return {
        "session_id": session_id,
        "session_dir": str(session_dir),
        "summary": summary,
        "config": json.loads(config_path.read_text(encoding="utf-8")),
        "comparison_metrics": json.loads(comparison_path.read_text(encoding="utf-8")),
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
                "trained_models": summary.get("trained_models", []),
                "completed_at": summary.get("completed_at"),
                "session_dir": str(path),
            }
        )

    return {
        "sessions": sessions,
        "total": len(sessions),
        "training_sessions_dir": str(TRAINING_SESSIONS_DIR),
    }