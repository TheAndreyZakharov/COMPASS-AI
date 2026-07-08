from __future__ import annotations

import shutil

from sandbox_app.backend.core.paths import PATHS
from sandbox_app.backend.data_generation.tasks import generate_tasks


def test_generate_tasks_dataset_custom_profile() -> None:
    dataset_id = "pytest_tasks_dataset"
    dataset_dir = PATHS.data_dir / "generated" / dataset_id

    if dataset_dir.exists():
        shutil.rmtree(dataset_dir)

    result = generate_tasks(
        {
            "dataset_id": dataset_id,
            "domain_profile": "custom",
            "tasks_count": 12,
            "projects_count": 3,
            "seed": 42,
            "overwrite": True,
            "status_distribution": {
                "todo": 1,
                "in_progress": 0,
                "review": 0,
                "done": 0,
                "blocked": 0,
                "failed": 0
            }
        }
    )

    tasks = result["tasks"]
    backlog = result["backlog"]
    metadata = result["metadata"]

    assert len(tasks) == 12
    assert len(backlog) == 12
    assert metadata["dataset_id"] == dataset_id
    assert metadata["domain_profile"] == "custom"
    assert metadata["counts"]["tasks"] == 12
    assert metadata["counts"]["backlog"] == 12

    assert (dataset_dir / "tasks.json").exists()
    assert (dataset_dir / "tasks.csv").exists()
    assert (dataset_dir / "backlog.json").exists()
    assert (dataset_dir / "backlog.csv").exists()
    assert (dataset_dir / "task_metadata.json").exists()

    first_task = tasks[0]
    assert first_task["task_id"].startswith("task_")
    assert first_task["status"] == "todo"
    assert first_task["required_skills"]
    assert "custom_features" in first_task

    shutil.rmtree(dataset_dir)