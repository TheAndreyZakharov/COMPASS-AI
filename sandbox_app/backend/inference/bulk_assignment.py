from __future__ import annotations

import csv
import html
import json
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd
from sandbox_app.backend.core.time import moscow_now_iso, moscow_stamp
from sandbox_app.backend.data_generation.test_team import TestTeamError, load_test_case
from sandbox_app.backend.inference.assignment_optimizer import (
    ASSIGNMENT_MODES,
    OptimizerWeights,
    apply_assignment,
    choose_candidate,
    employee_with_projected_workload,
    fairness_report,
    initial_workload_state,
    validate_assignment_mode,
    workload_after_assignment,
)
from sandbox_app.backend.inference.model_loader import ModelLoadError, load_sandbox_model
from sandbox_app.backend.inference.recommend import candidate_result, predict_scores
from sandbox_app.backend.inference.scoring import build_pair_feature_frame, to_float

SANDBOX_DIR = Path(__file__).resolve().parents[2]
ASSIGNMENT_SESSIONS_DIR = SANDBOX_DIR / "assignment_sessions"
ASSIGNMENT_READY_STATUSES = {"todo", "in_progress", "review", "blocked"}


class BulkAssignmentError(ValueError):
    """Raised when bulk assignment simulation fails."""


@dataclass(frozen=True)
class BulkAssignmentConfig:
    session_id: str
    model_name: str
    test_case_id: str
    assignment_mode: str = "balanced"
    recommendation_mode: str = "balanced"
    top_k: int = 3
    max_workload_per_person: float = 0.95
    fairness_penalty: float = 0.12
    fatigue_penalty: float = 0.12
    learning_bonus: float = 0.08
    workload_penalty: float = 0.18
    task_statuses: list[str] = field(default_factory=lambda: ["todo"])
    save_session: bool = True


def utc_now_iso() -> str:
    return moscow_now_iso()


def make_assignment_session_id() -> str:
    stamp = moscow_stamp()
    return f"assignment_{stamp}_{uuid.uuid4().hex[:8]}"


def validate_config(config: BulkAssignmentConfig) -> None:
    validate_assignment_mode(config.assignment_mode)
    validate_assignment_mode(config.recommendation_mode)

    if not config.session_id:
        raise BulkAssignmentError("session_id is required")

    if not config.model_name:
        raise BulkAssignmentError("model_name is required")

    if not config.test_case_id:
        raise BulkAssignmentError("test_case_id is required")

    if config.top_k < 1 or config.top_k > 100:
        raise BulkAssignmentError("top_k must be between 1 and 100")

    if config.max_workload_per_person <= 0.0 or config.max_workload_per_person > 1.5:
        raise BulkAssignmentError("max_workload_per_person must be in range (0, 1.5]")

    if config.fairness_penalty < 0.0:
        raise BulkAssignmentError("fairness_penalty must be non-negative")

    if config.fatigue_penalty < 0.0:
        raise BulkAssignmentError("fatigue_penalty must be non-negative")

    if config.learning_bonus < 0.0:
        raise BulkAssignmentError("learning_bonus must be non-negative")

    if config.workload_penalty < 0.0:
        raise BulkAssignmentError("workload_penalty must be non-negative")


def assignment_tasks(test_case: dict[str, Any], statuses: list[str]) -> list[dict[str, Any]]:
    active_tasks = list(test_case.get("active_tasks") or [])
    requested_statuses = set(statuses or ["todo"])

    todo_tasks = [
        task
        for task in active_tasks
        if str(task.get("status", "")).lower() in requested_statuses
    ]

    if todo_tasks:
        return todo_tasks

    return [
        task
        for task in active_tasks
        if str(task.get("status", "")).lower() in ASSIGNMENT_READY_STATUSES
    ]


def task_priority_sort_key(task: dict[str, Any]) -> tuple[float, float, str]:
    priority_weights = {
        "critical": 4.0,
        "high": 3.0,
        "medium": 2.0,
        "low": 1.0,
    }

    priority = str(task.get("priority", "")).lower()
    complexity = to_float(task.get("complexity"), 0.5)

    return (
        -priority_weights.get(priority, 2.0),
        -complexity,
        str(task.get("task_id", "")),
    )


def predict_task_candidates(
    model: Any,
    task: dict[str, Any],
    team: list[dict[str, Any]],
    recommendation_mode: str,
) -> list[dict[str, Any]]:
    feature_frame = build_pair_feature_frame(
        task=task,
        employees=team,
        recommendation_mode=recommendation_mode,
    )
    scores = predict_scores(model, feature_frame)

    if len(scores) != len(team):
        raise BulkAssignmentError("Model returned unexpected number of scores")

    rows = feature_frame.to_dict(orient="records")
    candidates = [
        candidate_result(
            task=task,
            employee=employee,
            row=row,
            model_score=score,
            mode=recommendation_mode,
        )
        for employee, row, score in zip(team, rows, scores, strict=True)
    ]
    candidates.sort(
        key=lambda item: (
            -to_float(item.get("score")),
            to_float(item.get("risk_summary", {}).get("max_risk_score")),
            str(item.get("employee_id", "")),
        )
    )

    return candidates


