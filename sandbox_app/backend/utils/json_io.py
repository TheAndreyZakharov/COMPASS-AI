from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class JsonFileError(RuntimeError):
    """Raised when a sandbox JSON file cannot be read or written safely."""


def read_json(path: Path) -> Any:
    """Read JSON from disk with a clear sandbox-specific error."""
    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError as exc:
        raise JsonFileError(f"JSON file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise JsonFileError(f"Invalid JSON in {path}: {exc}") from exc


def write_json(path: Path, payload: Any) -> None:
    """Write pretty JSON atomically enough for local sandbox usage."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = path.with_suffix(path.suffix + ".tmp")
        tmp_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        tmp_path.replace(path)
    except OSError as exc:
        raise JsonFileError(f"Cannot write JSON file {path}: {exc}") from exc


def read_json_or_default(path: Path, default: Any) -> Any:
    """Read JSON if present, otherwise return a supplied default."""
    if not path.exists():
        return default
    return read_json(path)


def ensure_json_serializable(payload: Any) -> Any:
    """Validate that payload can be serialized to JSON and return it unchanged."""
    try:
        json.dumps(payload, ensure_ascii=False)
    except TypeError as exc:
        raise JsonFileError(f"Payload is not JSON serializable: {exc}") from exc
    return payload