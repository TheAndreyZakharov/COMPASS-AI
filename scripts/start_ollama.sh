#!/usr/bin/env bash
set -euo pipefail

OLLAMA_APP="/Applications/Ollama.app"
OLLAMA_URL="http://localhost:11434/api/tags"

if [ -t 1 ]; then
  GREEN="\033[0;32m"
  YELLOW="\033[0;33m"
  RED="\033[0;31m"
  BLUE="\033[0;34m"
  BOLD="\033[1m"
  RESET="\033[0m"
else
  GREEN=""
  YELLOW=""
  RED=""
  BLUE=""
  BOLD=""
  RESET=""
fi

section() {
  echo
  echo -e "${BOLD}${BLUE}$1${RESET}"
}

info() {
  echo -e "${BLUE}➜${RESET} $1"
}

success() {
  echo -e "${GREEN}✓${RESET} $1"
}

warn_msg() {
  echo -e "${YELLOW}⚠${RESET} $1"
}

error_msg() {
  echo -e "${RED}✗${RESET} $1"
}

wait_for_ollama() {
  for attempt in {1..40}; do
    if curl -fsS "${OLLAMA_URL}" >/dev/null 2>&1; then
      success "Ollama server is ready: ${OLLAMA_URL}"
      return 0
    fi

    info "Waiting for Ollama server... attempt ${attempt}/40"
    sleep 2
  done

  return 1
}

section "Starting Ollama for COMPASS AI"

if curl -fsS "${OLLAMA_URL}" >/dev/null 2>&1; then
  success "Ollama server is already running."
else
  if [ -d "${OLLAMA_APP}" ]; then
    info "Opening Ollama app: ${OLLAMA_APP}"
    open -a Ollama >/dev/null 2>&1 || true

    if wait_for_ollama; then
      success "Ollama app started the local server."
    else
      warn_msg "Ollama app did not expose the server quickly enough."
    fi
  else
    warn_msg "Ollama.app not found at ${OLLAMA_APP}"
  fi
fi

if curl -fsS "${OLLAMA_URL}" >/dev/null 2>&1; then
  success "Ollama is available."
else
  if command -v ollama >/dev/null 2>&1; then
    warn_msg "Falling back to CLI server: ollama serve"
    exec ollama serve
  fi

  error_msg "Ollama is not available and CLI command was not found."
  exit 1
fi

section "Keeping Ollama task alive"

echo "Ollama is running."
echo "This terminal stays open so VS Code keeps a visible Ollama task."
echo "Stop everything with: COMPASS: stop stack"

while curl -fsS "${OLLAMA_URL}" >/dev/null 2>&1; do
  sleep 5
done

warn_msg "Ollama server stopped."