from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any

DEADLINE_STATUSES = ("early", "on_time", "late", "missed")
OUTCOME_LABELS = ("success", "good", "acceptable", "late", "failed", "rework")

GRADE_SCORE = {
    "junior": 0.38,
    "middle": 0.58,
    "senior": 0.78,
    "lead": 0.92,
    "principal": 0.96,
}


@dataclass(frozen=True)
class OutcomeConfig:
    good_outcome_share: float = 0.58
    bad_outcome_share: float = 0.18
    late_outcome_share: float = 0.16
    failed_outcome_share: float = 0.08
    rework_probability: float = 0.12
    overload_penalty_strength: float = 0.28
    fatigue_penalty_strength: float = 0.24
    skill_match_bonus_strength: float = 0.34
    learning_task_share: float = 0.16


def clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def normalize_complexity(task: dict[str, Any]) -> float:
    return clamp((float(task.get("complexity", 5.0)) - 1.0) / 9.0)


def skill_match_score(employee: dict[str, Any], task: dict[str, Any]) -> float:
    employee_skills = {str(item).lower() for item in employee.get("skills", [])}
    required_skills = {str(item).lower() for item in task.get("required_skills", [])}

    if not required_skills:
        return 1.0

    return len(employee_skills & required_skills) / len(required_skills)


def learning_match_score(employee: dict[str, Any], task: dict[str, Any]) -> float:
    learning_goals = {str(item).lower() for item in employee.get("learning_goals", [])}
    required_skills = {str(item).lower() for item in task.get("required_skills", [])}

    if not learning_goals or not required_skills:
        return 0.0

    return len(learning_goals & required_skills) / len(required_skills)


def choose_outcome_scenario(rng: random.Random, config: OutcomeConfig) -> str:
    weights = {
        "good": config.good_outcome_share,
        "bad": config.bad_outcome_share,
        "late": config.late_outcome_share,
        "failed": config.failed_outcome_share,
    }

    total = sum(max(0.0, value) for value in weights.values())
    if total <= 0:
        weights = {"good": 0.58, "bad": 0.18, "late": 0.16, "failed": 0.08}
        total = sum(weights.values())

    threshold = rng.random() * total
    cumulative = 0.0

    for scenario, weight in weights.items():
        cumulative += max(0.0, weight)
        if threshold <= cumulative:
            return scenario

    return "good"


def estimate_planned_hours(task: dict[str, Any], rng: random.Random) -> float:
    estimated_hours = float(task.get("estimated_hours", 8.0))
    noise = rng.uniform(0.88, 1.12)
    return round(max(0.5, estimated_hours * noise), 2)


def estimate_actual_hours(
    planned_hours: float,
    quality_score: float,
    deadline_risk: float,
    scenario: str,
    rng: random.Random,
) -> float:
    multiplier = 1.0

    if scenario == "good":
        multiplier *= rng.uniform(0.78, 1.08)
    elif scenario == "late":
        multiplier *= rng.uniform(1.15, 1.8)
    elif scenario == "failed":
        multiplier *= rng.uniform(1.25, 2.2)
    else:
        multiplier *= rng.uniform(0.95, 1.55)

    multiplier += deadline_risk * rng.uniform(0.15, 0.55)
    multiplier += (1.0 - quality_score) * rng.uniform(0.05, 0.35)

    return round(max(0.5, planned_hours * multiplier), 2)


def choose_deadline_status(
    planned_hours: float,
    actual_hours: float,
    deadline_risk: float,
    scenario: str,
    rng: random.Random,
) -> str:
    ratio = actual_hours / max(planned_hours, 0.5)

    if scenario == "failed" and rng.random() < 0.55:
        return "missed"

    if scenario == "late" or ratio > 1.45 or deadline_risk > 0.78:
        return "late" if rng.random() > 0.22 else "missed"

    if ratio < 0.82 and deadline_risk < 0.45:
        return "early"

    return "on_time"


def choose_outcome_label(
    quality_score: float,
    deadline_status: str,
    was_rework_needed: bool,
    scenario: str,
) -> str:
    if scenario == "failed" or quality_score < 0.24:
        return "failed"

    if was_rework_needed:
        return "rework"

    if deadline_status in {"late", "missed"}:
        return "late"

    if quality_score >= 0.86:
        return "success"

    if quality_score >= 0.68:
        return "good"

    return "acceptable"


