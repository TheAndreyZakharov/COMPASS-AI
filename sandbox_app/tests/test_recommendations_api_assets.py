from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_recommendation_api_assets_are_wired() -> None:
    api_py = read("backend/api/recommendations.py")
    recommend_py = read("backend/inference/recommend.py")
    scoring_py = read("backend/inference/scoring.py")
    risks_py = read("backend/inference/risk_factors.py")
    api_js = read("frontend/js/api.js")

    assert 'prefix="/recommendations"' in api_py
    assert 'router.post("/single")' in api_py
    assert 'router.get("/modes")' in api_py
    assert "RecommendationConfig" in recommend_py
    assert "recommend_single_task" in recommend_py
    assert "load_model as load_sandbox_model" in recommend_py
    assert "best_quality" in recommend_py
    assert "fastest_delivery" in recommend_py
    assert "best_learning" in recommend_py
    assert "risk_aware" in recommend_py
    assert "build_pair_feature_frame" in scoring_py
    assert "candidate_risks" in risks_py
    assert "singleRecommendation" in api_js
    assert "recommendationModes" in api_js