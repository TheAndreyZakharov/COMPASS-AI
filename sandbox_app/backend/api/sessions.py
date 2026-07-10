from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import APIRouter
from sandbox_app.backend.core.paths import PATHS
from sandbox_app.backend.core.time import MOSCOW_TZ
from sandbox_app.backend.utils.json_io import read_json_or_default

router = APIRouter(prefix="/sessions", tags=["sessions"])


def _session_dir_to_summary(path: Path, session_type: str) -> dict[str, Any]:
    metadata_candidates = [
        path / "session_summary.json",
        path / "assignment_config.json",
        path / "metadata.json",
    ]

    metadata: dict[str, Any] = {}
    for metadata_path in metadata_candidates:
        loaded = read_json_or_default(metadata_path, {})
        if isinstance(loaded, dict) and loaded:
            metadata = loaded
            break

    stat = path.stat()

    return {
        "session_id": path.name,
        "session_type": session_type,
        "path": str(path),
        "created_at": datetime.fromtimestamp(stat.st_ctime, tz=MOSCOW_TZ).isoformat(),
        "updated_at": datetime.fromtimestamp(stat.st_mtime, tz=MOSCOW_TZ).isoformat(),
        "files_count": sum(1 for child in path.rglob("*") if child.is_file()),
        "metadata": metadata,
    }


def _list_sessions(root: Path, session_type: str) -> list[dict[str, Any]]:
    if not root.exists():
        return []

    sessions = [
        _session_dir_to_summary(path, session_type)
        for path in root.iterdir()
        if path.is_dir() and not path.name.startswith(".")
    ]
    return sorted(sessions, key=lambda item: item["updated_at"], reverse=True)


@router.get("")
def list_sessions() -> dict[str, Any]:
    training_sessions = _list_sessions(PATHS.training_sessions_dir, "training")
    assignment_sessions = _list_sessions(PATHS.assignment_sessions_dir, "assignment")

    return {
        "training_sessions": training_sessions,
        "assignment_sessions": assignment_sessions,
        "counts": {
            "training_sessions": len(training_sessions),
            "assignment_sessions": len(assignment_sessions),
            "total": len(training_sessions) + len(assignment_sessions),
        },
    }


@router.get("/training")
def list_training_sessions() -> dict[str, Any]:
    sessions = _list_sessions(PATHS.training_sessions_dir, "training")
    return {"items": sessions, "count": len(sessions)}


@router.get("/assignment")
def list_assignment_sessions() -> dict[str, Any]:
    sessions = _list_sessions(PATHS.assignment_sessions_dir, "assignment")
    return {"items": sessions, "count": len(sessions)}
