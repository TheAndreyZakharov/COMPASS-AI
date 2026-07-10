from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sandbox_app.backend.inference.scoring import clamp, to_float

ASSIGNMENT_MODES = {
    "balanced": {
        "label": "Balanced",
        "description": "Балансирует качество, скорость, обучение, риски и fairness.",
    },
    "best_quality": {
        "label": "Best quality",
        "description": "Сильнее оптимизирует качество и skill match.",
    },
    "fastest_delivery": {
        "label": "Fastest delivery",
        "description": "Сильнее оптимизирует скорость и доступность.",
    },
    "best_learning": {
        "label": "Best learning",
        "description": "Сильнее учитывает learning goals и рост команды.",
    },
    "risk_aware": {
        "label": "Risk aware",
        "description": "Сильнее штрафует перегрузку, усталость и дедлайны.",
    },
}


@dataclass(frozen=True)
class OptimizerWeights:
    fairness_penalty: float = 0.12
    fatigue_penalty: float = 0.12
    learning_bonus: float = 0.08
    workload_penalty: float = 0.18


def validate_assignment_mode(mode: str) -> None:
    if mode not in ASSIGNMENT_MODES:
        allowed = ", ".join(sorted(ASSIGNMENT_MODES))
        raise ValueError(f"Unknown assignment_mode: {mode}. Allowed: {allowed}")


def projected_task_load(task: dict[str, Any]) -> float:
    estimated_hours = to_float(task.get("estimated_hours"), 8.0)
    return clamp(estimated_hours / 40.0, 0.02, 0.6)


