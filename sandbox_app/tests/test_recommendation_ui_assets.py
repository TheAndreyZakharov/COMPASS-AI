from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_recommendation_ui_assets_are_wired() -> None:
    assignment_lab = read("frontend/js/pages/assignment_lab.js")
    cards = read("frontend/js/components/recommendation_cards.js")
    comparison = read("frontend/js/components/candidate_comparison.js")
    workload = read("frontend/js/components/workload_chart.js")
    fairness = read("frontend/js/components/fairness_chart.js")
    api_js = read("frontend/js/api.js")
    css = read("frontend/css/styles.css")

    assert "renderRecommendationCards" in assignment_lab
    assert "renderCandidateComparison" in assignment_lab
    assert "renderWorkloadChart" in assignment_lab
    assert "renderFairnessChart" in assignment_lab
    assert "runSingleRecommendation" in assignment_lab
    assert "runBulkAssignment" in assignment_lab
    assert "Kanban after assignment" in assignment_lab
    assert "Export results" in assignment_lab

    assert "renderScoreBreakdown" in cards
    assert "renderRiskList" in cards
    assert "Candidate comparison" in comparison
    assert "Workload after assignment" in workload
    assert "Fairness report" in fairness

    assert "singleRecommendation" in api_js
    assert "runBulkAssignment" in api_js
    assert "assignmentSessions" in api_js
    assert "recommendableTasks" in api_js

    assert ".recommendation-card-grid" in css
    assert ".score-breakdown" in css
    assert ".bar-chart-list" in css
    assert ".export-links" in css