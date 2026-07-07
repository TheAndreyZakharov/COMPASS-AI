#!/usr/bin/env bash
set -euo pipefail

HOST="127.0.0.1"
PORT="8601"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SANDBOX_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
PROJECT_ROOT="$(cd "${SANDBOX_DIR}/.." && pwd)"

LOG_DIR="${SANDBOX_DIR}/logs"
PID_FILE="${LOG_DIR}/sandbox_app.pid"
SERVER_LOG="${LOG_DIR}/server.log"
PYTHON_BIN="${PROJECT_ROOT}/.venv/bin/python"

mkdir -p "${LOG_DIR}"

if [[ ! -x "${PYTHON_BIN}" ]]; then
  echo "ERROR: .venv python not found: ${PYTHON_BIN}"
  echo "Run: source .venv/bin/activate"
  exit 1
fi

PYTHON_CHECK="$("${PYTHON_BIN}" - <<'PY'
import sys
from pathlib import Path

python_path = Path(sys.executable).as_posix()
version_ok = sys.version_info[:2] == (3, 11)
venv_ok = "/.venv/" in python_path or python_path.endswith("/.venv/bin/python")

if not version_ok:
    raise SystemExit(f"ERROR: expected Python 3.11.x, got {sys.version.split()[0]}")
if not venv_ok:
    raise SystemExit(f"ERROR: python is not from project .venv: {python_path}")

print(f"OK: using {python_path}")
PY
)"
echo "${PYTHON_CHECK}"

if [[ -f "${PID_FILE}" ]]; then
  EXISTING_PID="$(cat "${PID_FILE}")"
  if [[ -n "${EXISTING_PID}" ]] && kill -0 "${EXISTING_PID}" 2>/dev/null; then
    echo "Sandbox app is already running with PID ${EXISTING_PID}"
    echo "URL: http://${HOST}:${PORT}"
    exit 0
  fi
  rm -f "${PID_FILE}"
fi

if lsof -tiTCP:"${PORT}" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "ERROR: port ${PORT} is already busy"
  lsof -nP -iTCP:"${PORT}" -sTCP:LISTEN
  exit 1
fi

echo "Starting COMPASS AI Sandbox on http://${HOST}:${PORT}"
echo "Logs: ${SERVER_LOG}"

cd "${PROJECT_ROOT}"
nohup "${PYTHON_BIN}" -m uvicorn sandbox_app.backend.main:app --host "${HOST}" --port "${PORT}" >>"${SERVER_LOG}" 2>&1 &
APP_PID="$!"
echo "${APP_PID}" >"${PID_FILE}"

for _ in $(seq 1 30); do
  if "${PYTHON_BIN}" - <<PY >/dev/null 2>&1
from urllib.request import urlopen
with urlopen("http://${HOST}:${PORT}/api/health", timeout=1) as response:
    raise SystemExit(0 if response.status == 200 else 1)
PY
  then
    echo "Sandbox app started with PID ${APP_PID}"
    echo "URL: http://${HOST}:${PORT}"
    exit 0
  fi

  if ! kill -0 "${APP_PID}" 2>/dev/null; then
    echo "ERROR: sandbox app failed to start"
    echo "See logs: ${SERVER_LOG}"
    rm -f "${PID_FILE}"
    exit 1
  fi

  sleep 1
done

echo "ERROR: sandbox app did not become healthy in time"
echo "See logs: ${SERVER_LOG}"
exit 1