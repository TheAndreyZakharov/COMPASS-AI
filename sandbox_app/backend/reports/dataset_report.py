from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from sandbox_app.backend.reports.html_export import (
    ExportError,
    read_csv_rows,
    read_json,
    write_report_bundle,
)

SANDBOX_DIR = Path(__file__).resolve().parents[2]
GENERATED_DIR = SANDBOX_DIR / "data" / "generated"
IMPORTED_DIR = SANDBOX_DIR / "data" / "imported"


REQUIRED_FIELDS = {
    "employees": ["employee_id"],
    "tasks": ["task_id"],
    "assignment_history": ["employee_id", "task_id"],
}


def dataset_dir(dataset_id: str, dataset_kind: str | None = None) -> tuple[str, Path]:
    roots = []

    if dataset_kind:
        roots.append((dataset_kind, dataset_root(dataset_kind)))
    else:
        roots.extend(
            [
                ("generated", GENERATED_DIR),
                ("imported", IMPORTED_DIR),
            ]
        )

    for kind, root in roots:
        path = root / dataset_id
        if path.exists() and path.is_dir():
            return kind, path

    raise ExportError(f"Dataset not found: {dataset_id}")


def dataset_root(dataset_kind: str) -> Path:
    if dataset_kind == "generated":
        return GENERATED_DIR

    if dataset_kind == "imported":
        return IMPORTED_DIR

    raise ExportError(f"Unsupported dataset kind: {dataset_kind}")


def count_json_records(path: Path) -> int:
    payload = read_json(path, default=[])

    if isinstance(payload, list):
        return len(payload)

    if isinstance(payload, dict):
        for key in ("items", "records", "rows", "data"):
            value = payload.get(key)
            if isinstance(value, list):
                return len(value)

    return 0


def count_parquet_rows(path: Path) -> int | None:
    if not path.exists():
        return None

    try:
        import pyarrow.parquet as pq  # type: ignore[import-not-found]
    except ImportError:
        return None

    try:
        return int(pq.ParquetFile(path).metadata.num_rows)
    except (OSError, ValueError):
        return None


def load_table_rows(base_dir: Path, table_name: str, limit: int = 200) -> list[dict[str, Any]]:
    csv_path = base_dir / f"{table_name}.csv"
    json_path = base_dir / f"{table_name}.json"

    rows = read_csv_rows(csv_path, limit=limit)
    if rows:
        return rows

    payload = read_json(json_path, default=[])

    if isinstance(payload, list):
        return [
            row
            for row in payload[:limit]
            if isinstance(row, dict)
        ]

    if isinstance(payload, dict):
        for key in ("items", "records", "rows", "data"):
            value = payload.get(key)
            if isinstance(value, list):
                return [
                    row
                    for row in value[:limit]
                    if isinstance(row, dict)
                ]

    return []


def missing_required_summary(
    rows: list[dict[str, Any]],
    table_name: str,
) -> dict[str, Any]:
    required = REQUIRED_FIELDS.get(table_name, [])
    missing = Counter()

    for row in rows:
        for field_name in required:
            if row.get(field_name) in (None, ""):
                missing[field_name] += 1

    return {
        "table": table_name,
        "required_fields": required,
        "missing": dict(missing),
    }


def duplicate_id_count(rows: list[dict[str, Any]], field_name: str) -> int:
    values = [
        str(row.get(field_name))
        for row in rows
        if row.get(field_name) not in (None, "")
    ]
    counts = Counter(values)
    return sum(count - 1 for count in counts.values() if count > 1)


def status_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter(str(row.get("status", "unknown")) for row in rows)
    return dict(sorted(counts.items()))


def dataset_counts(base_dir: Path) -> dict[str, Any]:
    training_pairs_path = base_dir / "training_pairs.parquet"

    return {
        "employees": count_json_records(base_dir / "employees.json"),
        "tasks": count_json_records(base_dir / "tasks.json"),
        "assignment_history": count_json_records(base_dir / "assignment_history.json"),
        "training_pairs": count_parquet_rows(training_pairs_path),
        "has_training_pairs_parquet": training_pairs_path.exists(),
    }


def generate_dataset_report(
    dataset_id: str,
    dataset_kind: str | None = None,
) -> dict[str, Any]:
    kind, base_dir = dataset_dir(dataset_id, dataset_kind)
    employees = load_table_rows(base_dir, "employees")
    tasks = load_table_rows(base_dir, "tasks")
    history = load_table_rows(base_dir, "assignment_history")
    metadata = read_json(base_dir / "dataset_metadata.json", default={})
    generation_report = read_json(base_dir / "generation_report.json", default={})

    counts = dataset_counts(base_dir)
    quality = {
        "employees": missing_required_summary(employees, "employees"),
        "tasks": missing_required_summary(tasks, "tasks"),
        "assignment_history": missing_required_summary(history, "assignment_history"),
        "duplicate_employee_ids": duplicate_id_count(employees, "employee_id"),
        "duplicate_task_ids": duplicate_id_count(tasks, "task_id"),
        "task_status_counts": status_counts(tasks),
    }

    missing_files = [
        file_name
        for file_name in (
            "employees.json",
            "tasks.json",
            "assignment_history.json",
            "training_pairs.parquet",
            "dataset_metadata.json",
            "generation_report.json",
        )
        if not (base_dir / file_name).exists()
    ]

    payload = {
        "summary": {
            "dataset_kind": kind,
            "employees": counts["employees"],
            "tasks": counts["tasks"],
            "assignment_history": counts["assignment_history"],
            "training_pairs": counts["training_pairs"],
            "missing_files": len(missing_files),
        },
        "sections": [
            {
                "title": "Dataset generation report",
                "body": "Сводка по сгенерированному или импортированному dataset.",
            },
            {
                "title": "Dataset quality report",
                "body": "Проверены required fields, дубликаты идентификаторов и статусы задач.",
            },
        ],
        "dataset_id": dataset_id,
        "dataset_kind": kind,
        "dataset_dir": str(base_dir),
        "counts": counts,
        "quality": quality,
        "missing_files": missing_files,
        "metadata": metadata,
        "generation_report": generation_report,
    }

    return write_report_bundle(
        kind="dataset",
        source_id=dataset_id,
        title=f"Dataset report · {dataset_id}",
        payload=payload,
        tables={
            "employees_preview": employees[:50],
            "tasks_preview": tasks[:50],
            "assignment_history_preview": history[:50],
        },
    )