def initial_workload_state(team: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    state: dict[str, dict[str, Any]] = {}

    for employee in team:
        employee_id = str(employee.get("employee_id", ""))
        state[employee_id] = {
            "employee_id": employee_id,
            "name": employee.get("name", ""),
            "role": employee.get("role", ""),
            "grade": employee.get("grade", ""),
            "initial_workload": to_float(employee.get("current_workload")),
            "projected_workload": to_float(employee.get("current_workload")),
            "fatigue_score": to_float(employee.get("fatigue_score")),
            "availability_score": to_float(employee.get("availability_score")),
            "assigned_tasks_count": 0,
            "assigned_estimated_hours": 0.0,
            "assigned_task_ids": [],
        }

    return state


def employee_with_projected_workload(
    employee: dict[str, Any],
    state: dict[str, Any],
) -> dict[str, Any]:
    updated = dict(employee)
    updated["current_workload"] = state["projected_workload"]
    return updated


def task_mode_bonus(candidate: dict[str, Any], assignment_mode: str) -> float:
    factors = candidate.get("factors", {})

    quality = to_float(factors.get("quality_fit_score"))
    speed = to_float(factors.get("speed_fit_score"))
    learning = to_float(factors.get("learning_fit_score"))
    risk_fit = to_float(factors.get("risk_fit_score"))
    skill = to_float(factors.get("skill_match_ratio"))

    if assignment_mode == "best_quality":
        return quality * 0.12 + skill * 0.08

    if assignment_mode == "fastest_delivery":
        return speed * 0.14 + risk_fit * 0.04

    if assignment_mode == "best_learning":
        return learning * 0.16 + quality * 0.04

    if assignment_mode == "risk_aware":
        return risk_fit * 0.16

    return quality * 0.05 + speed * 0.04 + learning * 0.03 + risk_fit * 0.04


def fairness_pressure(
    employee_state: dict[str, Any],
    workload_state: dict[str, dict[str, Any]],
) -> float:
    assigned_counts = [
        int(item["assigned_tasks_count"])
        for item in workload_state.values()
    ]

    if not assigned_counts:
        return 0.0

    max_assigned = max(assigned_counts) or 1
    current_assigned = int(employee_state["assigned_tasks_count"])

    return clamp(current_assigned / max(max_assigned, 1))


def optimized_score(
    candidate: dict[str, Any],
    employee_state: dict[str, Any],
    workload_state: dict[str, dict[str, Any]],
    assignment_mode: str,
    weights: OptimizerWeights,
) -> dict[str, Any]:
    base_score = to_float(candidate.get("score"))
    projected_workload = to_float(employee_state.get("projected_workload"))
    fatigue_score = to_float(employee_state.get("fatigue_score"))
    learning_score = to_float(candidate.get("factors", {}).get("learning_fit_score"))
    fairness_score = fairness_pressure(employee_state, workload_state)

    workload_penalty_value = projected_workload * weights.workload_penalty
    fatigue_penalty_value = fatigue_score * weights.fatigue_penalty
    fairness_penalty_value = fairness_score * weights.fairness_penalty
    learning_bonus_value = learning_score * weights.learning_bonus
    mode_bonus_value = task_mode_bonus(candidate, assignment_mode)

    final_score = clamp(
        base_score
        + mode_bonus_value
        + learning_bonus_value
        - workload_penalty_value
        - fatigue_penalty_value
        - fairness_penalty_value
    )

    return {
        "final_score": final_score,
        "base_score": base_score,
        "mode_bonus": round(mode_bonus_value, 6),
        "learning_bonus": round(learning_bonus_value, 6),
        "workload_penalty": round(workload_penalty_value, 6),
        "fatigue_penalty": round(fatigue_penalty_value, 6),
        "fairness_penalty": round(fairness_penalty_value, 6),
        "projected_workload": projected_workload,
        "fairness_pressure": fairness_score,
    }


def can_assign(
    employee_state: dict[str, Any],
    task: dict[str, Any],
    max_workload_per_person: float,
) -> bool:
    next_workload = to_float(employee_state["projected_workload"]) + projected_task_load(task)
    return next_workload <= max_workload_per_person


def choose_candidate(
    task: dict[str, Any],
    candidates: list[dict[str, Any]],
    workload_state: dict[str, dict[str, Any]],
    assignment_mode: str,
    weights: OptimizerWeights,
    max_workload_per_person: float,
) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    ranked: list[dict[str, Any]] = []

    for candidate in candidates:
        employee_id = str(candidate.get("employee_id", ""))
        employee_state = workload_state.get(employee_id)

        if employee_state is None:
            continue

        score_details = optimized_score(
            candidate=candidate,
            employee_state=employee_state,
            workload_state=workload_state,
            assignment_mode=assignment_mode,
            weights=weights,
        )
        next_workload = (
            to_float(employee_state["projected_workload"])
            + projected_task_load(task)
        )
        assignable = next_workload <= max_workload_per_person

        enriched = dict(candidate)
        enriched["assignment_score"] = score_details["final_score"]
        score_details["max_workload_per_person"] = max_workload_per_person
        score_details["next_projected_workload"] = round(next_workload, 6)
        score_details["workload_over_limit"] = round(
            max(0.0, next_workload - max_workload_per_person),
            6,
        )
        enriched["assignment_score_details"] = score_details
        enriched["assignable"] = assignable
        enriched["capacity_status"] = (
            "within_soft_limit"
            if assignable
            else "planned_queue_over_soft_limit"
        )
        enriched["workload_before_assignment"] = round(
            to_float(employee_state["projected_workload"]),
            6,
        )
        enriched["workload_after_assignment"] = round(next_workload, 6)
        enriched["workload_over_limit"] = score_details["workload_over_limit"]
        ranked.append(enriched)

    ranked.sort(
        key=lambda item: (
            not bool(item["assignable"]),
            -to_float(item.get("assignment_score")),
            to_float(item.get("risk_summary", {}).get("max_risk_score")),
            str(item.get("employee_id", "")),
        )
    )

    for candidate in ranked:
        if candidate["assignable"]:
            return candidate, ranked

    if ranked:
        return ranked[0], ranked

    return None, ranked


def apply_assignment(
    employee_state: dict[str, Any],
    task: dict[str, Any],
) -> dict[str, Any]:
    task_load = projected_task_load(task)
    estimated_hours = to_float(task.get("estimated_hours"), 8.0)

    employee_state["assigned_tasks_count"] = int(employee_state["assigned_tasks_count"]) + 1
    employee_state["assigned_estimated_hours"] = round(
        to_float(employee_state["assigned_estimated_hours"]) + estimated_hours,
        4,
    )
    employee_state["projected_workload"] = clamp(
        to_float(employee_state["projected_workload"]) + task_load
    )
    employee_state["assigned_task_ids"].append(task.get("task_id"))

    return employee_state


def workload_after_assignment(
    workload_state: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    rows = []

    for item in workload_state.values():
        rows.append(
            {
                "employee_id": item["employee_id"],
                "name": item["name"],
                "role": item["role"],
                "grade": item["grade"],
                "initial_workload": item["initial_workload"],
                "projected_workload": item["projected_workload"],
                "workload_delta": round(
                    to_float(item["projected_workload"])
                    - to_float(item["initial_workload"]),
                    6,
                ),
                "fatigue_score": item["fatigue_score"],
                "availability_score": item["availability_score"],
                "assigned_tasks_count": item["assigned_tasks_count"],
                "assigned_estimated_hours": item["assigned_estimated_hours"],
                "assigned_task_ids": item["assigned_task_ids"],
            }
        )

    return sorted(
        rows,
        key=lambda row: (
            -int(row["assigned_tasks_count"]),
            -to_float(row["projected_workload"]),
            str(row["employee_id"]),
        ),
    )


def fairness_report(workload_rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not workload_rows:
        return {
            "people": 0,
            "assigned_tasks_total": 0,
            "max_assigned_tasks": 0,
            "min_assigned_tasks": 0,
            "assignment_spread": 0,
            "avg_projected_workload": 0.0,
            "max_projected_workload": 0.0,
            "overloaded_people": 0,
        }

    assigned_counts = [int(row["assigned_tasks_count"]) for row in workload_rows]
    workloads = [to_float(row["projected_workload"]) for row in workload_rows]

    return {
        "people": len(workload_rows),
        "assigned_tasks_total": sum(assigned_counts),
        "max_assigned_tasks": max(assigned_counts),
        "min_assigned_tasks": min(assigned_counts),
        "assignment_spread": max(assigned_counts) - min(assigned_counts),
        "avg_projected_workload": round(sum(workloads) / len(workloads), 6),
        "max_projected_workload": max(workloads),
        "overloaded_people": sum(value >= 0.9 for value in workloads),
        "people_without_new_tasks": sum(value == 0 for value in assigned_counts),
    }
