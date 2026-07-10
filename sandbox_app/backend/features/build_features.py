from __future__ import annotations

import csv
import json
import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
from sandbox_app.backend.core.paths import PATHS
from sandbox_app.backend.core.time import moscow_now_iso
from sandbox_app.backend.features.custom_features import flatten_custom_features, parse_jsonish
from sandbox_app.backend.features.pair_features import (
    aggregate_history_by_employee,
    build_pair_features,
)
from sandbox_app.backend.features.skill_vectorizer import (
    collect_skill_vocabulary,
    parse_skill_list,
    skill_overlap_features,
    skill_vector,
)
from sandbox_app.backend.features.targets import build_target_row

DATASET_KINDS = {"generated", "imported"}
TARGET_MODES = {"quality", "speed", "balanced", "learning", "risk_aware"}
DEFAULT_SAFE_MAX_PAIRS = 120_000
HARD_SAFE_MAX_PAIRS = 250_000


class FeatureBuildError(RuntimeError):
    """Raised when feature building fails."""


@dataclass(frozen=True)
class FeatureBuildConfig:
    dataset_id: str
    dataset_kind: str = "generated"
    target_mode: str = "balanced"
    overwrite: bool = False
    max_pairs: int | None = None


def utc_now_iso() -> str:
    return moscow_now_iso()


def dataset_root(dataset_kind: str) -> Path:
    if dataset_kind not in DATASET_KINDS:
        allowed = ", ".join(sorted(DATASET_KINDS))
        raise FeatureBuildError(f"dataset_kind must be one of: {allowed}")

    return PATHS.data_dir / dataset_kind


def dataset_dir_for(config: FeatureBuildConfig) -> Path:
    dataset_dir = dataset_root(config.dataset_kind) / config.dataset_id

    if not dataset_dir.exists():
        raise FeatureBuildError(
            f"Dataset '{config.dataset_id}' was not found in {dataset_root(config.dataset_kind)}"
        )

    return dataset_dir


def read_json_file(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FeatureBuildError(f"Could not read JSON file: {path}") from exc


def read_csv_file(path: Path) -> list[dict[str, Any]]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as file_obj:
            rows = list(csv.DictReader(file_obj))
    except OSError as exc:
        raise FeatureBuildError(f"Could not read CSV file: {path}") from exc

    return [
        {key: parse_jsonish(value) for key, value in row.items()}
        for row in rows
    ]


def read_table_records(dataset_dir: Path, table_name: str) -> list[dict[str, Any]]:
    json_path = dataset_dir / f"{table_name}.json"
    csv_path = dataset_dir / f"{table_name}.csv"

    if json_path.exists():
        payload = read_json_file(json_path)
        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict):
            for key in ("items", "rows", "records", "data"):
                if isinstance(payload.get(key), list):
                    return payload[key]

    if csv_path.exists():
        return read_csv_file(csv_path)

    raise FeatureBuildError(f"Table '{table_name}' was not found in {dataset_dir}")


def positive_int_from_env(name: str, default: int) -> int:
    raw_value = os.getenv(name)

    if not raw_value:
        return default

    try:
        value = int(raw_value)
    except ValueError:
        return default

    return value if value > 0 else default


def effective_max_pairs(requested_max_pairs: int | None) -> tuple[int, dict[str, Any]]:
    default_limit = positive_int_from_env(
        "SANDBOX_TRAINING_DEFAULT_MAX_PAIRS",
        DEFAULT_SAFE_MAX_PAIRS,
    )
    hard_limit = positive_int_from_env(
        "SANDBOX_TRAINING_HARD_MAX_PAIRS",
        HARD_SAFE_MAX_PAIRS,
    )
    safe_limit = min(default_limit, hard_limit)
    requested = requested_max_pairs if requested_max_pairs is not None else safe_limit
    effective = min(max(1, int(requested)), hard_limit)

    return effective, {
        "requested_max_pairs": requested_max_pairs,
        "default_safe_max_pairs": safe_limit,
        "hard_safe_max_pairs": hard_limit,
        "effective_max_pairs": effective,
        "capped": requested_max_pairs is None or int(requested) != effective,
    }


