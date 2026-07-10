from __future__ import annotations

import json
import math
import random
import re
from dataclasses import asdict, dataclass, field
from datetime import timedelta
from pathlib import Path
from typing import Any

from sandbox_app.backend.core.paths import PATHS
from sandbox_app.backend.core.time import moscow_now, moscow_now_iso, moscow_stamp

TEST_CASES_DIR = PATHS.data_dir / "test_cases"
TEST_CASE_ID_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]{2,80}$")

DEFAULT_ROLES = [
    "backend_developer",
    "frontend_developer",
    "fullstack_developer",
    "qa_engineer",
    "data_analyst",
    "team_lead",
]

DEFAULT_GRADES = ["junior", "middle", "senior", "lead"]

DEFAULT_SKILLS = [
    "python",
    "fastapi",
    "postgresql",
    "react",
    "typescript",
    "testing",
    "analytics",
    "ml",
    "devops",
    "architecture",
]

DEFAULT_TASK_TYPES = [
    "feature",
    "bugfix",
    "refactoring",
    "analytics",
    "testing",
    "documentation",
    "integration",
]

DEFAULT_PRIORITIES = ["low", "medium", "high", "critical"]
ACTIVE_STATUSES = ["in_progress", "review", "blocked"]
HISTORY_OUTCOMES = ["good", "excellent", "late", "failed", "rework"]


class TestTeamError(ValueError):
    """Raised when test team generation or loading fails."""


@dataclass(frozen=True)
class TestTeamConfig:
    test_case_id: str | None = None
    domain_profile: str = "developers"
    people_count: int = 10
    active_tasks_count: int = 16
    history_depth: int = 8
    seed: int | None = 21001
    roles: list[str] = field(default_factory=lambda: DEFAULT_ROLES.copy())
    grades: list[str] = field(default_factory=lambda: DEFAULT_GRADES.copy())
    skills: list[str] = field(default_factory=lambda: DEFAULT_SKILLS.copy())
    task_types: list[str] = field(default_factory=lambda: DEFAULT_TASK_TYPES.copy())
    priorities: list[str] = field(default_factory=lambda: DEFAULT_PRIORITIES.copy())
    workload_min: float = 0.1
    workload_max: float = 0.85
    fatigue_min: float = 0.05
    fatigue_max: float = 0.8
    availability_min: float = 0.15
    availability_max: float = 1.0
    learning_goals_min: int = 1
    learning_goals_max: int = 3
    active_tasks_per_person_max: int = 4
    overwrite: bool = False

TestTeamConfig.__test__ = False

def utc_now_iso() -> str:
    return moscow_now_iso()


def clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return round(max(minimum, min(maximum, value)), 4)


def validate_identifier(value: str, field_name: str) -> None:
    if not TEST_CASE_ID_RE.match(value):
        raise TestTeamError(
            f"{field_name} must match {TEST_CASE_ID_RE.pattern}: {value!r}"
        )


def validate_config(config: TestTeamConfig) -> None:
    if config.test_case_id is not None:
        validate_identifier(config.test_case_id, "test_case_id")

    if config.people_count < 1:
        raise TestTeamError("people_count must be positive")

    if config.active_tasks_count < 0:
        raise TestTeamError("active_tasks_count must be non-negative")

    if config.history_depth < 0:
        raise TestTeamError("history_depth must be non-negative")

    if not config.roles:
        raise TestTeamError("roles must not be empty")

    if not config.grades:
        raise TestTeamError("grades must not be empty")

    if not config.skills:
        raise TestTeamError("skills must not be empty")

    if config.workload_min > config.workload_max:
        raise TestTeamError("workload_min must be <= workload_max")

    if config.fatigue_min > config.fatigue_max:
        raise TestTeamError("fatigue_min must be <= fatigue_max")

    if config.availability_min > config.availability_max:
        raise TestTeamError("availability_min must be <= availability_max")

    if config.learning_goals_min < 0:
        raise TestTeamError("learning_goals_min must be non-negative")

    if config.learning_goals_min > config.learning_goals_max:
        raise TestTeamError("learning_goals_min must be <= learning_goals_max")


def slug_time_id(prefix: str) -> str:
    stamp = moscow_stamp()
    return f"{prefix}_{stamp}"


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise TestTeamError(f"Could not read JSON file: {path}") from exc


def schema_path(profile_id: str) -> Path:
    return PATHS.config_dir / "feature_schemas" / f"{profile_id}.json"


