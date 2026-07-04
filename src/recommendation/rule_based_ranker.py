from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

import pandas as pd

from src.recommendation.growth_scoring import calculate_growth_score
from src.recommendation.skill_matching import calculate_skill_match
from src.recommendation.workload_scoring import calculate_workload_score

RecommendationMode = Literal[
    "fast_delivery",
    "balanced_workload",
    "growth",
    "risk_minimization",
]


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EMPLOYEES_PATH = PROJECT_ROOT / "data" / "synthetic" / "employees.csv"
DEFAULT_TASKS_PATH = PROJECT_ROOT / "data" / "synthetic" / "tasks.csv"


MODE_WEIGHTS: dict[str, dict[str, float]] = {
    "fast_delivery": {
        "skill": 0.30,
        "workload": 0.10,
        "growth": 0.05,
        "speed": 0.25,
        "quality": 0.15,
        "reliability": 0.15,
    },
    "balanced_workload": {
        "skill": 0.30,
        "workload": 0.25,
        "growth": 0.10,
        "speed": 0.10,
        "quality": 0.15,
        "reliability": 0.10,
    },
    "growth": {
        "skill": 0.25,
        "workload": 0.15,
        "growth": 0.30,
        "speed": 0.05,
        "quality": 0.15,
        "reliability": 0.10,
    },
    "risk_minimization": {
        "skill": 0.30,
        "workload": 0.20,
        "growth": 0.05,
        "speed": 0.10,
        "quality": 0.20,
        "reliability": 0.15,
    },
}


TASK_ROLE_AFFINITY: dict[str, set[str]] = {
    "backend_feature": {"backend_developer", "team_lead"},
    "api_integration": {"backend_developer", "team_lead"},
    "database_migration": {"backend_developer", "data_ml_engineer", "devops_engineer"},
    "security_task": {"backend_developer", "devops_engineer", "team_lead"},
    "frontend_feature": {"frontend_developer"},
    "analytics_report": {"data_ml_engineer", "frontend_developer", "team_lead"},
    "ml_pipeline": {"data_ml_engineer"},
    "devops_task": {"devops_engineer", "backend_developer"},
    "testing_task": {"qa_engineer", "backend_developer", "frontend_developer"},
    "bugfix": {"backend_developer", "frontend_developer", "qa_engineer"},
    "refactoring": {"backend_developer", "frontend_developer", "team_lead"},
    "documentation_task": {
        "backend_developer",
        "frontend_developer",
        "qa_engineer",
        "data_ml_engineer",
        "devops_engineer",
        "team_lead",
    },
}


@dataclass(frozen=True)
class RuleBasedCandidate:
    rank: int
    employee_id: str
    plane_user_id: str | None
    name: str
    role: str
    grade: str
    score: float
    reasons: list[str]
    risks: list[str]
    factors: dict[str, float]


@dataclass(frozen=True)
class RuleBasedRecommendation:
    task_id: str
    plane_work_item_id: str | None
    plane_issue_id: str | None
    title: str
    mode: str
    candidates: list[RuleBasedCandidate]
    source: str
    explanation: str


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default

        if isinstance(value, float) and math.isnan(value):
            return default

        return float(value)
    except (TypeError, ValueError):
        return default


def _nullable_string(value: Any) -> str | None:
    if value is None:
        return None

    if isinstance(value, float) and math.isnan(value):
        return None

    text = str(value).strip()
    return text if text else None


def _row_to_dict(row: pd.Series | dict[str, Any]) -> dict[str, Any]:
    if isinstance(row, pd.Series):
        return row.to_dict()

    return dict(row)


def _normalize_mode(mode: str) -> RecommendationMode:
    if mode not in MODE_WEIGHTS:
        return "balanced_workload"

    return mode  # type: ignore[return-value]


def role_affinity_score(task: dict[str, Any], employee: dict[str, Any]) -> float:
    task_type = str(task.get("task_type", "")).strip()
    role = str(employee.get("role", "")).strip()

    if not task_type or not role:
        return 0.5

    compatible_roles = TASK_ROLE_AFFINITY.get(task_type)

    if compatible_roles is None:
        return 0.5

    if role in compatible_roles:
        return 1.0

    if role == "team_lead":
        return 0.75

    return 0.25


def _candidate_reasons(
    skill_score: float,
    workload_score: float,
    growth_score: float,
    speed_score: float,
    quality_score: float,
    reliability_score: float,
    role_affinity: float,
) -> list[str]:
    reasons = [
        f"skill_match={skill_score:.2f}",
        f"workload_score={workload_score:.2f}",
        f"quality={quality_score:.2f}",
        f"deadline_reliability={reliability_score:.2f}",
    ]

    if role_affinity >= 0.9:
        reasons.append("role matches task type")

    if growth_score >= 0.5:
        reasons.append("supports growth goals")

    if speed_score >= 0.8:
        reasons.append("strong delivery speed")

    return reasons


def _candidate_risks(
    skill_missing: list[str],
    workload_risk_level: str,
    growth_risks: list[str],
    role_affinity: float,
) -> list[str]:
    risks: list[str] = []

    if skill_missing:
        risks.append(f"missing skills: {', '.join(skill_missing[:3])}")

    if workload_risk_level in {"high", "critical"}:
        risks.append(f"{workload_risk_level} workload risk")

    if role_affinity < 0.5:
        risks.append("role mismatch")

    risks.extend(growth_risks)

    return risks


