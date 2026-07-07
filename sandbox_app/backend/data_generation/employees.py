from __future__ import annotations

import csv
import json
import random
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sandbox_app.backend.core.paths import GENERATED_DATA_DIR
from sandbox_app.backend.features.schema import load_feature_schema

DEFAULT_FIRST_NAMES = [
    "Andrey",
    "Maria",
    "Ivan",
    "Anna",
    "Dmitry",
    "Elena",
    "Alexey",
    "Olga",
    "Sergey",
    "Natalia",
    "Mikhail",
    "Sofia",
    "Pavel",
    "Daria",
    "Nikita",
    "Polina",
]

DEFAULT_LAST_NAMES = [
    "Sokolov",
    "Ivanova",
    "Petrov",
    "Smirnova",
    "Volkov",
    "Fedorova",
    "Kuznetsov",
    "Morozova",
    "Orlov",
    "Novikova",
    "Lebedev",
    "Makarova",
]

DEFAULT_ROLES = [
    "Specialist",
    "Senior Specialist",
    "Lead",
]

DEFAULT_GRADES = [
    "junior",
    "middle",
    "senior",
    "lead",
]

DEFAULT_SKILLS = [
    "communication",
    "analysis",
    "planning",
    "quality_control",
    "problem_solving",
]

CSV_FIELDS = [
    "employee_id",
    "name",
    "role",
    "grade",
    "skills",
    "learning_goals",
    "current_workload",
    "active_tasks_count",
    "fatigue_level",
    "availability_score",
    "avg_completion_speed",
    "avg_quality_score",
    "deadline_reliability",
    "mentor_level",
    "custom_features",
]


@dataclass(frozen=True)
class TeamGenerationRequest:
    seed: int = 42
    employees_count: int = 20
    domain_profile: str = "developers"
    roles: tuple[str, ...] = ()
    grades: tuple[str, ...] = ()
    skills: tuple[str, ...] = ()
    skill_count_per_person_min: int = 2
    skill_count_per_person_max: int = 5
    junior_share: float = 0.25
    middle_share: float = 0.40
    senior_share: float = 0.25
    lead_share: float = 0.10
    fatigue_min: float = 0.05
    fatigue_max: float = 0.65
    workload_min: float = 0.10
    workload_max: float = 0.85


def generate_team(payload: dict[str, Any]) -> dict[str, Any]:
    request = parse_generation_request(payload)
    schema = load_feature_schema(request.domain_profile)

    rng = random.Random(request.seed)
    dataset_id = build_dataset_id(request.domain_profile)
    dataset_dir = GENERATED_DATA_DIR / dataset_id
    dataset_dir.mkdir(parents=True, exist_ok=True)

    roles = get_configured_values(request.roles, schema["roles"], DEFAULT_ROLES)
    grades = get_configured_values(request.grades, schema["grades"], DEFAULT_GRADES)
    skills = get_configured_values(request.skills, schema["skills"], DEFAULT_SKILLS)

    employees = [
        build_employee(index, request, schema, roles, grades, skills, rng)
        for index in range(1, request.employees_count + 1)
    ]

    metadata = build_metadata(dataset_id, request, schema, employees)
    write_json(dataset_dir / "employees.json", employees)
    write_csv(dataset_dir / "employees.csv", employees)
    write_json(dataset_dir / "team_metadata.json", metadata)

    return {
        "dataset_id": dataset_id,
        "dataset_dir": str(dataset_dir),
        "employees_count": len(employees),
        "employees_preview": employees[: min(20, len(employees))],
        "summary": build_summary(employees),
        "files": {
            "employees_json": str(dataset_dir / "employees.json"),
            "employees_csv": str(dataset_dir / "employees.csv"),
            "team_metadata": str(dataset_dir / "team_metadata.json"),
        },
        "metadata": metadata,
    }