def load_domain_schema(profile_id: str) -> dict[str, Any]:
    path = schema_path(profile_id)

    if not path.exists():
        return {}

    payload = read_json(path)
    return payload if isinstance(payload, dict) else {}


def list_from_schema(schema: dict[str, Any], key: str, fallback: list[str]) -> list[str]:
    value = schema.get(key)

    if isinstance(value, list) and value:
        return [str(item) for item in value if str(item).strip()]

    domain = schema.get("domain")
    if isinstance(domain, dict):
        nested = domain.get(key)
        if isinstance(nested, list) and nested:
            return [str(item) for item in nested if str(item).strip()]

    return fallback.copy()


def merged_config(config: TestTeamConfig) -> TestTeamConfig:
    schema = load_domain_schema(config.domain_profile)

    roles = config.roles or list_from_schema(schema, "roles", DEFAULT_ROLES)
    grades = config.grades or list_from_schema(schema, "grades", DEFAULT_GRADES)
    skills = config.skills or list_from_schema(schema, "skills", DEFAULT_SKILLS)

    return TestTeamConfig(
        test_case_id=config.test_case_id,
        domain_profile=config.domain_profile,
        people_count=config.people_count,
        active_tasks_count=config.active_tasks_count,
        history_depth=config.history_depth,
        seed=config.seed,
        roles=roles,
        grades=grades,
        skills=skills,
        task_types=config.task_types or DEFAULT_TASK_TYPES.copy(),
        priorities=config.priorities or DEFAULT_PRIORITIES.copy(),
        workload_min=config.workload_min,
        workload_max=config.workload_max,
        fatigue_min=config.fatigue_min,
        fatigue_max=config.fatigue_max,
        availability_min=config.availability_min,
        availability_max=config.availability_max,
        learning_goals_min=config.learning_goals_min,
        learning_goals_max=config.learning_goals_max,
        active_tasks_per_person_max=config.active_tasks_per_person_max,
        overwrite=config.overwrite,
    )


def weighted_choice(rng: random.Random, items: list[str], weights: list[float]) -> str:
    return rng.choices(items, weights=weights, k=1)[0]


def grade_quality_bonus(grade: str) -> float:
    return {
        "junior": -0.08,
        "middle": 0.02,
        "senior": 0.1,
        "lead": 0.14,
    }.get(grade, 0.0)


def person_name(index: int) -> str:
    return f"employee_{index + 1:04d}"


def pick_skills(
    rng: random.Random,
    skills: list[str],
    minimum: int,
    maximum: int,
) -> list[str]:
    count = rng.randint(minimum, min(maximum, len(skills)))
    return sorted(rng.sample(skills, count))


def generate_team(config: TestTeamConfig, rng: random.Random) -> list[dict[str, Any]]:
    team: list[dict[str, Any]] = []

    for index in range(config.people_count):
        grade = weighted_choice(rng, config.grades, [0.22, 0.38, 0.3, 0.1][: len(config.grades)])
        role = rng.choice(config.roles)
        skills = pick_skills(rng, config.skills, 3, min(7, len(config.skills)))
        learning_goals = pick_skills(
            rng,
            [skill for skill in config.skills if skill not in skills] or config.skills,
            config.learning_goals_min,
            max(config.learning_goals_min, config.learning_goals_max),
        )
        workload = clamp(rng.uniform(config.workload_min, config.workload_max))
        fatigue = clamp(rng.uniform(config.fatigue_min, config.fatigue_max))
        availability = clamp(rng.uniform(config.availability_min, config.availability_max))
        quality_base = 0.72 + grade_quality_bonus(grade) - fatigue * 0.12

        team.append(
            {
                "employee_id": f"employee_{index + 1:04d}",
                "name": person_name(index),
                "role": role,
                "grade": grade,
                "skills": skills,
                "learning_goals": learning_goals,
                "current_workload": workload,
                "fatigue_score": fatigue,
                "availability_score": availability,
                "avg_completion_speed": clamp(rng.uniform(0.45, 0.95) - workload * 0.08),
                "avg_quality_score": clamp(quality_base + rng.uniform(-0.08, 0.08)),
                "deadline_reliability": clamp(
                    rng.uniform(0.55, 0.96) - fatigue * 0.18 - workload * 0.08
                ),
                "mentor_level": clamp(
                    {"junior": 0.1, "middle": 0.35, "senior": 0.75, "lead": 0.9}.get(
                        grade,
                        0.3,
                    )
                ),
                "active_task_ids": [],
                "custom_features": {
                    "communication_score": clamp(rng.uniform(0.45, 0.95)),
                    "focus_score": clamp(1.0 - fatigue + rng.uniform(-0.08, 0.08)),
                    "domain_confidence": clamp(rng.uniform(0.45, 0.95)),
                },
            }
        )

    return team


