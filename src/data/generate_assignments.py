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


def weighted_choice(weights: dict[str, float], rng: random.Random) -> str:
    return rng.choices(list(weights.keys()), weights=list(weights.values()), k=1)[0]


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

    return 0.35


def deadline_pressure(task: pd.Series) -> float:
    deadline_days = float(task["deadline_days"])
    complexity = float(task["complexity"])
    estimated_hours = float(task["estimated_hours"])

    pressure = 0.0

    if deadline_days <= 3:
        pressure += 0.35
    elif deadline_days <= 7:
        pressure += 0.22
    elif deadline_days <= 14:
        pressure += 0.10

    if estimated_hours >= 80:
        pressure += 0.18
    elif estimated_hours >= 50:
        pressure += 0.10

    if complexity >= 5:
        pressure += 0.18
    elif complexity >= 4:
        pressure += 0.10

    return clamp(pressure)


def business_risk(task: pd.Series) -> float:
    criticality = float(task["business_criticality"])
    priority = str(task["priority"])

    risk = (criticality - 1.0) / 4.0

    if priority == "urgent":
        risk += 0.20
    elif priority == "high":
        risk += 0.12

    return clamp(risk)


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
    deadline_risk = deadline_pressure(task)
    business_risk_score = business_risk(task)

    speed_score = clamp(float(employee["avg_completion_speed"]) * (1.05 - overload / 2))
    collaboration_score = clamp(
        0.55
        + float(employee["mentor_level"]) * 0.06
        + (0.08 if employee["grade"] in {"senior", "lead"} else 0.0)
    )

    risk_score = clamp(
        overload * 0.45
        + complexity_gap * 0.35
        + (1.0 - skill_score) * 0.25
        + (1.0 - role_affinity) * 0.20
        + deadline_risk * 0.15
        + business_risk_score * 0.12
    )

    suitability = clamp(
        0.40 * skill_score
        + 0.18 * role_affinity
        + 0.13 * float(employee["deadline_reliability"])
        + 0.12 * float(employee["avg_quality_score"])
        + 0.08 * speed_score
        + 0.09 * growth_score
        - 0.22 * overload
        - 0.15 * complexity_gap
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
        "deadline_pressure": deadline_risk,
        "business_risk": business_risk_score,
        "suitability": suitability,
    }


def success_probability(
    employee: pd.Series,
    task: pd.Series,
    scores: dict[str, float],
    scenario: str,
    rng: random.Random,
    noise_std: float,
) -> float:
    probability = (
        0.34 * scores["skill_match_score"]
        + 0.17 * float(employee["deadline_reliability"])
        + 0.14 * float(employee["avg_quality_score"])
        + 0.10 * float(employee["avg_completion_speed"])
        + 0.08 * scores["collaboration_score"]
        + 0.07 * scores["growth_match_score"]
        + 0.05 * scores["role_affinity"]
        - 0.22 * scores["overload_penalty"]
        - 0.18 * scores["complexity_gap_penalty"]
        - 0.10 * scores["deadline_pressure"]
        - 0.08 * scores["business_risk"]
    )

    scenario_shift = {
        "ideal_match": 0.12,
        "balanced_match": 0.07,
        "growth_stretch": 0.00,
        "overload_risk": -0.14,
        "wrong_role": -0.25,
        "urgent_deadline": -0.10,
        "random_assignment": -0.06,
    }[scenario]

    probability += scenario_shift
    probability += rng.normalvariate(0.0, noise_std)

    return clamp(probability, 0.01, 0.99)


def employee_candidates_for_task(
    employees: pd.DataFrame,
    task: pd.Series,
) -> list[tuple[int, dict[str, float]]]:
    candidates: list[tuple[int, dict[str, float]]] = []

    for employee_index, employee in employees.iterrows():
        scores = calculate_assignment_scores(employee, task)
        candidates.append((int(employee_index), scores))

    candidates.sort(reverse=True, key=lambda item: item[1]["suitability"])
    return candidates


