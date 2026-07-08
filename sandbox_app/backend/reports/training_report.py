from __future__ import annotations

import html
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sandbox_app.backend.reports.training_plots import (
    TrainingPlotError,
    generate_training_plots,
)
from sandbox_app.backend.training.train_session import TRAINING_SESSIONS_DIR


class TrainingReportError(RuntimeError):
    """Raised when training report generation fails."""


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise TrainingReportError(f"Could not read JSON file: {path}") from exc


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def relative_path(path: str | Path, base_dir: Path) -> str:
    path = Path(path)
    try:
        return path.relative_to(base_dir).as_posix()
    except ValueError:
        return path.as_posix()


def table_html(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "<p>No rows.</p>"

    columns = sorted({column for row in rows for column in row})

    header = "".join(f"<th>{html.escape(column)}</th>" for column in columns)
    body_rows = []

    for row in rows:
        cells = "".join(
            f"<td>{html.escape(str(row.get(column, '')))}</td>"
            for column in columns
        )
        body_rows.append(f"<tr>{cells}</tr>")

    return f"<table><thead><tr>{header}</tr></thead><tbody>{''.join(body_rows)}</tbody></table>"


def image_html(title: str, path: str, session_dir: Path) -> str:
    src = relative_path(path, session_dir)
    safe_title = html.escape(title.replace("_", " ").title())
    safe_src = html.escape(src)

    return (
        "<figure>"
        f"<img src=\"{safe_src}\" alt=\"{safe_title}\" />"
        f"<figcaption>{safe_title}</figcaption>"
        "</figure>"
    )


def render_model_section(
    model_name: str,
    plots: dict[str, str],
    session_dir: Path,
    model_metadata: dict[str, Any],
    metrics: dict[str, Any],
) -> str:
    images = "".join(
        image_html(plot_name, plot_path, session_dir)
        for plot_name, plot_path in sorted(plots.items())
    )

    return f"""
    <section class="card">
      <h2>{html.escape(model_name)}</h2>
      <p>
        Artifact format:
        <strong>{html.escape(str(model_metadata.get("artifact_format", "")))}</strong>
      </p>
      <h3>Plots</h3>
      <div class="plots-grid">{images or "<p>No plots generated.</p>"}</div>
      <h3>Metrics</h3>
      <pre>{html.escape(json.dumps(metrics, ensure_ascii=False, indent=2))}</pre>
      <h3>Model metadata</h3>
      <pre>{html.escape(json.dumps(model_metadata, ensure_ascii=False, indent=2))}</pre>
    </section>
    """


def render_training_report_html(
    session_dir: Path,
    manifest: dict[str, Any],
) -> str:
    summary = manifest.get("summary", {})
    comparison_metrics = manifest.get("comparison_metrics", [])
    plots = manifest.get("plots", {})
    session_plots = plots.get("session_plots", {})
    model_plots = plots.get("model_plots", {})
    artifacts = manifest.get("artifacts", [])

    session_images = "".join(
        image_html(plot_name, plot_path, session_dir)
        for plot_name, plot_path in sorted(session_plots.items())
    )

    model_sections = []

    for artifact in artifacts:
        model_name = artifact.get("model_name", "")
        model_sections.append(
            render_model_section(
                model_name=model_name,
                plots=model_plots.get(model_name, {}),
                session_dir=session_dir,
                model_metadata=artifact.get("metadata", {}),
                metrics=artifact.get("metrics", {}),
            )
        )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Training report · {html.escape(str(summary.get("session_id", "")))}</title>
  <style>
    body {{
      background: #0f172a;
      color: #e5e7eb;
      font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.55;
      margin: 0;
      padding: 32px;
    }}
    h1, h2, h3 {{
      color: #f8fafc;
    }}
    .card {{
      background: #111827;
      border: 1px solid #334155;
      border-radius: 16px;
      margin: 0 0 24px;
      padding: 20px;
    }}
    .grid {{
      display: grid;
      gap: 16px;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    }}
    .metric {{
      background: #020617;
      border: 1px solid #1f2937;
      border-radius: 12px;
      padding: 14px;
    }}
    .metric strong {{
      display: block;
      font-size: 24px;
    }}
    table {{
      border-collapse: collapse;
      width: 100%;
    }}
    th, td {{
      border-bottom: 1px solid #334155;
      padding: 8px;
      text-align: left;
      vertical-align: top;
    }}
    th {{
      color: #bfdbfe;
    }}
    pre {{
      background: #020617;
      border: 1px solid #1f2937;
      border-radius: 12px;
      overflow: auto;
      padding: 12px;
    }}
    .plots-grid {{
      display: grid;
      gap: 16px;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    }}
    figure {{
      background: #020617;
      border: 1px solid #1f2937;
      border-radius: 12px;
      margin: 0;
      padding: 12px;
    }}
    img {{
      background: #ffffff;
      border-radius: 8px;
      display: block;
      max-width: 100%;
    }}
    figcaption {{
      color: #cbd5e1;
      margin-top: 8px;
    }}
  </style>
</head>
<body>
  <h1>Training report</h1>

  <section class="card">
    <h2>Session summary</h2>
        <div class="grid">
            <div class="metric">
                <span>Session</span>
                <strong>{html.escape(str(summary.get("session_id", "")))}</strong>
            </div>
            <div class="metric">
                <span>Status</span>
                <strong>{html.escape(str(summary.get("status", "")))}</strong>
            </div>
            <div class="metric">
                <span>Rows</span>
                <strong>{html.escape(str(summary.get("rows", "")))}</strong>
            </div>
            <div class="metric">
                <span>Features</span>
                <strong>{html.escape(str(summary.get("feature_count", "")))}</strong>
            </div>
        </div>
    <pre>{html.escape(json.dumps(summary, ensure_ascii=False, indent=2))}</pre>
  </section>

  <section class="card">
    <h2>Model comparison</h2>
    <div class="plots-grid">{session_images or "<p>No session plots generated.</p>"}</div>
    {table_html(comparison_metrics)}
  </section>

  {''.join(model_sections)}
</body>
</html>
"""


def collect_artifacts(session_dir: Path) -> list[dict[str, Any]]:
    artifacts: list[dict[str, Any]] = []
    models_dir = session_dir / "models"

    if not models_dir.exists():
        return artifacts

    for model_dir in sorted(path for path in models_dir.iterdir() if path.is_dir()):
        metadata_path = model_dir / "model_metadata.json"
        metrics_path = model_dir / "metrics.json"
        validation_path = model_dir / "export_validation.json"

        artifacts.append(
            {
                "model_name": model_dir.name,
                "model_dir": str(model_dir),
                "metadata": read_json(metadata_path) if metadata_path.exists() else {},
                "metrics": read_json(metrics_path) if metrics_path.exists() else {},
                "export_validation": (
                    read_json(validation_path) if validation_path.exists() else {}
                ),
            }
        )

    return artifacts


def session_dir_for(session_id: str) -> Path:
    session_dir = TRAINING_SESSIONS_DIR / session_id

    if not session_dir.exists():
        raise TrainingReportError(f"Training session not found: {session_id}")

    return session_dir


def generate_training_report(session_id: str) -> dict[str, Any]:
    session_dir = session_dir_for(session_id)
    reports_dir = session_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    try:
        plots = generate_training_plots(session_dir)
    except TrainingPlotError as exc:
        raise TrainingReportError(str(exc)) from exc

    summary = read_json(session_dir / "session_summary.json")
    comparison_metrics = read_json(session_dir / "comparison_metrics.json")
    artifacts = collect_artifacts(session_dir)

    manifest = {
        "session_id": session_id,
        "status": "generated",
        "generated_at": utc_now_iso(),
        "summary": summary,
        "comparison_metrics": comparison_metrics,
        "artifacts": artifacts,
        "plots": plots,
        "paths": {
            "reports_dir": str(reports_dir),
            "training_report_html": str(reports_dir / "training_report.html"),
            "manifest": str(reports_dir / "report_manifest.json"),
        },
    }

    html_text = render_training_report_html(session_dir, manifest)
    html_path = reports_dir / "training_report.html"
    manifest_path = reports_dir / "report_manifest.json"

    html_path.write_text(html_text, encoding="utf-8")
    write_json(manifest_path, manifest)

    return manifest


def read_training_report(session_id: str) -> dict[str, Any]:
    session_dir = session_dir_for(session_id)
    manifest_path = session_dir / "reports" / "report_manifest.json"

    if not manifest_path.exists():
        raise TrainingReportError("Training report was not generated yet")

    return read_json(manifest_path)


def read_training_report_html(session_id: str) -> str:
    session_dir = session_dir_for(session_id)
    html_path = session_dir / "reports" / "training_report.html"

    if not html_path.exists():
        raise TrainingReportError("Training report HTML was not generated yet")

    return html_path.read_text(encoding="utf-8")


def list_training_reports() -> dict[str, Any]:
    TRAINING_SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    reports: list[dict[str, Any]] = []

    for session_dir in sorted(TRAINING_SESSIONS_DIR.iterdir(), reverse=True):
        if not session_dir.is_dir():
            continue

        manifest_path = session_dir / "reports" / "report_manifest.json"
        summary_path = session_dir / "session_summary.json"

        if not summary_path.exists():
            continue

        summary = read_json(summary_path)
        manifest = read_json(manifest_path) if manifest_path.exists() else {}

        reports.append(
            {
                "session_id": session_dir.name,
                "dataset_id": summary.get("dataset_id"),
                "status": manifest.get("status", "not_generated"),
                "generated_at": manifest.get("generated_at"),
                "trained_models": summary.get("trained_models", []),
                "report_html": manifest.get("paths", {}).get("training_report_html"),
            }
        )

    return {
        "reports": reports,
        "total": len(reports),
        "training_sessions_dir": str(TRAINING_SESSIONS_DIR),
    }