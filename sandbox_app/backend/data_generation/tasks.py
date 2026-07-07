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
from sandbox_app.backend.data_generation.backlog import (
    KANBAN_STATUSES,
    build_kanban_summary,
    get_backlog_tasks,
)
from sandbox_app.backend.features.schema import load_feature_schema

DEFAULT_TASK_TYPES = [
    "feature",
    "bugfix",
    "research",
    "maintenance",
    "review",
    "incident",
]

DEFAULT_PRIORITIES = [
    "low",
    "medium",
    "high",
    "critical",
]

DEFAULT_SKILLS = [
    "communication",
    "analysis",
    "planning",
    "quality_control",
    "problem_solving",
]

CSV_FIELDS = [
    "task_id",
    "title",
    "description",
    "task_type",
    "priority",
    "complexity",
    "estimated_hours",
    "deadline_days",
    "required_skills",
    "status",
    "project_id",
    "created_at",
    "dependencies",
    "custom_features",
]


@dataclass(frozen=True)
class TaskGenerationRequest:
    seed: int = 42
    tasks_count: int = 100
    projects_count: int = 5
    domain_profile: str = "developers"
    task_types: tuple[str, ...] = ()
    priorities: tuple[str, ...] = ()
    skills: tuple[str, ...] = ()
    todo_share: float = 0.45
    in_progress_share: float = 0.20
    review_share: float = 0.10
    done_share: float = 0.15
    blocked_share: float = 0.05
    failed_share: float = 0.05
    min_complexity: int = 1
    max_complexity: int = 10
    min_deadline_days: int = 1
    max_deadline_days: int = 30
    min_estimated_hours: float = 1.0
    max_estimated_hours: float = 40.0
    skill_count_min: int = 1
    skill_count_max: int = 4
    dependency_probability: float = 0.12
    skill_mismatch_probability: float = 0.10


def generate_tasks(payload: dict[str, Any]) -> dict[str, Any]:
    request = parse_generation_request(payload)
    schema = load_feature_schema(request.domain_profile)

    rng = random.Random(request.seed)
    dataset_id = build_dataset_id(request.domain_profile)
    dataset_dir = GENERATED_DATA_DIR / dataset_id
    dataset_dir.mkdir(parents=True, exist_ok=True)

    task_types = get_configured_values(
        request.task_types,
        [],
        DEFAULT_TASK_TYPES,
    )
    priorities = get_configured_values(
        request.priorities,
        [],
        DEFAULT_PRIORITIES,
    )
    skills = get_configured_values(
        request.skills,
        schema["skills"],
        DEFAULT_SKILLS,
    )

    tasks = [
        build_task(index, request, schema, task_types, priorities, skills, rng)
        for index in range(1, request.tasks_count + 1)
    ]
    add_dependencies(tasks, request, rng)

    backlog_tasks = get_backlog_tasks(tasks)
    metadata = build_metadata(dataset_id, request, schema, tasks, backlog_tasks)

    write_json(dataset_dir / "tasks.json", tasks)
    write_csv(dataset_dir / "tasks.csv", tasks)
    write_json(dataset_dir / "backlog.json", backlog_tasks)
    write_csv(dataset_dir / "backlog.csv", backlog_tasks)
    write_json(dataset_dir / "task_metadata.json", metadata)

    return {
        "dataset_id": dataset_id,
        "dataset_dir": str(dataset_dir),
        "tasks_count": len(tasks),
        "backlog_count": len(backlog_tasks),
        "tasks_preview": tasks[: min(20, len(tasks))],
        "backlog_preview": backlog_tasks[: min(20, len(backlog_tasks))],
        "summary": build_summary(tasks),
        "files": {
            "tasks_json": str(dataset_dir / "tasks.json"),
            "tasks_csv": str(dataset_dir / "tasks.csv"),
            "backlog_json": str(dataset_dir / "backlog.json"),
            "backlog_csv": str(dataset_dir / "backlog.csv"),
            "task_metadata": str(dataset_dir / "task_metadata.json"),
        },
        "metadata": metadata,
    }


