from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from sandbox_app.backend.core.paths import PATHS
from sandbox_app.backend.utils.json_io import JsonFileError, read_json

router = APIRouter(prefix="/data-viewer", tags=["data-viewer"])

GENERATED_ROOT = getattr(PATHS, "generated_data_dir", PATHS.data_dir / "generated")
IMPORTED_ROOT = PATHS.data_dir / "imported"

DATASET_ID_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]{2,80}$")
TABLE_NAME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]{1,80}$")

SUPPORTED_TABLES = {
    "employees",
    "tasks",
    "backlog",
    "assignment_history",
    "training_pairs",
}

FILTERABLE_FIELDS = {
    "status",
    "role",
    "grade",
    "project_id",
    "priority",
}


class DataViewerError(RuntimeError):
    """Raised when a dataset cannot be read by the data viewer."""


def validate_dataset_id(dataset_id: str) -> str:
    if not DATASET_ID_RE.match(dataset_id):
        raise DataViewerError(
            "dataset_id must contain only letters, digits, underscores, or hyphens"
        )
    return dataset_id


def validate_table_name(table_name: str) -> str:
    if not TABLE_NAME_RE.match(table_name):
        raise DataViewerError(
            "table_name must contain only letters, digits, or underscores"
        )
    if table_name not in SUPPORTED_TABLES:
        allowed = ", ".join(sorted(SUPPORTED_TABLES))
        raise DataViewerError(f"Unsupported table '{table_name}'. Allowed: {allowed}")
    return table_name


def dataset_root(dataset_kind: str) -> Path:
    if dataset_kind == "generated":
        return GENERATED_ROOT
    if dataset_kind == "imported":
        return IMPORTED_ROOT
    raise DataViewerError("dataset_kind must be generated or imported")


def resolve_dataset_dir(dataset_id: str, dataset_kind: str | None = None) -> tuple[str, Path]:
    dataset_id = validate_dataset_id(dataset_id)

    if dataset_kind is not None:
        root = dataset_root(dataset_kind)
        path = root / dataset_id
        if path.exists() and path.is_dir():
            return dataset_kind, path
        raise DataViewerError(f"{dataset_kind} dataset '{dataset_id}' not found")

    for kind, root in (("generated", GENERATED_ROOT), ("imported", IMPORTED_ROOT)):
        path = root / dataset_id
        if path.exists() and path.is_dir():
            return kind, path

    raise DataViewerError(f"Dataset '{dataset_id}' not found")


def safe_read_json(path: Path) -> Any:
    if not path.exists():
        raise DataViewerError(f"File not found: {path.name}")
    return read_json(path)


def read_json_table(path: Path) -> list[dict[str, Any]]:
    payload = safe_read_json(path)

    if isinstance(payload, list):
        return normalize_rows(payload)

    if isinstance(payload, dict):
        for key in ("items", "rows", "data", "records"):
            value = payload.get(key)
            if isinstance(value, list):
                return normalize_rows(value)

    raise DataViewerError(f"JSON table must contain a list of records: {path.name}")


