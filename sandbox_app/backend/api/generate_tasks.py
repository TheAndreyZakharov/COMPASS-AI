from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Body, HTTPException

from sandbox_app.backend.data_generation.tasks import generate_tasks
from sandbox_app.backend.features.schema import FeatureSchemaError

router = APIRouter(prefix="/api/generate", tags=["generation"])

JsonBody = Annotated[dict[str, Any], Body()]


@router.post("/tasks")
def generate_tasks_endpoint(payload: JsonBody) -> dict[str, Any]:
    try:
        return generate_tasks(payload)
    except FeatureSchemaError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error