from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import torch
from torch.utils.data import DataLoader, Dataset

PROJECT_ROOT = Path(__file__).resolve().parents[2]

FEATURE_METADATA_PATH = PROJECT_ROOT / "data" / "processed" / "feature_metadata.json"
TRAIN_PATH = PROJECT_ROOT / "data" / "processed" / "train.parquet"
VAL_PATH = PROJECT_ROOT / "data" / "processed" / "val.parquet"
TEST_PATH = PROJECT_ROOT / "data" / "processed" / "test.parquet"


@dataclass(frozen=True)
class FeatureSpec:
    task_feature_columns: list[str]
    employee_feature_columns: list[str]
    pair_feature_columns: list[str]
    label_column: str

    @property
    def task_dim(self) -> int:
        return len(self.task_feature_columns)

    @property
    def employee_dim(self) -> int:
        return len(self.employee_feature_columns)

    @property
    def pair_dim(self) -> int:
        return len(self.pair_feature_columns)


def load_feature_spec(path: Path = FEATURE_METADATA_PATH) -> FeatureSpec:
    if not path.exists():
        raise FileNotFoundError(
            f"Missing feature metadata: {path}. "
            "Run: python src/features/build_features.py"
        )

    with path.open("r", encoding="utf-8") as file:
        metadata = json.load(file)

    return FeatureSpec(
        task_feature_columns=list(metadata["task_feature_columns"]),
        employee_feature_columns=list(metadata["employee_feature_columns"]),
        pair_feature_columns=list(metadata["pair_feature_columns"]),
        label_column=str(metadata["label_column"]),
    )


class AssignmentPairDataset(Dataset[dict[str, Any]]):
    def __init__(
        self,
        parquet_path: str | Path,
        feature_spec: FeatureSpec | None = None,
    ) -> None:
        self.parquet_path = Path(parquet_path)
        self.feature_spec = feature_spec or load_feature_spec()

        if not self.parquet_path.exists():
            raise FileNotFoundError(f"Missing dataset file: {self.parquet_path}")

        self.data = pd.read_parquet(self.parquet_path)
        self._validate_columns()

        self.task_features = torch.tensor(
            self.data[self.feature_spec.task_feature_columns].to_numpy(dtype="float32"),
            dtype=torch.float32,
        )
        self.employee_features = torch.tensor(
            self.data[self.feature_spec.employee_feature_columns].to_numpy(dtype="float32"),
            dtype=torch.float32,
        )
        self.pair_features = torch.tensor(
            self.data[self.feature_spec.pair_feature_columns].to_numpy(dtype="float32"),
            dtype=torch.float32,
        )
        self.labels = torch.tensor(
            self.data[self.feature_spec.label_column].to_numpy(dtype="float32"),
            dtype=torch.float32,
        ).view(-1, 1)

        self.assignment_ids = self.data["assignment_id"].astype(str).tolist()
        self.task_ids = self.data["task_id"].astype(str).tolist()
        self.employee_ids = self.data["employee_id"].astype(str).tolist()

    def _validate_columns(self) -> None:
        required_columns = {
            "assignment_id",
            "task_id",
            "employee_id",
            self.feature_spec.label_column,
            *self.feature_spec.task_feature_columns,
            *self.feature_spec.employee_feature_columns,
            *self.feature_spec.pair_feature_columns,
        }

        missing_columns = required_columns - set(self.data.columns)

        if missing_columns:
            raise ValueError(f"Missing columns in {self.parquet_path}: {sorted(missing_columns)}")

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, index: int) -> dict[str, Any]:
        return {
            "assignment_id": self.assignment_ids[index],
            "task_id": self.task_ids[index],
            "employee_id": self.employee_ids[index],
            "task_features": self.task_features[index],
            "employee_features": self.employee_features[index],
            "pair_features": self.pair_features[index],
            "label": self.labels[index],
        }


def create_dataloader(
    parquet_path: str | Path,
    batch_size: int = 256,
    shuffle: bool = False,
    feature_spec: FeatureSpec | None = None,
) -> DataLoader[dict[str, Any]]:
    dataset = AssignmentPairDataset(
        parquet_path=parquet_path,
        feature_spec=feature_spec,
    )

    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=0,
        pin_memory=False,
    )


def dataset_summary(dataset: AssignmentPairDataset) -> dict[str, int | float | str]:
    return {
        "path": str(dataset.parquet_path),
        "rows": len(dataset),
        "task_dim": dataset.feature_spec.task_dim,
        "employee_dim": dataset.feature_spec.employee_dim,
        "pair_dim": dataset.feature_spec.pair_dim,
        "positive_rate": round(float(dataset.labels.mean().item()), 6),
    }


def main() -> None:
    feature_spec = load_feature_spec()

    print("Feature dimensions:")
    print(f"task_dim: {feature_spec.task_dim}")
    print(f"employee_dim: {feature_spec.employee_dim}")
    print(f"pair_dim: {feature_spec.pair_dim}")

    train_dataset = AssignmentPairDataset(TRAIN_PATH, feature_spec=feature_spec)
    print("Train dataset summary:")
    print(dataset_summary(train_dataset))

    dataloader = create_dataloader(
        TRAIN_PATH,
        batch_size=16,
        shuffle=True,
        feature_spec=feature_spec,
    )

    batch = next(iter(dataloader))

    print("Batch shapes:")
    print("task_features:", tuple(batch["task_features"].shape))
    print("employee_features:", tuple(batch["employee_features"].shape))
    print("pair_features:", tuple(batch["pair_features"].shape))
    print("label:", tuple(batch["label"].shape))


if __name__ == "__main__":
    main()