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
    assert "function prettyJson" not in assignment_js
    assert "<pre" not in assignment_js
    assert "raw JSON" not in assignment_js
    assert "function toast" in assignment_js
    assert "function renderMarkdownText" in assignment_js
    assert "function readableMarkdownValue" in assignment_js
    assert "item.message || item.text || item.explanation" in assignment_js
    assert "markdown-text" in assignment_js
    assert "function testCaseCounts" in assignment_js
    assert "metadataCounts" in assignment_js
    assert "function renderTaskRequirementPanel" in assignment_js
    assert "function renderTaskCandidateFitChart" in assignment_js
    assert "function renderRecommendationFacts" in assignment_js
    assert "fit-radar" in assignment_js
    assert "Что требуется в задаче" in assignment_js
    assert "Факты для объяснения" in assignment_js
    assert "recommendationContexts" in assignment_js
    assert "loadRecommendationContexts" in assignment_js
    assert "Promise.allSettled" in assignment_js
    assert "startLongTaskToast" in assignment_js
    assert "Создаем набор из датасета..." in assignment_js
    assert '"assignmentTaskStatuses"' in assignment_js
    assert 'selectedValue("assignmentTaskStatuses")' in assignment_js

    assert "testCaseSummary" in api_js
    assert "testCaseRecommendationContext" in api_js
    assert "assignmentSessions" in api_js
