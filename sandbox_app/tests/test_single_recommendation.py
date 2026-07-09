from __future__ import annotations

import shutil
from typing import Any

from sandbox_app.backend.data_generation.test_team import (
    TEST_CASES_DIR,
    TestTeamConfig,
    generate_test_case,
)
from sandbox_app.backend.inference.recommend import (
    RecommendationConfig,
    list_recommendations,
    recommend_single_task,
)


class FakeLoadedModel:
    metadata = {
        "model_name": "fake_model",
        "feature_count": 8,
        "artifact_format": "fake",
    }

    def predict_scores(self, frame: Any) -> list[float]:
        scores: list[float] = []

        for row in frame.to_dict(orient="records"):
            score = (
                float(row.get("skill_match_ratio", 0.0)) * 0.45
                + float(row.get("quality_fit_score", 0.0)) * 0.25
                + float(row.get("risk_fit_score", 0.0)) * 0.2
                + float(row.get("employee_availability_score", 0.0)) * 0.1
            )
            scores.append(max(0.0, min(1.0, score)))

        return scores


def test_single_task_recommendation(monkeypatch: Any) -> None:
    test_case_id = "pytest_single_recommendation"
    test_case_dir = TEST_CASES_DIR / test_case_id

    if test_case_dir.exists():
        shutil.rmtree(test_case_dir)

    generated = generate_test_case(
        TestTeamConfig(
            test_case_id=test_case_id,
            domain_profile="developers",
            people_count=7,
            active_tasks_count=5,
            history_depth=3,
            seed=27022,
            overwrite=True,
        )
    )
    task_id = generated["preview"]["active_tasks"][0]["task_id"]

    def fake_loader(session_id: str, model_name: str) -> FakeLoadedModel:
        assert session_id == "session_for_test"
        assert model_name == "model_for_test"
        return FakeLoadedModel()

    monkeypatch.setattr(
        "sandbox_app.backend.inference.recommend.load_sandbox_model",
        fake_loader,
    )

    result = recommend_single_task(
        RecommendationConfig(
            session_id="session_for_test",
            model_name="model_for_test",
            test_case_id=test_case_id,
            task_id=task_id,
            recommendation_mode="balanced",
            top_k=3,
            save_result=True,
        )
    )

    assert result["test_case_id"] == test_case_id
    assert result["task_id"] == task_id
    assert result["top_1"]["employee_id"]
    assert len(result["top_3"]) <= 3
    assert len(result["candidates"]) == 3
    assert 0.0 <= result["top_1"]["score"] <= 1.0
    assert result["top_1"]["factors"]["mode"] == "balanced"
    assert result["top_1"]["risks"]

    listing = list_recommendations(test_case_id)
    assert listing["total"] == 1
    assert listing["recommendations"][0]["recommendation_id"] == result["recommendation_id"]

    shutil.rmtree(test_case_dir)