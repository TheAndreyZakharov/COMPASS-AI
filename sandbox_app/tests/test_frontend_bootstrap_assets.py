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
    assert "/js/app.js?v=20260710_bulk_queue" in index_html
    assert "/css/styles.css?v=20260710_bulk_queue" in index_html
    assert 'id="longToastStack"' in index_html
    assert "export function startLongTaskToast" in app_js
    assert "syncToastOffsets" in app_js
    assert "__compassAiSandboxRuntime" in app_js
    assert "runtimeState.globalEventsBound" in app_js
    assert "runtimeState.appBootstrapped" in app_js
    assert "datasetVerificationPassed" in app_js
    assert "startLongTaskVerification" in app_js
    assert "languageButton" in index_html
    assert "themeButton" in index_html
    assert "<title>COMPASS AI</title>" in index_html
    assert 'rel="icon" type="image/png" href="/brand/image.png"' in index_html
    assert '<img src="/brand/image.png" alt="" />' in index_html


def test_reports_page_matches_app_renderer_contract() -> None:
    reports_js = read("frontend/js/pages/reports.js")
    api_js = read("frontend/js/api.js")

    assert "export async function renderReports()" in reports_js
    assert "return renderReportsHtml();" in reports_js
    assert "export async function renderReportsPage()" in reports_js
    assert "export async function renderPage()" in reports_js
    assert "export default renderReports;" in reports_js
    assert "startLongTaskToast" in reports_js
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


def test_long_task_toasts_do_not_require_new_app_binding_in_lazy_pages() -> None:
    for path in [
        "frontend/js/pages/generator.js",
        "frontend/js/pages/training.js",
        "frontend/js/pages/import_data.js",
        "frontend/js/pages/reports.js",
        "frontend/js/pages/assignment_lab.js",
    ]:
        page_js = read(path)
        assert "sandbox-long-task-start" in page_js
        assert "import { startLongTaskToast" not in page_js
        assert ", startLongTaskToast" not in page_js
        assert "startLongTaskToast," not in page_js


def test_generator_schema_editor_avoids_duplicate_handlers_and_disabled_new_rows() -> None:
    generator_js = read("frontend/js/pages/generator.js")

    assert "isGenerating" in generator_js
    assert "Генерация уже выполняется." in generator_js
    assert "function syncFeatureRemoveButtons" in generator_js
    assert "syncAllFeatureRemoveButtons();" in generator_js
    assert "function generatorVerification" in generator_js
    assert "verify: generatorVerification(kind)" in generator_js
    assert "saveButton.dataset.bound" in generator_js
    assert "resetButton.dataset.bound" in generator_js
    assert "button.dataset.bound" in generator_js
