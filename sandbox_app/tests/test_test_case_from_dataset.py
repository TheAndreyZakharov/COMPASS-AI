from __future__ import annotations

import json
import shutil

from sandbox_app.backend.api.test_cases import (
    TestCaseFromDatasetRequest as DatasetCaseRequest,
    create_case_from_dataset,
)
from sandbox_app.backend.core.paths import PATHS
from sandbox_app.backend.data_generation.test_team import TEST_CASES_DIR, load_test_case


def write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def test_create_case_from_dataset_normalizes_assignment_history_id() -> None:
    dataset_id = "pytest_case_from_dataset"
    test_case_id = "pytest_case_from_dataset_case"
    dataset_dir = PATHS.data_dir / "generated" / dataset_id
    test_case_dir = TEST_CASES_DIR / test_case_id

    if dataset_dir.exists():
        shutil.rmtree(dataset_dir)
    if test_case_dir.exists():
        shutil.rmtree(test_case_dir)

    write_json(
        dataset_dir / "employees.json",
        [
            {
                "employee_id": "emp_001",
                "role": "Backend Engineer",
                "grade": "senior",
                "skills": ["python", "fastapi"],
                "current_workload": 0.2,
            }
        ],
    )
    write_json(
        dataset_dir / "tasks.json",
        [
            {
                "task_id": "task_001",
                "status": "todo",
                "priority": "high",
                "required_skills": ["python"],
                "assigned_employee_id": "emp_001",
            }
        ],
    )
    write_json(
        dataset_dir / "assignment_history.json",
        [
            {
                "assignment_id": "assignment_001",
                "employee_id": "emp_001",
                "task_id": "task_000",
                "outcome_label": "good",
            }
        ],
    )

    result = create_case_from_dataset(
        DatasetCaseRequest(
            dataset_id=dataset_id,
            dataset_kind="generated",
            test_case_id=test_case_id,
            task_statuses=["todo", "in_progress", "review", "blocked"],
            overwrite=True,
        )
    )
    loaded = load_test_case(test_case_id)

    assert result["test_case_id"] == test_case_id
    assert loaded["team"][0]["name"] == "emp_001"
    assert loaded["team"][0]["active_task_ids"] == ["task_001"]
    assert loaded["active_tasks"][0]["title"] == "task_001"
    assert loaded["history"][0]["history_id"] == "assignment_001"

    shutil.rmtree(dataset_dir)
    shutil.rmtree(test_case_dir)