def parse_generation_request(payload: dict[str, Any]) -> TeamGenerationRequest:
    employees_count = int(payload.get("employees_count", 20))

    if employees_count < 1:
        raise ValueError("employees_count must be greater than zero.")

    if employees_count > 100_000:
        raise ValueError("employees_count is too large for one request.")

    skill_min = int(payload.get("skill_count_per_person_min", 2))
    skill_max = int(payload.get("skill_count_per_person_max", 5))

    if skill_min < 0:
        raise ValueError("skill_count_per_person_min cannot be negative.")

    if skill_max < skill_min:
        raise ValueError("skill_count_per_person_max must be >= min.")

    fatigue_min = float(payload.get("fatigue_min", 0.05))
    fatigue_max = float(payload.get("fatigue_max", 0.65))
    workload_min = float(payload.get("workload_min", 0.10))
    workload_max = float(payload.get("workload_max", 0.85))

    validate_range(fatigue_min, fatigue_max, "fatigue")
    validate_range(workload_min, workload_max, "workload")

    return TeamGenerationRequest(
        seed=int(payload.get("seed", 42)),
        employees_count=employees_count,
        domain_profile=str(payload.get("domain_profile", "developers")),
        roles=tuple(payload.get("roles", []) or ()),
        grades=tuple(payload.get("grades", []) or ()),
        skills=tuple(payload.get("skills", []) or ()),
        skill_count_per_person_min=skill_min,
        skill_count_per_person_max=skill_max,
        junior_share=float(payload.get("junior_share", 0.25)),
        middle_share=float(payload.get("middle_share", 0.40)),
        senior_share=float(payload.get("senior_share", 0.25)),
        lead_share=float(payload.get("lead_share", 0.10)),
        fatigue_min=fatigue_min,
        fatigue_max=fatigue_max,
        workload_min=workload_min,
        workload_max=workload_max,
    )


def build_employee(
    index: int,
    request: TeamGenerationRequest,
    schema: dict[str, Any],
    roles: list[str],
    grades: list[str],
    skills: list[str],
    rng: random.Random,
) -> dict[str, Any]:
    grade = choose_grade(request, grades, rng)
    skill_count = choose_skill_count(request, skills, rng)
    employee_skills = sorted(rng.sample(skills, skill_count))
    learning_goals = choose_learning_goals(skills, employee_skills, rng)

    fatigue_level = round_float(
        rng.uniform(request.fatigue_min, request.fatigue_max)
    )
    current_workload = round_float(
        rng.uniform(request.workload_min, request.workload_max)
    )

    return {
        "employee_id": f"EMP-{index:05d}",
        "name": build_person_name(rng),
        "role": rng.choice(roles),
        "grade": grade,
        "skills": employee_skills,
        "learning_goals": learning_goals,
        "current_workload": current_workload,
        "active_tasks_count": build_active_tasks_count(current_workload, rng),
        "fatigue_level": fatigue_level,
        "availability_score": build_availability(current_workload, fatigue_level),
        "avg_completion_speed": build_grade_metric(grade, rng),
        "avg_quality_score": build_grade_metric(grade, rng),
        "deadline_reliability": build_grade_metric(grade, rng),
        "mentor_level": build_mentor_level(grade, rng),
        "custom_features": build_custom_features(schema, rng),
    }


def choose_grade(
    request: TeamGenerationRequest,
    grades: list[str],
    rng: random.Random,
) -> str:
    weights_by_grade = {
        "junior": request.junior_share,
        "middle": request.middle_share,
        "senior": request.senior_share,
        "lead": request.lead_share,
    }
    weights = [weights_by_grade.get(grade, 1.0) for grade in grades]

    return rng.choices(grades, weights=weights, k=1)[0]


def choose_skill_count(
    request: TeamGenerationRequest,
    skills: list[str],
    rng: random.Random,
) -> int:
    max_possible = min(request.skill_count_per_person_max, len(skills))
    min_possible = min(request.skill_count_per_person_min, max_possible)

    if max_possible <= 0:
        return 0

    return rng.randint(min_possible, max_possible)


def choose_learning_goals(
    skills: list[str],
    employee_skills: list[str],
    rng: random.Random,
) -> list[str]:
    missing_skills = sorted(set(skills) - set(employee_skills))

    if not missing_skills:
        return []

    goals_count = min(len(missing_skills), rng.randint(1, 3))
    return sorted(rng.sample(missing_skills, goals_count))


