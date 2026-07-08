from __future__ import annotations

import shutil

from sandbox_app.backend.api.data_viewer import (
    build_employee_history,
    build_kanban,
    dataset_descriptor,
    filter_rows,
    paginate_rows,
    read_table,
)
from sandbox_app.backend.core.paths import PATHS
from sandbox_app.backend.utils.json_io import write_json


def test_data_viewer_reads_generated_dataset_tables() -> None:
    dataset_id = "pytest_data_viewer"
    dataset_dir = PATHS.data_dir / "generated" / dataset_id

    if dataset_dir.exists():
        shutil.rmtree(dataset_dir)

    dataset_dir.mkdir(parents=True, exist_ok=True)

    write_json(
        dataset_dir / "employees.json",
        [
            {
                "employee_id": "employee_001",
                "name": "Test Employee",
                "role": "analyst",
                "grade": "middle",
                "skills": ["analysis"],
            }
        ],
    )
    write_json(
        dataset_dir / "tasks.json",
        [
            {
                "task_id": "task_001",
                "title": "Task One",
                "status": "todo",
                "project_id": "project_001",
                "priority": "high",
            },
            {
                "task_id": "task_002",
                "title": "Task Two",
                "status": "done",
                "project_id": "project_001",
                "priority": "medium",
            },
        ],
    )
    write_json(
        dataset_dir / "assignment_history.json",
        [
            {
                "assignment_id": "assignment_001",
                "employee_id": "employee_001",
                "task_id": "task_001",
                "completed_at": "2026-01-01T00:00:00+00:00",
                "quality_score": 0.9,
            }
        ],
    )
    write_json(
        dataset_dir / "dataset_metadata.json",
        {
            "dataset_id": dataset_id,
            "dataset_type": "generated",
            "domain_profile": "custom",
            "dataset_mode": "small_preview",
            "created_at": "2026-01-01T00:00:00+00:00",
        },
    )

    rows, file_format, path = read_table(dataset_dir, "tasks")
    filtered = filter_rows(rows, search="task", filters={"status": "todo"})
    page_items, pagination = paginate_rows(filtered, page=1, page_size=10)
    descriptor = dataset_descriptor(dataset_dir, "generated")
    kanban = build_kanban(dataset_dir)
    history = build_employee_history(dataset_dir, "employee_001")

    assert file_format == "json"
    assert path.name == "tasks.json"
    assert len(rows) == 2
    assert len(page_items) == 1
    assert pagination["total"] == 1
    assert descriptor["dataset_id"] == dataset_id
    assert descriptor["counts"]["tasks"] == 2
    assert kanban["counts"]["todo"] == 1
    assert kanban["counts"]["done"] == 1
    assert history["count"] == 1

    shutil.rmtree(dataset_dir)