def current_projected_team(
    original_team: list[dict[str, Any]],
    workload_state: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    projected: list[dict[str, Any]] = []

    for employee in original_team:
        employee_id = str(employee.get("employee_id", ""))
        state = workload_state.get(employee_id)

        if state is None:
            continue

        projected.append(employee_with_projected_workload(employee, state))

    return projected


def assigned_row(
    task: dict[str, Any],
    candidate: dict[str, Any],
    ranked_candidates: list[dict[str, Any]],
    employee_task_number: int,
) -> dict[str, Any]:
    score_details = candidate.get("assignment_score_details") or {}

    return {
        "task_id": task.get("task_id"),
        "task_title": task.get("title"),
        "project_id": task.get("project_id"),
        "priority": task.get("priority"),
        "status": task.get("status"),
        "task_type": task.get("task_type"),
        "complexity": task.get("complexity"),
        "estimated_hours": task.get("estimated_hours"),
        "required_skills": task.get("required_skills", []),
        "assigned_employee_id": candidate.get("employee_id"),
        "assigned_employee_name": candidate.get("name"),
        "assigned_employee_role": candidate.get("role"),
        "employee_task_number": employee_task_number,
        "capacity_status": candidate.get("capacity_status"),
        "over_soft_limit": not bool(candidate.get("assignable", False)),
        "workload_before_assignment": candidate.get("workload_before_assignment"),
        "workload_after_assignment": candidate.get("workload_after_assignment"),
        "workload_over_limit": score_details.get("workload_over_limit", 0.0),
        "max_workload_per_person": score_details.get("max_workload_per_person"),
        "assignment_score": candidate.get("assignment_score"),
        "model_score": candidate.get("model_score"),
        "top_candidates": ranked_candidates[:3],
        "score_details": score_details,
        "risks": candidate.get("risks"),
    }


def unassigned_row(
    task: dict[str, Any],
    reason: str,
    ranked_candidates: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "task_id": task.get("task_id"),
        "task_title": task.get("title"),
        "project_id": task.get("project_id"),
        "priority": task.get("priority"),
        "status": task.get("status"),
        "task_type": task.get("task_type"),
        "complexity": task.get("complexity"),
        "estimated_hours": task.get("estimated_hours"),
        "required_skills": task.get("required_skills", []),
        "reason": reason,
        "top_candidates": ranked_candidates[:3],
    }


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BulkAssignmentError(f"Could not read JSON file: {path}") from exc


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    if not rows:
        path.write_text("", encoding="utf-8")
        return

    normalized = []

    for row in rows:
        normalized.append(
            {
                key: json.dumps(value, ensure_ascii=False)
                if isinstance(value, list | dict)
                else value
                for key, value in row.items()
            }
        )

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(normalized[0].keys()))
        writer.writeheader()
        writer.writerows(normalized)


def assignment_report_html(payload: dict[str, Any]) -> str:
    summary = payload.get("summary", {})
    assigned = payload.get("assigned_tasks", [])
    unassigned = payload.get("unassigned_tasks", [])

    assigned_rows = "\n".join(
        "<tr>"
        f"<td>{html.escape(str(row.get('task_id', '')))}</td>"
        f"<td>{html.escape(str(row.get('task_title', '')))}</td>"
        f"<td>{html.escape(str(row.get('assigned_employee_name', '')))}</td>"
        f"<td>{html.escape(str(row.get('employee_task_number', '')))}</td>"
        f"<td>{html.escape(str(row.get('capacity_status', '')))}</td>"
        f"<td>{html.escape(str(row.get('assignment_score', '')))}</td>"
        "</tr>"
        for row in assigned[:100]
    )
    unassigned_rows = "\n".join(
        "<tr>"
        f"<td>{html.escape(str(row.get('task_id', '')))}</td>"
        f"<td>{html.escape(str(row.get('task_title', '')))}</td>"
        f"<td>{html.escape(str(row.get('reason', '')))}</td>"
        "</tr>"
        for row in unassigned[:100]
    )

    return f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <title>Assignment Report</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      margin: 32px;
      color: #111827;
    }}
    table {{
      border-collapse: collapse;
      width: 100%;
      margin: 16px 0 32px;
    }}
    th, td {{
      border: 1px solid #e5e7eb;
      padding: 8px;
      text-align: left;
      vertical-align: top;
    }}
    th {{
      background: #f9fafb;
    }}
    pre {{
      background: #f9fafb;
      padding: 16px;
      overflow: auto;
    }}
  </style>
