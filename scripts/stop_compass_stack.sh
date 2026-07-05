#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="/Users/andrey/Documents/projects/COMPASS-AI"

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

section "Stopping COMPASS AI local stack"

cd "${PROJECT_ROOT}"

section "Stopping dashboard"

stop_port 8501 "Streamlit dashboard"

section "Stopping API"

stop_port 8000 "FastAPI backend"

section "Stopping Ollama"

if [ -f "${PROJECT_ROOT}/scripts/stop_ollama.sh" ]; then
  "${PROJECT_ROOT}/scripts/stop_ollama.sh"
else
  stop_port 11434 "Ollama server"
fi

section "Stopping Plane safely"

if [ -f "${PROJECT_ROOT}/scripts/stop_plane.sh" ]; then
  "${PROJECT_ROOT}/scripts/stop_plane.sh"
else
  warn_msg "scripts/stop_plane.sh not found."
fi

section "Data safety"

success "No Docker volumes were deleted."
success "No Docker images were deleted."
success "No Docker containers were removed."
success "No docker compose down -v was used."
success "Plane data was preserved."
success "Generated data, models and reports were preserved."

section "Done"

success "COMPASS local stack stopped."