def task_complexity(rng: random.Random) -> float:
    return clamp(rng.betavariate(2.0, 2.4), 0.05, 0.98)


def required_skills_for_task(
    rng: random.Random,
    skills: list[str],
    task_type: str,
) -> list[str]:
    base_count = 2 if task_type in {"bugfix", "documentation", "testing"} else 3
    max_count = min(len(skills), base_count + rng.randint(0, 2))
    return sorted(rng.sample(skills, max_count))


def generate_active_tasks(
    config: TestTeamConfig,
    team: list[dict[str, Any]],
    rng: random.Random,
) -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []
    start_date = moscow_now().date()

    for index in range(config.active_tasks_count):
        task_type = rng.choice(config.task_types)
        assignee = rng.choice(team)
        complexity = task_complexity(rng)
        estimate = round(4.0 + complexity * 36.0 + rng.uniform(-2.0, 6.0), 2)
        deadline = start_date + timedelta(days=rng.randint(1, 21))

        task = {
            "task_id": f"active_task_{index + 1:04d}",
            "title": f"active_task_{index + 1:04d}",
            "project_id": f"project_{rng.randint(1, 4):02d}",
            "status": rng.choice(ACTIVE_STATUSES),
            "priority": weighted_choice(rng, config.priorities, [0.18, 0.46, 0.28, 0.08]),
            "task_type": task_type,
            "complexity": complexity,
            "estimated_hours": estimate,
            "deadline": deadline.isoformat(),
            "required_skills": required_skills_for_task(rng, config.skills, task_type),
            "assigned_employee_id": assignee["employee_id"],
            "progress": clamp(rng.uniform(0.05, 0.9)),
            "blocked_reason": None,
            "custom_features": {
                "business_value": clamp(rng.uniform(0.25, 1.0)),
                "uncertainty_score": clamp(rng.uniform(0.05, 0.75)),
                "collaboration_needed": rng.random() < 0.35,
            },
        }

        if task["status"] == "blocked":
            task["blocked_reason"] = rng.choice(
                [
                    "waiting_for_review",
                    "external_dependency",
                    "missing_requirements",
                    "environment_issue",
                ]
            )

        assignee["active_task_ids"].append(task["task_id"])
        tasks.append(task)

    for employee in team:
        employee["active_task_ids"] = employee["active_task_ids"][
            : config.active_tasks_per_person_max
        ]

    return tasks


def skill_match(employee: dict[str, Any], task: dict[str, Any]) -> float:
    employee_skills = set(employee.get("skills") or [])
    required_skills = set(task.get("required_skills") or [])

    if not required_skills:
        return 1.0

    return len(employee_skills & required_skills) / len(required_skills)


def outcome_score(employee: dict[str, Any], task: dict[str, Any], rng: random.Random) -> float:
    score = (
        skill_match(employee, task) * 0.34
        + float(employee["avg_quality_score"]) * 0.26
        + float(employee["deadline_reliability"]) * 0.18
        + float(employee["availability_score"]) * 0.12
        - float(employee["fatigue_score"]) * 0.11
        - float(task["complexity"]) * 0.08
        + rng.uniform(-0.08, 0.08)
    )

    return clamp(score)


def label_from_score(score: float, rng: random.Random) -> str:
    if score >= 0.82:
        return "excellent"

    if score >= 0.64:
        return "good"

    if score >= 0.44:
        return "late" if rng.random() < 0.55 else "rework"

    return "failed"


