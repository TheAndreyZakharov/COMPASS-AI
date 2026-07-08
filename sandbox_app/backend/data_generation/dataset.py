from __future__ import annotations

import random
import re
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sandbox_app.backend.core.paths import PATHS
from sandbox_app.backend.data_generation.history import generate_assignment_history
from sandbox_app.backend.data_generation.tasks import generate_tasks
from sandbox_app.backend.data_generation.training_pairs import (
    TrainingPairSettings,
    assign_splits,
    build_training_pairs,
    summarize_training_pairs,
    write_training_pairs_parquet,
)
from sandbox_app.backend.features.schema import load_feature_schema, schema_preview
from sandbox_app.backend.utils.json_io import read_json, write_json

GENERATED_ROOT = getattr(PATHS, "generated_data_dir", PATHS.data_dir / "generated")
DATASET_ID_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]{2,80}$")

TARGET_MODES = {"quality", "speed", "balanced", "learning", "risk_aware"}


class DatasetGenerationError(RuntimeError):
    """Raised when full sandbox dataset generation cannot be completed safely."""


@dataclass(frozen=True)
class DatasetMode:
    employees_count: int
    tasks_count: int
    history_depth_per_employee: int
    target_pairs: int
    candidates_per_task: int


DATASET_MODES = {
    "small_preview": DatasetMode(
        employees_count=10,
        tasks_count=100,
        history_depth_per_employee=12,
        target_pairs=1_000,
        candidates_per_task=10,
    ),
    "medium_validation": DatasetMode(
        employees_count=30,
        tasks_count=1_000,
        history_depth_per_employee=30,
        target_pairs=30_000,
        candidates_per_task=15,
    ),
    "large_training": DatasetMode(
        employees_count=100,
        tasks_count=10_000,
        history_depth_per_employee=60,
        target_pairs=1_000_000,
        candidates_per_task=20,
    ),
    "huge_training": DatasetMode(
        employees_count=100,
        tasks_count=10_000,
        history_depth_per_employee=60,
        target_pairs=1_000_000,
        candidates_per_task=20,
    ),
}


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def validate_dataset_id(dataset_id: str) -> str:
    if not isinstance(dataset_id, str) or not DATASET_ID_RE.match(dataset_id):
        raise DatasetGenerationError(
            "dataset_id must be 3-81 chars and contain only letters, digits, "
            "underscores, or hyphens"
        )

    return dataset_id


def generate_dataset_id(domain_profile: str, dataset_mode: str, seed: int | None) -> str:
    stamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    seed_part = "random" if seed is None else str(seed)
    return f"dataset_{domain_profile}_{dataset_mode}_{stamp}_{seed_part}"


def int_setting(
    payload: dict[str, Any],
    name: str,
    default: int,
    minimum: int,
    maximum: int,
) -> int:
    value = int(payload.get(name, default))
    if value < minimum or value > maximum:
        raise DatasetGenerationError(f"{name} must be between {minimum} and {maximum}")

    return value


def resolve_mode(payload: dict[str, Any]) -> tuple[str, DatasetMode]:
    dataset_mode = str(payload.get("dataset_mode", "small_preview"))
    if dataset_mode not in DATASET_MODES:
        raise DatasetGenerationError(
            f"dataset_mode must be one of: {', '.join(sorted(DATASET_MODES))}"
        )

    base = DATASET_MODES[dataset_mode]

    if dataset_mode == "huge_training":
        if payload.get("confirm_huge_generation") is not True:
            raise DatasetGenerationError(
                "huge_training requires confirm_huge_generation=true"
            )

        employees_count = int_setting(
            payload,
            "employees_count",
            base.employees_count,
            1,
            100_000,
        )
        tasks_count = int_setting(
            payload,
            "tasks_count",
            base.tasks_count,
            1,
            10_000_000,
        )
        history_depth_per_employee = int_setting(
            payload,
            "history_depth_per_employee",
            base.history_depth_per_employee,
            1,
            50_000,
        )
        target_pairs = int_setting(
            payload,
            "target_pairs",
            base.target_pairs,
            1,
            100_000_000,
        )
        candidates_per_task = int_setting(
            payload,
            "candidates_per_task",
            base.candidates_per_task,
            1,
            10_000,
        )
    else:
        employees_count = int_setting(
            payload,
            "employees_count",
            base.employees_count,
            1,
            base.employees_count,
        )
        tasks_count = int_setting(
            payload,
            "tasks_count",
            base.tasks_count,
            1,
            base.tasks_count,
        )
        history_depth_per_employee = int_setting(
            payload,
            "history_depth_per_employee",
            base.history_depth_per_employee,
            1,
            base.history_depth_per_employee,
        )
        target_pairs = int_setting(
            payload,
            "target_pairs",
            base.target_pairs,
            1,
            base.target_pairs,
        )
        candidates_per_task = int_setting(
            payload,
            "candidates_per_task",
            base.candidates_per_task,
            1,
            base.candidates_per_task,
        )

    return (
        dataset_mode,
        DatasetMode(
            employees_count=employees_count,
            tasks_count=tasks_count,
            history_depth_per_employee=history_depth_per_employee,
            target_pairs=target_pairs,
            candidates_per_task=candidates_per_task,
        ),
    )


