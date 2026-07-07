#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SANDBOX_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

PID_FILE="${SANDBOX_DIR}/logs/sandbox_app.pid"

if [[ -f "${PID_FILE}" ]]; then
  APP_PID="$(cat "${PID_FILE}")"
  if [[ -n "${APP_PID}" ]] && kill -0 "${APP_PID}" 2>/dev/null; then
    echo "ERROR: sandbox app is running with PID ${APP_PID}"
    echo "Stop it first: bash sandbox_app/scripts/stop.sh"
    exit 1
  fi
fi

find "${SANDBOX_DIR}" -type d -name "__pycache__" -prune -exec rm -rf {} +
find "${SANDBOX_DIR}" -type f -name "*.pyc" -delete
find "${SANDBOX_DIR}" -type d -name ".pytest_cache" -prune -exec rm -rf {} +

rm -f "${SANDBOX_DIR}/logs/sandbox_app.pid"
rm -f "${SANDBOX_DIR}/logs/server.log"

touch "${SANDBOX_DIR}/logs/.gitkeep"

echo "Sandbox temporary files cleaned"