def read_csv_table(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise DataViewerError(f"File not found: {path.name}")

    with path.open("r", encoding="utf-8", newline="") as file_obj:
        reader = csv.DictReader(file_obj)
        return [dict(row) for row in reader]


def read_parquet_table(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise DataViewerError(f"File not found: {path.name}")

    try:
        import pandas as pd
    except ImportError as exc:
        raise DataViewerError("pandas is required to read parquet tables") from exc

    try:
        frame = pd.read_parquet(path)
    except Exception as exc:
        raise DataViewerError(
            "Could not read parquet table. Check pyarrow or fastparquet."
        ) from exc

    return normalize_rows(frame.to_dict(orient="records"))


def normalize_rows(rows: list[Any]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []

    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise DataViewerError(f"Row {index} is not an object")
        normalized.append(row)

    return normalized


def table_path(dataset_dir: Path, table_name: str) -> tuple[Path, str]:
    table_name = validate_table_name(table_name)

    candidates = []
    if table_name == "training_pairs":
        candidates = [
            (dataset_dir / "training_pairs.parquet", "parquet"),
            (dataset_dir / "training_pairs.csv", "csv"),
            (dataset_dir / "training_pairs.json", "json"),
        ]
    else:
        candidates = [
            (dataset_dir / f"{table_name}.json", "json"),
            (dataset_dir / f"{table_name}.csv", "csv"),
        ]

    for path, file_format in candidates:
        if path.exists():
            return path, file_format

    raise DataViewerError(f"Table '{table_name}' not found in dataset")


def read_table(dataset_dir: Path, table_name: str) -> tuple[list[dict[str, Any]], str, Path]:
    path, file_format = table_path(dataset_dir, table_name)

    if file_format == "json":
        rows = read_json_table(path)
    elif file_format == "csv":
        rows = read_csv_table(path)
    elif file_format == "parquet":
        rows = read_parquet_table(path)
    else:
        raise DataViewerError(f"Unsupported table format: {file_format}")

    return rows, file_format, path


def parse_jsonish(value: Any) -> Any:
    if not isinstance(value, str):
        return value

    stripped = value.strip()
    if not stripped:
        return value

    if stripped[0] not in "[{":
        return value

    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        return value


def normalize_record_for_response(record: dict[str, Any]) -> dict[str, Any]:
    return {key: parse_jsonish(value) for key, value in record.items()}


def row_matches_search(row: dict[str, Any], search: str | None) -> bool:
    if not search:
        return True

    needle = search.lower()
    return any(needle in str(value).lower() for value in row.values())


def row_matches_filters(row: dict[str, Any], filters: dict[str, str | None]) -> bool:
    for field, expected in filters.items():
        if expected is None:
            continue

        actual = row.get(field)
        if actual is None:
            return False

        if str(actual).lower() != expected.lower():
            return False

    return True


def filter_rows(
    rows: list[dict[str, Any]],
    search: str | None,
    filters: dict[str, str | None],
) -> list[dict[str, Any]]:
    return [
        row
        for row in rows
        if row_matches_search(row, search) and row_matches_filters(row, filters)
    ]


def paginate_rows(
    rows: list[dict[str, Any]],
    page: int,
    page_size: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if page < 1:
        raise DataViewerError("page must be greater than or equal to 1")

    if page_size < 1 or page_size > 500:
        raise DataViewerError("page_size must be between 1 and 500")

    total = len(rows)
    start = (page - 1) * page_size
    end = start + page_size

    items = [normalize_record_for_response(row) for row in rows[start:end]]

    return items, {
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": (total + page_size - 1) // page_size,
        "has_next": end < total,
        "has_previous": page > 1,
    }


def read_optional_metadata(dataset_dir: Path) -> dict[str, Any]:
    metadata_candidates = [
        dataset_dir / "dataset_metadata.json",
        dataset_dir / "team_metadata.json",
        dataset_dir / "task_metadata.json",
        dataset_dir / "history_metadata.json",
        dataset_dir / "import_metadata.json",
    ]

    result: dict[str, Any] = {}
    for path in metadata_candidates:
        if path.exists():
            try:
                payload = read_json(path)
            except JsonFileError:
                continue
            if isinstance(payload, dict):
                result[path.stem] = payload

    return result


def dataset_table_counts(dataset_dir: Path) -> dict[str, int]:
    counts: dict[str, int] = {}

    for table_name in sorted(SUPPORTED_TABLES):
        try:
            rows, _, _ = read_table(dataset_dir, table_name)
        except DataViewerError:
            continue
        counts[table_name] = len(rows)

    return counts


def dataset_descriptor(dataset_dir: Path, dataset_kind: str) -> dict[str, Any]:
    metadata = read_optional_metadata(dataset_dir)
    counts = dataset_table_counts(dataset_dir)
    dataset_metadata = metadata.get("dataset_metadata", {})

    return {
        "dataset_id": dataset_dir.name,
        "dataset_kind": dataset_kind,
        "dataset_type": dataset_metadata.get("dataset_type", dataset_kind),
        "domain_profile": dataset_metadata.get("domain_profile"),
        "dataset_mode": dataset_metadata.get("dataset_mode"),
        "created_at": dataset_metadata.get("created_at"),
        "counts": counts,
        "available_tables": sorted(counts),
        "path": str(dataset_dir),
    }


def list_dataset_descriptors(root: Path, dataset_kind: str) -> list[dict[str, Any]]:
    root.mkdir(parents=True, exist_ok=True)

    datasets = [
        dataset_descriptor(path, dataset_kind)
        for path in sorted(root.iterdir())
        if path.is_dir()
    ]

    return sorted(
        datasets,
        key=lambda item: str(item.get("created_at") or item["dataset_id"]),
        reverse=True,
    )


def find_record(
    rows: list[dict[str, Any]],
    field_name: str,
    field_value: str,
) -> dict[str, Any]:
    for row in rows:
        if str(row.get(field_name)) == field_value:
            return normalize_record_for_response(row)

    raise DataViewerError(f"Record '{field_value}' not found")


def build_employee_history(
    dataset_dir: Path,
    employee_id: str,
) -> dict[str, Any]:
    history_rows, _, _ = read_table(dataset_dir, "assignment_history")
    employee_history = [
        normalize_record_for_response(row)
        for row in history_rows
        if str(row.get("employee_id")) == employee_id
    ]

    employee_history.sort(key=lambda row: str(row.get("completed_at", "")), reverse=True)

    return {
        "employee_id": employee_id,
        "count": len(employee_history),
        "items": employee_history,
    }


def build_kanban(dataset_dir: Path) -> dict[str, Any]:
    tasks, _, _ = read_table(dataset_dir, "tasks")
    columns = {
        "todo": [],
        "in_progress": [],
        "review": [],
        "done": [],
        "blocked": [],
        "failed": [],
    }

    for task in tasks:
        status = str(task.get("status", "todo"))
        if status not in columns:
            columns[status] = []
        columns[status].append(normalize_record_for_response(task))

    counts = {status: len(items) for status, items in columns.items()}

    return {
        "columns": columns,
        "counts": counts,
        "total": sum(counts.values()),
    }


@router.get("/datasets")
def list_datasets() -> dict[str, Any]:
    try:
        generated = list_dataset_descriptors(GENERATED_ROOT, "generated")
        imported = list_dataset_descriptors(IMPORTED_ROOT, "imported")

        return {
            "generated": generated,
            "imported": imported,
            "counts": {
                "generated": len(generated),
                "imported": len(imported),
                "total": len(generated) + len(imported),
            },
        }
    except (DataViewerError, JsonFileError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/datasets/{dataset_id}/summary")
def get_dataset_summary(
    dataset_id: str,
    dataset_kind: str | None = Query(default=None),
) -> dict[str, Any]:
    try:
        kind, dataset_dir = resolve_dataset_dir(dataset_id, dataset_kind)

        return {
            "dataset": dataset_descriptor(dataset_dir, kind),
            "metadata": read_optional_metadata(dataset_dir),
            "summary_counts": dataset_table_counts(dataset_dir),
        }
    except (DataViewerError, JsonFileError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/datasets/{dataset_id}/employees/{employee_id}")
def get_employee_profile(
    dataset_id: str,
    employee_id: str,
    dataset_kind: str | None = Query(default=None),
) -> dict[str, Any]:
    try:
        _, dataset_dir = resolve_dataset_dir(dataset_id, dataset_kind)
        rows, file_format, path = read_table(dataset_dir, "employees")

        return {
            "dataset_id": dataset_id,
            "table": "employees",
            "format": file_format,
            "source": str(path),
            "employee": find_record(rows, "employee_id", employee_id),
        }
    except (DataViewerError, JsonFileError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/datasets/{dataset_id}/tasks/{task_id}")
def get_task_profile(
    dataset_id: str,
    task_id: str,
    dataset_kind: str | None = Query(default=None),
) -> dict[str, Any]:
    try:
        _, dataset_dir = resolve_dataset_dir(dataset_id, dataset_kind)
        rows, file_format, path = read_table(dataset_dir, "tasks")

        return {
            "dataset_id": dataset_id,
            "table": "tasks",
            "format": file_format,
            "source": str(path),
            "task": find_record(rows, "task_id", task_id),
        }
    except (DataViewerError, JsonFileError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/datasets/{dataset_id}/employees/{employee_id}/history")
def get_employee_history(
    dataset_id: str,
    employee_id: str,
    dataset_kind: str | None = Query(default=None),
) -> dict[str, Any]:
    try:
        _, dataset_dir = resolve_dataset_dir(dataset_id, dataset_kind)
        return build_employee_history(dataset_dir, employee_id)
    except (DataViewerError, JsonFileError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/datasets/{dataset_id}/kanban")
def get_dataset_kanban(
    dataset_id: str,
    dataset_kind: str | None = Query(default=None),
) -> dict[str, Any]:
    try:
        _, dataset_dir = resolve_dataset_dir(dataset_id, dataset_kind)
        return build_kanban(dataset_dir)
    except (DataViewerError, JsonFileError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/datasets/{dataset_id}/{table_name}")
def get_dataset_table(
    dataset_id: str,
    table_name: str,
    dataset_kind: str | None = Query(default=None),
    page: int = Query(default=1),
    page_size: int = Query(default=50),
    search: str | None = Query(default=None),
    status: str | None = Query(default=None),
    role: str | None = Query(default=None),
    grade: str | None = Query(default=None),
    project_id: str | None = Query(default=None),
    priority: str | None = Query(default=None),
) -> dict[str, Any]:
    try:
        _, dataset_dir = resolve_dataset_dir(dataset_id, dataset_kind)
        rows, file_format, path = read_table(dataset_dir, table_name)

        filters = {
            "status": status,
            "role": role,
            "grade": grade,
            "project_id": project_id,
            "priority": priority,
        }
        filtered_rows = filter_rows(rows, search, filters)
        items, pagination = paginate_rows(filtered_rows, page, page_size)

        return {
            "dataset_id": dataset_id,
            "table": validate_table_name(table_name),
            "format": file_format,
            "source": str(path),
            "filters": {
                key: value
                for key, value in filters.items()
                if key in FILTERABLE_FIELDS and value is not None
            },
            "search": search,
            "pagination": pagination,
            "items": items,
        }
    except (DataViewerError, JsonFileError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc