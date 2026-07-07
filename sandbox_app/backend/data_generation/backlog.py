from __future__ import annotations

from typing import Any

TODO_STATUS = "todo"

KANBAN_STATUSES = [
    "todo",
    "in_progress",
    "review",
    "done",
    "blocked",
    "failed",
]


def get_backlog_tasks(tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        task
        for task in tasks
        if task.get("status") == TODO_STATUS
    ]


def build_kanban_summary(tasks: list[dict[str, Any]]) -> dict[str, int]:
    summary = {
        status: 0
        for status in KANBAN_STATUSES
    }

    for task in tasks:
        status = str(task.get("status", ""))

        if status not in summary:
            summary[status] = 0

        summary[status] += 1

    return summary