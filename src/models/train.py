from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import roc_auc_score
from torch import nn
from torch.utils.data import DataLoader

from src.models.dataset import (
    TRAIN_PATH,
    VAL_PATH,
    AssignmentPairDataset,
    create_dataloader,
    load_feature_spec,
)
from src.models.matching_net import MatchingNetConfig, TaskEmployeeMatchingNet

PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_PATH = PROJECT_ROOT / "models" / "compass_matching_model.pt"
TRAINING_HISTORY_PATH = PROJECT_ROOT / "reports" / "training_history.csv"
TRAINING_CONFIG_PATH = PROJECT_ROOT / "reports" / "training_config.json"

RANDOM_SEED = 42


def set_seed(seed: int = RANDOM_SEED) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def select_device() -> torch.device:
    if torch.backends.mps.is_available():
        return torch.device("mps")

    return torch.device("cpu")


def move_batch_to_device(batch: dict[str, Any], device: torch.device) -> dict[str, torch.Tensor]:
    return {
        "task_features": batch["task_features"].to(device),
        "employee_features": batch["employee_features"].to(device),
        "pair_features": batch["pair_features"].to(device),
        "label": batch["label"].to(device),
    }


def compute_roc_auc(labels: list[float], probabilities: list[float]) -> float:
    unique_labels = set(int(label) for label in labels)

    if len(unique_labels) < 2:
        return 0.5

    return float(roc_auc_score(labels, probabilities))


def train_one_epoch(
    model: TaskEmployeeMatchingNet,
    dataloader: DataLoader[dict[str, Any]],
    criterion: nn.Module,
    optimizer: torch.optim.Optimizer,
    device: torch.device,
) -> float:
    model.train()

    losses: list[float] = []

    for batch in dataloader:
        batch_on_device = move_batch_to_device(batch, device)

        optimizer.zero_grad(set_to_none=True)

        output = model(
            batch_on_device["task_features"],
            batch_on_device["employee_features"],
            batch_on_device["pair_features"],
        )

        loss = criterion(output["logits"], batch_on_device["label"])
        loss.backward()
        optimizer.step()

        losses.append(float(loss.detach().cpu().item()))

    return float(np.mean(losses))


@torch.no_grad()
def evaluate_epoch(
    model: TaskEmployeeMatchingNet,
    dataloader: DataLoader[dict[str, Any]],
    criterion: nn.Module,
    device: torch.device,
) -> dict[str, float]:
    model.eval()

    losses: list[float] = []
    labels: list[float] = []
    probabilities: list[float] = []

    for batch in dataloader:
        batch_on_device = move_batch_to_device(batch, device)

        output = model(
            batch_on_device["task_features"],
            batch_on_device["employee_features"],
            batch_on_device["pair_features"],
        )

        loss = criterion(output["logits"], batch_on_device["label"])

        batch_labels = batch_on_device["label"].detach().cpu().numpy().reshape(-1).tolist()
        batch_probabilities = (
            output["success_probability"].detach().cpu().numpy().reshape(-1).tolist()
        )

        losses.append(float(loss.detach().cpu().item()))
        labels.extend(float(value) for value in batch_labels)
        probabilities.extend(float(value) for value in batch_probabilities)

    return {
        "loss": float(np.mean(losses)),
        "roc_auc": compute_roc_auc(labels, probabilities),
    }


def save_checkpoint(
    model: TaskEmployeeMatchingNet,
    config: MatchingNetConfig,
    feature_columns: dict[str, list[str]],
    metrics: dict[str, float],
    path: Path = MODEL_PATH,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "model_state_dict": model.state_dict(),
        "model_config": {
            "task_input_dim": config.task_input_dim,
            "employee_input_dim": config.employee_input_dim,
            "pair_input_dim": config.pair_input_dim,
            "task_embedding_dim": config.task_embedding_dim,
            "employee_embedding_dim": config.employee_embedding_dim,
            "hidden_dim": config.hidden_dim,
            "dropout": config.dropout,
        },
        "feature_columns": feature_columns,
        "metrics": metrics,
    }

    torch.save(payload, path)


