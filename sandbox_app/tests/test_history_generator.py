from __future__ import annotations

import shutil

from sandbox_app.backend.core.paths import PATHS
from sandbox_app.backend.data_generation.history import generate_assignment_history


def test_generate_assignment_history_from_payload() -> None:
    dataset_id = "pytest_history_dataset"
    dataset_dir = PATHS.data_dir / "generated" / dataset_id

    if dataset_dir.exists():
        shutil.rmtree(dataset_dir)

    employees = [
        {
            "employee_id": "employee_001",
            "name": "Test Employee",
            "role": "specialist",
            "grade": "middle",
            "skills": ["analysis", "communication", "quality_control"],
            "availability_score": 0.8,
            "current_workload": 0.35,
            "fatigue_score": 0.25,
            "avg_completion_speed": 0.7,
            "avg_quality_score": 0.8,
            "deadline_reliability": 0.75,
            "mentor_level": 0.4,
            "learning_goals": ["planning"]
        }
    ]

    tasks = [
        {
            "task_id": "task_001",
            "title": "Test Task",
            "description": "Task for history generator test",
            "project_id": "project_001",
            "task_type": "analysis",
            "status": "done",
            "priority": "medium",
            "complexity": 5,
            "estimated_hours": 8,
            "deadline_days": 7,
            "required_skills": ["analysis", "planning"],
            "dependencies": [],
            "custom_features": {}
        }
    ]

    result = generate_assignment_history(
        {
            "dataset_id": dataset_id,
            "domain_profile": "custom",
            "employees": employees,
            "tasks": tasks,
            "history_depth_per_employee": 5,
            "seed": 123,
            "overwrite": True
        }
    )

    history = result["assignment_history"]
    metadata = result["metadata"]

    assert len(history) == 5
    assert metadata["dataset_id"] == dataset_id
    assert metadata["counts"]["employees"] == 1
    assert metadata["counts"]["tasks"] == 1
    assert metadata["counts"]["assignment_history"] == 5

    first = history[0]
    assert first["assignment_id"].startswith("assignment_")
    assert first["employee_id"] == "employee_001"
    assert first["task_id"] == "task_001"
    assert first["deadline_status"] in {"early", "on_time", "late", "missed"}
    assert first["outcome_label"] in {"success", "good", "acceptable", "late", "failed", "rework"}
    assert 0 <= first["quality_score"] <= 1
    assert 0 <= first["feedback_score"] <= 1

    assert (dataset_dir / "assignment_history.json").exists()
    assert (dataset_dir / "assignment_history.csv").exists()
    assert (dataset_dir / "history_metadata.json").exists()

    shutil.rmtree(dataset_dir)