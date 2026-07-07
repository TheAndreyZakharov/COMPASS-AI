#!/usr/bin/env bash
set -euo pipefail

HOST="127.0.0.1"
PORT="8601"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SANDBOX_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
PROJECT_ROOT="$(cd "${SANDBOX_DIR}/.." && pwd)"

PID_FILE="${SANDBOX_DIR}/logs/sandbox_app.pid"
PYTHON_BIN="${PROJECT_ROOT}/.venv/bin/python"

if [[ ! -x "${PYTHON_BIN}" ]]; then
  echo "ERROR: .venv python not found: ${PYTHON_BIN}"
  exit 1
fi

"${PYTHON_BIN}" - <<'PY'
import sys
from pathlib import Path

python_path = Path(sys.executable).as_posix()

if sys.version_info[:2] != (3, 11):
    raise SystemExit(f"ERROR: expected Python 3.11.x, got {sys.version.split()[0]}")
if "/.venv/" not in python_path and not python_path.endswith("/.venv/bin/python"):
    raise SystemExit(f"ERROR: python is not from project .venv: {python_path}")

print(f"OK: python from .venv: {python_path}")
PY

if [[ ! -f "${PID_FILE}" ]]; then
  echo "ERROR: PID file not found: ${PID_FILE}"
  echo "Run: bash sandbox_app/scripts/start.sh"
  exit 1
fi

APP_PID="$(cat "${PID_FILE}")"

if [[ -z "${APP_PID}" ]] || ! kill -0 "${APP_PID}" 2>/dev/null; then
  echo "ERROR: sandbox app process is not running"
  exit 1
fi

"${PYTHON_BIN}" - <<PY
import json
from urllib.request import urlopen

health_url = "http://${HOST}:${PORT}/api/health"
index_url = "http://${HOST}:${PORT}/"

with urlopen(health_url, timeout=5) as response:
    payload = json.loads(response.read().decode("utf-8"))
    if response.status != 200:
        raise SystemExit(f"ERROR: health returned {response.status}")
    if payload.get("status") != "ok":
        raise SystemExit(f"ERROR: unexpected health payload: {payload}")

with urlopen(index_url, timeout=5) as response:
    body = response.read().decode("utf-8")
    if response.status != 200:
        raise SystemExit(f"ERROR: index returned {response.status}")
    if "COMPASS AI Sandbox" not in body:
        raise SystemExit("ERROR: index page does not contain expected title")

print("OK: smoke test passed")
PY