from __future__ import annotations

from pathlib import Path
from typing import Any

from sandbox_app.backend.reports.html_export import (
    ExportError,
    read_csv_rows,
    read_json,
    write_report_bundle,
)

SANDBOX_DIR = Path(__file__).resolve().parents[2]
ASSIGNMENT_SESSIONS_DIR = SANDBOX_DIR / "assignment_sessions"


def assignment_session_dir(assignment_session_id: str) -> Path:
    path = ASSIGNMENT_SESSIONS_DIR / assignment_session_id

    if not path.exists() or not path.is_dir():
        raise ExportError(f"Assignment session not found: {assignment_session_id}")

    return path


def recommendation_rows(recommendations: Any) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    if not isinstance(recommendations, list):
        return rows

    for item in recommendations:
        if not isinstance(item, dict):
            continue

        candidates = item.get("candidates") or []
        task = item.get("task") or {}

        if not isinstance(candidates, list):
            continue

        for rank, candidate in enumerate(candidates, start=1):
            if not isinstance(candidate, dict):
                continue

            rows.append(
                {
                    "task_id": item.get("task_id") or task.get("task_id"),
                    "task_title": task.get("title"),
                    "rank": rank,
                    "employee_id": candidate.get("employee_id"),
                    "candidate_name": candidate.get("name"),
                    "score": candidate.get("score"),
                    "model_score": candidate.get("model_score"),
                    "risk_score": (candidate.get("risk_summary") or {}).get(
                        "max_risk_score"
                    ),
                    "recommendation_mode": item.get("recommendation_mode"),
                }
            )

    return rows


def generate_assignment_report(assignment_session_id: str) -> dict[str, Any]:
    session_dir = assignment_session_dir(assignment_session_id)

    config = read_json(session_dir / "assignment_config.json", default={})
    summary = read_json(session_dir / "session_summary.json", default={})
    fairness = read_json(session_dir / "fairness_report.json", default={})
    recommendations = read_json(session_dir / "recommendations.json", default=[])

    assigned = read_csv_rows(session_dir / "assigned_tasks.csv")
    unassigned = read_csv_rows(session_dir / "unassigned_tasks.csv")
    workload = read_csv_rows(session_dir / "workload_after_assignment.csv")
    recommendation_table = recommendation_rows(recommendations)

    payload = {
        "summary": {
            "assignment_session_id": assignment_session_id,
            "assigned_tasks": len(assigned),
            "unassigned_tasks": len(unassigned),
            "workload_rows": len(workload),
            "recommendation_rows": len(recommendation_table),
            "assignment_mode": config.get("assignment_mode"),
            "recommendation_mode": config.get("recommendation_mode"),
        },
        "sections": [
            {
                "title": "Bulk assignment report",
                "body": "Сводка по массовому распределению задач и результатам optimizer.",
            },
            {
                "title": "Recommendation report",
                "body": "Сохранённые candidates, ranking и score для задач assignment session.",
            },
            {
                "title": "Fairness report",
                "body": "Показатели равномерности распределения и перегрузки команды.",
            },
            {
                "title": "Workload report",
                "body": "Прогнозная загрузка сотрудников после назначения задач.",
            },
        ],
        "assignment_session_id": assignment_session_id,
        "assignment_session_dir": str(session_dir),
        "assignment_config": config,
        "session_summary": summary,
        "fairness_report": fairness,
        "recommendations": recommendations,
    }

    return write_report_bundle(
        kind="assignment",
        source_id=assignment_session_id,
        title=f"Assignment report · {assignment_session_id}",
        payload=payload,
        tables={
            "assigned_tasks": assigned,
            "unassigned_tasks": unassigned,
            "workload_after_assignment": workload,
            "recommendation_candidates": recommendation_table,
        },
    )