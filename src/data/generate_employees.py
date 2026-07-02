from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SYNTHETIC_SCHEMA_PATH = PROJECT_ROOT / "config" / "synthetic_schema.yaml"
SYNTHETIC_DATA_CONFIG_PATH = PROJECT_ROOT / "config" / "synthetic_data.yaml"


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def clamp(value: float, min_value: float = 0.0, max_value: float = 1.0) -> float:
    return round(max(min_value, min(max_value, value)), 3)


def build_role_grade_plan(config: dict[str, Any]) -> list[tuple[str, str]]:
    role_grade_config = config["employee_generation"]["role_grade_plan"]

    role_grade_plan: list[tuple[str, str]] = []

    for role, grades in role_grade_config.items():
        for grade, count in grades.items():
            role_grade_plan.extend([(role, grade)] * int(count))

    return role_grade_plan


def grade_base_level(grade: str) -> int:
    if grade == "junior":
        return 2
    if grade == "middle":
        return 3
    if grade == "senior":
        return 4
    if grade == "lead":
        return 4
    return 2


def generate_skill_levels(
    role: str,
    grade: str,
    schema: dict[str, Any],
    rng: random.Random,
) -> dict[str, int]:
    skills_schema = schema["skills"]
    all_skills = (
        skills_schema["technical"]
        + skills_schema["soft_management"]
        + skills_schema["domain"]
    )
    role_profile = skills_schema["role_skill_profiles"][role]
    primary = set(role_profile["primary"])
    secondary = set(role_profile["secondary"])

    base = grade_base_level(grade)
    skills: dict[str, int] = {}

    for skill in all_skills:
        if skill in primary:
            level = base + rng.choice([-1, 0, 0, 1])
        elif skill in secondary:
            level = base - 1 + rng.choice([-1, 0, 0, 1])
        else:
            level = rng.choice([0, 0, 0, 1, 1, 2])

        if grade == "junior":
            level = min(level, 3)

        if grade == "lead" and skill in primary:
            level = max(level, 4)

        skills[skill] = int(max(0, min(5, level)))

    return skills


def choose_workload(config: dict[str, Any], schema: dict[str, Any], rng: random.Random) -> float:
    distribution = config["employee_generation"]["workload_distribution"]
    bucket = rng.choices(
        population=list(distribution.keys()),
        weights=list(distribution.values()),
        k=1,
    )[0]

    workload_range = schema["team"]["workload_ranges"][bucket]
    return round(rng.uniform(workload_range["min"], workload_range["max"]), 3)


def generate_learning_goals(
    role: str,
    skills: dict[str, int],
    schema: dict[str, Any],
    rng: random.Random,
) -> list[str]:
    role_profile = schema["skills"]["role_skill_profiles"][role]
    candidate_skills = role_profile["primary"] + role_profile["secondary"]
    candidates = [skill for skill in candidate_skills if skills.get(skill, 0) < 4]

    if not candidates:
        candidates = candidate_skills

    goals_count = rng.choice([2, 2, 3, 3, 4])
    return sorted(rng.sample(candidates, k=min(goals_count, len(candidates))))


def mentor_level_for_grade(grade: str, rng: random.Random) -> int:
    if grade == "junior":
        return rng.choice([0, 0, 1])
    if grade == "middle":
        return rng.choice([1, 2, 2, 3])
    if grade == "senior":
        return rng.choice([3, 4, 4, 5])
    if grade == "lead":
        return rng.choice([4, 5, 5])
    return 1


def availability_from_workload(current_workload: float) -> str:
    if current_workload >= 0.95:
        return "unavailable"
    if current_workload >= 0.85:
        return "partially_available"
    return "available"


def generate_employees() -> pd.DataFrame:
    schema = load_yaml(SYNTHETIC_SCHEMA_PATH)
    config = load_yaml(SYNTHETIC_DATA_CONFIG_PATH)

    seed = int(config["random_seed"])
    rng = random.Random(seed)
    np.random.seed(seed)

    names = config["employee_generation"]["synthetic_names"]
    role_grade_plan = build_role_grade_plan(config)

    expected_count = int(config["employees_count"])

    if len(role_grade_plan) != expected_count:
        raise ValueError(
            f"role_grade_plan generated {len(role_grade_plan)} employees, "
            f"but employees_count={expected_count}."
        )

    if len(names) < len(role_grade_plan):
        raise ValueError("Not enough synthetic names for the role/grade plan.")

    employees: list[dict[str, Any]] = []

    for index, (role, grade) in enumerate(role_grade_plan, start=1):
        employee_id = f"EMP-{index:03d}"
        role_config = schema["team"]["roles"][role]
        experience_range = schema["team"]["experience_years_ranges"][grade]

        skills = generate_skill_levels(role=role, grade=grade, schema=schema, rng=rng)
        current_workload = choose_workload(config=config, schema=schema, rng=rng)
        experience_years = round(
            rng.uniform(experience_range["min"], experience_range["max"]),
            1,
        )

        active_tasks_count = max(0, int(round(current_workload * rng.uniform(4, 12))))

        grade_quality_bonus = {
            "junior": 0.00,
            "middle": 0.08,
            "senior": 0.15,
            "lead": 0.13,
        }[grade]

        role_bonus = {
            "backend_developer": 0.02,
            "frontend_developer": 0.01,
            "qa_engineer": 0.03,
            "data_ml_engineer": 0.02,
            "devops_engineer": 0.02,
            "team_lead": 0.04,
        }.get(role, 0.0)

        avg_completion_speed = clamp(
            rng.normalvariate(0.66 + grade_quality_bonus / 2 + role_bonus, 0.11)
        )
        avg_quality_score = clamp(
            rng.normalvariate(0.69 + grade_quality_bonus + role_bonus, 0.09)
        )
        deadline_reliability = clamp(
            rng.normalvariate(0.70 + grade_quality_bonus + role_bonus, 0.11)
        )

        mentor_level = mentor_level_for_grade(grade, rng)

        employees.append(
            {
                "employee_id": employee_id,
                "plane_user_id": "",
                "name": names[index - 1],
                "role": role,
                "grade": grade,
                "experience_years": experience_years,
                "primary_stack": role_config["primary_stack"],
                "skills": json.dumps(skills, ensure_ascii=False, sort_keys=True),
                "current_workload": current_workload,
                "active_tasks_count": active_tasks_count,
                "avg_completion_speed": avg_completion_speed,
                "avg_quality_score": avg_quality_score,
                "deadline_reliability": deadline_reliability,
                "learning_goals": json.dumps(
                    generate_learning_goals(role, skills, schema, rng),
                    ensure_ascii=False,
                ),
                "mentor_level": mentor_level,
                "availability": availability_from_workload(current_workload),
                "timezone": schema["team"]["timezone"],
            }
        )

    return pd.DataFrame(employees)


def save_employees(df: pd.DataFrame) -> None:
    config = load_yaml(SYNTHETIC_DATA_CONFIG_PATH)
    csv_path = PROJECT_ROOT / config["output"]["employees_csv"]
    json_path = PROJECT_ROOT / config["output"]["employees_json"]

    csv_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(csv_path, index=False)
    df.to_json(json_path, orient="records", force_ascii=False, indent=2)

    print(f"Employees generated: {len(df)}")
    print(f"CSV: {csv_path}")
    print(f"JSON: {json_path}")
    print()
    print("Employees by role:")
    print(df["role"].value_counts().to_string())
    print()
    print("Employees by grade:")
    print(df["grade"].value_counts().to_string())
    print()
    print(df[["employee_id", "name", "role", "grade", "current_workload"]].to_string(index=False))


def main() -> None:
    employees = generate_employees()
    save_employees(employees)


if __name__ == "__main__":
    main()