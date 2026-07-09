from __future__ import annotations

from sandbox_app.backend.reports.html_export import (
    build_html_report,
    safe_name,
    write_report_bundle,
)


def test_safe_name_normalizes_report_identifiers() -> None:
    assert safe_name("Dataset Report 123!") == "dataset_report_123"
    assert safe_name("___") == "unknown"


def test_build_html_report_contains_summary_and_tables() -> None:
    html = build_html_report(
        title="Test report",
        payload={
            "generated_at": "2026-07-09T00:00:00+00:00",
            "summary": {
                "rows": 2,
            },
            "sections": [
                {
                    "title": "Quality",
                    "body": "OK",
                }
            ],
        },
        tables={
            "items": [
                {
                    "id": "one",
                    "value": 1,
                }
            ]
        },
    )

    assert "Test report" in html
    assert "Quality" in html
    assert "items" in html
    assert "Raw JSON" in html


def test_write_report_bundle_creates_manifest() -> None:
    result = write_report_bundle(
        kind="pytest_report",
        source_id="helper",
        title="Pytest helper report",
        payload={
            "summary": {
                "rows": 1,
            },
            "sections": [],
        },
        tables={
            "rows": [
                {
                    "id": "row_1",
                    "value": "ok",
                }
            ]
        },
    )

    assert result["report_id"]
    assert "report.json" in result["files"]
    assert "report.html" in result["files"]
    assert "rows.csv" in result["files"]