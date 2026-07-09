#!/usr/bin/env bash
set -euo pipefail

OLLAMA_PORT="11434"
OLLAMA_APP="/Applications/Ollama.app"
DEFAULT_MODEL="qwen2.5:1.5b-instruct"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SANDBOX_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
PROJECT_ROOT="$(cd "${SANDBOX_DIR}/.." && pwd)"

LOG_DIR="${SANDBOX_DIR}/logs"
PID_FILE="${LOG_DIR}/ollama.pid"
STATE_FILE="${LOG_DIR}/ollama.state"
OLLAMA_LOG="${LOG_DIR}/ollama.log"

OLLAMA_BASE_URL="${SANDBOX_OLLAMA_BASE_URL:-http://localhost:${OLLAMA_PORT}}"
OLLAMA_MODEL="${SANDBOX_OLLAMA_MODEL:-${DEFAULT_MODEL}}"
OLLAMA_AUTO_PULL="${SANDBOX_OLLAMA_AUTO_PULL:-1}"
OLLAMA_TAGS_URL="${OLLAMA_BASE_URL%/}/api/tags"

mkdir -p "${LOG_DIR}"

info() {
  echo "Ollama: $1"
}

fail() {
  echo "ERROR: $1"
  exit 1
}

ollama_ready() {
  curl -fsS "${OLLAMA_TAGS_URL}" >/dev/null 2>&1
}

wait_for_ollama() {
  for _ in $(seq 1 60); do
    if ollama_ready; then
      return 0
    fi
    sleep 1
  done

  return 1
}

model_available() {
  curl -fsS "${OLLAMA_TAGS_URL}" | grep -Fq "\"name\":\"${OLLAMA_MODEL}\""
}

start_ollama_cli() {
  if ! command -v ollama >/dev/null 2>&1; then
    return 1
  fi

  info "starting CLI server: ollama serve"
  cd "${PROJECT_ROOT}"
  nohup ollama serve >>"${OLLAMA_LOG}" 2>&1 &
  echo "$!" >"${PID_FILE}"
  echo "cli" >"${STATE_FILE}"

  return 0
}

start_ollama_app() {
  if [[ ! -d "${OLLAMA_APP}" ]]; then
    return 1
  fi

  info "opening macOS app: ${OLLAMA_APP}"
  open -a Ollama >/dev/null 2>&1 || true
  echo "app" >"${STATE_FILE}"

  return 0
}

pull_model() {
  if [[ "${OLLAMA_AUTO_PULL}" != "1" ]]; then
    fail "model ${OLLAMA_MODEL} is not available and auto pull is disabled"
  fi

  if ! command -v ollama >/dev/null 2>&1; then
    fail "model ${OLLAMA_MODEL} is missing and ollama CLI is not available"
  fi

  info "pulling model: ${OLLAMA_MODEL}"
  ollama pull "${OLLAMA_MODEL}" >>"${OLLAMA_LOG}" 2>&1
}

info "target server: ${OLLAMA_BASE_URL}"
info "target model: ${OLLAMA_MODEL}"
info "logs: ${OLLAMA_LOG}"

if ollama_ready; then
  info "server is already running"
  echo "external" >"${STATE_FILE}"
else
  if ! start_ollama_app; then
    if ! start_ollama_cli; then
      fail "Ollama.app not found and ollama CLI is not available"
    fi
  fi

  if ! wait_for_ollama; then
    if [[ ! -f "${PID_FILE}" ]]; then
      info "app did not expose server in time; trying CLI fallback"
      start_ollama_cli || true
    fi

    if ! wait_for_ollama; then
      fail "Ollama server did not become ready; see ${OLLAMA_LOG}"
    fi
  fi
fi

if model_available; then
  info "model is available: ${OLLAMA_MODEL}"
else
  pull_model

  if ! model_available; then
    fail "model ${OLLAMA_MODEL} is still not available after pull"
  fi

  info "model is available: ${OLLAMA_MODEL}"
fi

info "ready"