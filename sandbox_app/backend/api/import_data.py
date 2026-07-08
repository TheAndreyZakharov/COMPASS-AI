from __future__ import annotations

import json
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from sandbox_app.backend.utils.importers import (
    ImportDataError,
    ImportSource,
    import_dataset_from_sources,
    infer_table_name,
    preview_import_source,
)

router = APIRouter(prefix="/import-data", tags=["import-data"])


def parse_bool_form(value: str | bool | None, default: bool = False) -> bool:
    if value is None:
        return default

    if isinstance(value, bool):
        return value

    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def parse_table_names(raw: str | None) -> list[str] | None:
    if raw is None or not raw.strip():
        return None

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ImportDataError("table_names must be a JSON array") from exc

    if not isinstance(payload, list) or not all(isinstance(item, str) for item in payload):
        raise ImportDataError("table_names must be a JSON array of strings")

    return payload


async def upload_to_source(
    upload: UploadFile,
    explicit_table_name: str | None = None,
) -> ImportSource:
    filename = upload.filename or "uploaded_file"
    content = await upload.read()

    if not content:
        raise ImportDataError(f"Uploaded file '{filename}' is empty")

    table_name = infer_table_name(filename, explicit_table_name)

    return ImportSource(
        table_name=table_name,
        filename=filename,
        content=content,
    )


@router.get("/supported-tables")
def get_supported_tables() -> dict[str, object]:
    return {
        "supported_tables": [
            "employees",
            "tasks",
            "assignment_history",
            "training_pairs",
        ],
        "supported_formats": ["csv", "json", "parquet"],
        "save_location": "sandbox_app/data/imported/<dataset_id>",
        "rules": {
            "dataset_id": "letters, digits, underscores, hyphens, 3-81 chars",
            "overwrite": "existing imported dataset is protected unless overwrite=true",
            "training_pairs": "saved as Parquet",
        },
    }


@router.post("/preview")
async def preview_import_file(
    file: Annotated[UploadFile, File()],
    table_name: Annotated[str | None, Form()] = None,
) -> dict[str, object]:
    try:
        source = await upload_to_source(file, table_name)
        return preview_import_source(source)
    except ImportDataError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/datasets")
async def import_dataset(
    files: Annotated[list[UploadFile], File()],
    dataset_id: Annotated[str, Form()],
    domain_profile: Annotated[str | None, Form()] = None,
    overwrite: Annotated[str | bool | None, Form()] = None,
    table_names: Annotated[str | None, Form()] = None,
) -> dict[str, object]:
    try:
        explicit_table_names = parse_table_names(table_names)
        sources: list[ImportSource] = []

        for index, upload in enumerate(files):
            explicit_table_name = None
            if explicit_table_names is not None:
                explicit_table_name = explicit_table_names[index]

            sources.append(await upload_to_source(upload, explicit_table_name))

        return import_dataset_from_sources(
            dataset_id=dataset_id,
            sources=sources,
            domain_profile=domain_profile,
            overwrite=parse_bool_form(overwrite),
        )
    except IndexError as exc:
        raise HTTPException(
            status_code=400,
            detail="table_names length must match files length",
        ) from exc
    except ImportDataError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc