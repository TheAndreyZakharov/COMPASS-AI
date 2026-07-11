from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sandbox_app.backend.api import (
    assignment_sessions,
    config,
    contracts,
    data_viewer,
    feature_schemas,
    features,
    generate_dataset,
    generate_history,
    generate_tasks,
    generate_team,
    import_data,
    kanban_lab,
    llm,
    models,
    recommendations,
    reports,
    sessions,
    settings,
    status,
    test_cases,
    training,
)
from sandbox_app.backend.core.logging import logger
from sandbox_app.backend.core.paths import PATHS, ensure_runtime_dirs
from sandbox_app.backend.core.settings import load_settings
from starlette.exceptions import HTTPException as StarletteHTTPException


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_runtime_dirs()
    settings = load_settings()
    logger.info(
        "Starting %s %s on %s:%s",
        settings["app"]["name"],
        settings["app"]["version"],
        settings["app"]["host"],
        settings["app"]["port"],
    )
    yield
    logger.info("Stopping sandbox backend")


def create_app() -> FastAPI:
    settings = load_settings()
    app_settings = settings["app"]

    app = FastAPI(
        title=app_settings["name"],
        version=app_settings["version"],
        description="Autonomous local FastAPI backend for COMPASS AI Sandbox.",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://127.0.0.1:8601",
            "http://localhost:8601",
        ],
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
    )

    register_exception_handlers(app)
    register_api_routes(app)
    register_frontend_routes(app)

    return app


def register_api_routes(app: FastAPI) -> None:
    api_prefix = "/api"
    app.include_router(status.router, prefix=api_prefix)
    app.include_router(config.router, prefix=api_prefix)
    app.include_router(contracts.router, prefix=api_prefix)
    app.include_router(feature_schemas.router, prefix=api_prefix)
    app.include_router(generate_team.router, prefix=api_prefix)
    app.include_router(generate_tasks.router, prefix=api_prefix)
    app.include_router(sessions.router, prefix=api_prefix)
    app.include_router(generate_history.router, prefix=api_prefix)
    app.include_router(generate_dataset.router, prefix=api_prefix)
    app.include_router(data_viewer.router, prefix=api_prefix)
    app.include_router(import_data.router, prefix=api_prefix)
    app.include_router(features.router, prefix=api_prefix)
    app.include_router(training.router, prefix=api_prefix)
    app.include_router(reports.router, prefix=api_prefix)
    app.include_router(models.router, prefix=api_prefix)
    app.include_router(test_cases.router, prefix=api_prefix)
    app.include_router(recommendations.router, prefix=api_prefix)
    app.include_router(assignment_sessions.router, prefix=api_prefix)
    app.include_router(kanban_lab.router, prefix=api_prefix)
    app.include_router(llm.router, prefix=api_prefix)
    app.include_router(settings.router, prefix=api_prefix)


def register_frontend_routes(app: FastAPI) -> None:
    PATHS.frontend_css_dir.mkdir(parents=True, exist_ok=True)
    PATHS.frontend_js_dir.mkdir(parents=True, exist_ok=True)
    PATHS.frontend_assets_dir.mkdir(parents=True, exist_ok=True)
    PATHS.brand_assets_dir.mkdir(parents=True, exist_ok=True)

    app.mount("/css", StaticFiles(directory=PATHS.frontend_css_dir), name="sandbox-css")
    app.mount("/js", StaticFiles(directory=PATHS.frontend_js_dir), name="sandbox-js")
    app.mount("/assets", StaticFiles(directory=PATHS.frontend_assets_dir), name="sandbox-assets")
    app.mount("/brand", StaticFiles(directory=PATHS.brand_assets_dir), name="sandbox-brand")

    @app.api_route("/favicon.ico", methods=["GET", "HEAD"], include_in_schema=False)
    async def favicon() -> FileResponse:
        return FileResponse(PATHS.brand_assets_dir / "image.png", media_type="image/png")

    @app.get("/", include_in_schema=False)
    async def frontend_index() -> FileResponse:
        return FileResponse(PATHS.frontend_dir / "index.html")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_fallback(full_path: str) -> FileResponse:
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API endpoint not found")

        index_path = PATHS.frontend_dir / "index.html"
        if index_path.exists():
            return FileResponse(index_path)

        raise HTTPException(status_code=404, detail="Frontend index.html not found")


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        return _json_error_response(request, exc.status_code, exc.detail)

    @app.exception_handler(StarletteHTTPException)
    async def starlette_exception_handler(
        request: Request,
        exc: StarletteHTTPException,
    ) -> JSONResponse:
        return _json_error_response(request, exc.status_code, exc.detail)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        return _json_error_response(
            request=request,
            status_code=422,
            detail="Request validation failed",
            extra={"errors": exc.errors()},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled sandbox backend error: %s", exc)
        return _json_error_response(
            request=request,
            status_code=500,
            detail="Internal sandbox backend error",
        )


def _json_error_response(
    request: Request,
    status_code: int,
    detail: Any,
    extra: dict[str, Any] | None = None,
) -> JSONResponse:
    payload: dict[str, Any] = {
        "error": {
            "status_code": status_code,
            "detail": detail,
            "path": request.url.path,
        }
    }

    if extra:
        payload["error"].update(extra)

    return JSONResponse(status_code=status_code, content=payload)


app = create_app()
