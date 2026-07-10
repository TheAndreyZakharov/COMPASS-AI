from __future__ import annotations

import csv
import json
import random
import re
from datetime import timedelta
from pathlib import Path
from typing import Any

from sandbox_app.backend.core.data_contracts import validate_record_required_fields
from sandbox_app.backend.core.paths import PATHS
from sandbox_app.backend.core.time import moscow_now, moscow_now_iso, moscow_stamp
from sandbox_app.backend.data_generation.outcomes import OutcomeConfig, build_outcome
from sandbox_app.backend.features.schema import load_feature_schema, schema_preview
from sandbox_app.backend.utils.json_io import read_json, write_json

GENERATED_ROOT = getattr(PATHS, "generated_data_dir", PATHS.data_dir / "generated")
DATASET_ID_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]{2,80}$")

CORE_OUTCOME_FEATURE_NAMES = {
    "assignment_id",
    "employee_id",
    "task_id",
    "assigned_at",
    "completed_at",
    "planned_hours",
    "actual_hours",
    "quality_score",
    "deadline_status",
    "outcome_label",
    "was_rework_needed",
    "feedback_score",
    "reviewer_id",
    "skill_match_score",
    "overload_score_at_assignment",
    "fatigue_score_at_assignment",
}


class HistoryGenerationError(RuntimeError):
    """Raised when sandbox assignment history generation cannot be completed safely."""


def utc_now():
    return moscow_now()


def utc_now_iso() -> str:
    return moscow_now_iso()


def validate_dataset_id(dataset_id: str) -> str:
    if not isinstance(dataset_id, str) or not DATASET_ID_RE.match(dataset_id):
        raise HistoryGenerationError(
            "dataset_id must be 3-81 chars and contain only letters, "
            "digits, underscores, or hyphens"
        )
    return dataset_id


def generate_dataset_id(domain_profile: str, seed: int | None) -> str:
    stamp = moscow_stamp()
    seed_part = "random" if seed is None else str(seed)
    return f"history_{domain_profile}_{stamp}_{seed_part}"


def int_setting(
    payload: dict[str, Any],
    name: str,
    default: int,
    minimum: int,
    maximum: int,
) -> int:
    value = int(payload.get(name, default))
    if value < minimum or value > maximum:
        raise HistoryGenerationError(f"{name} must be between {minimum} and {maximum}")
    return value


def float_setting(
    payload: dict[str, Any],
    name: str,
    default: float,
    minimum: float,
    maximum: float,
) -> float:
    value = float(payload.get(name, default))
    if value < minimum or value > maximum:
        raise HistoryGenerationError(f"{name} must be between {minimum} and {maximum}")
    return value


def normalize_records(payload: Any, name: str) -> list[dict[str, Any]]:
    if not isinstance(payload, list) or not payload:
        raise HistoryGenerationError(f"{name} must be a non-empty list")

    result: list[dict[str, Any]] = []
    for index, item in enumerate(payload):
        if not isinstance(item, dict):
            raise HistoryGenerationError(f"{name}[{index}] must be an object")
        result.append(item)

    return result


def load_dataset_records(
    dataset_id: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], Path]:
    dataset_id = validate_dataset_id(dataset_id)
    dataset_dir = GENERATED_ROOT / dataset_id

    employees_path = dataset_dir / "employees.json"
    tasks_path = dataset_dir / "tasks.json"

    if not employees_path.exists():
        raise HistoryGenerationError(
            f"employees.json not found for dataset_id '{dataset_id}'"
        )

    if not tasks_path.exists():
        raise HistoryGenerationError(
            f"tasks.json not found for dataset_id '{dataset_id}'"
        )

    employees = normalize_records(read_json(employees_path), "employees")
    tasks = normalize_records(read_json(tasks_path), "tasks")

    return employees, tasks, dataset_dir


