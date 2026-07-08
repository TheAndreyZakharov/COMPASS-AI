from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from sandbox_app.backend.data_generation.employees import TeamGenerationError, generate_team_dataset
from sandbox_app.backend.features.schema import FeatureSchemaError
from sandbox_app.backend.utils.json_io import JsonFileError

router = APIRouter(prefix="/generate", tags=["generation"])


@router.post("/team")
def generate_team(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    try:
        return generate_team_dataset(payload or {})
    except (TeamGenerationError, FeatureSchemaError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except JsonFileError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc