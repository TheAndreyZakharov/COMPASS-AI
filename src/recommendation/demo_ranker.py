from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, cast

import pandas as pd

from src.models.schemas import CandidateRecommendation, RecommendationMode, RecommendationResponse

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EMPLOYEES_CSV_PATH = PROJECT_ROOT / "data" / "synthetic" / "employees.csv"
TASKS_CSV_PATH = PROJECT_ROOT / "data" / "synthetic" / "tasks.csv"

VALID_MODES: set[str] = {
    "fast_delivery",
    "balanced_workload",
    "growth",
    "risk_minimization",
}

ROLE_AFFINITY: dict[str, set[str]] = {
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
        "documentation_task",
    },
    "qa_engineer": {
        "testing_task",
        "bugfix",
        "security_task",
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
        "security_task",
        "refactoring",
        "documentation_task",
        "api_integration",
    },
}


def normalize_mode(mode: str) -> RecommendationMode:
    if mode not in VALID_MODES:
        return "balanced_workload"

    return cast(RecommendationMode, mode)


def parse_json_cell(value: Any, default: Any) -> Any:
    if value is None:
        return default

    if isinstance(value, float) and math.isnan(value):
        return default

    if isinstance(value, str):
        value = value.strip()

        if not value:
            return default

        return json.loads(value)

    return value


def load_demo_data(task_id: str | None = None) -> tuple[pd.Series, pd.DataFrame]:
    if not EMPLOYEES_CSV_PATH.exists() or not TASKS_CSV_PATH.exists():
        raise FileNotFoundError("Synthetic data is missing. Run make generate-data first.")

    employees = pd.read_csv(EMPLOYEES_CSV_PATH)
    tasks = pd.read_csv(TASKS_CSV_PATH)

    if employees.empty:
        raise ValueError("employees.csv is empty.")

    if tasks.empty:
        raise ValueError("tasks.csv is empty.")

    if task_id:
        matched_tasks = tasks[tasks["task_id"] == task_id]
        if matched_tasks.empty:
            raise ValueError(f"Task not found in synthetic dataset: {task_id}")

        return matched_tasks.iloc[0], employees

    priority_rank = {
        "urgent": 5,
        "high": 4,
        "medium": 3,
        "low": 2,
        "none": 1,
    }

    tasks = tasks.copy()
    tasks["priority_rank"] = tasks["priority"].map(priority_rank).fillna(3)

    task = tasks.sort_values(
        by=["priority_rank", "business_criticality", "complexity"],
        ascending=[False, False, False],
    ).iloc[0]

    return task, employees


def workload_score(current_workload: float) -> float:
    return max(0.0, min(1.0, 1.0 - current_workload))


def role_affinity_score(role: str, task_type: str) -> float:
    if task_type in ROLE_AFFINITY.get(role, set()):
        return 1.0

    return 0.30


def skill_match_score(employee_skills: dict[str, int], required_skills: dict[str, int]) -> float:
    if not required_skills:
        return 0.50

    scores: list[float] = []

    for skill, required_level in required_skills.items():
        employee_level = employee_skills.get(skill, 0)

        if required_level <= 0:
            scores.append(1.0)
        else:
            scores.append(min(employee_level / required_level, 1.0))

    return round(sum(scores) / len(scores), 4)


def growth_match_score(learning_goals: list[str], required_skills: dict[str, int]) -> float:
    if not learning_goals or not required_skills:
        return 0.0

    required = set(required_skills.keys())
    goals = set(learning_goals)

    return round(len(required & goals) / max(1, len(required)), 4)