def read_training_pairs(dataset_dir: Path, max_pairs: int | None = None) -> list[dict[str, Any]]:
    parquet_path = dataset_dir / "training_pairs.parquet"
    json_path = dataset_dir / "training_pairs.json"
    csv_path = dataset_dir / "training_pairs.csv"

    if parquet_path.exists():
        if max_pairs is not None:
            try:
                import pyarrow.parquet as pq

                rows: list[dict[str, Any]] = []
                remaining = max_pairs
                batch_size = min(50_000, max_pairs)

                for batch in pq.ParquetFile(parquet_path).iter_batches(
                    batch_size=batch_size,
                ):
                    frame = batch.to_pandas()
                    if len(frame) > remaining:
                        frame = frame.head(remaining)
                    rows.extend(frame.to_dict(orient="records"))
                    remaining -= len(frame)

                    if remaining <= 0:
                        break

                return rows
            except ImportError:
                pass
            except Exception as exc:
                raise FeatureBuildError("Could not read training_pairs.parquet") from exc

        try:
            frame = pd.read_parquet(parquet_path)
        except Exception as exc:
            raise FeatureBuildError("Could not read training_pairs.parquet") from exc

        if max_pairs is not None:
            frame = frame.head(max_pairs)

        return frame.to_dict(orient="records")

    if json_path.exists():
        payload = read_json_file(json_path)
        if isinstance(payload, list):
            return payload[:max_pairs] if max_pairs is not None else payload

    if csv_path.exists():
        rows = read_csv_file(csv_path)
        return rows[:max_pairs] if max_pairs is not None else rows

    raise FeatureBuildError(f"training_pairs table was not found in {dataset_dir}")


