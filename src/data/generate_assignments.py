from __future__ import annotations

import json
import random
from datetime import datetime, timedelta
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


def load_json_cell(value: Any) -> Any:
    if isinstance(value, str) and value:
        return json.loads(value)
    return value


def clamp(value: float, min_value: float = 0.0, max_value: float = 1.0) -> float:
    return round(max(min_value, min(max_value, value)), 4)


def skill_match_score(
    employee_skills: dict[str, int],
    required_skills: dict[str, int],
) -> float:
    if not required_skills:
        return 0.5

    scores = []
    for skill, required_level in required_skills.items():
        employee_level = employee_skills.get(skill, 0)
        if required_level <= 0:
            scores.append(1.0)
        else:
            scores.append(min(employee_level / required_level, 1.0))

    return clamp(sum(scores) / len(scores))


def growth_match_score(
    learning_goals: list[str],
    required_skills: dict[str, int],
) -> float:
    if not learning_goals or not required_skills:
        return 0.0

    required = set(required_skills.keys())
    goals = set(learning_goals)
    return clamp(len(required & goals) / max(1, len(required)))


def overload_penalty(workload: float) -> float:
    if workload <= 0.70:
        return 0.0
    if workload <= 0.85:
        return 0.20
    if workload <= 0.95:
        return 0.50
    return 0.80


def comfortable_complexity(grade: str) -> tuple[int, int]:
    if grade == "junior":
        return 1, 2
    if grade == "middle":
        return 2, 4
    if grade == "senior":
        return 3, 5
    if grade == "lead":
        return 4, 5
    return 1, 3


def complexity_gap_penalty(grade: str, complexity: int) -> float:
    min_complexity, max_complexity = comfortable_complexity(grade)

    if min_complexity <= complexity <= max_complexity:
        return 0.0

    if complexity > max_complexity:
        return min(0.8, (complexity - max_complexity) * 0.25)

    return min(0.3, (min_complexity - complexity) * 0.10)


def role_task_affinity(role: str, task_type: str) -> float:
    affinity = {
        "backend_developer": {
            "backend_feature",
            "bugfix",
            "refactoring",
            "database_migration",
            "api_integration",
            "security_task",
        },
        "frontend_developer": {
            "frontend_feature",
            "bugfix",
            "refactoring",
            "documentation_task",
        },
        "qa_engineer": {
            "testing_task",
            "bugfix",
            "security_task",
            "documentation_task",
        },
        "data_ml_engineer": {
            "ml_pipeline",
            "analytics_report",
            "database_migration",
        },
        "devops_engineer": {
            "devops_task",
            "security_task",
            "monitoring_task",
        },
        "team_lead": {
            "refactoring",
            "security_task",
            "documentation_task",
            "api_integration",
        },
    }

    if task_type in affinity.get(role, set()):
        return 1.0

    return 0.45


def calculate_assignment_scores(
    employee: pd.Series,
    task: pd.Series,
) -> dict[str, float]:
    employee_skills = load_json_cell(employee["skills"])
    required_skills = load_json_cell(task["required_skills"])
    learning_goals = load_json_cell(employee["learning_goals"])

    skill_score = skill_match_score(employee_skills, required_skills)
    growth_score = growth_match_score(learning_goals, required_skills)

    workload = float(employee["current_workload"])
    overload = overload_penalty(workload)
    complexity_gap = complexity_gap_penalty(
        str(employee["grade"]),
        int(task["complexity"]),
    )

    role_affinity = role_task_affinity(str(employee["role"]), str(task["task_type"]))

    speed_score = clamp(float(employee["avg_completion_speed"]) * (1.05 - overload / 2))
    collaboration_score = clamp(
        0.55
        + float(employee["mentor_level"]) * 0.06
        + (0.08 if employee["grade"] in {"senior", "lead"} else 0.0)
    )
    risk_score = clamp(
        overload * 0.50
        + complexity_gap * 0.35
        + (1.0 - skill_score) * 0.25
        + (1.0 - role_affinity) * 0.20
    )

    return {
        "skill_match_score": skill_score,
        "growth_match_score": growth_score,
        "speed_score": speed_score,
        "collaboration_score": collaboration_score,
        "risk_score": risk_score,
        "overload_penalty": overload,
        "complexity_gap_penalty": complexity_gap,
        "role_affinity": role_affinity,
    }


def success_probability(
    employee: pd.Series,
    scores: dict[str, float],
    rng: random.Random,
) -> float:
    probability = (
        0.35 * scores["skill_match_score"]
        + 0.20 * float(employee["deadline_reliability"])
        + 0.15 * float(employee["avg_quality_score"])
        + 0.10 * float(employee["avg_completion_speed"])
        + 0.10 * scores["collaboration_score"]
        + 0.10 * scores["growth_match_score"]
        - 0.25 * scores["overload_penalty"]
        - 0.15 * scores["complexity_gap_penalty"]
    )

    probability += rng.normalvariate(0.0, 0.08)
    return clamp(probability, 0.02, 0.98)


