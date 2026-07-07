from __future__ import annotations

import json
import random
import shutil
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from sandbox_app.backend.core.paths import GENERATED_DATA_DIR
from sandbox_app.backend.data_generation.employees import generate_team
from sandbox_app.backend.data_generation.history import generate_history
from sandbox_app.backend.data_generation.outcomes import calculate_skill_match
from sandbox_app.backend.data_generation.tasks import generate_tasks

DATASET_MODES = {
    "small_preview": {
        "employees_count": 10,
        "tasks_count": 100,
        "target_pairs": 1_000,
        "history_depth_per_employee": 25,
        "candidates_per_task": 10,
    },
    "medium_validation": {
        "employees_count": 30,
        "tasks_count": 1_000,
        "target_pairs": 30_000,
        "history_depth_per_employee": 75,
        "candidates_per_task": 30,
    },
    "large_training": {
        "employees_count": 100,
        "tasks_count": 10_000,
        "target_pairs": 1_000_000,
        "history_depth_per_employee": 150,
        "candidates_per_task": 100,
    },
    "huge_training": {
        "employees_count": 100,
        "tasks_count": 10_000,
        "target_pairs": 1_000_000,
        "history_depth_per_employee": 150,
        "candidates_per_task": 100,
    },
}

HUGE_PAIR_LIMIT = 1_000_000


@dataclass(frozen=True)
class TrainingDatasetRequest:
    seed: int
    mode: str
    domain_profile: str
    employees_count: int
    tasks_count: int
    target_pairs: int
    history_depth_per_employee: int
    candidates_per_task: int
    projects_count: int
    balance_classes: bool
    confirm_huge_generation: bool


def generate_training_dataset(payload: dict[str, Any]) -> dict[str, Any]:
    request = parse_generation_request(payload)
    rng = random.Random(request.seed)

    dataset_id = build_dataset_id(request.mode, request.domain_profile)
    dataset_dir = GENERATED_DATA_DIR / dataset_id
    dataset_dir.mkdir(parents=True, exist_ok=True)

    team_result = generate_team(
        {
            "seed": request.seed,
            "employees_count": request.employees_count,
            "domain_profile": request.domain_profile,
        }
    )
    tasks_result = generate_tasks(
        {
            "seed": request.seed + 1,
            "tasks_count": request.tasks_count,
            "projects_count": request.projects_count,
            "domain_profile": request.domain_profile,
        }
    )

    employees = read_json(Path(team_result["files"]["employees_json"]))
    tasks = read_json(Path(tasks_result["files"]["tasks_json"]))

    history_result = generate_history(
        {
            "seed": request.seed + 2,
            "employees": employees,
            "tasks": tasks,
            "history_depth_per_employee": request.history_depth_per_employee,
        }
    )
    assignment_history = read_json(
        Path(history_result["files"]["assignment_history_json"])
    )

    training_pairs = build_training_pairs(employees, tasks, request, rng)

    if request.balance_classes:
        training_pairs = balance_training_pairs(training_pairs, rng)

    write_dataset_files(
        dataset_dir,
        employees,
        tasks,
        assignment_history,
        training_pairs,
    )

    metadata = build_dataset_metadata(
        dataset_id,
        request,
        employees,
        tasks,
        assignment_history,
        training_pairs,
    )
    generation_report = build_generation_report(training_pairs, metadata)

    write_json(dataset_dir / "dataset_metadata.json", metadata)
    write_json(dataset_dir / "generation_report.json", generation_report)

    cleanup_nested_dataset(team_result["dataset_dir"])
    cleanup_nested_dataset(tasks_result["dataset_dir"])
    cleanup_nested_dataset(history_result["dataset_dir"])

    return {
        "dataset_id": dataset_id,
        "dataset_dir": str(dataset_dir),
        "employees_count": len(employees),
        "tasks_count": len(tasks),
        "assignment_history_count": len(assignment_history),
        "training_pairs_count": len(training_pairs),
        "training_pairs_preview": training_pairs[: min(20, len(training_pairs))],
        "metadata": metadata,
        "generation_report": generation_report,
        "files": {
            "employees_csv": str(dataset_dir / "employees.csv"),
            "employees_json": str(dataset_dir / "employees.json"),
            "tasks_csv": str(dataset_dir / "tasks.csv"),
            "tasks_json": str(dataset_dir / "tasks.json"),
            "assignment_history_csv": str(
                dataset_dir / "assignment_history.csv"
            ),
            "assignment_history_json": str(
                dataset_dir / "assignment_history.json"
            ),
            "training_pairs_parquet": str(
                dataset_dir / "training_pairs.parquet"
            ),
            "dataset_metadata": str(dataset_dir / "dataset_metadata.json"),
            "generation_report": str(dataset_dir / "generation_report.json"),
        },
    }


