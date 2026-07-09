from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_assignment_lab_ui_assets_are_wired() -> None:
    assignment_js = read("frontend/js/pages/assignment_lab.js")
    api_js = read("frontend/js/api.js")

    assert "export async function renderAssignmentLab" in assignment_js
    assert "export async function renderAssignmentLabPage" in assignment_js
    assert "export async function renderPage" in assignment_js
    assert "export default renderAssignmentLabPage" in assignment_js

    assert "api.generateTestCase" in assignment_js
    assert "api.testCases" in assignment_js
    assert "api.testCaseSummary" in assignment_js
    assert "api.testCaseRecommendationContext" in assignment_js
    assert "api.recommendableTasks" in assignment_js
    assert "api.singleRecommendation" in assignment_js
    assert "api.runBulkAssignment" in assignment_js
    assert "api.assignmentSessions" in assignment_js
    assert "api.assignmentSession" in assignment_js
    assert "api.explainRecommendation" in assignment_js
    assert "api.explainAssignment" in assignment_js

    assert 'from "../app.js"' not in assignment_js
    assert "function htmlEscape" in assignment_js
    assert "function prettyJson" in assignment_js
    assert "function toast" in assignment_js
    assert "recommendationContexts" in assignment_js
    assert "loadRecommendationContexts" in assignment_js
    assert "Promise.allSettled" in assignment_js

    assert "testCaseSummary" in api_js
    assert "testCaseRecommendationContext" in api_js
    assert "assignmentSessions" in api_js