def prepare_dataset_dir(dataset_id: str, overwrite: bool) -> Path:
    dataset_id = validate_dataset_id(dataset_id)
    dataset_dir = GENERATED_ROOT / dataset_id
    dataset_dir.mkdir(parents=True, exist_ok=True)

    output_files = [
        "employees.json",
        "employees.csv",
        "team_metadata.json",
        "tasks.json",
        "tasks.csv",
        "backlog.json",
        "backlog.csv",
        "task_metadata.json",
        "assignment_history.json",
        "assignment_history.csv",
        "history_metadata.json",
        "training_pairs.parquet",
        "dataset_metadata.json",
        "generation_report.json",
    ]

    existing = [name for name in output_files if (dataset_dir / name).exists()]
    if existing and not overwrite:
        raise DatasetGenerationError(
            "Dataset files already exist. Use overwrite=true to replace: "
            + ", ".join(existing)
        )

    return dataset_dir


def extract_records(
    result: dict[str, Any],
    primary_key: str,
    fallback_path: Path,
) -> list[dict[str, Any]]:
    records = result.get(primary_key)

    if records is None:
        data = result.get("data", {})
        if isinstance(data, dict):
            records = data.get(primary_key)

    if records is None and fallback_path.exists():
        loaded = read_json(fallback_path)
        if isinstance(loaded, list):
            records = loaded

    if not isinstance(records, list) or not records:
        raise DatasetGenerationError(
            f"Could not resolve generated records for {primary_key}"
        )

    normalized: list[dict[str, Any]] = []
    for index, item in enumerate(records):
        if not isinstance(item, dict):
            raise DatasetGenerationError(f"{primary_key}[{index}] must be an object")
        normalized.append(item)

    return normalized


