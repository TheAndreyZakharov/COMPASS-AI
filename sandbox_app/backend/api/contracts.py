from __future__ import annotations

from fastapi import APIRouter, HTTPException
from sandbox_app.backend.core.data_contracts import (
    DataContractError,
    get_contract,
    get_contract_summary,
    load_data_contracts,
)
from sandbox_app.backend.utils.json_io import JsonFileError

router = APIRouter(prefix="/contracts", tags=["contracts"])


@router.get("")
def list_contracts() -> dict:
    try:
        return {
            "summary": get_contract_summary(),
            "contracts": load_data_contracts()["contracts"],
        }
    except (JsonFileError, DataContractError) as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/summary")
def contracts_summary() -> dict:
    try:
        return get_contract_summary()
    except (JsonFileError, DataContractError) as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/{contract_name}")
def contract_details(contract_name: str) -> dict:
    try:
        return {
            "name": contract_name,
            "contract": get_contract(contract_name),
        }
    except DataContractError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except JsonFileError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc