from __future__ import annotations

import csv
import json
import random
import re
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from sandbox_app.backend.core.data_contracts import validate_record_required_fields
from sandbox_app.backend.core.paths import PATHS
from sandbox_app.backend.data_generation.backlog import (
    build_backlog,
    build_kanban_summary,
)
from sandbox_app.backend.features.schema import load_feature_schema, schema_preview
from sandbox_app.backend.utils.json_io import write_json

GENERATED_ROOT = getattr(PATHS, "generated_data_dir", PATHS.data_dir / "generated")

DATASET_ID_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]{2,80}$")

TASK_STATUSES = ("todo", "in_progress", "review", "done", "blocked", "failed")
DEFAULT_PRIORITIES = ("low", "medium", "high", "critical")

DEFAULT_STATUS_DISTRIBUTION = {
    "todo": 0.42,
    "in_progress": 0.16,
    "review": 0.10,
    "done": 0.18,
    "blocked": 0.08,
    "failed": 0.06,
}

DEFAULT_PRIORITY_DISTRIBUTION = {
    "low": 0.22,
    "medium": 0.46,
    "high": 0.24,
    "critical": 0.08,
}

CORE_TASK_FEATURE_NAMES = {
    "task_id",
    "title",
    "description",
    "project_id",
    "task_type",
    "status",
    "priority",
    "complexity",
    "estimated_hours",
    "deadline_days",
    "required_skills",
    "dependencies",
    "created_at",
    "due_at",
    "assignee_id",
}

OUT_OF_DOMAIN_SKILLS = (
    "legacy_system_unknown",
    "missing_domain_context",
    "rare_tooling",
    "external_vendor_dependency",
    "ambiguous_requirement",
)


class TaskGenerationError(RuntimeError):
    """Raised when sandbox task generation cannot be completed safely."""


def utc_now() -> datetime:
    return datetime.now(UTC)


def utc_now_iso() -> str:
    return utc_now().isoformat()


def generate_dataset_id(domain_profile: str, seed: int | None) -> str:
    stamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    seed_part = "random" if seed is None else str(seed)
    return f"tasks_{domain_profile}_{stamp}_{seed_part}"


def validate_dataset_id(dataset_id: str) -> str:
    if not isinstance(dataset_id, str) or not DATASET_ID_RE.match(dataset_id):
        raise TaskGenerationError(
            "dataset_id must be 3-81 chars and contain only letters, "
            "digits, underscores, or hyphens"
        )
    return dataset_id


def int_setting(
    payload: dict[str, Any],
    name: str,
    default: int,
    minimum: int,
    maximum: int,
) -> int:
    value = int(payload.get(name, default))
    if value < minimum or value > maximum:
        raise TaskGenerationError(f"{name} must be between {minimum} and {maximum}")
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
        raise TaskGenerationError(f"{name} must be between {minimum} and {maximum}")
    return value


def list_setting(
    payload: dict[str, Any],
    name: str,
    fallback: list[str] | tuple[str, ...],
) -> list[str]:
    raw = payload.get(name)

    if raw is None:
        values = list(fallback)
    elif isinstance(raw, list):
        values = [str(item).strip() for item in raw if str(item).strip()]
    else:
        raise TaskGenerationError(f"{name} must be a list")

    if not values:
        raise TaskGenerationError(f"{name} must not be empty")

    return values


def distribution_setting(
    payload: dict[str, Any],
    name: str,
    fallback: dict[str, float],
    allowed_values: list[str] | tuple[str, ...],
) -> dict[str, float]:
    raw = payload.get(name, fallback)

    if not isinstance(raw, dict):
        raise TaskGenerationError(f"{name} must be an object")

    allowed = set(allowed_values)
    result: dict[str, float] = {}

    for key, value in raw.items():
        normalized_key = str(key)

        if normalized_key not in allowed:
            allowed_text = ", ".join(sorted(allowed))
            raise TaskGenerationError(
                f"{name} contains unsupported value '{normalized_key}'. "
                f"Allowed: {allowed_text}"
            )

        weight = float(value)
        if weight < 0:
            raise TaskGenerationError(f"{name}.{normalized_key} must be non-negative")

        result[normalized_key] = weight

    total = sum(result.values())
    if total <= 0:
        raise TaskGenerationError(f"{name} total weight must be greater than zero")

    return result