def score_employee_for_task(
    task: dict[str, Any],
    employee: dict[str, Any],
    *,
    mode: RecommendationMode = "balanced_workload",
    mentor_available: bool = False,
) -> RuleBasedCandidate:
    normalized_mode = _normalize_mode(mode)
    weights = MODE_WEIGHTS[normalized_mode]

    skill_result = calculate_skill_match(task, employee)
    workload_result = calculate_workload_score(employee)
    growth_result = calculate_growth_score(task, employee, mentor_available=mentor_available)

    speed_score = max(0.0, min(1.0, _safe_float(employee.get("avg_completion_speed"), 0.5)))
    quality_score = max(0.0, min(1.0, _safe_float(employee.get("avg_quality_score"), 0.5)))
    reliability_score = max(0.0, min(1.0, _safe_float(employee.get("deadline_reliability"), 0.5)))
    role_affinity = role_affinity_score(task, employee)

    weighted_score = (
        weights["skill"] * skill_result.score
        + weights["workload"] * workload_result.score
        + weights["growth"] * growth_result.score
        + weights["speed"] * speed_score
        + weights["quality"] * quality_score
        + weights["reliability"] * reliability_score
    )

    final_score = weighted_score * (0.85 + 0.15 * role_affinity)
    final_score = max(0.0, min(1.0, final_score))

    reasons = _candidate_reasons(
        skill_score=skill_result.score,
        workload_score=workload_result.score,
        growth_score=growth_result.score,
        speed_score=speed_score,
        quality_score=quality_score,
        reliability_score=reliability_score,
        role_affinity=role_affinity,
    )

    risks = _candidate_risks(
        skill_missing=skill_result.missing_skills,
        workload_risk_level=workload_result.risk_level,
        growth_risks=growth_result.risks,
        role_affinity=role_affinity,
    )

    return RuleBasedCandidate(
        rank=0,
        employee_id=str(employee.get("employee_id", "")),
        plane_user_id=_nullable_string(employee.get("plane_user_id")),
        name=str(employee.get("name", "")),
        role=str(employee.get("role", "")),
        grade=str(employee.get("grade", "")),
        score=round(final_score, 4),
        reasons=reasons,
        risks=risks,
        factors={
            "skill_match": skill_result.score,
            "role_affinity": round(role_affinity, 4),
            "workload_score": workload_result.score,
            "workload": workload_result.workload,
            "growth_match": growth_result.score,
            "speed": round(speed_score, 4),
            "quality": round(quality_score, 4),
            "deadline_reliability": round(reliability_score, 4),
        },
    )


def rank_employees_for_task(
    task: dict[str, Any] | pd.Series,
    employees: list[dict[str, Any]] | pd.DataFrame,
    *,
    mode: RecommendationMode = "balanced_workload",
    top_k: int = 3,
    mentor_available: bool = False,
) -> RuleBasedRecommendation:
    task_dict = _row_to_dict(task)

    if isinstance(employees, pd.DataFrame):
        employee_records = employees.to_dict(orient="records")
    else:
        employee_records = employees

    scored_candidates = [
        score_employee_for_task(
            task_dict,
            employee,
            mode=mode,
            mentor_available=mentor_available,
        )
        for employee in employee_records
    ]

    ranked_candidates = sorted(
        scored_candidates,
        key=lambda candidate: candidate.score,
        reverse=True,
    )

    top_candidates = [
        RuleBasedCandidate(
            rank=index,
            employee_id=candidate.employee_id,
            plane_user_id=candidate.plane_user_id,
            name=candidate.name,
            role=candidate.role,
            grade=candidate.grade,
            score=candidate.score,
            reasons=candidate.reasons,
            risks=candidate.risks,
            factors=candidate.factors,
        )
        for index, candidate in enumerate(ranked_candidates[:top_k], start=1)
    ]

    return RuleBasedRecommendation(
        task_id=str(task_dict.get("task_id", "")),
        plane_work_item_id=_nullable_string(task_dict.get("plane_work_item_id")),
        plane_issue_id=_nullable_string(task_dict.get("plane_issue_id")),
        title=str(task_dict.get("title", "")),
        mode=mode,
        candidates=top_candidates,
        source="rule_based_baseline",
        explanation=(
            "Rule-based baseline combines skill match, workload, growth fit, speed, "
            "quality and deadline reliability. The neural network is not used here."
        ),
    )


def load_synthetic_data(
    employees_path: Path = DEFAULT_EMPLOYEES_PATH,
    tasks_path: Path = DEFAULT_TASKS_PATH,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    employees = pd.read_csv(employees_path)
    tasks = pd.read_csv(tasks_path)
    return employees, tasks


def recommend_for_synthetic_task(
    *,
    task_id: str | None = None,
    mode: RecommendationMode = "balanced_workload",
    top_k: int = 3,
) -> RuleBasedRecommendation:
    employees, tasks = load_synthetic_data()

    if task_id:
        matched_tasks = tasks[tasks["task_id"] == task_id]
        if matched_tasks.empty:
            raise ValueError(f"Task not found: {task_id}")

        task = matched_tasks.iloc[0]
    else:
        task = tasks.iloc[0]

    return rank_employees_for_task(task, employees, mode=mode, top_k=top_k)


def recommendation_to_dict(recommendation: RuleBasedRecommendation) -> dict[str, Any]:
    return {
        "task_id": recommendation.task_id,
        "plane_work_item_id": recommendation.plane_work_item_id,
        "plane_issue_id": recommendation.plane_issue_id,
        "title": recommendation.title,
        "mode": recommendation.mode,
        "candidates": [asdict(candidate) for candidate in recommendation.candidates],
        "source": recommendation.source,
        "explanation": recommendation.explanation,
    }


if __name__ == "__main__":
    recommendation = recommend_for_synthetic_task()
    print(json.dumps(recommendation_to_dict(recommendation), ensure_ascii=False, indent=2))