def score_employee(
    employee: pd.Series,
    task: pd.Series,
    mode: RecommendationMode,
) -> tuple[float, dict[str, float]]:
    employee_skills = parse_json_cell(employee["skills"], default={})
    learning_goals = parse_json_cell(employee["learning_goals"], default=[])
    required_skills = parse_json_cell(task["required_skills"], default={})

    factors = {
        "skill_match": skill_match_score(employee_skills, required_skills),
        "role_affinity": role_affinity_score(str(employee["role"]), str(task["task_type"])),
        "workload": workload_score(float(employee["current_workload"])),
        "speed": float(employee["avg_completion_speed"]),
        "quality": float(employee["avg_quality_score"]),
        "deadline_reliability": float(employee["deadline_reliability"]),
        "growth_match": growth_match_score(learning_goals, required_skills),
    }

    if mode == "fast_delivery":
        score = (
            0.28 * factors["skill_match"]
            + 0.24 * factors["speed"]
            + 0.22 * factors["deadline_reliability"]
            + 0.16 * factors["role_affinity"]
            + 0.10 * factors["workload"]
        )

    elif mode == "growth":
        score = (
            0.26 * factors["skill_match"]
            + 0.24 * factors["growth_match"]
            + 0.18 * factors["workload"]
            + 0.14 * factors["quality"]
            + 0.10 * factors["deadline_reliability"]
            + 0.08 * factors["role_affinity"]
        )

    elif mode == "risk_minimization":
        score = (
            0.26 * factors["skill_match"]
            + 0.24 * factors["quality"]
            + 0.22 * factors["deadline_reliability"]
            + 0.16 * factors["workload"]
            + 0.12 * factors["role_affinity"]
        )

    else:
        score = (
            0.27 * factors["skill_match"]
            + 0.20 * factors["workload"]
            + 0.18 * factors["quality"]
            + 0.16 * factors["deadline_reliability"]
            + 0.11 * factors["speed"]
            + 0.08 * factors["role_affinity"]
        )

    return round(score, 4), factors


def reasons_for_employee(factors: dict[str, float], mode: RecommendationMode) -> list[str]:
    reasons = [
        f"skill_match={factors['skill_match']:.2f}",
        f"workload_score={factors['workload']:.2f}",
        f"quality={factors['quality']:.2f}",
        f"deadline_reliability={factors['deadline_reliability']:.2f}",
    ]

    if factors["role_affinity"] >= 0.9:
        reasons.append("role matches task type")

    if mode == "growth" and factors["growth_match"] > 0:
        reasons.append(f"growth_match={factors['growth_match']:.2f}")

    return reasons


def risks_for_employee(employee: pd.Series, factors: dict[str, float]) -> list[str]:
    risks: list[str] = []

    if float(employee["current_workload"]) >= 0.85:
        risks.append("high workload")

    if str(employee.get("availability", "")) != "available":
        risks.append("limited availability")

    if factors["skill_match"] < 0.45:
        risks.append("low skill match")

    if factors["role_affinity"] < 0.5:
        risks.append("role mismatch")

    return risks


def get_demo_recommendation(
    mode: str = "balanced_workload",
    task_id: str | None = None,
    top_k: int = 3,
) -> RecommendationResponse:
    normalized_mode = normalize_mode(mode)
    task, employees = load_demo_data(task_id=task_id)

    scored_candidates: list[CandidateRecommendation] = []

    for _, employee in employees.iterrows():
        score, factors = score_employee(employee, task, normalized_mode)

        scored_candidates.append(
            CandidateRecommendation(
                rank=0,
                employee_id=str(employee["employee_id"]),
                plane_user_id=None,
                name=str(employee["name"]),
                role=str(employee["role"]),
                grade=str(employee["grade"]),
                score=score,
                reasons=reasons_for_employee(factors, normalized_mode),
                risks=risks_for_employee(employee, factors),
                factors=factors,
            )
        )

    top_candidates = sorted(
        scored_candidates,
        key=lambda candidate: candidate.score,
        reverse=True,
    )[:top_k]

    for index, candidate in enumerate(top_candidates, start=1):
        candidate.rank = index

    return RecommendationResponse(
        task_id=str(task["task_id"]),
        plane_work_item_id=None,
        plane_issue_id=None,
        title=str(task["title"]),
        mode=normalized_mode,
        candidates=top_candidates,
        source="rule_based_demo",
        explanation=(
            "Demo recommendation uses lightweight rule-based scoring. "
            "The neural network is not used yet."
        ),
    )