def choose_employee_by_scenario(
    employees: pd.DataFrame,
    task: pd.Series,
    scenario: str,
    rng: random.Random,
    candidate_pool_size: int,
) -> tuple[pd.Series, dict[str, float]]:
    candidates = employee_candidates_for_task(employees, task)

    if scenario == "ideal_match":
        pool = candidates[: max(1, candidate_pool_size)]
        weights = [max(0.01, item[1]["suitability"]) for item in pool]

    elif scenario == "balanced_match":
        upper = max(candidate_pool_size, len(candidates) // 2)
        pool = candidates[:upper]
        weights = [
            max(
                0.01,
                item[1]["suitability"] - item[1]["overload_penalty"] * 0.20,
            )
            for item in pool
        ]

    elif scenario == "growth_stretch":
        pool = sorted(
            candidates,
            reverse=True,
            key=lambda item: (
                item[1]["growth_match_score"],
                -item[1]["complexity_gap_penalty"],
                item[1]["suitability"],
            ),
        )[: max(candidate_pool_size, 6)]
        weights = [
            max(0.01, 0.50 + item[1]["growth_match_score"] - item[1]["risk_score"] * 0.30)
            for item in pool
        ]

    elif scenario == "overload_risk":
        pool = sorted(
            candidates,
            reverse=True,
            key=lambda item: (
                item[1]["overload_penalty"],
                item[1]["skill_match_score"],
            ),
        )[: max(candidate_pool_size, 6)]
        weights = [max(0.01, 0.40 + item[1]["overload_penalty"]) for item in pool]

    elif scenario == "wrong_role":
        pool = sorted(
            candidates,
            key=lambda item: (
                item[1]["role_affinity"],
                item[1]["skill_match_score"],
            ),
        )[: max(candidate_pool_size, 6)]
        weights = [
            max(0.01, 1.0 - item[1]["role_affinity"] + 1.0 - item[1]["skill_match_score"])
            for item in pool
        ]

    elif scenario == "urgent_deadline":
        pool = sorted(
            candidates,
            reverse=True,
            key=lambda item: (
                item[1]["deadline_pressure"],
                item[1]["skill_match_score"],
                item[1]["overload_penalty"],
            ),
        )[: max(candidate_pool_size, 6)]
        weights = [
            max(
                0.01,
                item[1]["skill_match_score"]
                + item[1]["deadline_pressure"]
                + item[1]["overload_penalty"] * 0.40,
            )
            for item in pool
        ]

    else:
        pool = candidates
        weights = [1.0 for _ in pool]

    chosen_index, scores = rng.choices(pool, weights=weights, k=1)[0]
    employee = employees.loc[chosen_index]
    return employee, scores

def choose_scenario_for_pair(
    scores: dict[str, float],
    task: pd.Series,
    config: dict[str, Any],
    rng: random.Random,
) -> str:
    scenario_weights = dict(config["assignment_generation"]["scenario_weights"])

    skill_score = scores["skill_match_score"]
    role_affinity = scores["role_affinity"]
    overload = scores["overload_penalty"]
    growth_score = scores["growth_match_score"]
    complexity_gap = scores["complexity_gap_penalty"]
    deadline_risk = scores["deadline_pressure"]

    if skill_score >= 0.85 and role_affinity >= 1.0 and overload <= 0.20:
        scenario_weights["ideal_match"] *= 2.8
        scenario_weights["balanced_match"] *= 1.5

    if skill_score >= 0.65 and overload <= 0.20:
        scenario_weights["balanced_match"] *= 1.8

    if growth_score > 0 and complexity_gap <= 0.25:
        scenario_weights["growth_stretch"] *= 2.3

    if overload >= 0.50:
        scenario_weights["overload_risk"] *= 3.2

    if role_affinity < 0.50 or skill_score < 0.35:
        scenario_weights["wrong_role"] *= 3.0

    if deadline_risk >= 0.22 or str(task["priority"]) == "urgent":
        scenario_weights["urgent_deadline"] *= 2.6

    return weighted_choice(scenario_weights, rng)

def choose_task_for_scenario(
    tasks: pd.DataFrame,
    scenario: str,
    seed: int,
    index: int,
    attempt: int,
) -> pd.Series:
    if scenario == "urgent_deadline":
        urgent_tasks = tasks[
            (tasks["priority"].isin(["high", "urgent"]))
            | (tasks["deadline_days"].astype(float) <= 7)
        ]

        if not urgent_tasks.empty:
            return urgent_tasks.sample(n=1, random_state=seed + index + attempt).iloc[0]

    if scenario in {"wrong_role", "overload_risk"}:
        hard_tasks = tasks[
            (tasks["complexity"].astype(int) >= 4)
            | (tasks["business_criticality"].astype(int) >= 4)
        ]

        if not hard_tasks.empty:
            return hard_tasks.sample(n=1, random_state=seed + index + attempt).iloc[0]

    return tasks.sample(n=1, random_state=seed + index + attempt).iloc[0]


def outcome_from_probability(
    probability: float,
    scenario: str,
    rng: random.Random,
) -> tuple[str, int]:
    random_value = rng.random()

    if random_value < probability:
        if scenario == "growth_stretch" and rng.random() < 0.25:
            return "partial_success", 1

        if scenario == "urgent_deadline" and rng.random() < 0.12:
            return "delayed_delivery", 0

        if scenario == "overload_risk" and rng.random() < 0.10:
            return "delayed_delivery", 0

        return "full_success", 1

    if scenario == "wrong_role":
        return rng.choice(["failed_delivery", "cancelled_or_not_finished"]), 0

    if scenario == "overload_risk":
        return rng.choice(["delayed_delivery", "failed_delivery"]), 0

    if scenario == "urgent_deadline":
        return rng.choice(["delayed_delivery", "failed_delivery"]), 0

    if scenario == "growth_stretch":
        if rng.random() < 0.35:
            return "partial_success", 1

        return rng.choice(["delayed_delivery", "failed_delivery"]), 0

    if scenario == "random_assignment":
        return rng.choice(
            ["partial_success", "delayed_delivery", "failed_delivery", "cancelled_or_not_finished"]
        ), rng.choice([0, 0, 1])

    return rng.choice(["partial_success", "delayed_delivery", "failed_delivery"]), 0


def delivery_speed_category(
    outcome_status: str,
    actual_hours: float,
    estimated_hours: float,
    completed_on_time: bool,
) -> str:
    if outcome_status == "cancelled_or_not_finished":
        return "not_finished"

    ratio = actual_hours / max(1.0, estimated_hours)

    if completed_on_time and ratio <= 0.75:
        return "very_fast"

    if completed_on_time:
        return "on_time"

    if ratio <= 1.35:
        return "slightly_delayed"

    return "heavily_delayed"


def build_outcome_metrics(
    task: pd.Series,
    employee: pd.Series,
    outcome_status: str,
    success_label: int,
    rng: random.Random,
    config: dict[str, Any],
) -> dict[str, Any]:
    estimated_hours = float(task["estimated_hours"])

    actual_multiplier = rng.uniform(
        float(config["assignment_generation"]["min_actual_hours_multiplier"]),
        float(config["assignment_generation"]["max_actual_hours_multiplier"]),
    )

    if outcome_status == "full_success":
        actual_multiplier *= rng.uniform(0.60, 1.02)
        quality_score = clamp(rng.normalvariate(0.86, 0.07))
        reopened_count = rng.choice([0, 0, 0, 1])
        manager_rating = rng.choice([4, 4, 5, 5])

    elif outcome_status == "partial_success":
        actual_multiplier *= rng.uniform(0.90, 1.25)
        quality_score = clamp(rng.normalvariate(0.74, 0.09))
        reopened_count = rng.choice([0, 1, 1, 2])
        manager_rating = rng.choice([3, 4, 4])

    elif outcome_status == "delayed_delivery":
        actual_multiplier *= rng.uniform(1.20, 1.80)
        quality_score = clamp(rng.normalvariate(0.68, 0.12))
        reopened_count = rng.choice([1, 1, 2, 3])
        manager_rating = rng.choice([2, 3, 3, 4])

    elif outcome_status == "failed_delivery":
        actual_multiplier *= rng.uniform(1.30, 2.20)
        quality_score = clamp(rng.normalvariate(0.48, 0.15))
        reopened_count = rng.randint(2, int(config["assignment_generation"]["reopened_count_max"]))
        manager_rating = rng.choice([1, 2, 2, 3])

    else:
        actual_multiplier *= rng.uniform(0.20, 0.80)
        quality_score = clamp(rng.normalvariate(0.25, 0.12))
        reopened_count = rng.randint(0, 3)
        manager_rating = rng.choice([1, 1, 2])

    actual_hours = round(max(0.5, estimated_hours * actual_multiplier), 1)

    planned_duration_days = max(1, int(float(task["deadline_days"])))

    if outcome_status == "cancelled_or_not_finished":
        completed_on_time = False
        delay_days = planned_duration_days + rng.randint(3, 21)

    elif outcome_status in {"full_success", "partial_success"}:
        completed_on_time = rng.random() < 0.92
        delay_days = 0 if completed_on_time else rng.randint(1, 5)

    elif outcome_status == "delayed_delivery":
        completed_on_time = False
        delay_days = rng.randint(1, 14)

    else:
        completed_on_time = False
        delay_days = rng.randint(3, 30)

    employee_workload = clamp(
        float(employee["current_workload"]) + rng.normalvariate(0.0, 0.10)
    )

    return {
        "estimated_hours": estimated_hours,
        "actual_hours": actual_hours,
        "quality_score": quality_score,
        "reopened_count": reopened_count,
        "manager_rating": manager_rating,
        "completed_on_time": bool(completed_on_time),
        "delay_days": int(delay_days),
        "employee_workload_at_assignment": employee_workload,
        "delivery_speed_category": delivery_speed_category(
            outcome_status=outcome_status,
            actual_hours=actual_hours,
            estimated_hours=estimated_hours,
            completed_on_time=completed_on_time,
        ),
        "success_label": int(success_label),
    }

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

    max_unique_pairs = len(tasks) * len(employees)
    if assignments_count > max_unique_pairs:
        raise ValueError(
            f"assignments_count={assignments_count} is too large for unique "
            f"task+employee pairs. Maximum possible pairs: {max_unique_pairs}"
        )

    all_pairs = [
        (task_index, employee_index)
        for task_index in tasks.index
        for employee_index in employees.index
    ]
    rng.shuffle(all_pairs)

    selected_pairs = all_pairs[:assignments_count]

    assignments: list[dict[str, Any]] = []

    for index, (task_index, employee_index) in enumerate(selected_pairs, start=1):
        task = tasks.loc[task_index]
        employee = employees.loc[employee_index]

        scores = calculate_assignment_scores(employee, task)

        scenario = choose_scenario_for_pair(
            scores=scores,
            task=task,
            config=config,
            rng=rng,
        )

        probability = success_probability(
            employee=employee,
            task=task,
            scores=scores,
            scenario=scenario,
            rng=rng,
            noise_std=float(config["assignment_generation"]["success_probability_noise"]),
        )

        outcome_status, success_label = outcome_from_probability(probability, scenario, rng)

        outcome_metrics = build_outcome_metrics(
            task=task,
            employee=employee,
            outcome_status=outcome_status,
            success_label=success_label,
            rng=rng,
            config=config,
        )

        assigned_at = date_start + timedelta(days=rng.randint(0, total_days))

        if outcome_status == "cancelled_or_not_finished":
            completed_at = ""
        else:
            completed_at = assigned_at + timedelta(
                days=max(
                    1,
                    int(float(task["deadline_days"])) + outcome_metrics["delay_days"],
                )
            )
            completed_at = completed_at.isoformat()

        assignments.append(
            {
                "assignment_id": f"ASN-{index:06d}",
                "task_id": task["task_id"],
                "employee_id": employee["employee_id"],
                "plane_work_item_id": task.get("plane_work_item_id", ""),
                "plane_issue_id": task.get("plane_issue_id", ""),
                "assigned_at": assigned_at.isoformat(),
                "completed_at": completed_at,
                "completed_on_time": outcome_metrics["completed_on_time"],
                "estimated_hours": outcome_metrics["estimated_hours"],
                "actual_hours": outcome_metrics["actual_hours"],
                "quality_score": outcome_metrics["quality_score"],
                "reopened_count": outcome_metrics["reopened_count"],
                "manager_rating": outcome_metrics["manager_rating"],
                "employee_workload_at_assignment": outcome_metrics[
                    "employee_workload_at_assignment"
                ],
                "skill_match_score": scores["skill_match_score"],
                "growth_match_score": scores["growth_match_score"],
                "speed_score": scores["speed_score"],
                "collaboration_score": scores["collaboration_score"],
                "risk_score": scores["risk_score"],
                "success_probability": probability,
                "assignment_scenario": scenario,
                "outcome_status": outcome_status,
                "delay_days": outcome_metrics["delay_days"],
                "delivery_speed_category": outcome_metrics["delivery_speed_category"],
                "success_label": outcome_metrics["success_label"],
            }
        )

        if index % 10000 == 0:
            print(f"Generated assignments: {index}/{assignments_count}")

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
        "assignment_scenario",
        "outcome_status",
        "skill_match_score",
        "risk_score",
        "success_probability",
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

    print()
    print("Outcome status distribution:")
    print(df["outcome_status"].value_counts(normalize=True).sort_index().to_string())

    print()
    print("Assignment scenario distribution:")
    print(df["assignment_scenario"].value_counts(normalize=True).sort_index().to_string())

    print()
    print("Duplicate task+employee pairs:")
    print(df.duplicated(["task_id", "employee_id"]).sum())


def main() -> None:
    assignments = generate_assignments()
    save_assignments(assignments)


if __name__ == "__main__":
    main()