</head>
<body>
  <h1>Bulk Assignment Report</h1>
  <pre>{html.escape(json.dumps(summary, ensure_ascii=False, indent=2))}</pre>

  <h2>Assigned tasks</h2>
  <table>
    <thead>
      <tr>
        <th>Task</th>
        <th>Title</th>
        <th>Employee</th>
        <th>Employee queue #</th>
        <th>Capacity status</th>
        <th>Score</th>
      </tr>
    </thead>
    <tbody>{assigned_rows}</tbody>
  </table>

  <h2>Unassigned tasks</h2>
  <table>
    <thead>
      <tr>
        <th>Task</th>
        <th>Title</th>
        <th>Reason</th>
      </tr>
    </thead>
    <tbody>{unassigned_rows}</tbody>
  </table>
</body>
</html>
"""


def save_assignment_session(payload: dict[str, Any]) -> dict[str, Any]:
    session_id = str(payload["assignment_session_id"])
    session_dir = ASSIGNMENT_SESSIONS_DIR / session_id
    assigned_tasks = payload["assigned_tasks"]
    unassigned_tasks = payload["unassigned_tasks"]
    workload_rows = payload["workload_after_assignment"]
    report = payload["fairness_report"]

    session_dir.mkdir(parents=True, exist_ok=True)

    paths = {
        "assignment_config": session_dir / "assignment_config.json",
        "recommendations": session_dir / "recommendations.json",
        "assigned_tasks": session_dir / "assigned_tasks.csv",
        "unassigned_tasks": session_dir / "unassigned_tasks.csv",
        "workload_after_assignment": session_dir / "workload_after_assignment.csv",
        "fairness_report": session_dir / "fairness_report.json",
        "assignment_report": session_dir / "assignment_report.html",
        "session_summary": session_dir / "session_summary.json",
    }

    write_json(paths["assignment_config"], payload["config"])
    write_json(paths["recommendations"], payload)
    write_csv(paths["assigned_tasks"], assigned_tasks)
    write_csv(paths["unassigned_tasks"], unassigned_tasks)
    write_csv(paths["workload_after_assignment"], workload_rows)
    write_json(paths["fairness_report"], report)
    paths["assignment_report"].write_text(assignment_report_html(payload), encoding="utf-8")
    write_json(paths["session_summary"], payload["summary"])

    payload["paths"] = {key: str(value) for key, value in paths.items()}
    payload["assignment_session_dir"] = str(session_dir)

    write_json(paths["recommendations"], payload)
    write_json(paths["session_summary"], payload["summary"])

    return payload


def run_bulk_assignment(config: BulkAssignmentConfig) -> dict[str, Any]:
    validate_config(config)

    try:
        test_case = load_test_case(config.test_case_id)
    except TestTeamError as exc:
        raise BulkAssignmentError(str(exc)) from exc

    try:
        model = load_sandbox_model(config.session_id, config.model_name)
    except ModelLoadError as exc:
        raise BulkAssignmentError(str(exc)) from exc

    team = list(test_case.get("team") or [])
    tasks = assignment_tasks(test_case, config.task_statuses)
    tasks.sort(key=task_priority_sort_key)

    if not team:
        raise BulkAssignmentError("Test case team is empty")

    if not tasks:
        raise BulkAssignmentError("No assignment-ready tasks found in test case")

    weights = OptimizerWeights(
        fairness_penalty=config.fairness_penalty,
        fatigue_penalty=config.fatigue_penalty,
        learning_bonus=config.learning_bonus,
        workload_penalty=config.workload_penalty,
    )
    workload_state = initial_workload_state(team)
    assigned_tasks: list[dict[str, Any]] = []
    unassigned_tasks: list[dict[str, Any]] = []
    task_recommendations: list[dict[str, Any]] = []

    for task in tasks:
        projected_team = current_projected_team(team, workload_state)
        candidates = predict_task_candidates(
            model=model,
            task=task,
            team=projected_team,
            recommendation_mode=config.recommendation_mode,
        )
        selected, ranked = choose_candidate(
            task=task,
            candidates=candidates,
            workload_state=workload_state,
            assignment_mode=config.assignment_mode,
            weights=weights,
            max_workload_per_person=config.max_workload_per_person,
        )

        task_recommendations.append(
            {
                "task_id": task.get("task_id"),
                "task_title": task.get("title"),
                "ranked_candidates": ranked[: config.top_k],
            }
        )

        if selected is None:
            unassigned_tasks.append(
                unassigned_row(
                    task=task,
                    reason="No candidates available for this task",
                    ranked_candidates=ranked,
                )
            )
            continue

        employee_id = str(selected.get("employee_id", ""))
        employee_state = workload_state[employee_id]
        apply_assignment(employee_state, task)
        assigned_tasks.append(
            assigned_row(
                task=task,
                candidate=selected,
                ranked_candidates=ranked,
                employee_task_number=int(employee_state["assigned_tasks_count"]),
            )
        )

    workload_rows = workload_after_assignment(workload_state)
    fairness = fairness_report(workload_rows)
    assignment_session_id = make_assignment_session_id()

    payload = {
        "assignment_session_id": assignment_session_id,
        "created_at": utc_now_iso(),
        "status": "completed",
        "session_id": config.session_id,
        "model_name": config.model_name,
        "test_case_id": config.test_case_id,
        "assignment_mode": config.assignment_mode,
        "assignment_mode_details": ASSIGNMENT_MODES[config.assignment_mode],
        "recommendation_mode": config.recommendation_mode,
        "top_k": config.top_k,
        "assigned_tasks": assigned_tasks,
        "unassigned_tasks": unassigned_tasks,
        "workload_after_assignment": workload_rows,
        "fairness_report": fairness,
        "task_recommendations": task_recommendations,
        "config": asdict(config),
        "model_metadata": getattr(model, "metadata", {}),
        "summary": {
            "assignment_session_id": assignment_session_id,
            "created_at": utc_now_iso(),
            "status": "completed",
            "session_id": config.session_id,
            "model_name": config.model_name,
            "test_case_id": config.test_case_id,
            "assignment_mode": config.assignment_mode,
            "recommendation_mode": config.recommendation_mode,
            "tasks_total": len(tasks),
            "assigned_tasks": len(assigned_tasks),
            "unassigned_tasks": len(unassigned_tasks),
            "fairness_report": fairness,
        },
    }

    if config.save_session:
        return save_assignment_session(payload)

    return payload


def list_assignment_sessions() -> dict[str, Any]:
    ASSIGNMENT_SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    sessions: list[dict[str, Any]] = []

    for directory in sorted(ASSIGNMENT_SESSIONS_DIR.iterdir(), reverse=True):
        if not directory.is_dir():
            continue

        summary_path = directory / "session_summary.json"
        if not summary_path.exists():
            continue

        summary = read_json(summary_path)
        sessions.append(
            {
                "assignment_session_id": directory.name,
                "assignment_session_dir": str(directory),
                "created_at": summary.get("created_at"),
                "status": summary.get("status"),
                "session_id": summary.get("session_id"),
                "model_name": summary.get("model_name"),
                "test_case_id": summary.get("test_case_id"),
                "assignment_mode": summary.get("assignment_mode"),
                "tasks_total": summary.get("tasks_total", 0),
                "assigned_tasks": summary.get("assigned_tasks", 0),
                "unassigned_tasks": summary.get("unassigned_tasks", 0),
            }
        )

    return {
        "assignment_sessions": sessions,
        "total": len(sessions),
        "assignment_sessions_dir": str(ASSIGNMENT_SESSIONS_DIR),
    }


def load_assignment_session(assignment_session_id: str) -> dict[str, Any]:
    session_dir = ASSIGNMENT_SESSIONS_DIR / assignment_session_id
    path = session_dir / "recommendations.json"

    if not path.exists():
        raise BulkAssignmentError(f"Assignment session not found: {assignment_session_id}")

    payload = read_json(path)

    if not isinstance(payload, dict):
        raise BulkAssignmentError("Assignment session payload must be JSON object")

    return payload


def load_assignment_session_file(
    assignment_session_id: str,
    file_name: str,
) -> Path:
    allowed = {
        "assignment_config.json",
        "recommendations.json",
        "assigned_tasks.csv",
        "unassigned_tasks.csv",
        "workload_after_assignment.csv",
        "fairness_report.json",
        "assignment_report.html",
        "session_summary.json",
    }
    session_dir = ASSIGNMENT_SESSIONS_DIR / assignment_session_id
    path = (session_dir / file_name).resolve()
    root = session_dir.resolve()

    if file_name not in allowed:
        raise BulkAssignmentError(f"Unsupported assignment session file: {file_name}")

    if root not in path.parents and path != root:
        raise BulkAssignmentError("Invalid assignment session file path")

    if not path.exists() or not path.is_file():
        raise BulkAssignmentError(f"Assignment session file not found: {file_name}")

    return path


def assignment_sessions_dataframe() -> pd.DataFrame:
    return pd.DataFrame(list_assignment_sessions()["assignment_sessions"])
