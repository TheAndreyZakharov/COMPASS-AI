from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter

from sandbox_app.backend.core.paths import (
    ASSIGNMENT_SESSIONS_DIR,
    TRAINING_SESSIONS_DIR,
)

router = APIRouter(prefix="/api", tags=["sessions"])


def _session_items(root: Path) -> list[dict[str, Any]]:
    root.mkdir(parents=True, exist_ok=True)

    items: list[dict[str, Any]] = []

    for path in sorted(root.iterdir(), reverse=True):
        if not path.is_dir():
            continue

        stat = path.stat()
        items.append(
            {
                "id": path.name,
                "path": str(path),
                "created_at": stat.st_ctime,
                "updated_at": stat.st_mtime,
            },
        )

    return items


@router.get("/sessions")
def sessions() -> dict[str, Any]:
    return {
        "training_sessions": _session_items(TRAINING_SESSIONS_DIR),
        "assignment_sessions": _session_items(ASSIGNMENT_SESSIONS_DIR),
    }