from __future__ import annotations

import shutil
from typing import Any

from sandbox_app.backend.data_generation.test_team import (
    TEST_CASES_DIR,
    TestTeamConfig,
    generate_test_case,
)
from sandbox_app.backend.inference.bulk_assignment import (
    ASSIGNMENT_SESSIONS_DIR,
    BulkAssignmentConfig,
    list_assignment_sessions,
    run_bulk_assignment,
)


class FakeBulkModel:
    metadata = {
        "model_name": "fake_bulk_model",
        "artifact_format": "fake",
    }

    def predict_scores(self, frame: Any) -> list[float]:
        scores: list[float] = []

        for row in frame.to_dict(orient="records"):
            score = (
                float(row.get("skill_match_ratio", 0.0)) * 0.4
                + float(row.get("quality_fit_score", 0.0)) * 0.24
                + float(row.get("speed_fit_score", 0.0)) * 0.16
                + float(row.get("risk_fit_score", 0.0)) * 0.2
            )
            scores.append(max(0.0, min(1.0, score)))

        return scores


def test_bulk_assignment_session(monkeypatch: Any) -> None:
    test_case_id = "pytest_bulk_assignment"
    test_case_dir = TEST_CASES_DIR / test_case_id

    if test_case_dir.exists():
        shutil.rmtree(test_case_dir)

    generated = generate_test_case(
        TestTeamConfig(
            test_case_id=test_case_id,
            domain_profile="developers",
            people_count=8,
            active_tasks_count=10,
            history_depth=3,
            seed=27023,
            overwrite=True,
        )
    )

    def fake_loader(session_id: str, model_name: str) -> FakeBulkModel:
        assert session_id == "training_session_for_bulk_test"
        assert model_name == "bulk_model_for_test"
        return FakeBulkModel()

    monkeypatch.setattr(
        "sandbox_app.backend.inference.bulk_assignment.load_sandbox_model",
        fake_loader,
    )

    result = run_bulk_assignment(
        BulkAssignmentConfig(
            session_id="training_session_for_bulk_test",
            model_name="bulk_model_for_test",
            test_case_id=test_case_id,
            assignment_mode="balanced",
            recommendation_mode="balanced",
            top_k=3,
            max_workload_per_person=1.2,
            task_statuses=["todo"],
            save_session=True,
        )
    )

    assignment_session_id = result["assignment_session_id"]
    assignment_session_dir = ASSIGNMENT_SESSIONS_DIR / assignment_session_id

    assert result["status"] == "completed"
    assert result["summary"]["tasks_total"] == 10
    assert result["summary"]["assigned_tasks"] >= 1
    assert result["fairness_report"]["assigned_tasks_total"] >= 1
    assert result["workload_after_assignment"]

    assert (assignment_session_dir / "assignment_config.json").exists()
    assert (assignment_session_dir / "recommendations.json").exists()
    assert (assignment_session_dir / "assigned_tasks.csv").exists()
    assert (assignment_session_dir / "unassigned_tasks.csv").exists()
    assert (assignment_session_dir / "workload_after_assignment.csv").exists()
    assert (assignment_session_dir / "fairness_report.json").exists()
    assert (assignment_session_dir / "assignment_report.html").exists()

    listing = list_assignment_sessions()
    assert any(
        item["assignment_session_id"] == assignment_session_id
        for item in listing["assignment_sessions"]
    )

    shutil.rmtree(test_case_dir)
    shutil.rmtree(assignment_session_dir)

    assert generated["test_case_id"] == test_case_id