def parse_generation_request(payload: dict[str, Any]) -> TrainingDatasetRequest:
    mode = str(payload.get("mode", "small_preview"))

    if mode not in DATASET_MODES:
        raise ValueError(f"Unsupported dataset mode: {mode}")

    defaults = DATASET_MODES[mode]
    employees_count = int(
        payload.get("employees_count", defaults["employees_count"])
    )
    tasks_count = int(payload.get("tasks_count", defaults["tasks_count"]))
    target_pairs = int(payload.get("target_pairs", defaults["target_pairs"]))
    history_depth = int(
        payload.get(
            "history_depth_per_employee",
            defaults["history_depth_per_employee"],
        )
    )
    candidates_per_task = int(
        payload.get("candidates_per_task", defaults["candidates_per_task"])
    )
    confirm_huge = bool(payload.get("confirm_huge_generation", False))

    if target_pairs > HUGE_PAIR_LIMIT and not confirm_huge:
        raise ValueError(
            "Huge generation requires confirm_huge_generation=true."
        )

    if mode == "huge_training" and not confirm_huge:
        raise ValueError(
            "huge_training mode requires confirm_huge_generation=true."
        )

    validate_positive(employees_count, "employees_count")
    validate_positive(tasks_count, "tasks_count")
    validate_positive(target_pairs, "target_pairs")
    validate_positive(history_depth, "history_depth_per_employee")
    validate_positive(candidates_per_task, "candidates_per_task")

    return TrainingDatasetRequest(
        seed=int(payload.get("seed", 42)),
        mode=mode,
        domain_profile=str(payload.get("domain_profile", "developers")),
        employees_count=employees_count,
        tasks_count=tasks_count,
        target_pairs=target_pairs,
        history_depth_per_employee=history_depth,
        candidates_per_task=candidates_per_task,
        projects_count=int(payload.get("projects_count", 5)),
        balance_classes=bool(payload.get("balance_classes", True)),
        confirm_huge_generation=confirm_huge,
    )


def build_training_pairs(
    employees: list[dict[str, Any]],
    tasks: list[dict[str, Any]],
    request: TrainingDatasetRequest,
    rng: random.Random,
) -> list[dict[str, Any]]:
    pairs = []
    pair_index = 1
    max_candidates = min(request.candidates_per_task, len(employees))

    while len(pairs) < request.target_pairs:
        task = rng.choice(tasks)
        candidates = choose_candidates(task, employees, max_candidates, rng)

        for employee in candidates:
            if len(pairs) >= request.target_pairs:
                break

            score = calculate_pair_score(employee, task)
            pairs.append(
                build_pair_record(pair_index, employee, task, score)
            )
            pair_index += 1

    return pairs


def choose_candidates(
    task: dict[str, Any],
    employees: list[dict[str, Any]],
    max_candidates: int,
    rng: random.Random,
) -> list[dict[str, Any]]:
    ranked = sorted(
        employees,
        key=lambda employee: calculate_skill_match(employee, task),
        reverse=True,
    )
    top_count = max(1, max_candidates // 3)
    positive_pool = ranked[: max(top_count, 1)]
    random_pool = rng.sample(employees, max_candidates)

    candidates_by_id = {
        employee["employee_id"]: employee
        for employee in positive_pool + random_pool
    }

    candidates = list(candidates_by_id.values())
    rng.shuffle(candidates)

    return candidates[:max_candidates]


def build_pair_record(
    pair_index: int,
    employee: dict[str, Any],
    task: dict[str, Any],
    score: float,
) -> dict[str, Any]:
    label = 1 if score >= 0.62 else 0

    return {
        "pair_id": f"PAIR-{pair_index:010d}",
        "task_id": task["task_id"],
        "employee_id": employee["employee_id"],
        "label": label,
        "target_score": round_float(score),
        "skill_match": round_float(calculate_skill_match(employee, task)),
        "task_complexity": task.get("complexity", 0),
        "estimated_hours": task.get("estimated_hours", 0),
        "deadline_days": task.get("deadline_days", 0),
        "task_priority": task.get("priority", ""),
        "employee_grade": employee.get("grade", ""),
        "employee_workload": employee.get("current_workload", 0),
        "employee_fatigue": employee.get("fatigue_level", 0),
        "availability_score": employee.get("availability_score", 0),
        "avg_quality_score": employee.get("avg_quality_score", 0),
        "avg_completion_speed": employee.get("avg_completion_speed", 0),
        "deadline_reliability": employee.get("deadline_reliability", 0),
        "mentor_level": employee.get("mentor_level", 0),
    }


def calculate_pair_score(
    employee: dict[str, Any],
    task: dict[str, Any],
) -> float:
    skill_match = calculate_skill_match(employee, task)
    quality = float(employee.get("avg_quality_score", 0.5))
    speed = float(employee.get("avg_completion_speed", 0.5))
    reliability = float(employee.get("deadline_reliability", 0.5))
    workload = float(employee.get("current_workload", 0.5))
    fatigue = float(employee.get("fatigue_level", 0.3))
    complexity = float(task.get("complexity", 5)) / 10.0

    score = 0.18
    score += skill_match * 0.32
    score += quality * 0.18
    score += speed * 0.10
    score += reliability * 0.12
    score -= workload * 0.10
    score -= fatigue * 0.07
    score -= complexity * 0.05

    return clamp(score, 0.0, 1.0)


def balance_training_pairs(
    pairs: list[dict[str, Any]],
    rng: random.Random,
) -> list[dict[str, Any]]:
    positive_pairs = [pair for pair in pairs if pair["label"] == 1]
    negative_pairs = [pair for pair in pairs if pair["label"] == 0]

    if not positive_pairs or not negative_pairs:
        return pairs

    target_count = min(len(positive_pairs), len(negative_pairs))
    balanced_pairs = rng.sample(positive_pairs, target_count)
    balanced_pairs += rng.sample(negative_pairs, target_count)
    rng.shuffle(balanced_pairs)

    return balanced_pairs


def write_dataset_files(
    dataset_dir: Path,
    employees: list[dict[str, Any]],
    tasks: list[dict[str, Any]],
    assignment_history: list[dict[str, Any]],
    training_pairs: list[dict[str, Any]],
) -> None:
    write_json(dataset_dir / "employees.json", employees)
    write_json(dataset_dir / "tasks.json", tasks)
    write_json(dataset_dir / "assignment_history.json", assignment_history)

    pd.DataFrame(employees).to_csv(dataset_dir / "employees.csv", index=False)
    pd.DataFrame(tasks).to_csv(dataset_dir / "tasks.csv", index=False)
    pd.DataFrame(assignment_history).to_csv(
        dataset_dir / "assignment_history.csv",
        index=False,
    )
    pd.DataFrame(training_pairs).to_parquet(
        dataset_dir / "training_pairs.parquet",
        index=False,
    )


def build_dataset_metadata(
    dataset_id: str,
    request: TrainingDatasetRequest,
    employees: list[dict[str, Any]],
    tasks: list[dict[str, Any]],
    assignment_history: list[dict[str, Any]],
    training_pairs: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "dataset_id": dataset_id,
        "created_at": datetime.now(UTC).isoformat(),
        "generator": "sandbox_training_dataset_generator",
        "mode": request.mode,
        "domain_profile": request.domain_profile,
        "seed": request.seed,
        "employees_count": len(employees),
        "tasks_count": len(tasks),
        "assignment_history_count": len(assignment_history),
        "training_pairs_count": len(training_pairs),
        "class_balance": count_values(training_pairs, "label"),
        "roles": count_values(employees, "role"),
        "grades": count_values(employees, "grade"),
        "task_statuses": count_values(tasks, "status"),
        "task_priorities": count_values(tasks, "priority"),
        "request": request.__dict__,
    }


def build_generation_report(
    training_pairs: list[dict[str, Any]],
    metadata: dict[str, Any],
) -> dict[str, Any]:
    return {
        "dataset_id": metadata["dataset_id"],
        "mode": metadata["mode"],
        "training_pairs_count": len(training_pairs),
        "class_balance": metadata["class_balance"],
        "avg_target_score": average(training_pairs, "target_score"),
        "avg_skill_match": average(training_pairs, "skill_match"),
        "roles": metadata["roles"],
        "grades": metadata["grades"],
        "task_statuses": metadata["task_statuses"],
        "task_priorities": metadata["task_priorities"],
    }


def read_json(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    if not isinstance(payload, list):
        raise ValueError(f"Expected list JSON file: {path}")

    return payload


def write_json(path: Path, payload: Any) -> None:
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)
        file.write("\n")


def cleanup_nested_dataset(dataset_dir: str) -> None:
    path = Path(dataset_dir)

    if path.exists() and path.is_dir():
        shutil.rmtree(path)


def count_values(
    records: list[dict[str, Any]],
    key: str,
) -> dict[str, int]:
    counts: dict[str, int] = {}

    for record in records:
        value = str(record.get(key, ""))
        counts[value] = counts.get(value, 0) + 1

    return dict(sorted(counts.items()))


def average(
    records: list[dict[str, Any]],
    key: str,
) -> float:
    if not records:
        return 0.0

    total = sum(float(record.get(key, 0)) for record in records)
    return round_float(total / len(records))


def validate_positive(value: int, label: str) -> None:
    if value < 1:
        raise ValueError(f"{label} must be greater than zero.")


def build_dataset_id(mode: str, domain_profile: str) -> str:
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    short_id = uuid.uuid4().hex[:8]

    return f"dataset_{mode}_{domain_profile}_{timestamp}_{short_id}"


def round_float(value: float) -> float:
    return round(value, 4)


def clamp(
    value: float,
    min_value: float,
    max_value: float,
) -> float:
    return max(min_value, min(max_value, value))