from __future__ import annotations

import csv
import json
import math
import random
import secrets
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sandbox_app.backend.core.data_contracts import validate_record_required_fields
from sandbox_app.backend.core.paths import PATHS
from sandbox_app.backend.features.schema import load_feature_schema, schema_preview
from sandbox_app.backend.utils.json_io import write_json


class TeamGenerationError(RuntimeError):
    """Raised when team generation input is invalid or generation fails."""


CORE_EMPLOYEE_FIELDS = {
    "employee_id",
    "name",
    "role",
    "grade",
    "skills",
    "availability_score",
    "current_workload",
    "fatigue_score",
    "avg_completion_speed",
    "avg_quality_score",
    "deadline_reliability",
    "mentor_level",
    "learning_goals",
    "timezone",
    "team_id",
}

FIRST_NAMES = [
    "Alex",
    "Maria",
    "Dmitry",
    "Anna",
    "Ivan",
    "Elena",
    "Nikita",
    "Sofia",
    "Mikhail",
    "Daria",
    "Artem",
    "Polina",
    "Sergey",
    "Kira",
    "Andrey",
    "Alina",
    "Roman",
    "Vera",
    "Pavel",
    "Nina",
]

LAST_NAMES = [
    "Volkov",
    "Morozova",
    "Smirnov",
    "Kuznetsova",
    "Sokolov",
    "Popova",
    "Petrov",
    "Novikova",
    "Fedorov",
    "Orlova",
    "Lebedev",
    "Romanova",
    "Egorov",
    "Mikhailova",
    "Nikolaev",
    "Semenova",
]

DEFAULT_GRADE_WEIGHTS = {
    "junior": 0.22,
    "middle": 0.44,
    "senior": 0.26,
    "lead": 0.08,
}

GRADE_SIGNAL = {
    "junior": 0.34,
    "middle": 0.56,
    "senior": 0.78,
    "lead": 0.9,
}


def generate_team_dataset(payload: dict[str, Any] | None) -> dict[str, Any]:
    payload = payload or {}
    config = parse_generation_config(payload)
    rng = random.Random(config["seed"])

    schema = load_feature_schema(config["domain_profile"])
    roles = config["roles"] or schema["roles"]
    grades = config["grades"] or schema["grades"]
    skills = config["skills"] or schema["skills"]

    employees = [
        generate_employee(
            index=index,
            rng=rng,
            schema=schema,
            roles=roles,
            grades=grades,
            skills=skills,
            config=config,
        )
        for index in range(1, config["employees_count"] + 1)
    ]

    validate_generated_employees(employees)

    dataset_dir = PATHS.generated_data_dir / config["dataset_id"]
    employees_json_path = dataset_dir / "employees.json"
    employees_csv_path = dataset_dir / "employees.csv"
    metadata_path = dataset_dir / "team_metadata.json"

    metadata = build_team_metadata(
        config=config,
        schema=schema,
        employees=employees,
        dataset_dir=dataset_dir,
        employees_json_path=employees_json_path,
        employees_csv_path=employees_csv_path,
        metadata_path=metadata_path,
    )

    if config["save_dataset"]:
        if dataset_dir.exists() and not config["overwrite"]:
            dataset_id = config["dataset_id"]
            raise TeamGenerationError(
                f"Dataset '{dataset_id}' already exists. "
                "Pass overwrite=true to replace it."
            )

        dataset_dir.mkdir(parents=True, exist_ok=True)
        write_json(employees_json_path, employees)
        write_employees_csv(employees_csv_path, employees)
        write_json(metadata_path, metadata)

    return {
        "dataset_id": config["dataset_id"],
        "dataset_dir": str(dataset_dir),
        "domain_profile": config["domain_profile"],
        "seed": config["seed"],
        "counts": {
            "employees": len(employees),
        },
        "files": {
            "employees_json": str(employees_json_path),
            "employees_csv": str(employees_csv_path),
            "team_metadata": str(metadata_path),
        },
        "metadata": metadata,
        "preview": employees[: min(10, len(employees))],
    }


