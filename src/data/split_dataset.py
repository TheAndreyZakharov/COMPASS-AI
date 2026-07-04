from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from sklearn.model_selection import GroupShuffleSplit

PROJECT_ROOT = Path(__file__).resolve().parents[2]

TRAINING_PAIRS_PATH = PROJECT_ROOT / "data" / "processed" / "training_pairs.parquet"
TRAIN_PATH = PROJECT_ROOT / "data" / "processed" / "train.parquet"
VAL_PATH = PROJECT_ROOT / "data" / "processed" / "val.parquet"
TEST_PATH = PROJECT_ROOT / "data" / "processed" / "test.parquet"
SPLIT_METADATA_PATH = PROJECT_ROOT / "data" / "processed" / "split_metadata.json"

RANDOM_STATE = 42
TRAIN_SIZE = 0.70
VAL_SIZE = 0.15
TEST_SIZE = 0.15


def validate_no_task_leakage(train: pd.DataFrame, val: pd.DataFrame, test: pd.DataFrame) -> None:
    train_tasks = set(train["task_id"].astype(str))
    val_tasks = set(val["task_id"].astype(str))
    test_tasks = set(test["task_id"].astype(str))

    train_val_overlap = train_tasks & val_tasks
    train_test_overlap = train_tasks & test_tasks
    val_test_overlap = val_tasks & test_tasks

    if train_val_overlap or train_test_overlap or val_test_overlap:
        raise ValueError(
            "Task leakage detected: "
            f"train/val={len(train_val_overlap)}, "
            f"train/test={len(train_test_overlap)}, "
            f"val/test={len(val_test_overlap)}"
        )


def split_by_task_id(
    dataset: pd.DataFrame,
    random_state: int = RANDOM_STATE,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    groups = dataset["task_id"].astype(str)

    train_splitter = GroupShuffleSplit(
        n_splits=1,
        train_size=TRAIN_SIZE,
        random_state=random_state,
    )

    train_index, temp_index = next(train_splitter.split(dataset, groups=groups))

    train = dataset.iloc[train_index].copy()
    temp = dataset.iloc[temp_index].copy()

    temp_groups = temp["task_id"].astype(str)

    val_relative_size = VAL_SIZE / (VAL_SIZE + TEST_SIZE)

    val_test_splitter = GroupShuffleSplit(
        n_splits=1,
        train_size=val_relative_size,
        random_state=random_state,
    )

    val_index, test_index = next(val_test_splitter.split(temp, groups=temp_groups))

    val = temp.iloc[val_index].copy()
    test = temp.iloc[test_index].copy()

    validate_no_task_leakage(train, val, test)

    return train, val, test


def split_summary(split_name: str, data: pd.DataFrame) -> dict[str, float | int | str]:
    return {
        "split": split_name,
        "rows": int(len(data)),
        "tasks": int(data["task_id"].nunique()),
        "employees": int(data["employee_id"].nunique()),
        "success_rate": round(float(data["success_label"].mean()), 6),
    }


def save_split_metadata(train: pd.DataFrame, val: pd.DataFrame, test: pd.DataFrame) -> None:
    payload = {
        "random_state": RANDOM_STATE,
        "split_strategy": "group_split_by_task_id",
        "train_size_target": TRAIN_SIZE,
        "val_size_target": VAL_SIZE,
        "test_size_target": TEST_SIZE,
        "splits": [
            split_summary("train", train),
            split_summary("val", val),
            split_summary("test", test),
        ],
        "leakage_check": {
            "task_id_overlap_train_val": 0,
            "task_id_overlap_train_test": 0,
            "task_id_overlap_val_test": 0,
        },
    }

    SPLIT_METADATA_PATH.parent.mkdir(parents=True, exist_ok=True)

    with SPLIT_METADATA_PATH.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)


def split_dataset(
    input_path: Path = TRAINING_PAIRS_PATH,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if not input_path.exists():
        raise FileNotFoundError(
            f"Missing training features: {input_path}. "
            "Run: python src/features/build_features.py"
        )

    dataset = pd.read_parquet(input_path)

    required_columns = {"task_id", "employee_id", "success_label"}
    missing_columns = required_columns - set(dataset.columns)

    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

    train, val, test = split_by_task_id(dataset)

    TRAIN_PATH.parent.mkdir(parents=True, exist_ok=True)

    train.to_parquet(TRAIN_PATH, index=False)
    val.to_parquet(VAL_PATH, index=False)
    test.to_parquet(TEST_PATH, index=False)

    save_split_metadata(train, val, test)

    return train, val, test


def main() -> None:
    train, val, test = split_dataset()

    print(f"Train saved: {TRAIN_PATH}")
    print(f"Val saved: {VAL_PATH}")
    print(f"Test saved: {TEST_PATH}")
    print(f"Split metadata saved: {SPLIT_METADATA_PATH}")
    print(split_summary("train", train))
    print(split_summary("val", val))
    print(split_summary("test", test))


if __name__ == "__main__":
    main()