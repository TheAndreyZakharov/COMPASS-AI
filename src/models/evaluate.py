from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from src.models.dataset import (
    TEST_PATH,
    AssignmentPairDataset,
    create_dataloader,
    load_feature_spec,
)
from src.models.matching_net import MatchingNetConfig, TaskEmployeeMatchingNet
from src.models.train import move_batch_to_device, select_device

PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_PATH = PROJECT_ROOT / "models" / "compass_matching_model.pt"
MODEL_METRICS_PATH = PROJECT_ROOT / "reports" / "model_metrics.json"
TEST_PREDICTIONS_PATH = PROJECT_ROOT / "reports" / "test_predictions.csv"


def load_checkpoint(path: Path = MODEL_PATH) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(
            f"Missing checkpoint: {path}. Run: python src/models/train.py"
        )

    return torch.load(path, map_location="cpu")


def build_model_from_checkpoint(checkpoint: dict[str, Any]) -> TaskEmployeeMatchingNet:
    config_payload = checkpoint["model_config"]

    config = MatchingNetConfig(
        task_input_dim=int(config_payload["task_input_dim"]),
        employee_input_dim=int(config_payload["employee_input_dim"]),
        pair_input_dim=int(config_payload["pair_input_dim"]),
        task_embedding_dim=int(config_payload["task_embedding_dim"]),
        employee_embedding_dim=int(config_payload["employee_embedding_dim"]),
        hidden_dim=int(config_payload["hidden_dim"]),
        dropout=float(config_payload["dropout"]),
    )

    model = TaskEmployeeMatchingNet(config)
    model.load_state_dict(checkpoint["model_state_dict"])

    return model


@torch.no_grad()
def predict_test_set(
    model: TaskEmployeeMatchingNet,
    dataset: AssignmentPairDataset,
    device: torch.device,
    batch_size: int = 512,
) -> pd.DataFrame:
    dataloader = create_dataloader(
        TEST_PATH,
        batch_size=batch_size,
        shuffle=False,
        feature_spec=dataset.feature_spec,
    )

    model.eval()
    model.to(device)

    probabilities: list[float] = []

    for batch in dataloader:
        batch_on_device = move_batch_to_device(batch, device)

        output = model(
            batch_on_device["task_features"],
            batch_on_device["employee_features"],
            batch_on_device["pair_features"],
        )

        batch_probabilities = (
            output["success_probability"]
            .detach()
            .cpu()
            .numpy()
            .reshape(-1)
            .tolist()
        )

        probabilities.extend(float(value) for value in batch_probabilities)

    predictions = pd.DataFrame(
        {
            "assignment_id": dataset.assignment_ids,
            "task_id": dataset.task_ids,
            "employee_id": dataset.employee_ids,
            "success_label": dataset.labels.numpy().reshape(-1).astype(int),
            "success_probability": probabilities,
        }
    )

    predictions["prediction"] = (
        predictions["success_probability"] >= 0.5
    ).astype(int)

    return predictions


def safe_roc_auc(labels: np.ndarray, probabilities: np.ndarray) -> float:
    if len(set(labels.tolist())) < 2:
        return 0.5

    return float(roc_auc_score(labels, probabilities))


def safe_pr_auc(labels: np.ndarray, probabilities: np.ndarray) -> float:
    if len(set(labels.tolist())) < 2:
        return 0.5

    return float(average_precision_score(labels, probabilities))


def compute_metrics(predictions: pd.DataFrame) -> dict[str, float]:
    labels = predictions["success_label"].to_numpy()
    predicted_labels = predictions["prediction"].to_numpy()
    probabilities = predictions["success_probability"].to_numpy()

    return {
        "accuracy": float(accuracy_score(labels, predicted_labels)),
        "precision": float(
            precision_score(labels, predicted_labels, zero_division=0)
        ),
        "recall": float(recall_score(labels, predicted_labels, zero_division=0)),
        "f1": float(f1_score(labels, predicted_labels, zero_division=0)),
        "roc_auc": safe_roc_auc(labels, probabilities),
        "pr_auc": safe_pr_auc(labels, probabilities),
        "positive_rate": float(np.mean(labels)),
        "predicted_positive_rate": float(np.mean(predicted_labels)),
        "rows": float(len(predictions)),
    }


def save_metrics(metrics: dict[str, float], path: Path = MODEL_METRICS_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    rounded_metrics = {
        key: round(value, 6)
        for key, value in metrics.items()
    }

    with path.open("w", encoding="utf-8") as file:
        json.dump(rounded_metrics, file, ensure_ascii=False, indent=2)


def main() -> None:
    feature_spec = load_feature_spec()
    dataset = AssignmentPairDataset(TEST_PATH, feature_spec=feature_spec)
    checkpoint = load_checkpoint()
    model = build_model_from_checkpoint(checkpoint)
    device = select_device()

    predictions = predict_test_set(
        model=model,
        dataset=dataset,
        device=device,
    )
    metrics = compute_metrics(predictions)

    TEST_PREDICTIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
    predictions.to_csv(TEST_PREDICTIONS_PATH, index=False)
    save_metrics(metrics)

    printable_metrics = {
        key: round(value, 6)
        for key, value in metrics.items()
    }

    print(f"Device: {device}")
    print(f"Predictions saved: {TEST_PREDICTIONS_PATH}")
    print(f"Metrics saved: {MODEL_METRICS_PATH}")
    print(json.dumps(printable_metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()