def save_training_config(config: dict[str, Any], path: Path = TRAINING_CONFIG_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(config, file, ensure_ascii=False, indent=2)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train TaskEmployeeMatchingNet")

    parser.add_argument("--epochs", type=int, default=12)
    parser.add_argument("--batch-size", type=int, default=512)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--hidden-dim", type=int, default=256)
    parser.add_argument("--embedding-dim", type=int, default=128)
    parser.add_argument("--dropout", type=float, default=0.15)
    parser.add_argument("--patience", type=int, default=4)

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    set_seed()

    device = select_device()
    feature_spec = load_feature_spec()

    train_dataset = AssignmentPairDataset(TRAIN_PATH, feature_spec=feature_spec)
    val_dataset = AssignmentPairDataset(VAL_PATH, feature_spec=feature_spec)

    train_loader = create_dataloader(
        TRAIN_PATH,
        batch_size=args.batch_size,
        shuffle=True,
        feature_spec=feature_spec,
    )
    val_loader = create_dataloader(
        VAL_PATH,
        batch_size=args.batch_size,
        shuffle=False,
        feature_spec=feature_spec,
    )

    model_config = MatchingNetConfig(
        task_input_dim=feature_spec.task_dim,
        employee_input_dim=feature_spec.employee_dim,
        pair_input_dim=feature_spec.pair_dim,
        task_embedding_dim=args.embedding_dim,
        employee_embedding_dim=args.embedding_dim,
        hidden_dim=args.hidden_dim,
        dropout=args.dropout,
    )

    model = TaskEmployeeMatchingNet(model_config).to(device)

    criterion = nn.BCEWithLogitsLoss()
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=args.learning_rate,
        weight_decay=args.weight_decay,
    )

    training_config = {
        "device": str(device),
        "epochs": args.epochs,
        "batch_size": args.batch_size,
        "learning_rate": args.learning_rate,
        "weight_decay": args.weight_decay,
        "hidden_dim": args.hidden_dim,
        "embedding_dim": args.embedding_dim,
        "dropout": args.dropout,
        "patience": args.patience,
        "train_rows": len(train_dataset),
        "val_rows": len(val_dataset),
        "task_dim": feature_spec.task_dim,
        "employee_dim": feature_spec.employee_dim,
        "pair_dim": feature_spec.pair_dim,
    }

    save_training_config(training_config)

    print("Training config:")
    print(json.dumps(training_config, ensure_ascii=False, indent=2))

    history: list[dict[str, float | int]] = []
    best_val_roc_auc = -1.0
    epochs_without_improvement = 0

    for epoch in range(1, args.epochs + 1):
        train_loss = train_one_epoch(
            model=model,
            dataloader=train_loader,
            criterion=criterion,
            optimizer=optimizer,
            device=device,
        )
        val_metrics = evaluate_epoch(
            model=model,
            dataloader=val_loader,
            criterion=criterion,
            device=device,
        )

        row = {
            "epoch": epoch,
            "train_loss": train_loss,
            "val_loss": val_metrics["loss"],
            "val_roc_auc": val_metrics["roc_auc"],
        }

        history.append(row)

        print(
            f"epoch={epoch} "
            f"train_loss={train_loss:.5f} "
            f"val_loss={val_metrics['loss']:.5f} "
            f"val_roc_auc={val_metrics['roc_auc']:.5f}"
        )

        if val_metrics["roc_auc"] > best_val_roc_auc:
            best_val_roc_auc = val_metrics["roc_auc"]
            epochs_without_improvement = 0

            save_checkpoint(
                model=model,
                config=model_config,
                feature_columns={
                    "task_feature_columns": feature_spec.task_feature_columns,
                    "employee_feature_columns": feature_spec.employee_feature_columns,
                    "pair_feature_columns": feature_spec.pair_feature_columns,
                },
                metrics={
                    "best_epoch": float(epoch),
                    "best_val_roc_auc": float(best_val_roc_auc),
                    "best_val_loss": float(val_metrics["loss"]),
                },
            )

            print(f"saved best checkpoint: {MODEL_PATH}")
        else:
            epochs_without_improvement += 1

        if epochs_without_improvement >= args.patience:
            print(f"early stopping after {epoch} epochs")
            break

    TRAINING_HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(history).to_csv(TRAINING_HISTORY_PATH, index=False)

    print(f"Training history saved: {TRAINING_HISTORY_PATH}")
    print(f"Training config saved: {TRAINING_CONFIG_PATH}")
    print(f"Best checkpoint saved: {MODEL_PATH}")


if __name__ == "__main__":
    main()