def call_team_generator(
    payload: dict[str, Any],
    dataset_dir: Path,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    from sandbox_app.backend.data_generation import employees as employees_module

    generator_names = (
        "generate_employees",
        "generate_team",
        "generate_team_dataset",
        "generate_employee_dataset",
    )

    generator = None
    for name in generator_names:
        candidate = getattr(employees_module, name, None)
        if callable(candidate):
            generator = candidate
            break

    if generator is None:
        raise DatasetGenerationError(
            "Team generator function not found in "
            "sandbox_app.backend.data_generation.employees"
        )

    result = generator(payload)
    if not isinstance(result, dict):
        raise DatasetGenerationError("Team generator must return a dict")

    employees = extract_records(result, "employees", dataset_dir / "employees.json")
    metadata = result.get("metadata")

    if not isinstance(metadata, dict) and (dataset_dir / "team_metadata.json").exists():
        loaded_metadata = read_json(dataset_dir / "team_metadata.json")
        metadata = loaded_metadata if isinstance(loaded_metadata, dict) else {}

    return employees, metadata if isinstance(metadata, dict) else {}


def build_team_payload(
    payload: dict[str, Any],
    dataset_id: str,
    domain_profile: str,
    seed: int | None,
    mode: DatasetMode,
) -> dict[str, Any]:
    team_payload = dict(payload.get("team_settings", {}))
    team_payload.update(
        {
            "dataset_id": dataset_id,
            "domain_profile": domain_profile,
            "employees_count": mode.employees_count,
            "seed": seed,
            "overwrite": True,
        }
    )
    return team_payload


def build_tasks_payload(
    payload: dict[str, Any],
    dataset_id: str,
    domain_profile: str,
    seed: int | None,
    mode: DatasetMode,
) -> dict[str, Any]:
    tasks_payload = dict(payload.get("task_settings", {}))
    tasks_payload.update(
        {
            "dataset_id": dataset_id,
            "domain_profile": domain_profile,
            "tasks_count": mode.tasks_count,
            "seed": None if seed is None else seed + 1,
            "overwrite": True,
        }
    )
    return tasks_payload


def build_history_payload(
    payload: dict[str, Any],
    dataset_id: str,
    domain_profile: str,
    seed: int | None,
    mode: DatasetMode,
) -> dict[str, Any]:
    history_payload = dict(payload.get("history_settings", {}))
    history_payload.update(
        {
            "dataset_id": dataset_id,
            "domain_profile": domain_profile,
            "history_depth_per_employee": mode.history_depth_per_employee,
            "seed": None if seed is None else seed + 2,
            "overwrite": True,
        }
    )
    return history_payload


def build_dataset_metadata(
    dataset_id: str,
    dataset_dir: Path,
    dataset_mode: str,
    domain_profile: str,
    seed: int | None,
    mode: DatasetMode,
    employees: list[dict[str, Any]],
    tasks: list[dict[str, Any]],
    backlog: list[dict[str, Any]],
    assignment_history: list[dict[str, Any]],
    training_pairs_summary: dict[str, Any],
    schema_preview_payload: dict[str, Any],
) -> dict[str, Any]:
    return {
        "dataset_id": dataset_id,
        "dataset_type": "generated",
        "domain_profile": domain_profile,
        "dataset_mode": dataset_mode,
        "created_at": utc_now_iso(),
        "seed": seed,
        "schema_versions": {
            "feature_schema": schema_preview_payload.get("version", "unknown"),
            "generator": "1.0.0",
        },
        "generation_config": {
            "employees_count": mode.employees_count,
            "tasks_count": mode.tasks_count,
            "history_depth_per_employee": mode.history_depth_per_employee,
            "target_pairs": mode.target_pairs,
            "candidates_per_task": mode.candidates_per_task,
        },
        "counts": {
            "employees": len(employees),
            "tasks": len(tasks),
            "backlog": len(backlog),
            "assignment_history": len(assignment_history),
            "training_pairs": training_pairs_summary["pairs"],
        },
        "files": {
            "employees_csv": str(dataset_dir / "employees.csv"),
            "employees_json": str(dataset_dir / "employees.json"),
            "tasks_csv": str(dataset_dir / "tasks.csv"),
            "tasks_json": str(dataset_dir / "tasks.json"),
            "backlog_csv": str(dataset_dir / "backlog.csv"),
            "backlog_json": str(dataset_dir / "backlog.json"),
            "assignment_history_csv": str(dataset_dir / "assignment_history.csv"),
            "assignment_history_json": str(dataset_dir / "assignment_history.json"),
            "training_pairs_parquet": str(dataset_dir / "training_pairs.parquet"),
            "dataset_metadata_json": str(dataset_dir / "dataset_metadata.json"),
            "generation_report_json": str(dataset_dir / "generation_report.json"),
        },
        "quality_summary": {
            "training_pairs": training_pairs_summary,
        },
    }


def build_generation_report(
    started_at: str,
    finished_at: str,
    duration_seconds: float,
    metadata: dict[str, Any],
    team_metadata: dict[str, Any],
    task_metadata: dict[str, Any],
    history_metadata: dict[str, Any],
) -> dict[str, Any]:
    return {
        "status": "completed",
        "started_at": started_at,
        "finished_at": finished_at,
        "duration_seconds": round(duration_seconds, 3),
        "dataset_id": metadata["dataset_id"],
        "dataset_mode": metadata["dataset_mode"],
        "domain_profile": metadata["domain_profile"],
        "counts": metadata["counts"],
        "files": metadata["files"],
        "quality_summary": {
            "team": team_metadata.get("quality_summary", {}),
            "tasks": task_metadata.get("kanban_summary", {}),
            "history": history_metadata.get("quality_summary", {}),
            "training_pairs": metadata["quality_summary"]["training_pairs"],
        },
        "next_steps": [
            "open dataset in Data Viewer",
            "build features",
            "train models",
            "run recommendations",
        ],
    }


def validate_target_mode(target_mode: str) -> str:
    if target_mode not in TARGET_MODES:
        raise DatasetGenerationError(
            f"target_mode must be one of: {', '.join(sorted(TARGET_MODES))}"
        )

    return target_mode


def generate_full_dataset(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise DatasetGenerationError("Payload must be a JSON object")

    started_at = utc_now_iso()
    started_time = time.perf_counter()

    domain_profile = str(payload.get("domain_profile", "developers"))
    seed_value = payload.get("seed")
    seed = None if seed_value is None else int(seed_value)
    rng = random.Random(seed)

    dataset_mode, mode = resolve_mode(payload)
    dataset_id = str(
        payload.get("dataset_id")
        or generate_dataset_id(
            domain_profile=domain_profile,
            dataset_mode=dataset_mode,
            seed=seed,
        )
    )
    overwrite = bool(payload.get("overwrite", False))
    dataset_dir = prepare_dataset_dir(dataset_id, overwrite=overwrite)

    target_mode = validate_target_mode(str(payload.get("target_mode", "balanced")))

    schema = load_feature_schema(domain_profile)
    schema_preview_payload = schema_preview(schema)

    team_payload = build_team_payload(payload, dataset_id, domain_profile, seed, mode)
    employees, team_metadata = call_team_generator(team_payload, dataset_dir)

    tasks_payload = build_tasks_payload(payload, dataset_id, domain_profile, seed, mode)
    task_result = generate_tasks(tasks_payload)
    tasks = extract_records(task_result, "tasks", dataset_dir / "tasks.json")
    backlog = extract_records(task_result, "backlog", dataset_dir / "backlog.json")
    task_metadata = task_result.get("metadata", {})

    history_payload = build_history_payload(payload, dataset_id, domain_profile, seed, mode)
    history_result = generate_assignment_history(history_payload)
    assignment_history = extract_records(
        history_result,
        "assignment_history",
        dataset_dir / "assignment_history.json",
    )
    history_metadata = history_result.get("metadata", {})

    pair_settings = TrainingPairSettings(
        dataset_id=dataset_id,
        target_pairs=mode.target_pairs,
        candidates_per_task=mode.candidates_per_task,
        target_mode=target_mode,
        seed=None if seed is None else seed + 3,
    )
    training_pairs = build_training_pairs(
        employees=employees,
        tasks=tasks,
        assignment_history=assignment_history,
        settings=pair_settings,
    )
    training_pairs = assign_splits(training_pairs, seed=None if seed is None else seed + 4)
    rng.shuffle(training_pairs)

    training_pairs_path = dataset_dir / "training_pairs.parquet"
    write_training_pairs_parquet(training_pairs_path, training_pairs)
    training_pairs_summary = summarize_training_pairs(training_pairs)

    metadata = build_dataset_metadata(
        dataset_id=dataset_id,
        dataset_dir=dataset_dir,
        dataset_mode=dataset_mode,
        domain_profile=domain_profile,
        seed=seed,
        mode=mode,
        employees=employees,
        tasks=tasks,
        backlog=backlog,
        assignment_history=assignment_history,
        training_pairs_summary=training_pairs_summary,
        schema_preview_payload=schema_preview_payload,
    )

    finished_at = utc_now_iso()
    duration_seconds = time.perf_counter() - started_time
    generation_report = build_generation_report(
        started_at=started_at,
        finished_at=finished_at,
        duration_seconds=duration_seconds,
        metadata=metadata,
        team_metadata=team_metadata,
        task_metadata=task_metadata if isinstance(task_metadata, dict) else {},
        history_metadata=history_metadata if isinstance(history_metadata, dict) else {},
    )

    write_json(dataset_dir / "dataset_metadata.json", metadata)
    write_json(dataset_dir / "generation_report.json", generation_report)

    return {
        "dataset_id": dataset_id,
        "dataset_dir": str(dataset_dir),
        "metadata": metadata,
        "generation_report": generation_report,
        "preview": {
            "employees": employees[:5],
            "tasks": tasks[:5],
            "backlog": backlog[:5],
            "assignment_history": assignment_history[:5],
            "training_pairs_summary": training_pairs_summary,
        },
    }