def write_json_file(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def prepare_output_dir(dataset_dir: Path, overwrite: bool) -> Path:
    output_dir = dataset_dir / "features"

    if output_dir.exists() and not overwrite:
        raise FeatureBuildError("Features already exist. Set overwrite=true to rebuild.")

    if output_dir.exists():
        shutil.rmtree(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def normalize_numeric_rows(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str]]:
    feature_names = sorted({key for row in rows for key in row if key != "pair_id"})
    normalized_rows: list[dict[str, Any]] = []

    for row in rows:
        normalized = {"pair_id": row.get("pair_id", "")}

        for feature_name in feature_names:
            value = row.get(feature_name, 0.0)
            try:
                normalized[feature_name] = float(value)
            except (TypeError, ValueError):
                normalized[feature_name] = 0.0

        normalized_rows.append(normalized)

    return normalized_rows, feature_names


def employee_id(record: dict[str, Any]) -> str:
    return str(record.get("employee_id") or "")


def task_id(record: dict[str, Any]) -> str:
    return str(record.get("task_id") or "")


def build_feature_row(
    pair: dict[str, Any],
    employee: dict[str, Any],
    task: dict[str, Any],
    employee_history: dict[str, float],
    skill_vocabulary: list[str],
) -> dict[str, Any]:
    employee_skills = parse_skill_list(employee.get("skills"))
    task_skills = parse_skill_list(task.get("required_skills"))

    row: dict[str, Any] = {
        "pair_id": str(pair.get("pair_id") or ""),
    }
    row.update(build_pair_features(pair, employee, task, employee_history))
    row.update(skill_overlap_features(employee_skills, task_skills))
    row.update(skill_vector("employee_skill", employee_skills, skill_vocabulary))
    row.update(skill_vector("task_skill", task_skills, skill_vocabulary))
    row.update(flatten_custom_features("employee_custom", employee))
    row.update(flatten_custom_features("task_custom", task))

    return row


def build_features_for_dataset(config: FeatureBuildConfig) -> dict[str, Any]:
    if config.target_mode not in TARGET_MODES:
        allowed = ", ".join(sorted(TARGET_MODES))
        raise FeatureBuildError(f"target_mode must be one of: {allowed}")

    dataset_dir = dataset_dir_for(config)
    output_dir = prepare_output_dir(dataset_dir, config.overwrite)
    max_pairs, safety_limits = effective_max_pairs(config.max_pairs)

    employees = read_table_records(dataset_dir, "employees")
    tasks = read_table_records(dataset_dir, "tasks")
    assignment_history = read_table_records(dataset_dir, "assignment_history")
    training_pairs = read_training_pairs(dataset_dir, max_pairs=max_pairs)

    employee_by_id = {employee_id(record): record for record in employees}
    task_by_id = {task_id(record): record for record in tasks}
    history_by_employee = aggregate_history_by_employee(assignment_history)
    skill_vocabulary = collect_skill_vocabulary([*employees, *tasks])

    feature_rows: list[dict[str, Any]] = []
    target_rows: list[dict[str, Any]] = []
    skipped_pairs: list[dict[str, Any]] = []

    for pair in training_pairs:
        current_employee_id = str(pair.get("employee_id") or "")
        current_task_id = str(pair.get("task_id") or "")
        employee = employee_by_id.get(current_employee_id)
        task = task_by_id.get(current_task_id)

        if employee is None or task is None:
            skipped_pairs.append(
                {
                    "pair_id": pair.get("pair_id"),
                    "employee_id": current_employee_id,
                    "task_id": current_task_id,
                    "reason": "employee or task not found",
                }
            )
            continue

        feature_row = build_feature_row(
            pair=pair,
            employee=employee,
            task=task,
            employee_history=history_by_employee.get(current_employee_id, {}),
            skill_vocabulary=skill_vocabulary,
        )
        feature_rows.append(feature_row)
        target_rows.append(build_target_row(pair, feature_row, config.target_mode))

    if not feature_rows:
        raise FeatureBuildError("No feature rows were built")

    normalized_feature_rows, feature_names = normalize_numeric_rows(feature_rows)

    features_path = output_dir / "features.parquet"
    targets_path = output_dir / "targets.parquet"
    metadata_path = output_dir / "feature_metadata.json"

    features_frame = pd.DataFrame(normalized_feature_rows)
    numeric_feature_columns = [
        column for column in features_frame.columns if column != "pair_id"
    ]
    if numeric_feature_columns:
        features_frame[numeric_feature_columns] = features_frame[
            numeric_feature_columns
        ].astype("float32")

    targets_frame = pd.DataFrame(target_rows)
    if "label" in targets_frame.columns:
        targets_frame["label"] = targets_frame["label"].astype("int8")
    if "target_score" in targets_frame.columns:
        targets_frame["target_score"] = targets_frame["target_score"].astype("float32")

    features_frame.to_parquet(features_path, index=False)
    targets_frame.to_parquet(targets_path, index=False)

    metadata = {
        "dataset_id": config.dataset_id,
        "dataset_kind": config.dataset_kind,
        "target_mode": config.target_mode,
        "created_at": utc_now_iso(),
        "source_counts": {
            "employees": len(employees),
            "tasks": len(tasks),
            "assignment_history": len(assignment_history),
            "training_pairs": len(training_pairs),
        },
        "safety_limits": safety_limits,
        "output_counts": {
            "feature_rows": len(normalized_feature_rows),
            "target_rows": len(target_rows),
            "skipped_pairs": len(skipped_pairs),
        },
        "feature_dimensions": {
            "feature_count": len(feature_names),
            "skill_vocabulary_size": len(skill_vocabulary),
        },
        "feature_names": feature_names,
        "skill_vocabulary": skill_vocabulary,
        "paths": {
            "features": str(features_path),
            "targets": str(targets_path),
            "metadata": str(metadata_path),
        },
        "skipped_pairs_preview": skipped_pairs[:20],
    }

    write_json_file(metadata_path, metadata)

    return {
        "status": "built",
        "dataset_id": config.dataset_id,
        "dataset_kind": config.dataset_kind,
        "target_mode": config.target_mode,
        "dataset_dir": str(dataset_dir),
        "features_dir": str(output_dir),
        "metadata": metadata,
    }


def read_feature_metadata(dataset_id: str, dataset_kind: str = "generated") -> dict[str, Any]:
    dataset_dir = dataset_root(dataset_kind) / dataset_id
    metadata_path = dataset_dir / "features" / "feature_metadata.json"

    if not metadata_path.exists():
        raise FeatureBuildError("Feature metadata was not found. Build features first.")

    payload = read_json_file(metadata_path)
    if not isinstance(payload, dict):
        raise FeatureBuildError("Feature metadata must be a JSON object")

    return payload
