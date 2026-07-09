from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_bulk_assignment_api_assets_are_wired() -> None:
    api_py = read("backend/api/assignment_sessions.py")
    bulk_py = read("backend/inference/bulk_assignment.py")
    optimizer_py = read("backend/inference/assignment_optimizer.py")
    api_js = read("frontend/js/api.js")

    assert 'prefix="/assignment-sessions"' in api_py
    assert 'router.post("/run")' in api_py
    assert 'router.get("/modes")' in api_py
    assert "BulkAssignmentConfig" in bulk_py
    assert "run_bulk_assignment" in bulk_py
    assert "assignment_report.html" in bulk_py
    assert "fairness_report" in bulk_py
    assert "workload_after_assignment" in bulk_py
    assert "choose_candidate" in optimizer_py
    assert "ASSIGNMENT_MODES" in optimizer_py
    assert "runBulkAssignment" in api_js
    assert "assignmentSessions" in api_js
    assert "assignmentModes" in api_js