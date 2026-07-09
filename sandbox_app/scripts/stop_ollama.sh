#!/usr/bin/env bash
set -euo pipefail

OLLAMA_PORT="11434"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SANDBOX_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

LOG_DIR="${SANDBOX_DIR}/logs"
PID_FILE="${LOG_DIR}/ollama.pid"
STATE_FILE="${LOG_DIR}/ollama.state"
OLLAMA_BASE_URL="${SANDBOX_OLLAMA_BASE_URL:-http://localhost:${OLLAMA_PORT}}"
OLLAMA_TAGS_URL="${OLLAMA_BASE_URL%/}/api/tags"

info() {
  echo "Ollama: $1"
}

server_responds() {
  curl -fsS "${OLLAMA_TAGS_URL}" >/dev/null 2>&1
}

quit_ollama_app() {
  osascript -e 'tell application "Ollama" to quit' >/dev/null 2>&1 || true
}

kill_pid_gracefully() {
  local pid="$1"
  local label="$2"

  if [[ -z "${pid}" ]]; then
    return 0
  fi

  if ! kill -0 "${pid}" 2>/dev/null; then
    return 0
  fi

  info "stopping ${label} PID ${pid}"
  kill "${pid}" >/dev/null 2>&1 || true

  for _ in $(seq 1 8); do
    if ! kill -0 "${pid}" 2>/dev/null; then
      return 0
    fi
    sleep 1
  done

  if kill -0 "${pid}" 2>/dev/null; then
    info "force stopping ${label} PID ${pid}"
    kill -9 "${pid}" >/dev/null 2>&1 || true
  fi
}

stop_managed_pid() {
  if [[ ! -f "${PID_FILE}" ]]; then
    return 0
  fi

  local pid
  pid="$(cat "${PID_FILE}")"
  kill_pid_gracefully "${pid}" "managed Ollama"
  rm -f "${PID_FILE}"
}

stop_port_processes() {
  local pids
  pids="$(lsof -tiTCP:"${OLLAMA_PORT}" -sTCP:LISTEN 2>/dev/null || true)"

  if [[ -z "${pids}" ]]; then
    return 0
  fi

  info "stopping listeners on port ${OLLAMA_PORT}: ${pids}"

  for pid in ${pids}; do
    kill "${pid}" >/dev/null 2>&1 || true
  done

  sleep 1

  pids="$(lsof -tiTCP:"${OLLAMA_PORT}" -sTCP:LISTEN 2>/dev/null || true)"

  if [[ -n "${pids}" ]]; then
    info "force stopping listeners on port ${OLLAMA_PORT}: ${pids}"

    for pid in ${pids}; do
      kill -9 "${pid}" >/dev/null 2>&1 || true
    done
  fi
}

stop_named_processes() {
  local app_pids
  local cli_pids

  app_pids="$(pgrep -x "Ollama" 2>/dev/null || true)"
  cli_pids="$(pgrep -x "ollama" 2>/dev/null || true)"

  if [[ -n "${app_pids}" ]]; then
    info "stopping Ollama app processes: ${app_pids}"

    for pid in ${app_pids}; do
      kill "${pid}" >/dev/null 2>&1 || true
    done
  fi

  if [[ -n "${cli_pids}" ]]; then
    info "stopping ollama CLI processes: ${cli_pids}"

    for pid in ${cli_pids}; do
      kill "${pid}" >/dev/null 2>&1 || true
    done
  fi

  sleep 1

  app_pids="$(pgrep -x "Ollama" 2>/dev/null || true)"
  cli_pids="$(pgrep -x "ollama" 2>/dev/null || true)"

  if [[ -n "${app_pids}" ]]; then
    info "force stopping Ollama app processes: ${app_pids}"

    for pid in ${app_pids}; do
      kill -9 "${pid}" >/dev/null 2>&1 || true
    done
  fi

  if [[ -n "${cli_pids}" ]]; then
    info "force stopping ollama CLI processes: ${cli_pids}"

    for pid in ${cli_pids}; do
      kill -9 "${pid}" >/dev/null 2>&1 || true
    done
  fi
}

stop_once() {
  quit_ollama_app
  stop_managed_pid
  stop_port_processes
  stop_named_processes
  quit_ollama_app
}

stable_stopped_check() {
  for _ in $(seq 1 5); do
    if server_responds; then
      return 1
    fi
    sleep 1
  done

  return 0
}

info "stopping server: ${OLLAMA_BASE_URL}"

for attempt in $(seq 1 8); do
  stop_once

  if stable_stopped_check; then
    rm -f "${STATE_FILE}"
    info "stopped"
    exit 0
  fi

  info "server came back after stop attempt ${attempt}/8; retrying"
done

rm -f "${STATE_FILE}"

if server_responds; then
  echo "ERROR: Ollama still responds on ${OLLAMA_TAGS_URL}"
  echo "Check manually:"
  echo "  lsof -nP -iTCP:${OLLAMA_PORT} -sTCP:LISTEN"
  echo "  pgrep -laf 'Ollama|ollama'"
  exit 1
fi

info "stopped"