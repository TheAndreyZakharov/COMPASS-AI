from __future__ import annotations

import csv
import io
import json
import re
import shutil
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sandbox_app.backend.core.paths import PATHS
from sandbox_app.backend.utils.validation import validate_records_against_contract

IMPORTED_ROOT = PATHS.data_dir / "imported"

SUPPORTED_TABLES = {
    "employees",
    "tasks",
    "assignment_history",
    "training_pairs",
}

SUPPORTED_FORMATS = {
    ".csv": "csv",
    ".json": "json",
    ".parquet": "parquet",
}

DATASET_ID_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]{2,80}$")


class ImportDataError(RuntimeError):
    """Raised when external dataset import fails."""


@dataclass(frozen=True)
class ImportSource:
    table_name: str
    filename: str
    content: bytes

    @property
    def suffix(self) -> str:
        return Path(self.filename).suffix.lower()


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def validate_dataset_id(dataset_id: str) -> str:
    if not DATASET_ID_RE.match(dataset_id):
        raise ImportDataError(
            "dataset_id must contain only letters, digits, underscores, or hyphens"
        )
    return dataset_id


def validate_table_name(table_name: str) -> str:
    if table_name not in SUPPORTED_TABLES:
        allowed = ", ".join(sorted(SUPPORTED_TABLES))
        raise ImportDataError(f"Unsupported table '{table_name}'. Allowed: {allowed}")
    return table_name


def infer_table_name(filename: str, explicit_table_name: str | None = None) -> str:
    if explicit_table_name:
        return validate_table_name(explicit_table_name)

    stem = Path(filename).stem.lower()
    normalized = stem.replace("-", "_")

    aliases = {
        "history": "assignment_history",
        "assignment_history": "assignment_history",
        "employees": "employees",
        "tasks": "tasks",
        "training_pairs": "training_pairs",
    }

    table_name = aliases.get(normalized)
    if table_name is None:
        raise ImportDataError(
            f"Could not infer table name from filename '{filename}'. "
            "Use employees, tasks, assignment_history, or training_pairs."
        )

    return table_name


def parse_jsonish_cell(value: Any) -> Any:
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


def normalize_records(rows: list[Any]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []

    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ImportDataError(f"Row {index} must be an object")

        normalized.append(
            {key: parse_jsonish_cell(value) for key, value in row.items()}
        )

    return normalized


def read_csv_records(content: bytes) -> list[dict[str, Any]]:
    text = content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))

    if not reader.fieldnames:
        raise ImportDataError("CSV file must contain a header row")

    return normalize_records([dict(row) for row in reader])