def build_person_name(rng: random.Random) -> str:
    first_name = rng.choice(DEFAULT_FIRST_NAMES)
    last_name = rng.choice(DEFAULT_LAST_NAMES)

    return f"{first_name} {last_name}"


def build_active_tasks_count(
    current_workload: float,
    rng: random.Random,
) -> int:
    base_count = round(current_workload * 10)
    noise = rng.randint(0, 2)

    return max(0, base_count + noise)


def build_availability(
    current_workload: float,
    fatigue_level: float,
) -> float:
    availability = 1.0 - current_workload * 0.65 - fatigue_level * 0.35

    return round_float(clamp(availability, 0.0, 1.0))


def build_grade_metric(grade: str, rng: random.Random) -> float:
    ranges_by_grade = {
        "junior": (0.45, 0.72),
        "middle": (0.58, 0.84),
        "senior": (0.70, 0.94),
        "lead": (0.74, 0.97),
    }
    min_value, max_value = ranges_by_grade.get(grade, (0.50, 0.90))

    return round_float(rng.uniform(min_value, max_value))


def build_mentor_level(grade: str, rng: random.Random) -> float:
    ranges_by_grade = {
        "junior": (0.00, 0.20),
        "middle": (0.15, 0.45),
        "senior": (0.45, 0.82),
        "lead": (0.70, 1.00),
    }
    min_value, max_value = ranges_by_grade.get(grade, (0.10, 0.60))

    return round_float(rng.uniform(min_value, max_value))


def build_custom_features(
    schema: dict[str, Any],
    rng: random.Random,
) -> dict[str, Any]:
    custom_features = {}

    for feature in schema.get("employee_features", []):
        feature_name = feature["name"]
        custom_features[feature_name] = build_feature_value(feature, rng)

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


def build_metadata(
    dataset_id: str,
    request: TeamGenerationRequest,
    schema: dict[str, Any],
    employees: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "dataset_id": dataset_id,
        "created_at": datetime.now(UTC).isoformat(),
        "generator": "sandbox_team_generator",
        "domain_profile": request.domain_profile,
        "schema_title": schema.get("title", ""),
        "seed": request.seed,
        "employees_count": len(employees),
        "summary": build_summary(employees),
        "request": {
            "employees_count": request.employees_count,
            "roles": list(request.roles),
            "grades": list(request.grades),
            "skills": list(request.skills),
            "skill_count_per_person_min": request.skill_count_per_person_min,
            "skill_count_per_person_max": request.skill_count_per_person_max,
            "junior_share": request.junior_share,
            "middle_share": request.middle_share,
            "senior_share": request.senior_share,
            "lead_share": request.lead_share,
            "fatigue_min": request.fatigue_min,
            "fatigue_max": request.fatigue_max,
            "workload_min": request.workload_min,
            "workload_max": request.workload_max,
        },
    }


def build_summary(employees: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "roles": count_values(employees, "role"),
        "grades": count_values(employees, "grade"),
        "avg_workload": average(employees, "current_workload"),
        "avg_fatigue": average(employees, "fatigue_level"),
        "avg_availability": average(employees, "availability_score"),
        "avg_quality": average(employees, "avg_quality_score"),
        "avg_speed": average(employees, "avg_completion_speed"),
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


def write_csv(path: Path, employees: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
        writer.writeheader()

        for employee in employees:
            writer.writerow(serialize_employee_for_csv(employee))


def serialize_employee_for_csv(employee: dict[str, Any]) -> dict[str, Any]:
    row = {}

    for field in CSV_FIELDS:
        value = employee.get(field)

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

    return [str(value).strip() for value in values if str(value).strip()]


def validate_range(
    min_value: float,
    max_value: float,
    label: str,
) -> None:
    if min_value < 0 or max_value > 1:
        raise ValueError(f"{label} range must be between 0 and 1.")

    if min_value > max_value:
        raise ValueError(f"{label} min cannot be greater than max.")


def build_dataset_id(domain_profile: str) -> str:
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    short_id = uuid.uuid4().hex[:8]

    return f"team_{domain_profile}_{timestamp}_{short_id}"


def round_float(value: float) -> float:
    return round(value, 4)


def clamp(
    value: float,
    min_value: float,
    max_value: float,
) -> float:
    return max(min_value, min(max_value, value))