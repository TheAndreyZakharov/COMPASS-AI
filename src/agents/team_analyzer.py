from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from src.agents.state import AgentState

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EMPLOYEES_PATH = PROJECT_ROOT / "data" / "synthetic" / "employees.csv"


def parse_json_cell(value: Any, default: Any) -> Any:
    if value is None:
        return default

    if isinstance(value, float):
        return default

    if isinstance(value, str):
        value = value.strip()

        if not value:
            return default

        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return default

    return value


def load_employee_profiles(path: Path = EMPLOYEES_PATH) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(
            f"Missing employees file: {path}. "
            "Run: python scripts/generate_synthetic_data.py"
        )

    employees = pd.read_csv(path)
    result: list[dict[str, Any]] = []

    for _, row in employees.iterrows():
        employee = row.to_dict()
        employee["skills"] = parse_json_cell(employee.get("skills"), {})
        employee["learning_goals"] = parse_json_cell(employee.get("learning_goals"), [])
        employee["current_workload"] = float(employee.get("current_workload", 0.0))
        employee["active_tasks_count"] = int(employee.get("active_tasks_count", 0))
        employee["avg_completion_speed"] = float(employee.get("avg_completion_speed", 0.0))
        employee["avg_quality_score"] = float(employee.get("avg_quality_score", 0.0))
        employee["deadline_reliability"] = float(employee.get("deadline_reliability", 0.0))
        employee["mentor_level"] = int(employee.get("mentor_level", 0))
        result.append(employee)

    return result


def availability_score(employee: dict[str, Any]) -> float:
    availability = str(employee.get("availability", "available")).lower()
    workload = float(employee.get("current_workload", 0.0))

    if availability == "unavailable":
        return 0.0

    if availability == "partially_available":
        return max(0.0, 0.6 - workload * 0.25)

    return max(0.0, 1.0 - workload)


def workload_risk(employee: dict[str, Any]) -> str:
    workload = float(employee.get("current_workload", 0.0))

    if workload >= 0.95:
        return "critical"

    if workload >= 0.85:
        return "high"

    if workload >= 0.70:
        return "medium"

    return "low"


def build_employee_features(employee: dict[str, Any]) -> dict[str, Any]:
    return {
        "employee_id": str(employee.get("employee_id", "")),
        "plane_user_id": str(employee.get("plane_user_id", "") or ""),
        "name": str(employee.get("name", "")),
        "role": str(employee.get("role", "")),
        "grade": str(employee.get("grade", "")),
        "skills": employee.get("skills", {}),
        "learning_goals": employee.get("learning_goals", []),
        "current_workload": float(employee.get("current_workload", 0.0)),
        "active_tasks_count": int(employee.get("active_tasks_count", 0)),
        "availability": str(employee.get("availability", "available")),
        "availability_score": round(availability_score(employee), 6),
        "workload_risk": workload_risk(employee),
        "avg_completion_speed": float(employee.get("avg_completion_speed", 0.0)),
        "avg_quality_score": float(employee.get("avg_quality_score", 0.0)),
        "deadline_reliability": float(employee.get("deadline_reliability", 0.0)),
        "mentor_level": int(employee.get("mentor_level", 0)),
    }


def run_team_analyzer(state: AgentState) -> AgentState:
    try:
        employees = load_employee_profiles()
        state.employees = employees
        state.employee_features = [
            build_employee_features(employee)
            for employee in employees
        ]
    except Exception as error:
        state.add_error("team_analyzer", str(error))

    return state