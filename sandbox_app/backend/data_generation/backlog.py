from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

TASK_STATUSES = ("todo", "in_progress", "review", "done", "blocked", "failed")


def build_backlog(tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [task for task in tasks if task.get("status") == "todo"]


def build_kanban_summary(
    tasks: list[dict[str, Any]], backlog: list[dict[str, Any]]
) -> dict[str, Any]:
    status_counts = Counter(
        str(task.get("status", "unknown")) for task in tasks
    )
    priority_counts = Counter(
        str(task.get("priority", "unknown")) for task in tasks
    )
    backlog_priority_counts = Counter(
        str(task.get("priority", "unknown")) for task in backlog
    )

    project_status_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for task in tasks:
        project_id = str(task.get("project_id", "unknown"))
        status = str(task.get("status", "unknown"))
        project_status_counts[project_id][status] += 1

    return {
        "total_tasks": len(tasks),
        "backlog_tasks": len(backlog),
        "status_counts": {status: status_counts.get(status, 0) for status in TASK_STATUSES},
        "priority_counts": dict(sorted(priority_counts.items())),
        "backlog_priority_counts": dict(sorted(backlog_priority_counts.items())),
        "project_status_counts": {
            project_id: {status: counts.get(status, 0) for status in TASK_STATUSES}
            for project_id, counts in sorted(project_status_counts.items())
        },
    }