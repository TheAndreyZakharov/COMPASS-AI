from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_app_uses_lazy_page_imports_and_keeps_backend_status_alive() -> None:
    app_js = read("frontend/js/app.js")
    index_html = read("frontend/index.html")

    assert "Started server process" not in app_js
    assert "import { renderAssignmentLab }" not in app_js
    assert "import { renderReports }" not in app_js
    assert "async function updateBackendStatus" in app_js
    assert "await api.health()" in app_js
    assert "async function loadRouteRenderer" in app_js
    assert "await import(cacheBustedModulePath(route.modulePath))" in app_js
    assert "APP_BUILD_ID" in app_js
    assert "/js/app.js?v=20260709_frontend_bootstrap_fix" in index_html


def test_reports_page_matches_app_renderer_contract() -> None:
    reports_js = read("frontend/js/pages/reports.js")
    api_js = read("frontend/js/api.js")

    assert "export async function renderReports()" in reports_js
    assert "return renderReportsHtml();" in reports_js
    assert "export async function renderReportsPage()" in reports_js
    assert "export async function renderPage()" in reports_js
    assert "export default renderReports;" in reports_js
    assert "from \"../app.js\"" not in reports_js
    assert "api.datasets()" in reports_js
    assert "Promise.allSettled" in reports_js
    assert "exportReports" in api_js
    assert "generateDatasetExport" in api_js


def test_assignment_lab_exports_router_compatible_names() -> None:
    assignment_lab_js = read("frontend/js/pages/assignment_lab.js")

    assert "export async function renderAssignmentLabPage" in assignment_lab_js
    assert "export async function renderAssignmentLab" in assignment_lab_js
    assert "export async function renderPage" in assignment_lab_js
    assert "export default renderAssignmentLabPage" in assignment_lab_js