def parse_generation_config(payload: dict[str, Any]) -> dict[str, Any]:
    domain_profile = str(payload.get("domain_profile", "developers"))
    employees_count = parse_int(
        value=payload.get("employees_count", 20),
        field_name="employees_count",
        minimum=1,
        maximum=5000,
    )
    seed = parse_optional_int(payload.get("seed"), "seed")
    if seed is None:
        seed = secrets.randbelow(2_147_483_647)

    dataset_id = str(payload.get("dataset_id") or build_dataset_id("team"))
    validate_dataset_id(dataset_id)

    skill_count_min = parse_int(
        value=payload.get("skill_count_per_person_min", 3),
        field_name="skill_count_per_person_min",
        minimum=1,
        maximum=100,
    )
    skill_count_max = parse_int(
        value=payload.get("skill_count_per_person_max", 7),
        field_name="skill_count_per_person_max",
        minimum=1,
        maximum=100,
    )

    if skill_count_min > skill_count_max:
        raise TeamGenerationError(
            "skill_count_per_person_min cannot be greater than "
            "skill_count_per_person_max"
        )

    learning_goals_min = parse_int(
        value=payload.get("learning_goals_count_min", 1),
        field_name="learning_goals_count_min",
        minimum=0,
        maximum=20,
    )
    learning_goals_max = parse_int(
        value=payload.get("learning_goals_count_max", 3),
        field_name="learning_goals_count_max",
        minimum=0,
        maximum=20,
    )

    if learning_goals_min > learning_goals_max:
        raise TeamGenerationError(
            "learning_goals_count_min cannot be greater than "
            "learning_goals_count_max"
        )

    workload_range = parse_number_range(
        value=payload.get("workload_range", [0.05, 0.95]),
        field_name="workload_range",
        minimum=0,
        maximum=1,
    )
    fatigue_range = parse_number_range(
        value=payload.get("fatigue_range", [0.02, 0.88]),
        field_name="fatigue_range",
        minimum=0,
        maximum=1,
    )
    availability_range = parse_number_range(
        value=payload.get("availability_range", [0.1, 1.0]),
        field_name="availability_range",
        minimum=0,
        maximum=1,
    )

    return {
        "dataset_id": dataset_id,
        "domain_profile": domain_profile,
        "employees_count": employees_count,
        "roles": parse_optional_string_list(payload.get("roles"), "roles"),
        "grades": parse_optional_string_list(payload.get("grades"), "grades"),
        "skills": parse_optional_string_list(payload.get("skills"), "skills"),
        "skill_count_per_person_min": skill_count_min,
        "skill_count_per_person_max": skill_count_max,
        "learning_goals_count_min": learning_goals_min,
        "learning_goals_count_max": learning_goals_max,
        "seniority_distribution": payload.get("seniority_distribution"),
        "workload_range": workload_range,
        "fatigue_range": fatigue_range,
        "availability_range": availability_range,
        "seed": seed,
        "save_dataset": bool(payload.get("save_dataset", True)),
        "overwrite": bool(payload.get("overwrite", False)),
        "team_id": str(payload.get("team_id", "sandbox_team")),
        "timezone": str(payload.get("timezone", "UTC")),
    }


