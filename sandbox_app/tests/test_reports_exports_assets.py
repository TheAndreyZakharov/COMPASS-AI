from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_report_export_assets_are_wired() -> None:
    html_export = read("backend/reports/html_export.py")
    dataset_report = read("backend/reports/dataset_report.py")
    model_report = read("backend/reports/model_report.py")
    assignment_report = read("backend/reports/assignment_report.py")
    reports_api = read("backend/api/reports.py")
    reports_js = read("frontend/js/pages/reports.js")
    api_js = read("frontend/js/api.js")

    assert "write_report_bundle" in html_export
    assert "REPORTS_DIR" in html_export
    assert "EXPORTS_DIR" in html_export
    assert "build_html_report" in html_export

    assert "generate_dataset_report" in dataset_report
    assert "Dataset quality report" in dataset_report
    assert "missing_required_summary" in dataset_report

    assert "generate_model_report" in model_report
    assert "comparison_metrics" in model_report

    assert "generate_assignment_report" in assignment_report
    assert "fairness_report" in assignment_report
    assert "workload_after_assignment" in assignment_report

    assert 'router.get("/exports")' in reports_api
    assert 'router.post("/exports/datasets/{dataset_id}")' in reports_api
    assert 'router.post("/exports/models/{session_id}")' in reports_api
    assert 'router.post("/exports/assignments/{assignment_session_id}")' in reports_api

    assert "Reports and exports" in reports_js
    assert "Promise.allSettled" in reports_js
    assert "api.datasets()" in reports_js
    assert "api.dataViewerDatasets()" not in reports_js
    assert "generateDatasetExport" in reports_js
    assert "generateModelExport" in reports_js
    assert "generateAssignmentExport" in reports_js
    assert "from \"../app.js\"" not in reports_js
    assert "export async function renderReportsPage" in reports_js
    assert "export async function renderReports" in reports_js
    assert "export async function renderPage" in reports_js
    assert "export default renderReports;" in reports_js

    assert "exportReports" in api_js
    assert "exportReportFileUrl" in api_js
    assert "dataViewerDatasets" in api_js