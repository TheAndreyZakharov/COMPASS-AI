from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from sandbox_app.backend.data_generation.tasks import TaskGenerationError, generate_tasks
from sandbox_app.backend.features.schema import FeatureSchemaError
from sandbox_app.backend.utils.json_io import JsonFileError

router = APIRouter(prefix="/generate", tags=["generation"])


@router.post("/tasks")
def generate_tasks_endpoint(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        result = generate_tasks(payload)
        return {
            "dataset_id": result["dataset_id"],
            "dataset_dir": result["dataset_dir"],
            "metadata": result["metadata"],
            "preview": result["preview"],
        }
    except (TaskGenerationError, FeatureSchemaError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except JsonFileError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc