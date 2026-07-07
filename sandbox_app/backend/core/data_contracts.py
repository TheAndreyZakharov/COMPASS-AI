from __future__ import annotations

from typing import Any

from sandbox_app.backend.core.paths import CONFIG_DIR
from sandbox_app.backend.utils.json_io import read_json

DATA_CONTRACTS_PATH = CONFIG_DIR / "data_contracts" / "data_contracts.json"


def load_data_contracts() -> dict[str, Any]:
    return read_json(DATA_CONTRACTS_PATH)


def list_contract_names() -> list[str]:
    contracts = load_data_contracts()
    entities = contracts.get("entities", {})

    if not isinstance(entities, dict):
        return []

    return sorted(entities.keys())


def get_contract(contract_name: str) -> dict[str, Any]:
    contracts = load_data_contracts()
    entities = contracts.get("entities", {})

    if not isinstance(entities, dict):
        raise ValueError("Invalid data contracts file: entities must be an object.")

    contract = entities.get(contract_name)

    if not isinstance(contract, dict):
        raise KeyError(f"Unknown data contract: {contract_name}")

    return contract