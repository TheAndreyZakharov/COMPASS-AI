from __future__ import annotations

import csv
import html
import json
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

SANDBOX_DIR = Path(__file__).resolve().parents[2]
REPORTS_DIR = SANDBOX_DIR / "reports"
EXPORTS_DIR = SANDBOX_DIR / "data" / "exports"


class ExportError(RuntimeError):
    """Raised when report export cannot be generated."""


def utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def short_id() -> str:
    return uuid4().hex[:8]


def report_id(kind: str, source_id: str) -> str:
    safe_kind = safe_name(kind)
    safe_source = safe_name(source_id)
    stamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    return f"{stamp}_{safe_kind}_{safe_source}_{short_id()}"


def safe_name(value: str) -> str:
    cleaned = "".join(
        char.lower() if char.isalnum() else "_"
        for char in str(value).strip()
    )
    cleaned = "_".join(part for part in cleaned.split("_") if part)
    return cleaned or "unknown"


def ensure_dirs(report_key: str) -> tuple[Path, Path]:
    report_dir = REPORTS_DIR / report_key
    export_dir = EXPORTS_DIR / report_key
    report_dir.mkdir(parents=True, exist_ok=True)
    export_dir.mkdir(parents=True, exist_ok=True)
    return report_dir, export_dir


def read_json(path: Path, default: Any | None = None) -> Any:
    if not path.exists():
        return {} if default is None else default

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {} if default is None else default


def write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def read_csv_rows(path: Path, limit: int | None = None) -> list[dict[str, Any]]:
    if not path.exists():
        return []

    rows: list[dict[str, Any]] = []

    with path.open("r", encoding="utf-8", newline="") as file_obj:
        reader = csv.DictReader(file_obj)
        for row in reader:
            rows.append(dict(row))
            if limit is not None and len(rows) >= limit:
                break

    return rows


def write_csv_rows(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return

    fieldnames = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8", newline="") as file_obj:
        writer = csv.DictWriter(file_obj, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def html_table(rows: list[dict[str, Any]], max_rows: int = 50) -> str:
    if not rows:
        return "<p class='muted'>No rows.</p>"

    limited = rows[:max_rows]
    columns = sorted({key for row in limited for key in row})

    header = "".join(f"<th>{html.escape(str(column))}</th>" for column in columns)
    body = "".join(
        "<tr>"
        + "".join(
            f"<td>{html.escape(format_cell(row.get(column)))}</td>"
            for column in columns
        )
        + "</tr>"
        for row in limited
    )

    return (
        "<div class='table-wrap'>"
        "<table><thead><tr>"
        f"{header}"
        "</tr></thead><tbody>"
        f"{body}"
        "</tbody></table></div>"
    )


def format_cell(value: Any) -> str:
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)

    if value is None:
        return ""

    return str(value)


def metric_cards(metrics: dict[str, Any]) -> str:
    cards = []

    for key, value in metrics.items():
        cards.append(
            "<article class='card'>"
            f"<span>{html.escape(str(key))}</span>"
            f"<strong>{html.escape(format_cell(value))}</strong>"
            "</article>"
        )

    return "<section class='cards'>" + "".join(cards) + "</section>"


def build_html_report(
    title: str,
    payload: dict[str, Any],
    tables: dict[str, list[dict[str, Any]]] | None = None,
) -> str:
    tables = tables or {}
    summary = payload.get("summary", {})
    sections = payload.get("sections", [])

    rendered_sections = []

    for section in sections:
        if not isinstance(section, dict):
            continue

        heading = html.escape(str(section.get("title", "Section")))
        body = html.escape(str(section.get("body", "")))
        rendered_sections.append(f"<section><h2>{heading}</h2><p>{body}</p></section>")

    rendered_tables = []

    for table_name, rows in tables.items():
        rendered_tables.append(
            "<section>"
            f"<h2>{html.escape(table_name)}</h2>"
            f"{html_table(rows)}"
            "</section>"
        )

    raw_json = html.escape(json.dumps(payload, ensure_ascii=False, indent=2))

    return f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <title>{html.escape(title)}</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      margin: 0;
      background: #f8fafc;
      color: #0f172a;
    }}
    main {{
      margin: 0 auto;
      max-width: 1180px;
      padding: 32px;
    }}
    header,
    section {{
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 18px;
      margin-bottom: 18px;
      padding: 22px;
    }}
    h1,
    h2 {{
      margin: 0 0 12px;
    }}
    .muted {{
      color: #64748b;
    }}
    .cards {{
      display: grid;
      gap: 12px;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      margin-top: 16px;
    }}
    .card {{
      border: 1px solid #e2e8f0;
      border-radius: 14px;
      padding: 14px;
    }}
    .card span {{
      color: #64748b;
      display: block;
      font-size: 12px;
      margin-bottom: 6px;
    }}
    .card strong {{
      font-size: 22px;
    }}
    .table-wrap {{
      overflow-x: auto;
    }}
    table {{
      border-collapse: collapse;
      width: 100%;
    }}
    th,
    td {{
      border-bottom: 1px solid #e2e8f0;
      font-size: 13px;
      padding: 9px;
      text-align: left;
      vertical-align: top;
    }}
    th {{
      background: #f1f5f9;
    }}
    pre {{
      background: #0f172a;
      border-radius: 14px;
      color: #e2e8f0;
      overflow-x: auto;
      padding: 16px;
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <p class="muted">COMPASS AI Sandbox export</p>
      <h1>{html.escape(title)}</h1>
      <p class="muted">Generated at {html.escape(str(payload.get("generated_at", "")))}</p>
      {metric_cards(summary) if isinstance(summary, dict) else ""}
    </header>
    {"".join(rendered_sections)}
    {"".join(rendered_tables)}
    <section>
      <h2>Raw JSON</h2>
      <pre>{raw_json}</pre>
    </section>
  </main>
</body>
</html>
"""


def copy_to_exports(report_dir: Path, export_dir: Path) -> None:
    for path in report_dir.iterdir():
        if path.is_file():
            shutil.copy2(path, export_dir / path.name)


def write_report_bundle(
    kind: str,
    source_id: str,
    title: str,
    payload: dict[str, Any],
    tables: dict[str, list[dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    key = report_id(kind, source_id)
    report_dir, export_dir = ensure_dirs(key)
    tables = tables or {}

    payload = {
        **payload,
        "report_id": key,
        "report_kind": kind,
        "source_id": source_id,
        "generated_at": utc_now_iso(),
    }

    json_path = report_dir / "report.json"
    html_path = report_dir / "report.html"
    manifest_path = report_dir / "report_manifest.json"

    write_json(json_path, payload)
    html_path.write_text(build_html_report(title, payload, tables), encoding="utf-8")

    csv_files = []

    for table_name, rows in tables.items():
        csv_name = f"{safe_name(table_name)}.csv"
        csv_path = report_dir / csv_name
        write_csv_rows(csv_path, rows)
        csv_files.append(csv_name)

    manifest = {
        "report_id": key,
        "report_kind": kind,
        "source_id": source_id,
        "title": title,
        "generated_at": payload["generated_at"],
        "files": ["report.json", "report.html", "report_manifest.json", *csv_files],
        "report_dir": str(report_dir),
        "export_dir": str(export_dir),
    }
    write_json(manifest_path, manifest)
    copy_to_exports(report_dir, export_dir)

    return {
        **manifest,
        "summary": payload.get("summary", {}),
        "payload": payload,
    }


def list_export_reports() -> list[dict[str, Any]]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    reports: list[dict[str, Any]] = []

    for report_dir in sorted(REPORTS_DIR.iterdir(), reverse=True):
        if not report_dir.is_dir():
            continue

        manifest = read_json(report_dir / "report_manifest.json", default={})
        if isinstance(manifest, dict) and manifest:
            reports.append(manifest)

    return reports


def safe_report_file(report_key: str, file_name: str) -> Path:
    safe_key = safe_name(report_key)
    requested_name = Path(file_name).name

    candidates = [
        REPORTS_DIR / safe_key / requested_name,
        EXPORTS_DIR / safe_key / requested_name,
    ]

    for candidate in candidates:
        try:
            resolved = candidate.resolve()
        except OSError as exc:
            raise ExportError("Invalid export path") from exc

        roots = [REPORTS_DIR.resolve(), EXPORTS_DIR.resolve()]
        if (
            any(resolved == root or root in resolved.parents for root in roots)
            and resolved.exists()
            and resolved.is_file()
        ):
            return resolved

    raise ExportError(f"Export file not found: {file_name}")