def resolve_input_records(
    payload: dict[str, Any],
    domain_profile: str,
    seed: int | None,
) -> tuple[str, list[dict[str, Any]], list[dict[str, Any]], Path]:
    dataset_id_raw = payload.get("dataset_id")
    employees_payload = payload.get("employees")
    tasks_payload = payload.get("tasks")

    if employees_payload is not None and tasks_payload is not None:
        dataset_id = str(dataset_id_raw or generate_dataset_id(domain_profile, seed))
        dataset_dir = GENERATED_ROOT / validate_dataset_id(dataset_id)
        dataset_dir.mkdir(parents=True, exist_ok=True)
        return (
            dataset_id,
            normalize_records(employees_payload, "employees"),
            normalize_records(tasks_payload, "tasks"),
            dataset_dir,
        )

    if dataset_id_raw is None:
        raise HistoryGenerationError(
            "Provide either dataset_id or both employees and tasks in payload"
        )

    employees, tasks, dataset_dir = load_dataset_records(str(dataset_id_raw))
    return str(dataset_id_raw), employees, tasks, dataset_dir


def prepare_output_files(dataset_dir: Path, overwrite: bool) -> None:
    dataset_dir.mkdir(parents=True, exist_ok=True)

    output_files = [
        dataset_dir / "assignment_history.json",
        dataset_dir / "assignment_history.csv",
        dataset_dir / "history_metadata.json",
    ]

    existing = [path.name for path in output_files if path.exists()]
    if existing and not overwrite:
        raise HistoryGenerationError(
            "History files already exist for this dataset_id. "
            "Use overwrite=true to replace: "
            + ", ".join(existing)
        )


def select_task_for_employee(
    rng: random.Random,
    employee: dict[str, Any],
    tasks: list[dict[str, Any]],
    learning_task_share: float,
) -> dict[str, Any]:
    learning_goals = {str(item).lower() for item in employee.get("learning_goals", [])}

    if learning_goals and rng.random() < learning_task_share:
        matching_tasks = [
            task
            for task in tasks
            if learning_goals
            & {str(skill).lower() for skill in task.get("required_skills", [])}
        ]
        if matching_tasks:
            return rng.choice(matching_tasks)

    return rng.choice(tasks)


def assignment_dates(
    rng: random.Random,
    actual_hours: float,
    history_start_days_ago: int,
    history_end_days_ago: int,
) -> tuple[str, str]:
    now = utc_now()

    start_days_ago = rng.randint(history_end_days_ago, history_start_days_ago)
    assigned_at = now - timedelta(
        days=start_days_ago,
        hours=rng.randint(0, 23),
        minutes=rng.randint(0, 59),
    )

    duration_days = max(0.02, actual_hours / 8.0)
    completed_at = assigned_at + timedelta(
        days=duration_days,
        hours=rng.uniform(0, 8),
    )

    if completed_at > now:
        completed_at = now - timedelta(hours=rng.uniform(1, 12))

    return assigned_at.isoformat(), completed_at.isoformat()


def generate_custom_outcome_features(
    rng: random.Random,
    outcome_feature_definitions: list[dict[str, Any]],
) -> dict[str, Any]:
    custom_features: dict[str, Any] = {}

    for feature in outcome_feature_definitions:
        name = str(feature.get("name", ""))
        feature_type = str(feature.get("type", ""))

        if name in CORE_OUTCOME_FEATURE_NAMES:
            continue

        if feature_type == "numeric":
            minimum = float(feature.get("min", 0))
            maximum = float(feature.get("max", 1))
            custom_features[name] = round(rng.uniform(minimum, maximum), 3)

        elif feature_type == "categorical":
            values = [str(item) for item in feature.get("values", [])]
            custom_features[name] = rng.choice(values) if values else None

        elif feature_type == "boolean":
            custom_features[name] = bool(rng.getrandbits(1))

        elif feature_type == "text":
            custom_features[name] = f"Generated outcome value for {name}"

        elif feature_type == "skill_list":
            custom_features[name] = []

    return custom_features


def build_config(payload: dict[str, Any]) -> OutcomeConfig:
    return OutcomeConfig(
        good_outcome_share=float_setting(
            payload,
            "good_outcome_share",
            0.58,
            0,
            1,
        ),
        bad_outcome_share=float_setting(
            payload,
            "bad_outcome_share",
            0.18,
            0,
            1,
        ),
        late_outcome_share=float_setting(
            payload,
            "late_outcome_share",
            0.16,
            0,
            1,
        ),
        failed_outcome_share=float_setting(
            payload,
            "failed_outcome_share",
            0.08,
            0,
            1,
        ),
        rework_probability=float_setting(
            payload,
            "rework_probability",
            0.12,
            0,
            1,
        ),
        overload_penalty_strength=float_setting(
            payload,
            "overload_penalty_strength",
            0.28,
            0,
            2,
        ),
        fatigue_penalty_strength=float_setting(
            payload,
            "fatigue_penalty_strength",
            0.24,
            0,
            2,
        ),
        skill_match_bonus_strength=float_setting(
            payload,
            "skill_match_bonus_strength",
            0.34,
            0,
            2,
        ),
        learning_task_share=float_setting(
            payload,
            "learning_task_share",
            0.16,
            0,
            1,
        ),
    )


