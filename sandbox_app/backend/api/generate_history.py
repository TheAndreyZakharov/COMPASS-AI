from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Body, HTTPException

from sandbox_app.backend.data_generation.history import generate_history

router = APIRouter(prefix="/api/generate", tags=["generation"])

JsonBody = Annotated[dict[str, Any], Body()]


@router.post("/history")
def generate_history_endpoint(payload: JsonBody) -> dict[str, Any]:
    try:
        return generate_history(payload)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error