def choose_employee_for_task(
    employees: pd.DataFrame,
    task: pd.Series,
    rng: random.Random,
) -> tuple[pd.Series, dict[str, float]]:
    candidates: list[tuple[float, int, dict[str, float]]] = []

    for employee_index, employee in employees.iterrows():
        scores = calculate_assignment_scores(employee, task)
        suitability = (
            0.45 * scores["skill_match_score"]
            + 0.20 * scores["role_affinity"]
            + 0.15 * float(employee["deadline_reliability"])
            + 0.10 * float(employee["avg_quality_score"])
            + 0.10 * scores["growth_match_score"]
            - 0.25 * scores["overload_penalty"]
        )
        suitability += rng.normalvariate(0.0, 0.05)
        candidates.append((suitability, int(employee_index), scores))

    candidates.sort(reverse=True, key=lambda item: item[0])

    pool_size = min(5, len(candidates))
    top_candidates = candidates[:pool_size]
    weights = [max(0.01, item[0]) for item in top_candidates]
    chosen = rng.choices(top_candidates, weights=weights, k=1)[0]

    employee = employees.loc[chosen[1]]
    return employee, chosen[2]


def generate_assignments() -> pd.DataFrame:
    config = load_yaml(SYNTHETIC_DATA_CONFIG_PATH)

    seed = int(config["random_seed"]) + 2
    rng = random.Random(seed)
    np.random.seed(seed)

    employees_path = PROJECT_ROOT / config["output"]["employees_csv"]
    tasks_path = PROJECT_ROOT / config["output"]["tasks_csv"]

    if not employees_path.exists():
        raise FileNotFoundError(f"Missing employees file: {employees_path}")

    if not tasks_path.exists():
        raise FileNotFoundError(f"Missing tasks file: {tasks_path}")

    employees = pd.read_csv(employees_path)
    tasks = pd.read_csv(tasks_path)

    assignments_count = int(config["assignments_count"])
    date_start = datetime.fromisoformat(config["date_range_start"])
    date_end = datetime.fromisoformat(config["date_range_end"])
    total_days = (date_end - date_start).days

    assignments: list[dict[str, Any]] = []

    for index in range(1, assignments_count + 1):
        task = tasks.sample(n=1, random_state=seed + index).iloc[0]
        employee, scores = choose_employee_for_task(employees, task, rng)

        probability = success_probability(employee, scores, rng)
        success_label = int(rng.random() < probability)

        estimated_hours = float(task["estimated_hours"])
        actual_multiplier = rng.uniform(
            config["assignment_generation"]["min_actual_hours_multiplier"],
            config["assignment_generation"]["max_actual_hours_multiplier"],
        )

        if success_label == 1:
            actual_multiplier *= rng.uniform(0.75, 1.10)
        else:
            actual_multiplier *= rng.uniform(1.05, 1.60)

        actual_hours = round(max(1.0, estimated_hours * actual_multiplier), 1)

        assigned_at = date_start + timedelta(days=rng.randint(0, total_days))
        planned_duration_days = max(1, int(float(task["deadline_days"])))
        completed_on_time = success_label == 1 or rng.random() < 0.25

        if completed_on_time:
            completed_at = assigned_at + timedelta(
                days=rng.randint(1, planned_duration_days),
            )
        else:
            completed_at = assigned_at + timedelta(
                days=planned_duration_days + rng.randint(1, 14),
            )

        if success_label == 1:
            quality_score = clamp(rng.normalvariate(0.82, 0.08))
            reopened_count = rng.choice([0, 0, 0, 1])
            manager_rating = rng.choice([4, 4, 5])
        else:
            quality_score = clamp(rng.normalvariate(0.58, 0.16))
            reopened_count = rng.randint(
                1,
                int(config["assignment_generation"]["reopened_count_max"]),
            )
            manager_rating = rng.choice([1, 2, 2, 3])

        employee_workload = clamp(
            float(employee["current_workload"]) + rng.normalvariate(0.0, 0.08)
        )

        assignments.append(
            {
                "assignment_id": f"ASN-{index:06d}",
                "task_id": task["task_id"],
                "employee_id": employee["employee_id"],
                "plane_work_item_id": task.get("plane_work_item_id", ""),
                "plane_issue_id": task.get("plane_issue_id", ""),
                "assigned_at": assigned_at.isoformat(),
                "completed_at": completed_at.isoformat(),
                "completed_on_time": bool(completed_on_time),
                "estimated_hours": estimated_hours,
                "actual_hours": actual_hours,
                "quality_score": quality_score,
                "reopened_count": reopened_count,
                "manager_rating": manager_rating,
                "employee_workload_at_assignment": employee_workload,
                "skill_match_score": scores["skill_match_score"],
                "growth_match_score": scores["growth_match_score"],
                "speed_score": scores["speed_score"],
                "collaboration_score": scores["collaboration_score"],
                "risk_score": scores["risk_score"],
                "success_label": success_label,
            }
        )

    return pd.DataFrame(assignments)


def save_assignments(df: pd.DataFrame) -> None:
    config = load_yaml(SYNTHETIC_DATA_CONFIG_PATH)
    csv_path = PROJECT_ROOT / config["output"]["assignments_csv"]
    json_path = PROJECT_ROOT / config["output"]["assignments_json"]

    csv_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(csv_path, index=False)
    df.to_json(json_path, orient="records", force_ascii=False, indent=2)

    preview_columns = [
        "assignment_id",
        "task_id",
        "employee_id",
        "skill_match_score",
        "success_label",
    ]

    print(f"Assignments generated: {len(df)}")
    print(f"CSV: {csv_path}")
    print(f"JSON: {json_path}")
    print()
    print(df[preview_columns].head(20).to_string(index=False))
    print()
    print("Success label distribution:")
    print(df["success_label"].value_counts(normalize=True).sort_index().to_string())


def main() -> None:
    assignments = generate_assignments()
    save_assignments(assignments)


if __name__ == "__main__":
    main()