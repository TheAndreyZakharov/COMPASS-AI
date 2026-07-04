from __future__ import annotations

from pathlib import Path

import pytest

from src.models.dataset import AssignmentPairDataset, create_dataloader, load_feature_spec

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TRAIN_PATH = PROJECT_ROOT / "data" / "processed" / "train.parquet"
FEATURE_METADATA_PATH = PROJECT_ROOT / "data" / "processed" / "feature_metadata.json"


pytestmark = pytest.mark.skipif(
    not TRAIN_PATH.exists() or not FEATURE_METADATA_PATH.exists(),
    reason="processed training data is not generated",
)


def test_assignment_pair_dataset_loads_processed_data() -> None:
    feature_spec = load_feature_spec()
    dataset = AssignmentPairDataset(TRAIN_PATH, feature_spec=feature_spec)

    assert len(dataset) > 0
    assert feature_spec.task_dim > 0
    assert feature_spec.employee_dim > 0
    assert feature_spec.pair_dim > 0


def test_assignment_pair_dataset_item_shapes() -> None:
    feature_spec = load_feature_spec()
    dataset = AssignmentPairDataset(TRAIN_PATH, feature_spec=feature_spec)

    item = dataset[0]

    assert item["task_features"].shape[0] == feature_spec.task_dim
    assert item["employee_features"].shape[0] == feature_spec.employee_dim
    assert item["pair_features"].shape[0] == feature_spec.pair_dim
    assert item["label"].shape == (1,)


def test_assignment_pair_dataloader_batch_shapes() -> None:
    feature_spec = load_feature_spec()
    dataloader = create_dataloader(
        TRAIN_PATH,
        batch_size=8,
        shuffle=False,
        feature_spec=feature_spec,
    )

    batch = next(iter(dataloader))

    assert batch["task_features"].shape == (8, feature_spec.task_dim)
    assert batch["employee_features"].shape == (8, feature_spec.employee_dim)
    assert batch["pair_features"].shape == (8, feature_spec.pair_dim)
    assert batch["label"].shape == (8, 1)