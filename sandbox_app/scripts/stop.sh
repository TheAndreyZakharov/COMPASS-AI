#!/usr/bin/env bash
set -euo pipefail

PORT="8601"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SANDBOX_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

LOG_DIR="${SANDBOX_DIR}/logs"
PID_FILE="${LOG_DIR}/sandbox_app.pid"

stop_sandbox_app() {
  if [[ ! -f "${PID_FILE}" ]]; then
    echo "Sandbox app PID file not found"
    if lsof -tiTCP:"${PORT}" -sTCP:LISTEN >/dev/null 2>&1; then
      echo "Port ${PORT} is still busy:"
      lsof -nP -iTCP:"${PORT}" -sTCP:LISTEN
    fi
    return 0
  fi

  APP_PID="$(cat "${PID_FILE}")"

  if [[ -z "${APP_PID}" ]]; then
    rm -f "${PID_FILE}"
    echo "Removed empty PID file"
    return 0
  fi

  if ! kill -0 "${APP_PID}" 2>/dev/null; then
    rm -f "${PID_FILE}"
    echo "Sandbox app was not running; removed stale PID file"
    return 0
  fi

  echo "Stopping COMPASS AI Sandbox PID ${APP_PID}"
  kill "${APP_PID}"

  for _ in $(seq 1 20); do
    if ! kill -0 "${APP_PID}" 2>/dev/null; then
      rm -f "${PID_FILE}"
      echo "Sandbox app stopped"
      return 0
    fi
    sleep 1
  done

  echo "Process did not stop gracefully; forcing stop"
  kill -9 "${APP_PID}" 2>/dev/null || true
  rm -f "${PID_FILE}"
  echo "Sandbox app stopped"
}

stop_sandbox_app

echo "Stopping Ollama for sandbox LLM explanations"
bash "${SCRIPT_DIR}/stop_ollama.sh"