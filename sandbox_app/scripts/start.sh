#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."

APP_MODULE="sandbox_app.backend.main:app"
HOST="127.0.0.1"
PORT="8601"
LOG_DIR="sandbox_app/logs"
PID_FILE="$LOG_DIR/sandbox_app.pid"
LOG_FILE="$LOG_DIR/server.log"

mkdir -p "$LOG_DIR"

if [ ! -d ".venv" ]; then
  echo "Missing .venv. Create and activate the project virtual environment first."
  exit 1
fi

if [ -z "${VIRTUAL_ENV:-}" ]; then
  echo "Virtual environment is not active. Run: source .venv/bin/activate"
  exit 1
fi

EXPECTED_PYTHON="$(pwd)/.venv/bin/python"
CURRENT_PYTHON="$(python -c 'import sys; print(sys.executable)')"

if [ "$CURRENT_PYTHON" != "$EXPECTED_PYTHON" ]; then
  echo "Wrong Python interpreter: $CURRENT_PYTHON"
  echo "Expected: $EXPECTED_PYTHON"
  exit 1
fi

python -c "import fastapi, uvicorn" >/dev/null 2>&1 || {
  echo "Missing FastAPI runtime dependencies. Run: python -m pip install \"fastapi>=0.115,<1\" \"uvicorn[standard]>=0.30,<1\""
  exit 1
}

if [ -f "$PID_FILE" ]; then
  OLD_PID="$(cat "$PID_FILE")"
  if kill -0 "$OLD_PID" >/dev/null 2>&1; then
    echo "Sandbox app is already running with PID $OLD_PID"
    echo "URL: http://$HOST:$PORT"
    exit 0
  fi
  rm -f "$PID_FILE"
fi

if lsof -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Port $PORT is already busy."
  echo "Stop the process using that port or change sandbox_app/config/app_settings.json."
  exit 1
fi

python -m uvicorn "$APP_MODULE" --host "$HOST" --port "$PORT" --reload > "$LOG_FILE" 2>&1 &

APP_PID="$!"
echo "$APP_PID" > "$PID_FILE"

echo "Sandbox app started"
echo "PID: $APP_PID"
echo "URL: http://$HOST:$PORT"
echo "Logs: $LOG_FILE"