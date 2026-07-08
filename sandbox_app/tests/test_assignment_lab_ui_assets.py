from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_assignment_lab_ui_assets_are_wired() -> None:
    assignment_js = read("frontend/js/pages/assignment_lab.js")
    api_js = read("frontend/js/api.js")

    assert "export async function renderAssignmentLab" in assignment_js
    assert "api.generateTestCase" in assignment_js
    assert "api.testCases" in assignment_js
    assert "api.testCaseSummary" in assignment_js
    assert "api.testCaseRecommendationContext" in assignment_js
    assert "Generate test case" in assignment_js
    assert "active_tasks_count" in assignment_js

    assert "testCases" in api_js
    assert "generateTestCase" in api_js
    assert "testCaseRecommendationContext" in api_js