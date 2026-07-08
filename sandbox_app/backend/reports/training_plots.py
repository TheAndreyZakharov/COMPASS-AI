from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.calibration import calibration_curve
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    PrecisionRecallDisplay,
    RocCurveDisplay,
    confusion_matrix,
    precision_recall_curve,
    roc_curve,
)


class TrainingPlotError(RuntimeError):
    """Raised when training plots cannot be generated."""


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise TrainingPlotError(f"Could not read JSON file: {path}") from exc


def save_figure(path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(path, dpi=140, bbox_inches="tight")
    plt.close()
    return str(path)


def safe_series(frame: pd.DataFrame, column: str, default: float = 0.0) -> pd.Series:
    if column not in frame.columns:
        return pd.Series([default] * len(frame), index=frame.index)

    return pd.to_numeric(frame[column], errors="coerce").fillna(default)


def plot_score_distribution(predictions: pd.DataFrame, path: Path) -> str:
    scores = safe_series(predictions, "predicted_score")
    plt.figure(figsize=(8, 5))
    plt.hist(scores, bins=20)
    plt.title("Score distribution")
    plt.xlabel("Predicted score")
    plt.ylabel("Rows")
    return save_figure(path)


def plot_confusion(predictions: pd.DataFrame, path: Path) -> str:
    y_true = safe_series(predictions, "label").astype(int)
    y_score = safe_series(predictions, "predicted_score")
    y_pred = (y_score >= 0.5).astype(int)
    matrix = confusion_matrix(y_true, y_pred, labels=[0, 1])

    plt.figure(figsize=(6, 5))
    display = ConfusionMatrixDisplay(confusion_matrix=matrix, display_labels=[0, 1])
    display.plot(values_format="d")
    plt.title("Confusion matrix")
    return save_figure(path)


def plot_roc(predictions: pd.DataFrame, path: Path) -> str | None:
    y_true = safe_series(predictions, "label").astype(int)
    y_score = safe_series(predictions, "predicted_score")

    if y_true.nunique() < 2:
        return None

    fpr, tpr, _ = roc_curve(y_true, y_score)
    plt.figure(figsize=(7, 5))
    display = RocCurveDisplay(fpr=fpr, tpr=tpr)
    display.plot()
    plt.title("ROC curve")
    return save_figure(path)


def plot_precision_recall(predictions: pd.DataFrame, path: Path) -> str | None:
    y_true = safe_series(predictions, "label").astype(int)
    y_score = safe_series(predictions, "predicted_score")

    if y_true.nunique() < 2:
        return None

    precision, recall, _ = precision_recall_curve(y_true, y_score)
    plt.figure(figsize=(7, 5))
    display = PrecisionRecallDisplay(precision=precision, recall=recall)
    display.plot()
    plt.title("Precision-recall curve")
    return save_figure(path)


def plot_calibration(predictions: pd.DataFrame, path: Path) -> str | None:
    y_true = safe_series(predictions, "label").astype(int)
    y_score = safe_series(predictions, "predicted_score")

    if y_true.nunique() < 2:
        return None

    fraction_positive, mean_predicted = calibration_curve(
        y_true,
        np.clip(y_score, 1e-6, 1.0 - 1e-6),
        n_bins=8,
        strategy="uniform",
    )

    plt.figure(figsize=(7, 5))
    plt.plot(mean_predicted, fraction_positive, marker="o")
    plt.plot([0, 1], [0, 1], linestyle="--")
    plt.title("Calibration plot")
    plt.xlabel("Mean predicted score")
    plt.ylabel("Fraction of positives")
    return save_figure(path)


def plot_learning_curve(metrics: dict[str, Any], path: Path) -> str | None:
    rows: list[dict[str, Any]] = []

    for split_name in ("train", "validation", "test", "all"):
        split_metrics = metrics.get(split_name)
        if not isinstance(split_metrics, dict):
            continue

        rows.append(
            {
                "split": split_name,
                "f1": split_metrics.get("f1"),
                "accuracy": split_metrics.get("accuracy"),
                "roc_auc": split_metrics.get("roc_auc"),
            }
        )

    if not rows:
        return None

    frame = pd.DataFrame(rows)
    frame = frame.set_index("split")
    metric_columns = [
        column
        for column in ("f1", "accuracy", "roc_auc")
        if column in frame.columns and frame[column].notna().any()
    ]

    if not metric_columns:
        return None

    plt.figure(figsize=(8, 5))
    for metric_name in metric_columns:
        plt.plot(frame.index, frame[metric_name], marker="o", label=metric_name)

    plt.title("Learning curve by split")
    plt.xlabel("Split")
    plt.ylabel("Metric")
    plt.ylim(0.0, 1.05)
    plt.legend()
    return save_figure(path)


def plot_loss_curve(metadata: dict[str, Any], path: Path) -> str | None:
    history = metadata.get("training_history") or {}
    loss_history = history.get("loss_history")

    if not isinstance(loss_history, list) or not loss_history:
        return None

    losses = [float(value) for value in loss_history]

    plt.figure(figsize=(8, 5))
    plt.plot(range(1, len(losses) + 1), losses, marker="o")
    plt.title("PyTorch loss curve")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    return save_figure(path)


def plot_feature_importance(
    predictions: pd.DataFrame,
    metadata: dict[str, Any],
    path: Path,
) -> str | None:
    feature_names = metadata.get("feature_names")
    if not isinstance(feature_names, list) or not feature_names:
        return None

    candidate_columns = [
        column
        for column in predictions.columns
        if column.startswith("feature_") or column in feature_names
    ]

    if candidate_columns:
        values = (
            predictions[candidate_columns]
            .apply(pd.to_numeric, errors="coerce")
            .fillna(0.0)
            .abs()
            .mean()
            .sort_values(ascending=False)
            .head(20)
        )
    else:
        top_features = feature_names[:20]
        values = pd.Series(
            np.linspace(len(top_features), 1, len(top_features)),
            index=top_features,
        )

    if values.empty:
        return None

    plt.figure(figsize=(9, 6))
    values.sort_values().plot(kind="barh")
    plt.title("Feature importance proxy")
    plt.xlabel("Importance")
    return save_figure(path)


def plot_model_comparison(comparison_rows: list[dict[str, Any]], path: Path) -> str | None:
    if not comparison_rows:
        return None

    frame = pd.DataFrame(comparison_rows)
    if "model_name" not in frame.columns:
        return None

    metric_columns = [
        column
        for column in ("roc_auc", "f1", "accuracy", "top_1_accuracy", "top_3_accuracy")
        if column in frame.columns and frame[column].notna().any()
    ]

    if not metric_columns:
        return None

    frame = frame.set_index("model_name")[metric_columns].apply(
        pd.to_numeric,
        errors="coerce",
    )

    plt.figure(figsize=(10, 6))
    frame.plot(kind="bar")
    plt.title("Model comparison")
    plt.xlabel("Model")
    plt.ylabel("Metric")
    plt.ylim(0.0, 1.05)
    plt.xticks(rotation=30, ha="right")
    return save_figure(path)


def generate_model_plots(model_dir: Path, plots_dir: Path) -> dict[str, str]:
    predictions_path = model_dir / "predictions.parquet"
    metrics_path = model_dir / "metrics.json"
    metadata_path = model_dir / "model_metadata.json"

    if not predictions_path.exists():
        raise TrainingPlotError(f"predictions.parquet not found: {model_dir}")

    predictions = pd.read_parquet(predictions_path)
    metrics = read_json(metrics_path) if metrics_path.exists() else {}
    metadata = read_json(metadata_path) if metadata_path.exists() else {}

    model_name = model_dir.name
    model_plots_dir = plots_dir / model_name
    paths: dict[str, str] = {}

    paths["score_distribution"] = plot_score_distribution(
        predictions,
        model_plots_dir / "score_distribution.png",
    )
    paths["confusion_matrix"] = plot_confusion(
        predictions,
        model_plots_dir / "confusion_matrix.png",
    )

    roc_path = plot_roc(predictions, model_plots_dir / "roc_curve.png")
    if roc_path:
        paths["roc_curve"] = roc_path

    pr_path = plot_precision_recall(
        predictions,
        model_plots_dir / "precision_recall_curve.png",
    )
    if pr_path:
        paths["precision_recall_curve"] = pr_path

    calibration_path = plot_calibration(predictions, model_plots_dir / "calibration_plot.png")
    if calibration_path:
        paths["calibration_plot"] = calibration_path

    learning_path = plot_learning_curve(metrics, model_plots_dir / "learning_curve.png")
    if learning_path:
        paths["learning_curve"] = learning_path

    loss_path = plot_loss_curve(metadata, model_plots_dir / "loss_curve.png")
    if loss_path:
        paths["loss_curve"] = loss_path

    feature_path = plot_feature_importance(
        predictions,
        metadata,
        model_plots_dir / "feature_importance.png",
    )
    if feature_path:
        paths["feature_importance"] = feature_path

    return paths


def generate_training_plots(session_dir: Path) -> dict[str, Any]:
    models_dir = session_dir / "models"
    plots_dir = session_dir / "reports" / "plots"
    comparison_path = session_dir / "comparison_metrics.json"

    if not models_dir.exists():
        raise TrainingPlotError(f"models directory not found: {session_dir}")

    model_plots: dict[str, dict[str, str]] = {}

    for model_dir in sorted(path for path in models_dir.iterdir() if path.is_dir()):
        model_plots[model_dir.name] = generate_model_plots(model_dir, plots_dir)

    comparison_rows = read_json(comparison_path) if comparison_path.exists() else []
    if not isinstance(comparison_rows, list):
        comparison_rows = []

    session_plots: dict[str, str] = {}
    comparison_plot = plot_model_comparison(
        comparison_rows,
        plots_dir / "model_comparison.png",
    )
    if comparison_plot:
        session_plots["model_comparison"] = comparison_plot

    return {
        "session_plots": session_plots,
        "model_plots": model_plots,
        "plots_dir": str(plots_dir),
    }