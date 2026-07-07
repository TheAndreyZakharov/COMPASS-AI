from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles

from sandbox_app.backend.api.config import router as config_router
from sandbox_app.backend.api.contracts import router as contracts_router
from sandbox_app.backend.api.feature_schemas import router as feature_schemas_router
from sandbox_app.backend.api.generate_team import router as generate_team_router
from sandbox_app.backend.api.sessions import router as sessions_router
from sandbox_app.backend.api.status import router as status_router
from sandbox_app.backend.core.logging import configure_logging
from sandbox_app.backend.core.paths import (
    FRONTEND_ASSETS_DIR,
    FRONTEND_DIR,
    FRONTEND_INDEX_PATH,
    ensure_runtime_dirs,
)
from sandbox_app.backend.core.settings import load_app_settings

configure_logging()
ensure_runtime_dirs()

logger = logging.getLogger(__name__)
settings = load_app_settings()

app = FastAPI(
    title=settings.get("app_name", "COMPASS AI Sandbox"),
    version=settings.get("app_version", "0.1.0"),
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8601",
        "http://localhost:8601",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(status_router)
app.include_router(config_router)
app.include_router(sessions_router)
app.include_router(contracts_router)
app.include_router(feature_schemas_router)
app.include_router(generate_team_router)

css_dir = FRONTEND_DIR / "css"
js_dir = FRONTEND_DIR / "js"

if css_dir.exists():
    app.mount("/css", StaticFiles(directory=css_dir), name="css")

if js_dir.exists():
    app.mount("/js", StaticFiles(directory=js_dir), name="js")

if FRONTEND_ASSETS_DIR.exists():
    app.mount(
        "/assets",
        StaticFiles(directory=FRONTEND_ASSETS_DIR),
        name="assets",
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    logger.exception("Unhandled sandbox backend error: %s", exc)

    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "Unexpected sandbox backend error.",
            "path": str(request.url.path),
        },
    )


@app.get("/")
def index() -> FileResponse:
    return FileResponse(FRONTEND_INDEX_PATH)


@app.get("/{path:path}")
def frontend_fallback(path: str) -> Response:
    if path.startswith("api/"):
        return JSONResponse(
            status_code=404,
            content={
                "error": "not_found",
                "message": "API endpoint not found.",
                "path": f"/{path}",
            },
        )

    return FileResponse(FRONTEND_INDEX_PATH)