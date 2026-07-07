from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

APP_NAME = "COMPASS AI Sandbox"
APP_VERSION = "0.1.0"

SANDBOX_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DIR = SANDBOX_ROOT / "frontend"
ASSETS_DIR = FRONTEND_DIR / "assets"
INDEX_PATH = FRONTEND_DIR / "index.html"

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

if ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {
        "app": APP_NAME,
        "version": APP_VERSION,
        "status": "ok",
        "local_mode": True,
    }


@app.get("/api/status")
def status() -> dict[str, Any]:
    return health()


@app.get("/")
def index() -> FileResponse:
    return FileResponse(INDEX_PATH)


@app.get("/{path:path}")
def frontend_fallback(path: str) -> FileResponse:
    return FileResponse(INDEX_PATH)