from __future__ import annotations

from functools import lru_cache
from typing import Any

from sandbox_app.backend.core.paths import PATHS
from sandbox_app.backend.utils.json_io import JsonFileError, read_json


class DataContractError(RuntimeError):
    """Raised when sandbox data contracts are missing or invalid."""


REQUIRED_TOP_LEVEL_KEYS = {
    "version",
    "description",
    "formats",
    "shared_enums",
    "contracts",
}

REQUIRED_CONTRACTS = {
    "employees",
    "tasks",
    "assignment_history",
    "training_pairs",
    "current_team",
    "current_backlog",
    "recommendations",
    "training_session",
    "assignment_session",
    "dataset_metadata",
}


@lru_cache(maxsize=1)
def load_data_contracts() -> dict[str, Any]:
    payload = read_json(PATHS.data_contracts_dir / "data_contracts.json")
    return validate_data_contracts(payload)


def reload_data_contracts_cache() -> None:
    load_data_contracts.cache_clear()


def validate_data_contracts(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise DataContractError("data_contracts.json must contain a JSON object")

    missing_top_level = sorted(REQUIRED_TOP_LEVEL_KEYS - set(payload))
    if missing_top_level:
        raise DataContractError(
            "data_contracts.json missing top-level keys: "
            + ", ".join(missing_top_level)
        )

    contracts = payload.get("contracts")
    if not isinstance(contracts, dict):
        raise DataContractError("data_contracts.json contracts must be an object")

    missing_contracts = sorted(REQUIRED_CONTRACTS - set(contracts))
    if missing_contracts:
        raise DataContractError(
            "data_contracts.json missing contracts: "
            + ", ".join(missing_contracts)
        )

    formats = payload.get("formats")
    if not isinstance(formats, dict):
        raise DataContractError("data_contracts.json formats must be an object")

    for required_format in ("csv", "json", "parquet"):
        if required_format not in formats:
            raise DataContractError(f"data_contracts.json missing format: {required_format}")

    shared_enums = payload.get("shared_enums")
    if not isinstance(shared_enums, dict):
        raise DataContractError("data_contracts.json shared_enums must be an object")

    for enum_name in (
        "task_statuses",
        "deadline_statuses",
        "outcome_labels",
        "recommendation_modes",
        "target_modes",
        "session_statuses",
    ):
        values = shared_enums.get(enum_name)
        if not isinstance(values, list) or not values:
            raise DataContractError(f"shared_enums.{enum_name} must be a non-empty list")

    for contract_name, contract in contracts.items():
        _validate_contract(contract_name, contract)

    return payload


def _validate_contract(contract_name: str, contract: Any) -> None:
    if not isinstance(contract, dict):
        raise DataContractError(f"Contract {contract_name} must be an object")

    if "description" not in contract:
        raise DataContractError(f"Contract {contract_name} missing description")

    if "primary_key" not in contract:
        raise DataContractError(f"Contract {contract_name} missing primary_key")

    if "storage" not in contract or not isinstance(contract["storage"], dict):
        raise DataContractError(f"Contract {contract_name} missing storage object")

    if "required_fields" not in contract and "required_fields_ref" not in contract:
        raise DataContractError(
            f"Contract {contract_name} must define required_fields or required_fields_ref"
        )

    required_fields = contract.get("required_fields")
    if required_fields is not None and not isinstance(required_fields, dict):
        raise DataContractError(f"Contract {contract_name} required_fields must be an object")

    optional_fields = contract.get("optional_fields")
    if optional_fields is not None and not isinstance(optional_fields, dict):
        raise DataContractError(f"Contract {contract_name} optional_fields must be an object")


def list_contract_names() -> list[str]:
    contracts = load_data_contracts()["contracts"]
    return sorted(contracts.keys())


def get_contract(contract_name: str) -> dict[str, Any]:
    contracts = load_data_contracts()["contracts"]

    if contract_name not in contracts:
        available = ", ".join(sorted(contracts))
        raise DataContractError(
            f"Unknown contract '{contract_name}'. Available contracts: {available}"
        )

    return contracts[contract_name]


def get_contract_summary() -> dict[str, Any]:
    payload = load_data_contracts()
    contracts = payload["contracts"]

    return {
        "version": payload["version"],
        "description": payload["description"],
        "formats": sorted(payload["formats"].keys()),
        "shared_enums": {
            name: len(values)
            for name, values in payload["shared_enums"].items()
            if isinstance(values, list)
        },
        "contracts": [
            {
                "name": name,
                "primary_key": contract.get("primary_key"),
                "storage": sorted(contract.get("storage", {}).keys()),
                "required_fields_count": len(contract.get("required_fields", {})),
                "has_required_fields_ref": "required_fields_ref" in contract,
                "optional_fields_count": len(contract.get("optional_fields", {})),
            }
            for name, contract in sorted(contracts.items())
        ],
        "count": len(contracts),
    }


def validate_record_required_fields(contract_name: str, record: dict[str, Any]) -> list[str]:
    contract = get_contract(contract_name)
    required_fields = contract.get("required_fields", {})

    if not isinstance(record, dict):
        raise DataContractError("Record must be an object")

    return sorted(field_name for field_name in required_fields if field_name not in record)


def load_data_contracts_safe() -> tuple[dict[str, Any] | None, str | None]:
    try:
        return load_data_contracts(), None
    except (JsonFileError, DataContractError) as exc:
        return None, str(exc)