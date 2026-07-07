#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."

PID_FILE="sandbox_app/logs/sandbox_app.pid"

if [ ! -f "$PID_FILE" ]; then
  echo "Sandbox app is not running: PID file not found."
  exit 0
fi

APP_PID="$(cat "$PID_FILE")"

if kill -0 "$APP_PID" >/dev/null 2>&1; then
  kill "$APP_PID"
  echo "Stopping sandbox app with PID $APP_PID"

  for _ in 1 2 3 4 5; do
    if ! kill -0 "$APP_PID" >/dev/null 2>&1; then
      break
    fi
    sleep 1
  done

  if kill -0 "$APP_PID" >/dev/null 2>&1; then
    echo "Process did not stop gracefully. Sending SIGKILL."
    kill -9 "$APP_PID"
  fi
else
  echo "Sandbox app process is already stopped."
fi

rm -f "$PID_FILE"
echo "Sandbox app stopped."