def generate_employee(
    index: int,
    rng: random.Random,
    schema: dict[str, Any],
    roles: list[str],
    grades: list[str],
    skills: list[str],
    config: dict[str, Any],
) -> dict[str, Any]:
    grade = choose_grade(rng, grades, config.get("seniority_distribution"))
    role = rng.choice(roles)

    skill_count = rng.randint(
        config["skill_count_per_person_min"],
        min(config["skill_count_per_person_max"], len(skills)),
    )
    employee_skills = sorted(rng.sample(skills, k=skill_count))

    workload = round_float(rng.uniform(*config["workload_range"]))
    fatigue = generate_fatigue(rng, workload, config["fatigue_range"])
    availability = generate_availability(
        rng=rng,
        workload=workload,
        fatigue=fatigue,
        availability_range=config["availability_range"],
    )

    grade_signal = GRADE_SIGNAL.get(grade, 0.55)
    skill_signal = min(1.0, len(employee_skills) / max(1, len(skills)))

    completion_speed = generate_completion_speed(
        rng=rng,
        grade_signal=grade_signal,
        skill_signal=skill_signal,
        availability=availability,
        fatigue=fatigue,
    )
    quality = generate_quality(
        rng=rng,
        grade_signal=grade_signal,
        skill_signal=skill_signal,
        fatigue=fatigue,
    )
    reliability = generate_reliability(
        rng=rng,
        quality=quality,
        availability=availability,
        workload=workload,
    )
    mentor_level = clamp(grade_signal * 0.85 + rng.uniform(-0.12, 0.08))

    learning_goals = choose_learning_goals(
        rng=rng,
        all_skills=skills,
        current_skills=employee_skills,
        min_count=config["learning_goals_count_min"],
        max_count=config["learning_goals_count_max"],
    )

    return {
        "employee_id": f"emp_{index:06d}",
        "name": build_person_name(index),
        "role": role,
        "grade": grade,
        "skills": employee_skills,
        "availability_score": round_float(availability),
        "current_workload": round_float(workload),
        "fatigue_score": round_float(fatigue),
        "avg_completion_speed": round_float(completion_speed),
        "avg_quality_score": round_float(quality),
        "deadline_reliability": round_float(reliability),
        "mentor_level": round_float(mentor_level),
        "learning_goals": learning_goals,
        "timezone": config["timezone"],
        "team_id": config["team_id"],
        "custom_features": generate_custom_employee_features(
            rng=rng,
            schema=schema,
            role=role,
            grade=grade,
            skills=skills,
            employee_skills=employee_skills,
        ),
    }


def generate_fatigue(
    rng: random.Random,
    workload: float,
    fatigue_range: tuple[float, float],
) -> float:
    fatigue_noise = rng.uniform(-0.08, 0.12)
    fatigue_base = rng.uniform(*fatigue_range)
    return clamp(fatigue_base * 0.55 + workload * 0.45 + fatigue_noise)


def generate_availability(
    rng: random.Random,
    workload: float,
    fatigue: float,
    availability_range: tuple[float, float],
) -> float:
    availability_base = rng.uniform(*availability_range)
    availability_noise = rng.uniform(-0.05, 0.12)
    return clamp(
        availability_base
        - workload * 0.3
        - fatigue * 0.2
        + availability_noise
    )


def generate_completion_speed(
    rng: random.Random,
    grade_signal: float,
    skill_signal: float,
    availability: float,
    fatigue: float,
) -> float:
    return clamp(
        grade_signal * 0.55
        + skill_signal * 0.18
        + availability * 0.17
        - fatigue * 0.12
        + rng.uniform(-0.08, 0.08)
    )


def generate_quality(
    rng: random.Random,
    grade_signal: float,
    skill_signal: float,
    fatigue: float,
) -> float:
    return clamp(
        grade_signal * 0.58
        + skill_signal * 0.2
        - fatigue * 0.08
        + rng.uniform(-0.06, 0.1)
    )


def generate_reliability(
    rng: random.Random,
    quality: float,
    availability: float,
    workload: float,
) -> float:
    return clamp(
        quality * 0.45
        + availability * 0.32
        + (1 - workload) * 0.15
        + rng.uniform(-0.06, 0.08)
    )


def generate_custom_employee_features(
    rng: random.Random,
    schema: dict[str, Any],
    role: str,
    grade: str,
    skills: list[str],
    employee_skills: list[str],
) -> dict[str, Any]:
    custom_features: dict[str, Any] = {}

    for feature in schema["feature_groups"]["employee"]:
        name = feature["name"]

        if name in CORE_EMPLOYEE_FIELDS:
            continue

        custom_features[name] = generate_feature_value(
            rng=rng,
            feature=feature,
            role=role,
            grade=grade,
            skills=skills,
            employee_skills=employee_skills,
        )

    return custom_features


def generate_feature_value(
    rng: random.Random,
    feature: dict[str, Any],
    role: str,
    grade: str,
    skills: list[str],
    employee_skills: list[str],
) -> Any:
    feature_type = feature["type"]

    if feature_type == "numeric":
        minimum = float(feature.get("min", 0))
        maximum = float(feature.get("max", 1))
        return round_float(rng.uniform(minimum, maximum))

    if feature_type == "categorical":
        values = feature.get("values", [])
        return rng.choice(values)

    if feature_type == "boolean":
        return rng.random() >= 0.5

    if feature_type == "text":
        return f"Generated {feature['name']} for {grade} {role}"

    if feature_type == "skill_list":
        source = [skill for skill in skills if skill not in employee_skills] or skills
        max_count = min(4, max(1, len(source)))
        count = min(len(source), rng.randint(1, max_count))
        return sorted(rng.sample(source, k=count))

    raise TeamGenerationError(f"Unsupported feature type: {feature_type}")


def choose_grade(
    rng: random.Random,
    grades: list[str],
    seniority_distribution: Any,
) -> str:
    if seniority_distribution is None:
        weights = [
            DEFAULT_GRADE_WEIGHTS.get(grade, 1 / len(grades))
            for grade in grades
        ]
        return weighted_choice(rng, grades, weights)

    if not isinstance(seniority_distribution, dict):
        raise TeamGenerationError(
            "seniority_distribution must be an object with grade weights"
        )

    unknown = sorted(set(seniority_distribution) - set(grades))
    if unknown:
        raise TeamGenerationError(
            "seniority_distribution contains grades not allowed by selected "
            f"profile: {', '.join(unknown)}"
        )

    weights = [float(seniority_distribution.get(grade, 0)) for grade in grades]
    if sum(weights) <= 0:
        raise TeamGenerationError(
            "seniority_distribution weights must sum to a positive number"
        )

    return weighted_choice(rng, grades, weights)


def choose_learning_goals(
    rng: random.Random,
    all_skills: list[str],
    current_skills: list[str],
    min_count: int,
    max_count: int,
) -> list[str]:
    if max_count == 0:
        return []

    missing_skills = [skill for skill in all_skills if skill not in current_skills]
    source = missing_skills or all_skills

    if not source:
        return []

    count = rng.randint(min_count, min(max_count, len(source)))
    if count <= 0:
        return []

    return sorted(rng.sample(source, k=count))


def weighted_choice(
    rng: random.Random,
    items: list[str],
    weights: list[float],
) -> str:
    total = sum(weights)
    if total <= 0:
        raise TeamGenerationError("weights must sum to a positive number")

    threshold = rng.random() * total
    cumulative = 0.0

    for item, weight in zip(items, weights, strict=True):
        cumulative += weight
        if cumulative >= threshold:
            return item

    return items[-1]


def write_employees_csv(path: Path, employees: list[dict[str, Any]]) -> None:
    custom_feature_names = sorted(
        {
            feature_name
            for employee in employees
            for feature_name in employee.get("custom_features", {})
        }
    )

    fieldnames = [
        "employee_id",
        "name",
        "role",
        "grade",
        "skills",
        "availability_score",
        "current_workload",
        "fatigue_score",
        "avg_completion_speed",
        "avg_quality_score",
        "deadline_reliability",
        "mentor_level",
        "learning_goals",
        "timezone",
        "team_id",
    ]
    fieldnames.extend(f"custom_{name}" for name in custom_feature_names)

    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for employee in employees:
            row = build_employee_csv_row(employee, fieldnames)
            writer.writerow(row)


def build_employee_csv_row(
    employee: dict[str, Any],
    fieldnames: list[str],
) -> dict[str, str | int | float | bool | None]:
    row: dict[str, str | int | float | bool | None] = {}

    for field in fieldnames:
        if field.startswith("custom_"):
            custom_name = field.removeprefix("custom_")
            custom_value = employee.get("custom_features", {}).get(custom_name)
            row[field] = serialize_csv_value(custom_value)
            continue

        row[field] = serialize_csv_value(employee.get(field))

    return row


def build_team_metadata(
    config: dict[str, Any],
    schema: dict[str, Any],
    employees: list[dict[str, Any]],
    dataset_dir: Path,
    employees_json_path: Path,
    employees_csv_path: Path,
    metadata_path: Path,
) -> dict[str, Any]:
    role_counts = count_values(employee["role"] for employee in employees)
    grade_counts = count_values(employee["grade"] for employee in employees)

    return {
        "dataset_id": config["dataset_id"],
        "dataset_type": "generated",
        "generator": "team",
        "domain_profile": config["domain_profile"],
        "created_at": datetime.now(UTC).isoformat(),
        "seed": config["seed"],
        "counts": {
            "employees": len(employees),
            "roles": role_counts,
            "grades": grade_counts,
        },
        "quality_summary": build_quality_summary(employees),
        "schema_preview": schema_preview(schema),
        "generation_config": {
            key: value
            for key, value in config.items()
            if key not in {"overwrite"}
        },
        "files": {
            "dataset_dir": str(dataset_dir),
            "employees_json": str(employees_json_path),
            "employees_csv": str(employees_csv_path),
            "team_metadata": str(metadata_path),
        },
    }


def build_quality_summary(employees: list[dict[str, Any]]) -> dict[str, float]:
    return {
        "avg_availability_score": average(
            employee["availability_score"] for employee in employees
        ),
        "avg_current_workload": average(
            employee["current_workload"] for employee in employees
        ),
        "avg_fatigue_score": average(
            employee["fatigue_score"] for employee in employees
        ),
        "avg_quality_score": average(
            employee["avg_quality_score"] for employee in employees
        ),
        "avg_deadline_reliability": average(
            employee["deadline_reliability"] for employee in employees
        ),
    }


def validate_generated_employees(employees: list[dict[str, Any]]) -> None:
    for employee in employees:
        missing_fields = validate_record_required_fields("employees", employee)
        if missing_fields:
            employee_id = employee.get("employee_id", "<unknown>")
            missing = ", ".join(missing_fields)
            raise TeamGenerationError(
                f"Generated employee {employee_id} is missing required "
                f"fields: {missing}"
            )


def build_person_name(index: int) -> str:
    first = FIRST_NAMES[(index - 1) % len(FIRST_NAMES)]
    last = LAST_NAMES[((index - 1) // len(FIRST_NAMES)) % len(LAST_NAMES)]
    return f"{first} {last}"


def build_dataset_id(prefix: str) -> str:
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    suffix = secrets.token_hex(3)
    return f"{prefix}_{timestamp}_{suffix}"


def validate_dataset_id(dataset_id: str) -> None:
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-")
    has_invalid_chars = any(char not in allowed for char in dataset_id)

    if not dataset_id or has_invalid_chars:
        raise TeamGenerationError(
            "dataset_id must contain only letters, digits, underscores, "
            "and hyphens"
        )


def parse_int(value: Any, field_name: str, minimum: int, maximum: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise TeamGenerationError(f"{field_name} must be an integer") from exc

    if parsed < minimum or parsed > maximum:
        raise TeamGenerationError(
            f"{field_name} must be between {minimum} and {maximum}"
        )

    return parsed


def parse_optional_int(value: Any, field_name: str) -> int | None:
    if value is None:
        return None

    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise TeamGenerationError(f"{field_name} must be an integer") from exc


def parse_optional_string_list(value: Any, field_name: str) -> list[str] | None:
    if value is None:
        return None

    if not isinstance(value, list) or not value:
        raise TeamGenerationError(
            f"{field_name} must be a non-empty list of strings"
        )

    parsed = [str(item).strip() for item in value]
    if any(not item for item in parsed):
        raise TeamGenerationError(f"{field_name} must contain non-empty strings")

    return parsed


def parse_number_range(
    value: Any,
    field_name: str,
    minimum: float,
    maximum: float,
) -> tuple[float, float]:
    if not isinstance(value, list) or len(value) != 2:
        raise TeamGenerationError(f"{field_name} must be a list with two numbers")

    left = float(value[0])
    right = float(value[1])

    if left < minimum or right > maximum or left > right:
        raise TeamGenerationError(
            f"{field_name} must be between {minimum} and {maximum}, "
            "and min cannot exceed max"
        )

    return left, right


def serialize_csv_value(value: Any) -> str | int | float | bool | None:
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return value


def count_values(values: Any) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value)
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def average(values: Any) -> float:
    collected = [float(value) for value in values]
    if not collected:
        return 0.0
    return round_float(sum(collected) / len(collected))


def clamp(value: float) -> float:
    if math.isnan(value):
        return 0.0
    return max(0.0, min(1.0, value))


def round_float(value: float) -> float:
    return round(float(value), 4)