def generate_assignment_history(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise HistoryGenerationError("Payload must be a JSON object")

    domain_profile = str(payload.get("domain_profile", "developers"))
    seed_value = payload.get("seed")
    seed = None if seed_value is None else int(seed_value)
    rng = random.Random(seed)

    schema = load_feature_schema(domain_profile)
    preview = schema_preview(schema)

    dataset_id, employees, tasks, dataset_dir = resolve_input_records(
        payload,
        domain_profile,
        seed,
    )

    overwrite = bool(payload.get("overwrite", False))
    prepare_output_files(dataset_dir, overwrite=overwrite)

    history_depth_per_employee = int_setting(
        payload,
        "history_depth_per_employee",
        default=8,
        minimum=1,
        maximum=5000,
    )
    history_start_days_ago = int_setting(
        payload,
        "history_start_days_ago",
        default=365,
        minimum=1,
        maximum=3650,
    )
    history_end_days_ago = int_setting(
        payload,
        "history_end_days_ago",
        default=1,
        minimum=0,
        maximum=3650,
    )

    if history_end_days_ago > history_start_days_ago:
        raise HistoryGenerationError(
            "history_end_days_ago cannot be greater than history_start_days_ago"
        )

    outcome_config = build_config(payload)
    outcome_feature_definitions = schema.get("feature_groups", {}).get("outcome", [])

    history: list[dict[str, Any]] = []
    assignment_index = 1

    for employee in employees:
        employee_id = str(employee.get("employee_id", "")).strip()
        if not employee_id:
            raise HistoryGenerationError("Every employee must have employee_id")

        for _ in range(history_depth_per_employee):
            task = select_task_for_employee(
                rng=rng,
                employee=employee,
                tasks=tasks,
                learning_task_share=outcome_config.learning_task_share,
            )
            task_id = str(task.get("task_id", "")).strip()
            if not task_id:
                raise HistoryGenerationError("Every task must have task_id")

            outcome = build_outcome(employee, task, outcome_config, rng)
            assigned_at, completed_at = assignment_dates(
                rng=rng,
                actual_hours=float(outcome["actual_hours"]),
                history_start_days_ago=history_start_days_ago,
                history_end_days_ago=history_end_days_ago,
            )

            assignment = {
                "assignment_id": f"assignment_{assignment_index:08d}",
                "employee_id": employee_id,
                "task_id": task_id,
                "assigned_at": assigned_at,
                "completed_at": completed_at,
                "planned_hours": outcome["planned_hours"],
                "actual_hours": outcome["actual_hours"],
                "quality_score": outcome["quality_score"],
                "deadline_status": outcome["deadline_status"],
                "outcome_label": outcome["outcome_label"],
                "was_rework_needed": outcome["was_rework_needed"],
                "feedback_score": outcome["feedback_score"],
                "skill_match_score": outcome["skill_match_score"],
                "overload_score_at_assignment": outcome[
                    "overload_score_at_assignment"
                ],
                "fatigue_score_at_assignment": outcome[
                    "fatigue_score_at_assignment"
                ],
                "custom_outcome_features": generate_custom_outcome_features(
                    rng,
                    outcome_feature_definitions,
                ),
            }

            missing_required = validate_record_required_fields(
                "assignment_history",
                assignment,
            )
            if missing_required:
                raise HistoryGenerationError(
                    f"Generated assignment {assignment['assignment_id']} "
                    "missing required fields: "
                    + ", ".join(missing_required)
                )

            history.append(assignment)
            assignment_index += 1

    metadata = build_metadata(
        dataset_id=dataset_id,
        dataset_dir=dataset_dir,
        domain_profile=domain_profile,
        seed=seed,
        employees=employees,
        tasks=tasks,
        history=history,
        history_depth_per_employee=history_depth_per_employee,
        history_start_days_ago=history_start_days_ago,
        history_end_days_ago=history_end_days_ago,
        outcome_config=outcome_config,
        schema_preview_payload=preview,
    )

    write_json(dataset_dir / "assignment_history.json", history)
    write_json(dataset_dir / "history_metadata.json", metadata)
    write_assignment_history_csv(dataset_dir / "assignment_history.csv", history)

    return {
        "dataset_id": dataset_id,
        "dataset_dir": str(dataset_dir),
        "assignment_history": history,
        "metadata": metadata,
        "preview": {
            "assignment_history": history[:10],
        },
    }


def build_metadata(
    dataset_id: str,
    dataset_dir: Path,
    domain_profile: str,
    seed: int | None,
    employees: list[dict[str, Any]],
    tasks: list[dict[str, Any]],
    history: list[dict[str, Any]],
    history_depth_per_employee: int,
    history_start_days_ago: int,
    history_end_days_ago: int,
    outcome_config: OutcomeConfig,
    schema_preview_payload: dict[str, Any],
) -> dict[str, Any]:
    outcome_counts: dict[str, int] = {}
    deadline_counts: dict[str, int] = {}

    for assignment in history:
        outcome_label = str(assignment["outcome_label"])
        deadline_status = str(assignment["deadline_status"])

        outcome_counts[outcome_label] = outcome_counts.get(outcome_label, 0) + 1
        deadline_counts[deadline_status] = (
            deadline_counts.get(deadline_status, 0) + 1
        )

    avg_quality = sum(float(item["quality_score"]) for item in history) / max(
        1,
        len(history),
    )
    avg_feedback = sum(float(item["feedback_score"]) for item in history) / max(
        1,
        len(history),
    )
    rework_count = sum(
        1 for item in history if item.get("was_rework_needed") is True
    )

    return {
        "dataset_id": dataset_id,
        "domain_profile": domain_profile,
        "seed": seed,
        "created_at": utc_now_iso(),
        "generator": "sandbox_app.backend.data_generation.history",
        "schema_preview": schema_preview_payload,
        "settings": {
            "history_depth_per_employee": history_depth_per_employee,
            "history_start_days_ago": history_start_days_ago,
            "history_end_days_ago": history_end_days_ago,
            "good_outcome_share": outcome_config.good_outcome_share,
            "bad_outcome_share": outcome_config.bad_outcome_share,
            "late_outcome_share": outcome_config.late_outcome_share,
            "failed_outcome_share": outcome_config.failed_outcome_share,
            "rework_probability": outcome_config.rework_probability,
            "overload_penalty_strength": outcome_config.overload_penalty_strength,
            "fatigue_penalty_strength": outcome_config.fatigue_penalty_strength,
            "skill_match_bonus_strength": (
                outcome_config.skill_match_bonus_strength
            ),
            "learning_task_share": outcome_config.learning_task_share,
        },
        "counts": {
            "employees": len(employees),
            "tasks": len(tasks),
            "assignment_history": len(history),
            "rework": rework_count,
        },
        "quality_summary": {
            "avg_quality_score": round(avg_quality, 3),
            "avg_feedback_score": round(avg_feedback, 3),
            "outcome_counts": dict(sorted(outcome_counts.items())),
            "deadline_counts": dict(sorted(deadline_counts.items())),
        },
        "files": {
            "assignment_history_json": str(
                dataset_dir / "assignment_history.json"
            ),
            "assignment_history_csv": str(
                dataset_dir / "assignment_history.csv"
            ),
            "history_metadata_json": str(dataset_dir / "history_metadata.json"),
        },
    }


def write_assignment_history_csv(
    path: Path,
    history: list[dict[str, Any]],
) -> None:
    fieldnames = [
        "assignment_id",
        "employee_id",
        "task_id",
        "assigned_at",
        "completed_at",
        "planned_hours",
        "actual_hours",
        "quality_score",
        "deadline_status",
        "outcome_label",
        "was_rework_needed",
        "feedback_score",
        "skill_match_score",
        "overload_score_at_assignment",
        "fatigue_score_at_assignment",
        "custom_outcome_features",
    ]

    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8", newline="") as file_obj:
        writer = csv.DictWriter(file_obj, fieldnames=fieldnames)
        writer.writeheader()

        for assignment in history:
            row = dict(assignment)
            row["custom_outcome_features"] = json.dumps(
                assignment.get("custom_outcome_features", {}),
                ensure_ascii=False,
            )
            writer.writerow({field: row.get(field, "") for field in fieldnames})
