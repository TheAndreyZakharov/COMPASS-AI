from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import nn


@dataclass(frozen=True)
class MatchingNetConfig:
    task_input_dim: int
    employee_input_dim: int
    pair_input_dim: int
    task_embedding_dim: int = 128
    employee_embedding_dim: int = 128
    hidden_dim: int = 256
    dropout: float = 0.15


class TaskEncoder(nn.Module):
    def __init__(
        self,
        input_dim: int,
        embedding_dim: int = 128,
        hidden_dim: int = 256,
        dropout: float = 0.15,
    ) -> None:
        super().__init__()

        self.network = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, embedding_dim),
            nn.LayerNorm(embedding_dim),
            nn.ReLU(),
        )

    def forward(self, task_features: torch.Tensor) -> torch.Tensor:
        return self.network(task_features)


class EmployeeEncoder(nn.Module):
    def __init__(
        self,
        input_dim: int,
        embedding_dim: int = 128,
        hidden_dim: int = 128,
        dropout: float = 0.15,
    ) -> None:
        super().__init__()

        self.network = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, embedding_dim),
            nn.LayerNorm(embedding_dim),
            nn.ReLU(),
        )

    def forward(self, employee_features: torch.Tensor) -> torch.Tensor:
        return self.network(employee_features)


class MatchingBlock(nn.Module):
    def __init__(
        self,
        task_embedding_dim: int,
        employee_embedding_dim: int,
        pair_input_dim: int,
        hidden_dim: int = 256,
        dropout: float = 0.15,
    ) -> None:
        super().__init__()

        matching_input_dim = (
            task_embedding_dim
            + employee_embedding_dim
            + task_embedding_dim
            + task_embedding_dim
            + pair_input_dim
        )

        self.network = nn.Sequential(
            nn.Linear(matching_input_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.LayerNorm(hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim // 2, 1),
        )

    def forward(
        self,
        task_embedding: torch.Tensor,
        employee_embedding: torch.Tensor,
        pair_features: torch.Tensor,
    ) -> torch.Tensor:
        if task_embedding.shape != employee_embedding.shape:
            raise ValueError(
                "Task and employee embeddings must have the same shape for matching. "
                f"Got {task_embedding.shape} and {employee_embedding.shape}."
            )

        abs_diff = torch.abs(task_embedding - employee_embedding)
        multiply = task_embedding * employee_embedding

        matching_features = torch.cat(
            [
                task_embedding,
                employee_embedding,
                abs_diff,
                multiply,
                pair_features,
            ],
            dim=1,
        )

        return self.network(matching_features)


class TaskEmployeeMatchingNet(nn.Module):
    def __init__(self, config: MatchingNetConfig) -> None:
        super().__init__()

        if config.task_embedding_dim != config.employee_embedding_dim:
            raise ValueError("task_embedding_dim and employee_embedding_dim must be equal")

        self.config = config

        self.task_encoder = TaskEncoder(
            input_dim=config.task_input_dim,
            embedding_dim=config.task_embedding_dim,
            hidden_dim=config.hidden_dim,
            dropout=config.dropout,
        )

        self.employee_encoder = EmployeeEncoder(
            input_dim=config.employee_input_dim,
            embedding_dim=config.employee_embedding_dim,
            hidden_dim=max(config.hidden_dim // 2, 64),
            dropout=config.dropout,
        )

        self.matching_block = MatchingBlock(
            task_embedding_dim=config.task_embedding_dim,
            employee_embedding_dim=config.employee_embedding_dim,
            pair_input_dim=config.pair_input_dim,
            hidden_dim=config.hidden_dim,
            dropout=config.dropout,
        )

    def forward(
        self,
        task_features: torch.Tensor,
        employee_features: torch.Tensor,
        pair_features: torch.Tensor,
    ) -> dict[str, torch.Tensor]:
        task_embedding = self.task_encoder(task_features)
        employee_embedding = self.employee_encoder(employee_features)
        logits = self.matching_block(task_embedding, employee_embedding, pair_features)
        success_probability = torch.sigmoid(logits)

        return {
            "logits": logits,
            "success_probability": success_probability,
            "task_embedding": task_embedding,
            "employee_embedding": employee_embedding,
        }


def main() -> None:
    config = MatchingNetConfig(
        task_input_dim=404,
        employee_input_dim=60,
        pair_input_dim=13,
    )

    model = TaskEmployeeMatchingNet(config)

    batch_size = 4
    task_features = torch.randn(batch_size, config.task_input_dim)
    employee_features = torch.randn(batch_size, config.employee_input_dim)
    pair_features = torch.randn(batch_size, config.pair_input_dim)

    output = model(task_features, employee_features, pair_features)

    print(model)
    print("logits:", tuple(output["logits"].shape))
    print("success_probability:", tuple(output["success_probability"].shape))
    print("task_embedding:", tuple(output["task_embedding"].shape))
    print("employee_embedding:", tuple(output["employee_embedding"].shape))


if __name__ == "__main__":
    main()