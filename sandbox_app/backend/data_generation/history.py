from __future__ import annotations

import csv
import json
import random
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from sandbox_app.backend.core.paths import GENERATED_DATA_DIR
from sandbox_app.backend.data_generation.outcomes import build_assignment_outcome

CSV_FIELDS = [
    "assignment_id",
    "task_id",
    "employee_id",
    "assigned_at",
    "completed_at",
    "planned_hours",
    "actual_hours",
    "quality_score",
    "deadline_status",
    "outcome_label",
    "was_rework_needed",
    "feedback_score",
    "success_score",
    "skill_match_score",
    "task_complexity",
    "employee_workload",
    "employee_fatigue",
    "employee_grade",
]


@dataclass(frozen=True)
class HistoryGenerationRequest:
    seed: int = 42
    employees_dataset_id: str = ""
    tasks_dataset_id: str = ""
    history_depth_per_employee: int = 100
    good_outcome_share: float = 0.62
    bad_outcome_share: float = 0.16
    late_outcome_share: float = 0.14
    failed_outcome_share: float = 0.08
    rework_probability: float = 0.12
    overload_penalty_strength: float = 0.22
    fatigue_penalty_strength: float = 0.18
    skill_match_bonus_strength: float = 0.34
    learning_bonus_strength: float = 0.08
    complexity_penalty_strength: float = 0.20
    learning_task_share: float = 0.20


def generate_history(payload: dict[str, Any]) -> dict[str, Any]:
    request = parse_generation_request(payload)
    rng = random.Random(request.seed)

    employees = load_records_from_payload_or_dataset(
        payload,
        "employees",
        request.employees_dataset_id,
        "employees.json",
    )
    tasks = load_records_from_payload_or_dataset(
        payload,
        "tasks",
        request.tasks_dataset_id,
        "tasks.json",
    )

    if not employees:
        raise ValueError("employees are required for history generation.")

    if not tasks:
        raise ValueError("tasks are required for history generation.")

    dataset_id = build_dataset_id()
    dataset_dir = GENERATED_DATA_DIR / dataset_id
    dataset_dir.mkdir(parents=True, exist_ok=True)

    params = build_outcome_params(request)
    assignments = build_assignments(employees, tasks, request, params, rng)
    metadata = build_metadata(dataset_id, request, assignments)

    write_json(dataset_dir / "assignment_history.json", assignments)
    write_csv(dataset_dir / "assignment_history.csv", assignments)
    write_json(dataset_dir / "history_metadata.json", metadata)

    return {
        "dataset_id": dataset_id,
        "dataset_dir": str(dataset_dir),
        "assignments_count": len(assignments),
        "history_preview": assignments[: min(20, len(assignments))],
        "summary": build_summary(assignments),
        "files": {
            "assignment_history_json": str(
                dataset_dir / "assignment_history.json"
            ),
            "assignment_history_csv": str(
                dataset_dir / "assignment_history.csv"
            ),
            "history_metadata": str(dataset_dir / "history_metadata.json"),
        },
        "metadata": metadata,
    }


def parse_generation_request(payload: dict[str, Any]) -> HistoryGenerationRequest:
    history_depth = int(payload.get("history_depth_per_employee", 100))

    if history_depth < 1:
        raise ValueError("history_depth_per_employee must be greater than zero.")

    if history_depth > 10_000:
        raise ValueError("history_depth_per_employee is too large.")

    return HistoryGenerationRequest(
        seed=int(payload.get("seed", 42)),
        employees_dataset_id=str(payload.get("employees_dataset_id", "")),
        tasks_dataset_id=str(payload.get("tasks_dataset_id", "")),
        history_depth_per_employee=history_depth,
        good_outcome_share=float(payload.get("good_outcome_share", 0.62)),
        bad_outcome_share=float(payload.get("bad_outcome_share", 0.16)),
        late_outcome_share=float(payload.get("late_outcome_share", 0.14)),
        failed_outcome_share=float(payload.get("failed_outcome_share", 0.08)),
        rework_probability=float(payload.get("rework_probability", 0.12)),
        overload_penalty_strength=float(
            payload.get("overload_penalty_strength", 0.22)
        ),
        fatigue_penalty_strength=float(
            payload.get("fatigue_penalty_strength", 0.18)
        ),
        skill_match_bonus_strength=float(
            payload.get("skill_match_bonus_strength", 0.34)
        ),
        learning_bonus_strength=float(
            payload.get("learning_bonus_strength", 0.08)
        ),
        complexity_penalty_strength=float(
            payload.get("complexity_penalty_strength", 0.20)
        ),
        learning_task_share=float(payload.get("learning_task_share", 0.20)),
    )


def build_assignments(
    employees: list[dict[str, Any]],
    tasks: list[dict[str, Any]],
    request: HistoryGenerationRequest,
    params: dict[str, float],
    rng: random.Random,
) -> list[dict[str, Any]]:
    assignments = []
    assignment_index = 1

    for employee in employees:
        for _ in range(request.history_depth_per_employee):
            task = choose_task_for_employee(employee, tasks, request, rng)
            assigned_at = build_assigned_at(rng)
            planned_hours = float(task.get("estimated_hours", 8.0))
            outcome = build_assignment_outcome(
                employee,
                task,
                assigned_at,
                planned_hours,
                params,
                rng,
            )

            assignments.append(
                build_assignment_record(
                    assignment_index,
                    employee,
                    task,
                    assigned_at,
                    planned_hours,
                    outcome,
                )
            )
            assignment_index += 1

    return assignments


def choose_task_for_employee(
    employee: dict[str, Any],
    tasks: list[dict[str, Any]],
    request: HistoryGenerationRequest,
    rng: random.Random,
) -> dict[str, Any]:
    if rng.random() < request.learning_task_share:
        learning_task = choose_learning_task(employee, tasks, rng)

        if learning_task is not None:
            return learning_task

    return rng.choice(tasks)


def choose_learning_task(
    employee: dict[str, Any],
    tasks: list[dict[str, Any]],
    rng: random.Random,
) -> dict[str, Any] | None:
    learning_goals = set(employee.get("learning_goals", []))

    if not learning_goals:
        return None

    candidates = [
        task
        for task in tasks
        if learning_goals.intersection(set(task.get("required_skills", [])))
    ]

    if not candidates:
        return None

    return rng.choice(candidates)


def build_assignment_record(
    assignment_index: int,
    employee: dict[str, Any],
    task: dict[str, Any],
    assigned_at: datetime,
    planned_hours: float,
    outcome: dict[str, Any],
) -> dict[str, Any]:
    return {
        "assignment_id": f"ASN-{assignment_index:08d}",
        "task_id": task["task_id"],
        "employee_id": employee["employee_id"],
        "assigned_at": assigned_at.replace(tzinfo=UTC).isoformat(),
        "completed_at": outcome["completed_at"],
        "planned_hours": round_float(planned_hours),
        "actual_hours": outcome["actual_hours"],
        "quality_score": outcome["quality_score"],
        "deadline_status": outcome["deadline_status"],
        "outcome_label": outcome["outcome_label"],
        "was_rework_needed": outcome["was_rework_needed"],
        "feedback_score": outcome["feedback_score"],
        "success_score": outcome["success_score"],
        "skill_match_score": outcome["skill_match_score"],
        "task_complexity": task.get("complexity", 0),
        "employee_workload": employee.get("current_workload", 0),
        "employee_fatigue": employee.get("fatigue_level", 0),
        "employee_grade": employee.get("grade", ""),
    }


def build_assigned_at(rng: random.Random) -> datetime:
    days_ago = rng.randint(1, 365)
    hours_ago = rng.randint(0, 23)

    return datetime.now(UTC) - timedelta(days=days_ago, hours=hours_ago)


def build_outcome_params(
    request: HistoryGenerationRequest,
) -> dict[str, float]:
    return {
        "rework_probability": request.rework_probability,
        "overload_penalty_strength": request.overload_penalty_strength,
        "fatigue_penalty_strength": request.fatigue_penalty_strength,
        "skill_match_bonus_strength": request.skill_match_bonus_strength,
        "learning_bonus_strength": request.learning_bonus_strength,
        "complexity_penalty_strength": request.complexity_penalty_strength,
    }


def build_metadata(
    dataset_id: str,
    request: HistoryGenerationRequest,
    assignments: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "dataset_id": dataset_id,
        "created_at": datetime.now(UTC).isoformat(),
        "generator": "sandbox_assignment_history_generator",
        "assignments_count": len(assignments),
        "summary": build_summary(assignments),
        "request": {
            "seed": request.seed,
            "employees_dataset_id": request.employees_dataset_id,
            "tasks_dataset_id": request.tasks_dataset_id,
            "history_depth_per_employee": request.history_depth_per_employee,
            "good_outcome_share": request.good_outcome_share,
            "bad_outcome_share": request.bad_outcome_share,
            "late_outcome_share": request.late_outcome_share,
            "failed_outcome_share": request.failed_outcome_share,
            "rework_probability": request.rework_probability,
            "overload_penalty_strength": request.overload_penalty_strength,
            "fatigue_penalty_strength": request.fatigue_penalty_strength,
            "skill_match_bonus_strength": request.skill_match_bonus_strength,
            "learning_task_share": request.learning_task_share,
        },
    }


def build_summary(assignments: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "outcomes": count_values(assignments, "outcome_label"),
        "deadline_statuses": count_values(assignments, "deadline_status"),
        "grades": count_values(assignments, "employee_grade"),
        "avg_quality": average(assignments, "quality_score"),
        "avg_feedback": average(assignments, "feedback_score"),
        "avg_actual_hours": average(assignments, "actual_hours"),
        "avg_skill_match": average(assignments, "skill_match_score"),
        "rework_count": count_true(assignments, "was_rework_needed"),
    }


def load_records_from_payload_or_dataset(
    payload: dict[str, Any],
    payload_key: str,
    dataset_id: str,
    file_name: str,
) -> list[dict[str, Any]]:
    payload_records = payload.get(payload_key)

    if isinstance(payload_records, list):
        return payload_records

    if not dataset_id:
        return []

    dataset_path = GENERATED_DATA_DIR / dataset_id / file_name

    if not dataset_path.exists():
        raise ValueError(f"Dataset file not found: {dataset_path}")

    with dataset_path.open("r", encoding="utf-8") as file:
        records = json.load(file)

    if not isinstance(records, list):
        raise ValueError(f"Dataset file must contain a list: {dataset_path}")

    return records


def count_values(
    records: list[dict[str, Any]],
    key: str,
) -> dict[str, int]:
    counts: dict[str, int] = {}

    for record in records:
        value = str(record.get(key, ""))
        counts[value] = counts.get(value, 0) + 1

    return dict(sorted(counts.items()))


def count_true(
    records: list[dict[str, Any]],
    key: str,
) -> int:
    return sum(1 for record in records if bool(record.get(key)))


def average(
    records: list[dict[str, Any]],
    key: str,
) -> float:
    if not records:
        return 0.0

    total = sum(float(record.get(key, 0)) for record in records)
    return round_float(total / len(records))


def write_json(path: Path, payload: Any) -> None:
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)
        file.write("\n")


def write_csv(path: Path, assignments: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
        writer.writeheader()

        for assignment in assignments:
            writer.writerow(assignment)


def build_dataset_id() -> str:
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    short_id = uuid.uuid4().hex[:8]

    return f"history_{timestamp}_{short_id}"


def round_float(value: float) -> float:
    return round(value, 4)