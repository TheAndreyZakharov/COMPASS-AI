from __future__ import annotations

from datetime import UTC, datetime

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

APP_NAME = "COMPASS AI Sandbox"
APP_VERSION = "0.1.0"
TARGET_PYTHON = "3.11.x"

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "app": APP_NAME,
        "version": APP_VERSION,
        "target_python": TARGET_PYTHON,
        "checked_at": datetime.now(UTC).isoformat(),
    }


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return """
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>COMPASS AI Sandbox</title>
        <style>
          body {
            margin: 0;
            min-height: 100vh;
            display: grid;
            place-items: center;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: #f6f7f9;
            color: #111827;
          }
          main {
            width: min(720px, calc(100vw - 32px));
            padding: 32px;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            background: #ffffff;
          }
          h1 {
            margin: 0 0 12px;
            font-size: 28px;
          }
          p {
            margin: 0;
            line-height: 1.6;
            color: #4b5563;
          }
          code {
            padding: 2px 6px;
            border-radius: 4px;
            background: #f3f4f6;
          }
        </style>
      </head>
      <body>
        <main>
          <h1>COMPASS AI Sandbox</h1>
          <p>Local sandbox backend is running on <code>127.0.0.1:8601</code>.</p>
          <p>Health endpoint: <code>/api/health</code>.</p>
        </main>
      </body>
    </html>
    """