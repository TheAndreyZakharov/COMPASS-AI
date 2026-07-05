#!/usr/bin/env bash
set -euo pipefail

OLLAMA_URL="http://localhost:11434/api/tags"

if [ -t 1 ]; then
  GREEN="\033[0;32m"
  YELLOW="\033[0;33m"
  BLUE="\033[0;34m"
  BOLD="\033[1m"
  RESET="\033[0m"
else
  GREEN=""
  YELLOW=""
  BLUE=""
  BOLD=""
  RESET=""
fi

section() {
  echo
  echo -e "${BOLD}${BLUE}$1${RESET}"
}

success() {
  echo -e "${GREEN}✓${RESET} $1"
}

warn_msg() {
  echo -e "${YELLOW}⚠${RESET} $1"
}

stop_port() {
  local port="$1"
  local label="$2"

  local pids
  pids="$(lsof -ti tcp:"${port}" 2>/dev/null || true)"

  if [ -z "${pids}" ]; then
    success "${label} is not running on port ${port}."
    return 0
  fi

  warn_msg "Stopping ${label} on port ${port}: ${pids}"

  for pid in ${pids}; do
    kill "${pid}" >/dev/null 2>&1 || true
  done

  sleep 2

  pids="$(lsof -ti tcp:"${port}" 2>/dev/null || true)"

  if [ -n "${pids}" ]; then
    warn_msg "Force stopping ${label} on port ${port}: ${pids}"

    for pid in ${pids}; do
      kill -9 "${pid}" >/dev/null 2>&1 || true
    done
  fi

  success "${label} stopped."
}

section "Stopping Ollama for COMPASS AI"

stop_port 11434 "Ollama server"

osascript -e 'tell application "Ollama" to quit' >/dev/null 2>&1 || true

sleep 2

if curl -fsS "${OLLAMA_URL}" >/dev/null 2>&1; then
  warn_msg "Ollama server still responds."
else
  success "Ollama server is not responding."
fi

if pgrep -x "Ollama" >/dev/null 2>&1; then
  warn_msg "Ollama app may still be running. You can quit it manually if needed."
else
  success "Ollama app is closed or was not running."
fi