def generate_history(
    config: TestTeamConfig,
    team: list[dict[str, Any]],
    rng: random.Random,
) -> list[dict[str, Any]]:
    history: list[dict[str, Any]] = []
    today = moscow_now().date()

    for employee in team:
        for index in range(config.history_depth):
            task_type = rng.choice(config.task_types)
            synthetic_task = {
                "task_id": f"history_task_{employee['employee_id']}_{index + 1:03d}",
                "task_type": task_type,
                "complexity": task_complexity(rng),
                "required_skills": required_skills_for_task(rng, config.skills, task_type),
            }
            score = outcome_score(employee, synthetic_task, rng)
            label = label_from_score(score, rng)
            planned_hours = round(4.0 + synthetic_task["complexity"] * 28.0, 2)
            delay_factor = 1.0 + max(0.0, 0.72 - score) * rng.uniform(0.25, 1.1)
            actual_hours = round(planned_hours * delay_factor, 2)
            completed_at = today - timedelta(days=rng.randint(1, 180))

            history.append(
                {
                    "history_id": f"hist_{len(history) + 1:06d}",
                    "employee_id": employee["employee_id"],
                    "task_id": synthetic_task["task_id"],
                    "task_type": task_type,
                    "required_skills": synthetic_task["required_skills"],
                    "planned_hours": planned_hours,
                    "actual_hours": actual_hours,
                    "quality_score": clamp(score + rng.uniform(-0.05, 0.05)),
                    "deadline_status": "on_time" if label in {"good", "excellent"} else "late",
                    "outcome_label": label,
                    "was_rework_needed": label == "rework",
                    "feedback_score": clamp(score + rng.uniform(-0.08, 0.08)),
                    "completed_at": completed_at.isoformat(),
                }
            )

    return history


def workload_summary(team: list[dict[str, Any]]) -> dict[str, Any]:
    workloads = [float(person["current_workload"]) for person in team]
    fatigue = [float(person["fatigue_score"]) for person in team]
    availability = [float(person["availability_score"]) for person in team]

    return {
        "avg_workload": round(sum(workloads) / len(workloads), 4) if workloads else 0.0,
        "avg_fatigue": round(sum(fatigue) / len(fatigue), 4) if fatigue else 0.0,
        "avg_availability": round(sum(availability) / len(availability), 4)
        if availability
        else 0.0,
        "overloaded_people": sum(value >= 0.78 for value in workloads),
        "high_fatigue_people": sum(value >= 0.7 for value in fatigue),
    }


def active_task_summary(tasks: list[dict[str, Any]]) -> dict[str, Any]:
    by_status: dict[str, int] = {}
    by_priority: dict[str, int] = {}

    for task in tasks:
        by_status[str(task["status"])] = by_status.get(str(task["status"]), 0) + 1
        by_priority[str(task["priority"])] = by_priority.get(str(task["priority"]), 0) + 1

    return {
        "by_status": by_status,
        "by_priority": by_priority,
        "total": len(tasks),
    }


def history_summary(history: list[dict[str, Any]]) -> dict[str, Any]:
    outcomes: dict[str, int] = {}

    for item in history:
        label = str(item["outcome_label"])
        outcomes[label] = outcomes.get(label, 0) + 1

    return {
        "outcomes": outcomes,
        "total": len(history),
    }


def test_case_dir(test_case_id: str) -> Path:
    validate_identifier(test_case_id, "test_case_id")
    return TEST_CASES_DIR / test_case_id


def validate_records(name: str, records: list[dict[str, Any]], required: set[str]) -> None:
    if not isinstance(records, list):
        raise TestTeamError(f"{name} must be a list")

    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise TestTeamError(f"{name}[{index}] must be an object")

        missing = required - set(record)
        if missing:
            raise TestTeamError(f"{name}[{index}] missing required fields: {sorted(missing)}")


def validate_test_case_payload(
    team: list[dict[str, Any]],
    active_tasks: list[dict[str, Any]],
    history: list[dict[str, Any]],
) -> None:
    validate_records(
        "team",
        team,
        {"employee_id", "name", "role", "grade", "skills"},
    )
    validate_records(
        "active_tasks",
        active_tasks,
        {"task_id", "title", "status", "priority", "required_skills"},
    )
    validate_records(
        "history",
        history,
        {"history_id", "employee_id", "task_id", "outcome_label"},
    )


def save_test_case(
    test_case_id: str,
    team: list[dict[str, Any]],
    active_tasks: list[dict[str, Any]],
    history: list[dict[str, Any]],
    metadata: dict[str, Any],
    overwrite: bool,
) -> dict[str, Any]:
    validate_identifier(test_case_id, "test_case_id")
    validate_test_case_payload(team, active_tasks, history)

    directory = test_case_dir(test_case_id)

    if directory.exists() and not overwrite:
        raise TestTeamError(f"Test case already exists: {test_case_id}")

    directory.mkdir(parents=True, exist_ok=True)

    write_json(directory / "team.json", team)
    write_json(directory / "active_tasks.json", active_tasks)
    write_json(directory / "history.json", history)
    write_json(directory / "metadata.json", metadata)

    return {
        "test_case_id": test_case_id,
        "test_case_dir": str(directory),
        "paths": {
            "team": str(directory / "team.json"),
            "active_tasks": str(directory / "active_tasks.json"),
            "history": str(directory / "history.json"),
            "metadata": str(directory / "metadata.json"),
        },
        "metadata": metadata,
        "preview": {
            "team": team[:5],
            "active_tasks": active_tasks[:5],
            "history": history[:5],
        },
    }


def generate_test_case(config: TestTeamConfig) -> dict[str, Any]:
    config = merged_config(config)
    validate_config(config)

    test_case_id = config.test_case_id or slug_time_id("test_case")
    rng = random.Random(config.seed)

    team = generate_team(config, rng)
    active_tasks = generate_active_tasks(config, team, rng)
    history = generate_history(config, team, rng)

    metadata = {
        "test_case_id": test_case_id,
        "created_at": utc_now_iso(),
        "generator": "sandbox_test_team_generator",
        "config": asdict(config),
        "counts": {
            "people": len(team),
            "active_tasks": len(active_tasks),
            "history": len(history),
        },
        "summaries": {
            "workload": workload_summary(team),
            "active_tasks": active_task_summary(active_tasks),
            "history": history_summary(history),
        },
        "recommendation_ready": True,
        "bulk_assignment_ready": True,
    }

    return save_test_case(
        test_case_id=test_case_id,
        team=team,
        active_tasks=active_tasks,
        history=history,
        metadata=metadata,
        overwrite=config.overwrite,
    )


def import_test_case(
    test_case_id: str,
    team: list[dict[str, Any]],
    active_tasks: list[dict[str, Any]],
    history: list[dict[str, Any]],
    metadata: dict[str, Any] | None,
    overwrite: bool,
) -> dict[str, Any]:
    validate_identifier(test_case_id, "test_case_id")
    validate_test_case_payload(team, active_tasks, history)

    payload_metadata = dict(metadata or {})
    payload_metadata.update(
        {
            "test_case_id": test_case_id,
            "imported_at": utc_now_iso(),
            "generator": payload_metadata.get("generator", "manual_import"),
            "counts": {
                "people": len(team),
                "active_tasks": len(active_tasks),
                "history": len(history),
            },
            "summaries": {
                "workload": workload_summary(team),
                "active_tasks": active_task_summary(active_tasks),
                "history": history_summary(history),
            },
            "recommendation_ready": True,
            "bulk_assignment_ready": True,
        }
    )

    return save_test_case(
        test_case_id=test_case_id,
        team=team,
        active_tasks=active_tasks,
        history=history,
        metadata=payload_metadata,
        overwrite=overwrite,
    )


def load_test_case(test_case_id: str) -> dict[str, Any]:
    directory = test_case_dir(test_case_id)

    if not directory.exists():
        raise TestTeamError(f"Test case not found: {test_case_id}")

    team = read_json(directory / "team.json")
    active_tasks = read_json(directory / "active_tasks.json")
    history = read_json(directory / "history.json")
    metadata = read_json(directory / "metadata.json")

    validate_test_case_payload(team, active_tasks, history)

    return {
        "test_case_id": test_case_id,
        "test_case_dir": str(directory),
        "team": team,
        "active_tasks": active_tasks,
        "history": history,
        "metadata": metadata,
    }


def load_test_case_table(test_case_id: str, table_name: str) -> Any:
    allowed_tables = {
        "team": "team.json",
        "active_tasks": "active_tasks.json",
        "history": "history.json",
        "metadata": "metadata.json",
    }

    if table_name not in allowed_tables:
        raise TestTeamError(f"Unknown test case table: {table_name}")

    directory = test_case_dir(test_case_id)
    path = directory / allowed_tables[table_name]

    if not path.exists():
        raise TestTeamError(f"Test case table not found: {test_case_id}/{table_name}")

    return read_json(path)


def list_test_cases() -> dict[str, Any]:
    TEST_CASES_DIR.mkdir(parents=True, exist_ok=True)

    items: list[dict[str, Any]] = []

    for directory in sorted(TEST_CASES_DIR.iterdir(), reverse=True):
        if not directory.is_dir():
            continue

        metadata_path = directory / "metadata.json"
        if not metadata_path.exists():
            continue

        metadata = read_json(metadata_path)
        counts = metadata.get("counts", {}) if isinstance(metadata, dict) else {}

        items.append(
            {
                "test_case_id": directory.name,
                "test_case_dir": str(directory),
                "created_at": metadata.get("created_at") or metadata.get("imported_at"),
                "domain_profile": metadata.get("config", {}).get("domain_profile"),
                "people": counts.get("people", 0),
                "active_tasks": counts.get("active_tasks", 0),
                "history": counts.get("history", 0),
                "recommendation_ready": metadata.get("recommendation_ready", False),
                "bulk_assignment_ready": metadata.get("bulk_assignment_ready", False),
            }
        )

    return {
        "test_cases": items,
        "total": len(items),
        "test_cases_dir": str(TEST_CASES_DIR),
    }


def delete_test_case(test_case_id: str) -> dict[str, Any]:
    directory = test_case_dir(test_case_id)

    if not directory.exists():
        raise TestTeamError(f"Test case not found: {test_case_id}")

    for path in sorted(directory.rglob("*"), reverse=True):
        if path.is_file():
            path.unlink()
        elif path.is_dir() and path != directory:
            path.rmdir()

    directory.rmdir()

    return {
        "deleted": True,
        "test_case_id": test_case_id,
    }


def assignment_capacity(team: list[dict[str, Any]]) -> list[dict[str, Any]]:
    capacity: list[dict[str, Any]] = []

    for person in team:
        workload = float(person.get("current_workload") or 0.0)
        fatigue = float(person.get("fatigue_score") or 0.0)
        availability = float(person.get("availability_score") or 0.0)
        raw_capacity = availability * (1.0 - workload) * (1.0 - fatigue * 0.65)

        capacity.append(
            {
                "employee_id": person["employee_id"],
                "name": person.get("name", ""),
                "role": person.get("role", ""),
                "grade": person.get("grade", ""),
                "current_workload": workload,
                "fatigue_score": fatigue,
                "availability_score": availability,
                "assignment_capacity": clamp(raw_capacity),
                "active_tasks": len(person.get("active_task_ids") or []),
            }
        )

    return sorted(
        capacity,
        key=lambda item: (
            -float(item["assignment_capacity"]),
            float(item["current_workload"]),
            float(item["fatigue_score"]),
        ),
    )


def build_test_case_summary(test_case_id: str) -> dict[str, Any]:
    payload = load_test_case(test_case_id)
    metadata = payload["metadata"]
    team = payload["team"]
    active_tasks = payload["active_tasks"]
    history = payload["history"]

    return {
        "test_case_id": test_case_id,
        "people_count": len(team),
        "active_tasks_count": len(active_tasks),
        "history_count": len(history),
        "team_size": len(team),
        "history_rows": len(history),
        "metadata": metadata,
        "capacity": assignment_capacity(team),
        "team_preview": team[:10],
        "active_tasks_preview": active_tasks[:10],
        "history_preview": history[:10],
    }


def active_todo_tasks(test_case_id: str) -> list[dict[str, Any]]:
    active_tasks = load_test_case_table(test_case_id, "active_tasks")
    if not isinstance(active_tasks, list):
        raise TestTeamError("active_tasks must be a list")

    return [
        task
        for task in active_tasks
        if task.get("status") in {"todo", "in_progress", "blocked", "review"}
    ]


def estimate_assignment_load(active_tasks: list[dict[str, Any]]) -> float:
    if not active_tasks:
        return 0.0

    total_hours = sum(float(task.get("estimated_hours") or 0.0) for task in active_tasks)
    return round(total_hours, 2)


def recommendation_context(test_case_id: str) -> dict[str, Any]:
    payload = load_test_case(test_case_id)
    active_tasks = payload["active_tasks"]
    pending_tasks = active_todo_tasks(test_case_id)

    return {
        "test_case_id": test_case_id,
        "team": payload["team"],
        "active_tasks": active_tasks,
        "history": payload["history"],
        "metadata": payload["metadata"],
        "capacity": assignment_capacity(payload["team"]),
        "pending_tasks": pending_tasks,
        "estimated_pending_hours": estimate_assignment_load(pending_tasks),
        "team_size": len(payload["team"]),
        "active_tasks_count": len(active_tasks),
        "history_rows": len(payload["history"]),
        "complexity_hint": math.log1p(len(active_tasks) * max(1, len(payload["team"]))),
    }