def read_json_records(content: bytes) -> list[dict[str, Any]]:
    try:
        payload = json.loads(content.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise ImportDataError(f"Invalid JSON: {exc}") from exc

    if isinstance(payload, list):
        return normalize_records(payload)

    if isinstance(payload, dict):
        for key in ("items", "rows", "records", "data"):
            value = payload.get(key)
            if isinstance(value, list):
                return normalize_records(value)

    raise ImportDataError("JSON file must contain a list or object with rows/items/data")


def read_parquet_records(content: bytes) -> list[dict[str, Any]]:
    try:
        import pandas as pd
    except ImportError as exc:
        raise ImportDataError("pandas is required to read Parquet files") from exc

    try:
        frame = pd.read_parquet(io.BytesIO(content))
    except Exception as exc:
        raise ImportDataError("Could not read Parquet file. Check pyarrow.") from exc

    return normalize_records(frame.to_dict(orient="records"))


def read_import_source(source: ImportSource) -> tuple[list[dict[str, Any]], str]:
    suffix = source.suffix
    file_format = SUPPORTED_FORMATS.get(suffix)

    if file_format is None:
        allowed = ", ".join(sorted(SUPPORTED_FORMATS))
        raise ImportDataError(f"Unsupported file extension '{suffix}'. Allowed: {allowed}")

    if file_format == "csv":
        return read_csv_records(source.content), file_format

    if file_format == "json":
        return read_json_records(source.content), file_format

    if file_format == "parquet":
        return read_parquet_records(source.content), file_format

    raise ImportDataError(f"Unsupported file format: {file_format}")


def preview_records(records: list[dict[str, Any]], limit: int = 20) -> list[dict[str, Any]]:
    return records[:limit]


def csv_safe_value(value: Any) -> str:
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    if value is None:
        return ""
    return str(value)


def write_json_file(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def write_csv_file(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames: list[str] = []
    for record in records:
        for field_name in record:
            if field_name not in fieldnames:
                fieldnames.append(field_name)

    with path.open("w", encoding="utf-8", newline="") as file_obj:
        writer = csv.DictWriter(file_obj, fieldnames=fieldnames)
        writer.writeheader()

        for record in records:
            writer.writerow(
                {field_name: csv_safe_value(record.get(field_name)) for field_name in fieldnames}
            )


def write_parquet_file(path: Path, records: list[dict[str, Any]]) -> None:
    try:
        import pandas as pd
    except ImportError as exc:
        raise ImportDataError("pandas is required to write Parquet files") from exc

    normalized = [
        {
            key: json.dumps(value, ensure_ascii=False, sort_keys=True)
            if isinstance(value, (dict, list))
            else value
            for key, value in record.items()
        }
        for record in records
    ]

    frame = pd.DataFrame(normalized)
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        frame.to_parquet(path, index=False)
    except Exception as exc:
        raise ImportDataError("Could not write Parquet file. Check pyarrow.") from exc


def save_imported_table(
    dataset_dir: Path,
    table_name: str,
    records: list[dict[str, Any]],
) -> dict[str, str]:
    paths: dict[str, str] = {}

    if table_name == "training_pairs":
        parquet_path = dataset_dir / "training_pairs.parquet"
        write_parquet_file(parquet_path, records)
        paths["parquet"] = str(parquet_path)
    else:
        json_path = dataset_dir / f"{table_name}.json"
        csv_path = dataset_dir / f"{table_name}.csv"
        write_json_file(json_path, records)
        write_csv_file(csv_path, records)
        paths["json"] = str(json_path)
        paths["csv"] = str(csv_path)

    return paths


def build_table_report(
    source: ImportSource,
    records: list[dict[str, Any]],
    file_format: str,
) -> dict[str, Any]:
    validation_errors = validate_records_against_contract(source.table_name, records)
    warnings: list[str] = []

    if not records:
        warnings.append("Imported table is empty")

    return {
        "table_name": source.table_name,
        "filename": source.filename,
        "format": file_format,
        "rows": len(records),
        "columns": sorted({key for record in records for key in record}),
        "validation_errors": validation_errors,
        "warnings": warnings,
        "preview": preview_records(records),
    }


def preview_import_source(source: ImportSource) -> dict[str, Any]:
    records, file_format = read_import_source(source)
    return build_table_report(source, records, file_format)


def import_dataset_from_sources(
    dataset_id: str,
    sources: list[ImportSource],
    *,
    domain_profile: str | None = None,
    overwrite: bool = False,
    imported_by: str = "local_user",
) -> dict[str, Any]:
    dataset_id = validate_dataset_id(dataset_id)

    if not sources:
        raise ImportDataError("At least one file is required")

    dataset_dir = IMPORTED_ROOT / dataset_id
    if dataset_dir.exists() and not overwrite:
        raise ImportDataError(
            f"Imported dataset '{dataset_id}' already exists. Set overwrite=true."
        )

    table_payloads: dict[str, list[dict[str, Any]]] = {}
    table_reports: list[dict[str, Any]] = []

    for source in sources:
        validate_table_name(source.table_name)

        if source.table_name in table_payloads:
            raise ImportDataError(f"Duplicate table import: {source.table_name}")

        records, file_format = read_import_source(source)
        report = build_table_report(source, records, file_format)

        if report["validation_errors"]:
            table_reports.append(report)
            continue

        table_payloads[source.table_name] = records
        table_reports.append(report)

    validation_errors = [
        error
        for report in table_reports
        for error in report.get("validation_errors", [])
    ]

    if validation_errors:
        return {
            "status": "validation_failed",
            "dataset_id": dataset_id,
            "dataset_dir": str(dataset_dir),
            "tables": table_reports,
            "validation_errors": validation_errors,
            "warnings": [
                warning
                for report in table_reports
                for warning in report.get("warnings", [])
            ],
            "preview": {
                report["table_name"]: report.get("preview", [])
                for report in table_reports
            },
        }

    if dataset_dir.exists():
        shutil.rmtree(dataset_dir)

    dataset_dir.mkdir(parents=True, exist_ok=True)

    saved_paths: dict[str, dict[str, str]] = {}
    for table_name, records in table_payloads.items():
        saved_paths[table_name] = save_imported_table(dataset_dir, table_name, records)

    counts = {table_name: len(records) for table_name, records in table_payloads.items()}

    metadata = {
        "dataset_id": dataset_id,
        "dataset_type": "imported",
        "domain_profile": domain_profile,
        "created_at": utc_now_iso(),
        "imported_by": imported_by,
        "counts": counts,
        "tables": [
            {
                "table_name": report["table_name"],
                "filename": report["filename"],
                "format": report["format"],
                "rows": report["rows"],
                "columns": report["columns"],
            }
            for report in table_reports
        ],
        "warnings": [
            warning
            for report in table_reports
            for warning in report.get("warnings", [])
        ],
    }

    write_json_file(dataset_dir / "import_metadata.json", metadata)
    write_json_file(dataset_dir / "dataset_metadata.json", metadata)

    return {
        "status": "imported",
        "dataset_id": dataset_id,
        "dataset_dir": str(dataset_dir),
        "paths": saved_paths,
        "metadata": metadata,
        "tables": table_reports,
        "validation_errors": [],
        "warnings": metadata["warnings"],
        "preview": {
            report["table_name"]: report.get("preview", [])
            for report in table_reports
        },
    }