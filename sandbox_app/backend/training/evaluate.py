from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    log_loss,
    mean_absolute_error,
    precision_score,
    recall_score,
    roc_auc_score,
)


def safe_float(value: Any) -> float | None:
    if value is None:
        return None

    try:
        result = float(value)
    except (TypeError, ValueError):
        return None

    if np.isnan(result) or np.isinf(result):
        return None

    return result


def safe_metric(callback, *args: Any, **kwargs: Any) -> float | None:
    try:
        value = callback(*args, **kwargs)
    except Exception:
        return None

    return safe_float(value)


def binary_predictions(scores: np.ndarray, threshold: float = 0.5) -> np.ndarray:
    return (scores >= threshold).astype(int)


def top_k_accuracy(predictions: pd.DataFrame, k: int) -> float | None:
    required_columns = {"task_id", "label", "predicted_score"}
    if not required_columns.issubset(predictions.columns):
        return None

    task_groups = predictions.groupby("task_id", dropna=False)
    total_tasks = 0
    successful_tasks = 0

    for _, group in task_groups:
        labels = group["label"].astype(int)
        if labels.max() <= 0:
            continue

        top_group = group.sort_values("predicted_score", ascending=False).head(k)
        total_tasks += 1
        successful_tasks += int(top_group["label"].astype(int).max() > 0)

    if total_tasks == 0:
        return None

    return successful_tasks / total_tasks


def evaluate_predictions(predictions: pd.DataFrame) -> dict[str, float | None]:
    if predictions.empty:
        return {
            "roc_auc": None,
            "f1": None,
            "precision": None,
            "recall": None,
            "accuracy": None,
            "log_loss": None,
            "mae_for_score": None,
            "top_1_accuracy": None,
            "top_3_accuracy": None,
        }

    y_true = predictions["label"].astype(int).to_numpy()
    y_score = predictions["predicted_score"].astype(float).to_numpy()
    y_pred = binary_predictions(y_score)

    metrics = {
        "roc_auc": safe_metric(roc_auc_score, y_true, y_score),
        "f1": safe_metric(f1_score, y_true, y_pred, zero_division=0),
        "precision": safe_metric(precision_score, y_true, y_pred, zero_division=0),
        "recall": safe_metric(recall_score, y_true, y_pred, zero_division=0),
        "accuracy": safe_metric(accuracy_score, y_true, y_pred),
        "log_loss": safe_metric(log_loss, y_true, np.clip(y_score, 1e-6, 1.0 - 1e-6)),
        "mae_for_score": None,
        "top_1_accuracy": top_k_accuracy(predictions, 1),
        "top_3_accuracy": top_k_accuracy(predictions, 3),
    }

    if "target_score" in predictions.columns:
        metrics["mae_for_score"] = safe_metric(
            mean_absolute_error,
            predictions["target_score"].astype(float).to_numpy(),
            y_score,
        )

    return metrics


def evaluate_by_split(predictions: pd.DataFrame) -> dict[str, dict[str, float | None]]:
    if "split" not in predictions.columns:
        return {"all": evaluate_predictions(predictions)}

    result: dict[str, dict[str, float | None]] = {}

    for split_name, split_frame in predictions.groupby("split", dropna=False):
        result[str(split_name)] = evaluate_predictions(split_frame)

    if "test" not in result:
        result["test"] = evaluate_predictions(predictions)

    return result


def comparison_row(
    model_name: str,
    metrics_by_split: dict[str, dict[str, float | None]],
) -> dict[str, Any]:
    test_metrics = metrics_by_split.get("test") or metrics_by_split.get("all") or {}

    return {
        "model_name": model_name,
        "roc_auc": test_metrics.get("roc_auc"),
        "f1": test_metrics.get("f1"),
        "precision": test_metrics.get("precision"),
        "recall": test_metrics.get("recall"),
        "accuracy": test_metrics.get("accuracy"),
        "log_loss": test_metrics.get("log_loss"),
        "mae_for_score": test_metrics.get("mae_for_score"),
        "top_1_accuracy": test_metrics.get("top_1_accuracy"),
        "top_3_accuracy": test_metrics.get("top_3_accuracy"),
    }