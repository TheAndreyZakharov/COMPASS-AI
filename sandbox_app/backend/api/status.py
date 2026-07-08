from __future__ import annotations

import platform
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from fastapi import APIRouter
from sandbox_app.backend.core.paths import PATHS
from sandbox_app.backend.core.settings import load_settings

router = APIRouter(tags=["status"])


def _path_status(path: Path) -> dict[str, Any]:
    return {
        "path": str(path),
        "exists": path.exists(),
        "is_dir": path.is_dir(),
    }


@router.get("/health")
def health() -> dict[str, Any]:
    settings = load_settings()
    return {
        "status": "ok",
        "app": settings["app"]["name"],
        "version": settings["app"]["version"],
        "target_python": settings["app"]["target_python"],
        "python": platform.python_version(),
        "checked_at": datetime.now(UTC).isoformat(),
    }


@router.get("/status")
def status() -> dict[str, Any]:
    settings = load_settings()
    python_path = Path(sys.executable).as_posix()

    return {
        "status": "ok",
        "app": settings["app"],
        "runtime": {
            "python_version": platform.python_version(),
            "python_executable": python_path,
            "is_project_venv": (
                "/.venv/" in python_path
                or python_path.endswith("/.venv/bin/python")
            ),
        },
        "paths": {
            "sandbox_root": _path_status(PATHS.sandbox_root),
            "frontend": _path_status(PATHS.frontend_dir),
            "config": _path_status(PATHS.config_dir),
            "generated_data": _path_status(PATHS.generated_data_dir),
            "imported_data": _path_status(PATHS.imported_data_dir),
            "training_sessions": _path_status(PATHS.training_sessions_dir),
            "assignment_sessions": _path_status(PATHS.assignment_sessions_dir),
            "reports": _path_status(PATHS.reports_dir),
            "logs": _path_status(PATHS.logs_dir),
        },
        "isolation": settings.get("isolation", {}),
        "checked_at": datetime.now(UTC).isoformat(),
    }