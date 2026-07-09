from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from sandbox_app.backend.reports.html_export import (
    ExportError,
    read_json,
    write_report_bundle,
)

SANDBOX_DIR = Path(__file__).resolve().parents[2]
TRAINING_SESSIONS_DIR = SANDBOX_DIR / "training_sessions"


def training_session_dir(session_id: str) -> Path:
    path = TRAINING_SESSIONS_DIR / session_id

    if not path.exists() or not path.is_dir():
        raise ExportError(f"Training session not found: {session_id}")

    return path


def read_csv_metrics(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8", newline="") as file_obj:
        return [dict(row) for row in csv.DictReader(file_obj)]


def model_artifacts(session_dir: Path) -> list[dict[str, Any]]:
    models_dir = session_dir / "models"

    if not models_dir.exists():
        return []

    artifacts = []

    for model_dir in sorted(models_dir.iterdir()):
        if not model_dir.is_dir():
            continue

        metrics = read_json(model_dir / "metrics.json", default={})
        metadata = read_json(model_dir / "model_metadata.json", default={})
        validation = read_json(model_dir / "export_validation.json", default={})
        files = sorted(path.name for path in model_dir.iterdir() if path.is_file())

        artifacts.append(
            {
                "model_name": model_dir.name,
                "metrics": metrics,
                "metadata": metadata,
                "validation": validation,
                "files": files,
                "has_joblib": "model.joblib" in files,
                "has_pt": "model.pt" in files,
                "has_onnx": "model.onnx" in files,
            }
        )

    return artifacts


def flatten_model_metrics(artifacts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []

    for artifact in artifacts:
        metrics = artifact.get("metrics", {})
        validation = artifact.get("validation", {})

        row = {
            "model_name": artifact.get("model_name"),
            "validation_status": validation.get("status"),
            "has_joblib": artifact.get("has_joblib"),
            "has_pt": artifact.get("has_pt"),
            "has_onnx": artifact.get("has_onnx"),
        }

        if isinstance(metrics, dict):
            for key, value in metrics.items():
                if isinstance(value, (str, int, float, bool)) or value is None:
                    row[key] = value

        rows.append(row)

    return rows


def generate_model_report(session_id: str) -> dict[str, Any]:
    session_dir = training_session_dir(session_id)
    summary = read_json(session_dir / "session_summary.json", default={})
    config = read_json(session_dir / "session_config.json", default={})
    dataset_metadata = read_json(session_dir / "dataset_metadata.json", default={})
    feature_metadata = read_json(session_dir / "feature_metadata.json", default={})
    comparison_json = read_json(session_dir / "comparison_metrics.json", default={})
    comparison_csv = read_csv_metrics(session_dir / "comparison_metrics.csv")
    artifacts = model_artifacts(session_dir)
    artifact_rows = flatten_model_metrics(artifacts)

    payload = {
        "summary": {
            "session_id": session_id,
            "models": len(artifacts),
            "comparison_rows": len(comparison_csv),
            "dataset_id": dataset_metadata.get("dataset_id"),
            "target_mode": config.get("target_mode"),
        },
        "sections": [
            {
                "title": "Model comparison report",
                "body": "Сравнение сохранённых моделей, metrics, artifacts и validation status.",
            }
        ],
        "session_id": session_id,
        "session_dir": str(session_dir),
        "session_summary": summary,
        "session_config": config,
        "dataset_metadata": dataset_metadata,
        "feature_metadata": feature_metadata,
        "comparison_metrics": comparison_json,
        "models": artifacts,
    }

    return write_report_bundle(
        kind="model",
        source_id=session_id,
        title=f"Model comparison report · {session_id}",
        payload=payload,
        tables={
            "comparison_metrics": comparison_csv,
            "model_artifacts": artifact_rows,
        },
    )