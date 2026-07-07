from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Body, HTTPException

from sandbox_app.backend.data_generation.training_pairs import (
    generate_training_dataset,
)
from sandbox_app.backend.features.schema import FeatureSchemaError

router = APIRouter(prefix="/api/generate", tags=["generation"])

JsonBody = Annotated[dict[str, Any], Body()]


@router.post("/dataset")
def generate_dataset_endpoint(payload: JsonBody) -> dict[str, Any]:
    try:
        return generate_training_dataset(payload)
    except FeatureSchemaError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error