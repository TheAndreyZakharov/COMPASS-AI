from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pandas as pd

from src.integration.plane_client import PlaneClient, PlaneClientError
from src.integration.plane_mapping import (
    task_project_id,
    task_to_plane_work_item_payload,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TASKS_CSV_PATH = PROJECT_ROOT / "data" / "synthetic" / "tasks.csv"
MAPPING_CSV_PATH = PROJECT_ROOT / "data" / "processed" / "task_plane_mapping.csv"


def load_tasks(limit: int | None = None) -> pd.DataFrame:
    if not TASKS_CSV_PATH.exists():
        raise FileNotFoundError(
            f"Missing synthetic tasks file: {TASKS_CSV_PATH}. Run make generate-data first."
        )

    tasks = pd.read_csv(TASKS_CSV_PATH)

    if limit is not None:
        tasks = tasks.head(limit)

    return tasks


def label_name_to_id(labels: list[dict[str, Any]]) -> dict[str, str]:
    mapping: dict[str, str] = {}

    for label in labels:
        name = str(label.get("name", "")).strip().lower()
        label_id = str(label.get("id", "")).strip()

        if name and label_id:
            mapping[name] = label_id

    return mapping


def existing_compass_markers(work_items: list[dict[str, Any]]) -> dict[str, str]:
    markers: dict[str, str] = {}

    marker_patterns = [
        re.compile(r"COMPASS_TASK_ID=([A-Z]+-\d+)"),
        re.compile(r"COMPASS task_id:\s*</strong>\s*([A-Z]+-\d+)"),
        re.compile(r"COMPASS task_id:\s*([A-Z]+-\d+)"),
    ]

    for item in work_items:
        item_id = str(item.get("id", "")).strip()
        description = str(item.get("description_html", "") or "")

        if not item_id:
            continue

        for pattern in marker_patterns:
            match = pattern.search(description)

            if match:
                task_id = match.group(1).strip()
                markers[task_id] = item_id
                break

    return markers


def create_tasks(limit: int | None = None) -> pd.DataFrame:
    tasks = load_tasks(limit=limit)
    mapping_rows: list[dict[str, Any]] = []

    with PlaneClient() as client:
        labels_by_project: dict[str, dict[str, str]] = {}
        existing_by_project: dict[str, dict[str, str]] = {}

        for _, task_row in tasks.iterrows():
            task = task_row.to_dict()
            project_id = task_project_id(task)
            task_id = str(task["task_id"])

            if project_id not in labels_by_project:
                labels_by_project[project_id] = label_name_to_id(client.list_labels(project_id))

            if project_id not in existing_by_project:
                existing_by_project[project_id] = existing_compass_markers(
                    client.list_work_items(project_id)
                )

            if task_id in existing_by_project[project_id]:
                plane_work_item_id = existing_by_project[project_id][task_id]
                action = "exists"
            else:
                payload = task_to_plane_work_item_payload(
                    task=task,
                    label_name_to_id=labels_by_project[project_id],
                )

                created = client.create_work_item(
                    project_id=project_id,
                    name=payload["name"],
                    description_html=payload["description_html"],
                    priority=payload["priority"],
                    labels=payload.get("labels", []),
                    target_date=payload.get("target_date"),
                )

                plane_work_item_id = str(created.get("id", "")).strip()

                if not plane_work_item_id:
                    raise PlaneClientError(f"Plane did not return id for task {task_id}.")

                existing_by_project[project_id][task_id] = plane_work_item_id
                action = "created"

            mapping_rows.append(
                {
                    "task_id": task_id,
                    "plane_work_item_id": plane_work_item_id,
                    "plane_issue_id": plane_work_item_id,
                    "plane_project_id": project_id,
                    "project_key": task.get("project_key", ""),
                    "title": task.get("title", ""),
                    "action": action,
                }
            )

    mapping = pd.DataFrame(mapping_rows)
    MAPPING_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    mapping.to_csv(MAPPING_CSV_PATH, index=False)

    return mapping


def main() -> None:
    mapping = create_tasks()

    print("Plane synthetic task seed completed.")
    print(f"Mapping saved to: {MAPPING_CSV_PATH}")
    print()
    print(mapping["action"].value_counts().to_string())
    print()
    print(mapping.head(20).to_string(index=False))


if __name__ == "__main__":
    main()