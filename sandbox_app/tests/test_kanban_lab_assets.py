from __future__ import annotations

from pathlib import Path
from typing import Any

from sandbox_app.backend.api.kanban_lab import (
    KanbanBoardRecommendationRequest,
    KanbanBoardSaveRequest,
    delete_board,
    get_board,
    list_boards,
    recommend_board,
    save_board,
)
from sandbox_app.backend.core.paths import PATHS

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_kanban_lab_assets_are_wired() -> None:
    page_js = read("frontend/js/pages/kanban_lab.js")
    app_js = read("frontend/js/app.js")
    api_js = read("frontend/js/api.js")
    index_html = read("frontend/index.html")
    css = read("frontend/css/styles.css")
    api_py = read("backend/api/kanban_lab.py")
    main_py = read("backend/main.py")

    assert "/kanban-lab" in app_js
    assert "./pages/kanban_lab.js" in app_js
    assert "Канбан-лаборатория" in index_html
    assert "renderKanbanLab" in page_js
    assert "function textByLanguage" in page_js
    assert "function statusLabel" in page_js
    assert "createLabCopyFromDataset" in page_js
    assert "runRecommendations" in page_js
    assert "dragstart" in page_js
    assert "drop" in page_js
    assert "moveColumn" in page_js
    assert "clearColumn" in page_js
    assert "addManualTask" in page_js
    assert "checkboxGroupInput" in page_js
    assert "addManualEmployee" in page_js
    assert "deleteEmployee" in page_js
    assert "clearTeam" in page_js
    assert "data-delete-employee-card" in page_js
    assert "renderTaskCandidateFitChart" in page_js
    assert "sandbox-long-task-start" in page_js
    assert "recommendKanbanBoard" in api_js
    assert "kanbanLabBoards" in api_js
    assert "saveKanbanLabBoard" in api_js
    assert "loadSavedLabBoard" in page_js
    assert "saveLabBoard" in page_js
    assert "data/kanban_lab" not in page_js
    assert "Загрузите проверочный набор или создайте лабораторную копию из датасета." in app_js
    assert "Load a test set or create a lab copy from a dataset." in app_js

    assert 'prefix="/kanban-lab"' in api_py
    assert 'router.post("/recommend-board")' in api_py
    assert 'router.post("/boards")' in api_py
    assert 'router.get("/boards")' in api_py
    assert "KanbanBoardRecommendationRequest" in api_py
    assert "KanbanBoardSaveRequest" in api_py
    assert "recommendation_for_task" in api_py
    assert "kanban_lab.router" in main_py

    assert ".kanban-lab-board" in css
    assert ".kanban-lab-card" in css
    assert ".kanban-detail-stack" in css
    assert ".checkbox-picker" in css
    assert ".employee-grid" in css
    assert ".employee-preview-card" in css


class FakeKanbanModel:
    metadata = {"model_name": "fake_kanban_model"}

    def predict_scores(self, frame: Any) -> list[float]:
        return [
            max(
                0.0,
                min(
                    1.0,
                    float(row.get("skill_match_ratio", 0.0)) * 0.7
                    + float(row.get("quality_fit_score", 0.0)) * 0.3,
                ),
            )
            for row in frame.to_dict(orient="records")
        ]


def test_kanban_lab_recommend_board_uses_copied_tasks(monkeypatch: Any) -> None:
    monkeypatch.setattr(
        "sandbox_app.backend.api.kanban_lab.load_sandbox_model",
        lambda _session_id, _model_name: FakeKanbanModel(),
    )

    result = recommend_board(
        KanbanBoardRecommendationRequest(
            session_id="session_test",
            model_name="fake_kanban_model",
            source_id="lab_copy",
            recommendation_mode="balanced",
            top_k=2,
            team=[
                {
                    "employee_id": "emp_backend",
                    "name": "employee_backend",
                    "role": "Backend Engineer",
                    "grade": "senior",
                    "skills": ["python", "fastapi"],
                    "current_workload": 0.2,
                    "fatigue_score": 0.1,
                    "availability_score": 0.9,
                    "avg_quality_score": 0.9,
                    "avg_completion_speed": 0.8,
                    "deadline_reliability": 0.9,
                },
                {
                    "employee_id": "emp_frontend",
                    "name": "employee_frontend",
                    "role": "Frontend Engineer",
                    "grade": "middle",
                    "skills": ["react", "css"],
                    "current_workload": 0.2,
                    "fatigue_score": 0.1,
                    "availability_score": 0.9,
                    "avg_quality_score": 0.7,
                    "avg_completion_speed": 0.7,
                    "deadline_reliability": 0.8,
                },
            ],
            tasks=[
                {
                    "task_id": "manual_task_1",
                    "title": "Build FastAPI endpoint",
                    "status": "todo",
                    "priority": "high",
                    "task_type": "backend",
                    "complexity": 0.6,
                    "estimated_hours": 8,
                    "required_skills": ["python", "fastapi"],
                },
                {
                    "task_id": "done_task_1",
                    "title": "Already done",
                    "status": "done",
                    "required_skills": ["python"],
                },
            ],
            statuses_for_recommendation=["todo"],
        )
    )

    assert result["status"] == "completed"
    assert result["source"] == "kanban_lab"
    assert result["total"] == 1
    recommendation = result["recommendations"][0]
    assert recommendation["task_id"] == "manual_task_1"
    assert recommendation["top_1"]["employee_id"] == "emp_backend"
    assert recommendation["candidates"]


def test_kanban_lab_boards_are_saved_in_dedicated_storage() -> None:
    lab_id = "pytest_kanban_saved_board"

    try:
        saved = save_board(
            KanbanBoardSaveRequest(
                lab_id=lab_id,
                name="Pytest kanban saved board",
                source_test_case_id="pytest_source_case",
                source_dataset_value="generated:pytest_dataset",
                team=[
                    {
                        "employee_id": "emp_1",
                        "skills": ["python"],
                    }
                ],
                tasks=[
                    {
                        "task_id": "task_1",
                        "status": "todo",
                        "required_skills": ["python"],
                    }
                ],
                config={"model_name": "fake_model"},
            )
        )

        assert saved["status"] == "saved"
        assert saved["board"]["lab_id"] == lab_id
        assert str(PATHS.kanban_lab_dir) in saved["path"]
        assert str(PATHS.generated_data_dir) not in saved["path"]

        loaded = get_board(lab_id)
        assert loaded["lab_id"] == lab_id
        assert loaded["tasks"][0]["task_id"] == "task_1"

        listing = list_boards()
        assert any(item["lab_id"] == lab_id for item in listing["boards"])
    finally:
        try:  # noqa: SIM105
            delete_board(lab_id)
        except Exception:
            pass