def default_priority_distribution(priorities: list[str]) -> dict[str, float]:
    distribution = {
        priority: DEFAULT_PRIORITY_DISTRIBUTION.get(priority, 1.0)
        for priority in priorities
    }

    if not distribution:
        raise TaskGenerationError("priorities must not be empty")

    return distribution


def weighted_choice(rng: random.Random, distribution: dict[str, float]) -> str:
    total = sum(distribution.values())
    threshold = rng.random() * total
    cumulative = 0.0

    for value, weight in distribution.items():
        cumulative += weight
        if threshold <= cumulative:
            return value

    return next(reversed(distribution))


def random_float(
    rng: random.Random,
    minimum: float,
    maximum: float,
    digits: int = 3,
) -> float:
    return round(rng.uniform(minimum, maximum), digits)


def prepare_dataset_dir(dataset_id: str, overwrite: bool) -> Path:
    dataset_id = validate_dataset_id(dataset_id)
    dataset_dir = GENERATED_ROOT / dataset_id
    dataset_dir.mkdir(parents=True, exist_ok=True)

    output_files = [
        dataset_dir / "tasks.json",
        dataset_dir / "tasks.csv",
        dataset_dir / "backlog.json",
        dataset_dir / "backlog.csv",
        dataset_dir / "task_metadata.json",
    ]

    existing = [path.name for path in output_files if path.exists()]
    if existing and not overwrite:
        existing_text = ", ".join(existing)
        raise TaskGenerationError(
            "Task files already exist for this dataset_id. "
            f"Use overwrite=true to replace: {existing_text}"
        )

    return dataset_dir


def normalize_range(
    payload: dict[str, Any],
    min_name: str,
    max_name: str,
    default_min: float,
    default_max: float,
    hard_min: float,
    hard_max: float,
) -> tuple[float, float]:
    minimum = float(payload.get(min_name, default_min))
    maximum = float(payload.get(max_name, default_max))

    if minimum < hard_min or maximum > hard_max or minimum > maximum:
        raise TaskGenerationError(
            f"Invalid range {min_name}/{max_name}. "
            f"Expected {hard_min} <= min <= max <= {hard_max}"
        )

    return minimum, maximum


def choose_required_skills(
    rng: random.Random,
    skills: list[str],
    minimum: int,
    maximum: int,
    skill_mismatch_probability: float,
) -> list[str]:
    if not skills:
        raise TaskGenerationError("skills must not be empty")

    count = rng.randint(minimum, maximum)
    selected = rng.sample(skills, k=min(count, len(skills)))

    if rng.random() < skill_mismatch_probability:
        selected.append(rng.choice(OUT_OF_DOMAIN_SKILLS))

    return sorted(set(selected))


def choose_dependencies(
    rng: random.Random,
    previous_task_ids: list[str],
    probability: float,
    max_dependencies_per_task: int,
) -> list[str]:
    if max_dependencies_per_task <= 0:
        return []

    if not previous_task_ids or rng.random() > probability:
        return []

    max_count = min(max_dependencies_per_task, len(previous_task_ids))
    count = rng.randint(1, max_count)

    return sorted(rng.sample(previous_task_ids, k=count))


def generate_custom_task_features(
    rng: random.Random,
    task_feature_definitions: list[dict[str, Any]],
    skills: list[str],
) -> dict[str, Any]:
    custom_features: dict[str, Any] = {}

    for feature in task_feature_definitions:
        name = str(feature.get("name", ""))
        feature_type = str(feature.get("type", ""))

        if name in CORE_TASK_FEATURE_NAMES:
            continue

        if feature_type == "numeric":
            minimum = float(feature.get("min", 0))
            maximum = float(feature.get("max", 1))
            custom_features[name] = random_float(rng, minimum, maximum)

        elif feature_type == "categorical":
            values = [str(item) for item in feature.get("values", [])]
            custom_features[name] = rng.choice(values) if values else None

        elif feature_type == "boolean":
            custom_features[name] = bool(rng.getrandbits(1))

        elif feature_type == "text":
            custom_features[name] = f"Generated value for {name}"

        elif feature_type == "skill_list":
            if skills:
                count = rng.randint(1, min(3, len(skills)))
                custom_features[name] = sorted(rng.sample(skills, k=count))
            else:
                custom_features[name] = []

    return custom_features


def make_task_title(
    task_type: str,
    project_id: str,
    index: int,
    domain_profile: str,
) -> str:
    readable_type = task_type.replace("_", " ").replace("-", " ")
    return f"{readable_type.title()} #{index:04d} for {project_id} [{domain_profile}]"