def parse_generation_request(payload: dict[str, Any]) -> TaskGenerationRequest:
    tasks_count = int(payload.get("tasks_count", 100))
    projects_count = int(payload.get("projects_count", 5))

    if tasks_count < 1:
        raise ValueError("tasks_count must be greater than zero.")

    if tasks_count > 500_000:
        raise ValueError("tasks_count is too large for one request.")

    if projects_count < 1:
        raise ValueError("projects_count must be greater than zero.")

    min_complexity = int(payload.get("min_complexity", 1))
    max_complexity = int(payload.get("max_complexity", 10))
    min_deadline_days = int(payload.get("min_deadline_days", 1))
    max_deadline_days = int(payload.get("max_deadline_days", 30))
    min_estimated_hours = float(payload.get("min_estimated_hours", 1.0))
    max_estimated_hours = float(payload.get("max_estimated_hours", 40.0))

    validate_order(min_complexity, max_complexity, "complexity")
    validate_order(min_deadline_days, max_deadline_days, "deadline_days")
    validate_order(min_estimated_hours, max_estimated_hours, "estimated_hours")

    return TaskGenerationRequest(
        seed=int(payload.get("seed", 42)),
        tasks_count=tasks_count,
        projects_count=projects_count,
        domain_profile=str(payload.get("domain_profile", "developers")),
        task_types=tuple(payload.get("task_types", []) or ()),
        priorities=tuple(payload.get("priorities", []) or ()),
        skills=tuple(payload.get("skills", []) or ()),
        todo_share=float(payload.get("todo_share", 0.45)),
        in_progress_share=float(payload.get("in_progress_share", 0.20)),
        review_share=float(payload.get("review_share", 0.10)),
        done_share=float(payload.get("done_share", 0.15)),
        blocked_share=float(payload.get("blocked_share", 0.05)),
        failed_share=float(payload.get("failed_share", 0.05)),
        min_complexity=min_complexity,
        max_complexity=max_complexity,
        min_deadline_days=min_deadline_days,
        max_deadline_days=max_deadline_days,
        min_estimated_hours=min_estimated_hours,
        max_estimated_hours=max_estimated_hours,
        skill_count_min=int(payload.get("skill_count_min", 1)),
        skill_count_max=int(payload.get("skill_count_max", 4)),
        dependency_probability=float(payload.get("dependency_probability", 0.12)),
        skill_mismatch_probability=float(
            payload.get("skill_mismatch_probability", 0.10)
        ),
    )


def build_task(
    index: int,
    request: TaskGenerationRequest,
    schema: dict[str, Any],
    task_types: list[str],
    priorities: list[str],
    skills: list[str],
    rng: random.Random,
) -> dict[str, Any]:
    task_type = rng.choice(task_types)
    priority = rng.choice(priorities)
    complexity = rng.randint(request.min_complexity, request.max_complexity)
    estimated_hours = build_estimated_hours(complexity, request, rng)
    deadline_days = rng.randint(
        request.min_deadline_days,
        request.max_deadline_days,
    )
    required_skills = choose_required_skills(request, skills, rng)
    project_id = f"PRJ-{rng.randint(1, request.projects_count):03d}"
    created_at = datetime.now(UTC) - timedelta(days=rng.randint(0, 60))

    return {
        "task_id": f"TASK-{index:06d}",
        "title": build_title(task_type, index),
        "description": build_description(task_type, priority, complexity),
        "task_type": task_type,
        "priority": priority,
        "complexity": complexity,
        "estimated_hours": estimated_hours,
        "deadline_days": deadline_days,
        "required_skills": required_skills,
        "status": choose_status(request, rng),
        "project_id": project_id,
        "created_at": created_at.isoformat(),
        "dependencies": [],
        "custom_features": build_custom_features(schema, rng),
    }


def choose_status(
    request: TaskGenerationRequest,
    rng: random.Random,
) -> str:
    weights = [
        request.todo_share,
        request.in_progress_share,
        request.review_share,
        request.done_share,
        request.blocked_share,
        request.failed_share,
    ]

    return rng.choices(KANBAN_STATUSES, weights=weights, k=1)[0]


def choose_required_skills(
    request: TaskGenerationRequest,
    skills: list[str],
    rng: random.Random,
) -> list[str]:
    if not skills:
        return []

    max_possible = min(request.skill_count_max, len(skills))
    min_possible = min(request.skill_count_min, max_possible)
    skill_count = rng.randint(min_possible, max_possible)

    selected_skills = rng.sample(skills, skill_count)

    if rng.random() < request.skill_mismatch_probability:
        selected_skills.append(f"rare_skill_{rng.randint(1, 20):02d}")

    return sorted(set(selected_skills))


def add_dependencies(
    tasks: list[dict[str, Any]],
    request: TaskGenerationRequest,
    rng: random.Random,
) -> None:
    for index, task in enumerate(tasks):
        if index == 0:
            continue

        if rng.random() > request.dependency_probability:
            continue

        previous_tasks = tasks[:index]
        dependency_count = rng.randint(1, min(3, len(previous_tasks)))
        dependencies = rng.sample(previous_tasks, dependency_count)

        task["dependencies"] = [
            dependency["task_id"]
            for dependency in dependencies
        ]