def outcome_quality_score(
    employee: dict[str, Any],
    task: dict[str, Any],
    config: OutcomeConfig,
    scenario: str,
    rng: random.Random,
) -> float:
    skill_score = skill_match_score(employee, task)
    learning_score = learning_match_score(employee, task)
    workload = clamp(
        float(employee.get("current_workload", employee.get("workload_current", 0.45)))
    )
    fatigue = clamp(float(employee.get("fatigue_score", 0.35)))
    complexity = normalize_complexity(task)
    grade = str(employee.get("grade", "middle")).lower()
    grade_score = GRADE_SCORE.get(grade, 0.58)

    base = 0.42
    base += skill_score * config.skill_match_bonus_strength
    base += learning_score * 0.08
    base += grade_score * 0.13
    base -= workload * config.overload_penalty_strength
    base -= fatigue * config.fatigue_penalty_strength
    base -= complexity * 0.17

    if scenario == "good":
        base += rng.uniform(0.04, 0.18)
    elif scenario == "bad":
        base -= rng.uniform(0.14, 0.34)
    elif scenario == "late":
        base -= rng.uniform(0.04, 0.18)
    elif scenario == "failed":
        base -= rng.uniform(0.32, 0.58)

    base += rng.uniform(-0.08, 0.08)

    return round(clamp(base), 3)


def deadline_risk_score(
    employee: dict[str, Any],
    task: dict[str, Any],
    config: OutcomeConfig,
) -> float:
    workload = float(
        employee.get(
            "current_workload",
            employee.get("workload_current", 0.45),
        )
    )
    workload = clamp(workload)
    fatigue = clamp(float(employee.get("fatigue_score", 0.35)))
    reliability = clamp(float(employee.get("deadline_reliability", 0.65)))
    complexity = normalize_complexity(task)
    skill_gap = 1.0 - skill_match_score(employee, task)

    risk = 0.18
    risk += workload * config.overload_penalty_strength
    risk += fatigue * config.fatigue_penalty_strength
    risk += complexity * 0.2
    risk += skill_gap * 0.18
    risk -= reliability * 0.22

    return round(clamp(risk), 3)


def was_learning_task(
    employee: dict[str, Any],
    task: dict[str, Any],
    config: OutcomeConfig,
    rng: random.Random,
) -> bool:
    match = learning_match_score(employee, task)
    return match > 0 and rng.random() < config.learning_task_share


def build_outcome(
    employee: dict[str, Any],
    task: dict[str, Any],
    config: OutcomeConfig,
    rng: random.Random,
) -> dict[str, Any]:
    scenario = choose_outcome_scenario(rng, config)
    quality_score = outcome_quality_score(employee, task, config, scenario, rng)
    deadline_risk = deadline_risk_score(employee, task, config)

    planned_hours = estimate_planned_hours(task, rng)
    actual_hours = estimate_actual_hours(planned_hours, quality_score, deadline_risk, scenario, rng)

    deadline_status = choose_deadline_status(
        planned_hours=planned_hours,
        actual_hours=actual_hours,
        deadline_risk=deadline_risk,
        scenario=scenario,
        rng=rng,
    )

    rework_base = config.rework_probability
    rework_base += (1.0 - quality_score) * 0.28
    rework_base += (1.0 - skill_match_score(employee, task)) * 0.12
    was_rework_needed = rng.random() < clamp(rework_base, 0.0, 0.85)

    outcome_label = choose_outcome_label(
        quality_score=quality_score,
        deadline_status=deadline_status,
        was_rework_needed=was_rework_needed,
        scenario=scenario,
    )

    feedback_score = quality_score
    if deadline_status in {"late", "missed"}:
        feedback_score -= 0.12
    if was_rework_needed:
        feedback_score -= 0.16
    if outcome_label == "failed":
        feedback_score -= 0.18

    return {
        "planned_hours": planned_hours,
        "actual_hours": actual_hours,
        "quality_score": quality_score,
        "deadline_status": deadline_status,
        "outcome_label": outcome_label,
        "was_rework_needed": bool(was_rework_needed),
        "feedback_score": round(clamp(feedback_score), 3),
        "skill_match_score": round(skill_match_score(employee, task), 3),
        "overload_score_at_assignment": round(
            clamp(
                float(
                    employee.get(
                        "current_workload",
                        employee.get("workload_current", 0.45),
                    )
                )
            ),
            3,
        ),
        "fatigue_score_at_assignment": round(clamp(float(employee.get("fatigue_score", 0.35))), 3),
        "deadline_risk_score": deadline_risk,
        "learning_task": was_learning_task(employee, task, config, rng),
        "scenario": scenario,
    }