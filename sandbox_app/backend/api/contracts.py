from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from sandbox_app.backend.core.data_contracts import (
    get_contract,
    list_contract_names,
    load_data_contracts,
)

router = APIRouter(prefix="/api", tags=["contracts"])


@router.get("/contracts")
def contracts() -> dict[str, Any]:
    payload = load_data_contracts()

    return {
        "version": payload.get("version"),
        "storage_formats": payload.get("storage_formats", {}),
        "contracts": list_contract_names(),
    }


@router.get("/contracts/{contract_name}")
def contract(contract_name: str) -> dict[str, Any]:
    try:
        return get_contract(contract_name)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error