def build_custom_features(
    schema: dict[str, Any],
    rng: random.Random,
) -> dict[str, Any]:
    custom_features = {}

    for feature in schema.get("task_features", []):
        custom_features[feature["name"]] = build_feature_value(feature, rng)

    return custom_features


def build_feature_value(
    feature: dict[str, Any],
    rng: random.Random,
) -> Any:
    feature_type = feature["type"]

    if feature_type == "numeric":
        return round_float(rng.uniform(feature.get("min", 0), feature.get("max", 1)))

    if feature_type == "boolean":
        return bool(rng.getrandbits(1))

    if feature_type == "categorical":
        values = feature.get("values", [])
        return rng.choice(values) if values else ""

    if feature_type == "text":
        return ""

    if feature_type == "skill_list":
        return []

    return None


def build_estimated_hours(
    complexity: int,
    request: TaskGenerationRequest,
    rng: random.Random,
) -> float:
    complexity_ratio = complexity / max(request.max_complexity, 1)
    base_hours = request.min_estimated_hours
    hours_range = request.max_estimated_hours - request.min_estimated_hours
    noise = rng.uniform(0.75, 1.25)

    estimated_hours = base_hours + hours_range * complexity_ratio * noise
    estimated_hours = clamp(
        estimated_hours,
        request.min_estimated_hours,
        request.max_estimated_hours,
    )

    return round_float(estimated_hours)


def build_title(task_type: str, index: int) -> str:
    readable_type = task_type.replace("_", " ").title()

    return f"{readable_type} task {index}"


def build_description(
    task_type: str,
    priority: str,
    complexity: int,
) -> str:
    return (
        f"Synthetic {task_type} task with {priority} priority "
        f"and complexity {complexity}."
    )


def build_metadata(
    dataset_id: str,
    request: TaskGenerationRequest,
    schema: dict[str, Any],
    tasks: list[dict[str, Any]],
    backlog_tasks: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "dataset_id": dataset_id,
        "created_at": datetime.now(UTC).isoformat(),
        "generator": "sandbox_task_generator",
        "domain_profile": request.domain_profile,
        "schema_title": schema.get("title", ""),
        "tasks_count": len(tasks),
        "backlog_count": len(backlog_tasks),
        "summary": build_summary(tasks),
        "request": {
            "seed": request.seed,
            "tasks_count": request.tasks_count,
            "projects_count": request.projects_count,
            "task_types": list(request.task_types),
            "priorities": list(request.priorities),
            "skills": list(request.skills),
            "dependency_probability": request.dependency_probability,
            "skill_mismatch_probability": request.skill_mismatch_probability,
        },
    }


def build_summary(tasks: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "statuses": build_kanban_summary(tasks),
        "task_types": count_values(tasks, "task_type"),
        "priorities": count_values(tasks, "priority"),
        "projects": count_values(tasks, "project_id"),
        "avg_complexity": average(tasks, "complexity"),
        "avg_estimated_hours": average(tasks, "estimated_hours"),
        "avg_deadline_days": average(tasks, "deadline_days"),
    }


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


def write_json(path: Path, payload: Any) -> None:
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)
        file.write("\n")


def write_csv(path: Path, tasks: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
        writer.writeheader()

        for task in tasks:
            writer.writerow(serialize_task_for_csv(task))


def serialize_task_for_csv(task: dict[str, Any]) -> dict[str, Any]:
    row = {}

    for field in CSV_FIELDS:
        value = task.get(field)

        if isinstance(value, list | dict):
            row[field] = json.dumps(value, ensure_ascii=False)
        else:
            row[field] = value

    return row


def get_configured_values(
    request_values: tuple[str, ...],
    schema_values: list[str],
    fallback_values: list[str],
) -> list[str]:
    values = list(request_values) or schema_values or fallback_values

    return [
        str(value).strip()
        for value in values
        if str(value).strip()
    ]


def validate_order(
    min_value: float,
    max_value: float,
    label: str,
) -> None:
    if min_value > max_value:
        raise ValueError(f"{label} min cannot be greater than max.")


def build_dataset_id(domain_profile: str) -> str:
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    short_id = uuid.uuid4().hex[:8]

    return f"tasks_{domain_profile}_{timestamp}_{short_id}"


def round_float(value: float) -> float:
    return round(value, 4)


def clamp(
    value: float,
    min_value: float,
    max_value: float,
) -> float:
    return max(min_value, min(max_value, value))