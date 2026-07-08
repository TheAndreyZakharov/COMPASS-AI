from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler


class TorchTrainingError(RuntimeError):
    """Raised when PyTorch training cannot run."""


@dataclass
class TorchMLPBundle:
    model: Any
    scaler: StandardScaler
    feature_names: list[str]
    config: dict[str, Any]

    def predict_score(self, features: pd.DataFrame) -> np.ndarray:
        try:
            import torch
        except ImportError as exc:
            raise TorchTrainingError("PyTorch is not installed") from exc

        self.model.eval()
        matrix = self.scaler.transform(features[self.feature_names])
        tensor = torch.tensor(matrix, dtype=torch.float32)

        with torch.no_grad():
            logits = self.model(tensor).reshape(-1)
            scores = torch.sigmoid(logits).cpu().numpy()

        return np.clip(scores, 0.0, 1.0)

    def save(self, path: Path) -> None:
        try:
            import torch
        except ImportError as exc:
            raise TorchTrainingError("PyTorch is not installed") from exc

        path.parent.mkdir(parents=True, exist_ok=True)
        torch.save(
            {
                "state_dict": self.model.state_dict(),
                "feature_names": self.feature_names,
                "config": self.config,
                "scaler_mean": self.scaler.mean_.tolist(),
                "scaler_scale": self.scaler.scale_.tolist(),
            },
            path,
        )


def build_mlp(input_dim: int, hidden_size: int, dropout: float):
    try:
        from torch import nn
    except ImportError as exc:
        raise TorchTrainingError("PyTorch is not installed") from exc

    return nn.Sequential(
        nn.Linear(input_dim, hidden_size),
        nn.ReLU(),
        nn.Dropout(dropout),
        nn.Linear(hidden_size, max(4, hidden_size // 2)),
        nn.ReLU(),
        nn.Linear(max(4, hidden_size // 2), 1),
    )


def train_torch_mlp(
    features: pd.DataFrame,
    labels: pd.Series,
    seed: int,
    params: dict[str, Any] | None = None,
) -> TorchMLPBundle:
    try:
        import torch
        from torch import nn
    except ImportError as exc:
        raise TorchTrainingError("PyTorch is not installed") from exc

    params = params or {}
    torch.manual_seed(seed)
    np.random.seed(seed)

    feature_names = list(features.columns)
    scaler = StandardScaler()
    matrix = scaler.fit_transform(features)
    target = labels.astype(float).to_numpy()

    x_tensor = torch.tensor(matrix, dtype=torch.float32)
    y_tensor = torch.tensor(target, dtype=torch.float32).reshape(-1, 1)

    hidden_size = int(params.get("hidden_size", 64))
    dropout = float(params.get("dropout", 0.05))
    epochs = int(params.get("epochs", 24))
    learning_rate = float(params.get("learning_rate", 0.001))
    weight_decay = float(params.get("weight_decay", 0.00001))

    model = build_mlp(
        input_dim=features.shape[1],
        hidden_size=hidden_size,
        dropout=dropout,
    )

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=learning_rate,
        weight_decay=weight_decay,
    )
    criterion = nn.BCEWithLogitsLoss()

    model.train()
    for _ in range(epochs):
        optimizer.zero_grad()
        logits = model(x_tensor)
        loss = criterion(logits, y_tensor)
        loss.backward()
        optimizer.step()

    return TorchMLPBundle(
        model=model,
        scaler=scaler,
        feature_names=feature_names,
        config={
            "hidden_size": hidden_size,
            "dropout": dropout,
            "epochs": epochs,
            "learning_rate": learning_rate,
            "weight_decay": weight_decay,
        },
    )