def make_task_description(
    task_type: str,
    required_skills: list[str],
    priority: str,
    complexity: float,
) -> str:
    skills_part = ", ".join(required_skills)
    return (
        f"Generated {task_type} task with {priority} priority, "
        f"complexity {complexity}, and required skills: {skills_part}."
    )


def generate_tasks(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise TaskGenerationError("Payload must be a JSON object")

    domain_profile = str(payload.get("domain_profile", "developers"))
    seed_value = payload.get("seed")
    seed = None if seed_value is None else int(seed_value)
    rng = random.Random(seed)

    schema = load_feature_schema(domain_profile)
    preview = schema_preview(schema)

    tasks_count = int_setting(
        payload,
        "tasks_count",
        default=100,
        minimum=1,
        maximum=250_000,
    )
    projects_count = int_setting(
        payload,
        "projects_count",
        default=5,
        minimum=1,
        maximum=500,
    )

    task_types = list_setting(payload, "task_types", schema.get("task_types", []))
    priorities = list_setting(payload, "priorities", DEFAULT_PRIORITIES)
    skills = list_setting(payload, "skills", schema.get("skills", []))

    required_skills_min = int_setting(
        payload,
        "required_skills_min",
        default=1,
        minimum=1,
        maximum=50,
    )
    required_skills_max = int_setting(
        payload,
        "required_skills_max",
        default=4,
        minimum=1,
        maximum=50,
    )

    if required_skills_min > required_skills_max:
        raise TaskGenerationError(
            "required_skills_min cannot be greater than required_skills_max"
        )

    complexity_min, complexity_max = normalize_range(
        payload,
        "complexity_min",
        "complexity_max",
        default_min=1,
        default_max=10,
        hard_min=1,
        hard_max=10,
    )
    estimated_hours_min, estimated_hours_max = normalize_range(
        payload,
        "estimated_hours_min",
        "estimated_hours_max",
        default_min=1,
        default_max=80,
        hard_min=0.5,
        hard_max=1000,
    )
    deadline_days_min, deadline_days_max = normalize_range(
        payload,
        "deadline_days_min",
        "deadline_days_max",
        default_min=1,
        default_max=45,
        hard_min=0,
        hard_max=3650,
    )

    dependencies_probability = float_setting(
        payload,
        "dependencies_probability",
        default=0.18,
        minimum=0,
        maximum=1,
    )
    max_dependencies_per_task = int_setting(
        payload,
        "max_dependencies_per_task",
        default=3,
        minimum=0,
        maximum=25,
    )
    skill_mismatch_probability = float_setting(
        payload,
        "skill_mismatch_probability",
        default=0.08,
        minimum=0,
        maximum=1,
    )

    status_distribution = distribution_setting(
        payload,
        "status_distribution",
        DEFAULT_STATUS_DISTRIBUTION,
        TASK_STATUSES,
    )
    priority_distribution = distribution_setting(
        payload,
        "priority_distribution",
        default_priority_distribution(priorities),
        priorities,
    )

    dataset_id = str(payload.get("dataset_id") or generate_dataset_id(domain_profile, seed))
    overwrite = bool(payload.get("overwrite", False))
    dataset_dir = prepare_dataset_dir(dataset_id, overwrite=overwrite)

    created_at = utc_now()
    task_feature_definitions = schema.get("feature_groups", {}).get("task", [])

    tasks: list[dict[str, Any]] = []
    task_ids: list[str] = []

    for index in range(1, tasks_count + 1):
        task_id = f"task_{index:06d}"
        project_id = f"project_{rng.randint(1, projects_count):03d}"
        task_type = rng.choice(task_types)
        priority = weighted_choice(rng, priority_distribution)
        status = weighted_choice(rng, status_distribution)

        complexity = random_float(rng, complexity_min, complexity_max)
        estimated_hours = random_float(
            rng,
            estimated_hours_min,
            estimated_hours_max,
        )
        deadline_days = int(
            round(random_float(rng, deadline_days_min, deadline_days_max, digits=0))
        )

        required_skills = choose_required_skills(
            rng,
            skills,
            required_skills_min,
            required_skills_max,
            skill_mismatch_probability,
        )
        dependencies = choose_dependencies(
            rng,
            task_ids,
            dependencies_probability,
            max_dependencies_per_task,
        )

        created_offset_days = rng.randint(0, 30)
        task_created_at = created_at - timedelta(days=created_offset_days)
        due_at = task_created_at + timedelta(days=deadline_days)

        title = make_task_title(task_type, project_id, index, domain_profile)
        description = make_task_description(
            task_type,
            required_skills,
            priority,
            complexity,
        )

        task = {
            "task_id": task_id,
            "title": title,
            "description": description,
            "project_id": project_id,
            "task_type": task_type,
            "status": status,
            "priority": priority,
            "complexity": complexity,
            "estimated_hours": estimated_hours,
            "deadline_days": deadline_days,
            "required_skills": required_skills,
            "dependencies": dependencies,
            "created_at": task_created_at.isoformat(),
            "due_at": due_at.isoformat(),
            "custom_features": generate_custom_task_features(
                rng,
                task_feature_definitions,
                skills,
            ),
        }

        missing_required = validate_record_required_fields("tasks", task)
        if missing_required:
            missing_text = ", ".join(missing_required)
            raise TaskGenerationError(
                f"Generated task {task_id} missing required fields: {missing_text}"
            )

        tasks.append(task)
        task_ids.append(task_id)

    backlog = build_backlog(tasks)
    kanban_summary = build_kanban_summary(tasks, backlog)

    metadata = {
        "dataset_id": dataset_id,
        "domain_profile": domain_profile,
        "seed": seed,
        "created_at": utc_now_iso(),
        "generator": "sandbox_app.backend.data_generation.tasks",
        "schema_preview": preview,
        "settings": {
            "tasks_count": tasks_count,
            "projects_count": projects_count,
            "task_types": task_types,
            "priorities": priorities,
            "required_skills_min": required_skills_min,
            "required_skills_max": required_skills_max,
            "complexity_min": complexity_min,
            "complexity_max": complexity_max,
            "estimated_hours_min": estimated_hours_min,
            "estimated_hours_max": estimated_hours_max,
            "deadline_days_min": deadline_days_min,
            "deadline_days_max": deadline_days_max,
            "dependencies_probability": dependencies_probability,
            "max_dependencies_per_task": max_dependencies_per_task,
            "skill_mismatch_probability": skill_mismatch_probability,
            "status_distribution": status_distribution,
            "priority_distribution": priority_distribution,
        },
        "counts": {
            "tasks": len(tasks),
            "backlog": len(backlog),
            "projects": projects_count,
        },
        "kanban_summary": kanban_summary,
        "files": {
            "tasks_json": str(dataset_dir / "tasks.json"),
            "tasks_csv": str(dataset_dir / "tasks.csv"),
            "backlog_json": str(dataset_dir / "backlog.json"),
            "backlog_csv": str(dataset_dir / "backlog.csv"),
            "task_metadata_json": str(dataset_dir / "task_metadata.json"),
        },
    }

    write_json(dataset_dir / "tasks.json", tasks)
    write_json(dataset_dir / "backlog.json", backlog)
    write_json(dataset_dir / "task_metadata.json", metadata)

    write_tasks_csv(dataset_dir / "tasks.csv", tasks)
    write_tasks_csv(dataset_dir / "backlog.csv", backlog)

    return {
        "dataset_id": dataset_id,
        "dataset_dir": str(dataset_dir),
        "tasks": tasks,
        "backlog": backlog,
        "metadata": metadata,
        "preview": {
            "tasks": tasks[:10],
            "backlog": backlog[:10],
        },
    }


def write_tasks_csv(path: Path, tasks: list[dict[str, Any]]) -> None:
    fieldnames = [
        "task_id",
        "title",
        "description",
        "project_id",
        "task_type",
        "status",
        "priority",
        "complexity",
        "estimated_hours",
        "deadline_days",
        "required_skills",
        "dependencies",
        "created_at",
        "due_at",
        "custom_features",
    ]

    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8", newline="") as file_obj:
        writer = csv.DictWriter(file_obj, fieldnames=fieldnames)
        writer.writeheader()

        for task in tasks:
            row = dict(task)
            row["required_skills"] = json.dumps(
                task.get("required_skills", []),
                ensure_ascii=False,
            )
            row["dependencies"] = json.dumps(
                task.get("dependencies", []),
                ensure_ascii=False,
            )
            row["custom_features"] = json.dumps(
                task.get("custom_features", {}),
                ensure_ascii=False,
            )
            writer.writerow({field: row.get(field, "") for field in fieldnames})