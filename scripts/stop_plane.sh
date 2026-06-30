#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="/Users/andrey/Documents/projects/COMPASS-AI"
PLANE_DIR="${PROJECT_ROOT}/plane/docker/plane-source"
PLANE_URL="http://localhost"

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

info() {
  echo -e "${BLUE}➜${RESET} $1"
}

success() {
  echo -e "${GREEN}✓${RESET} $1"
}

wait_msg() {
  echo -e "${YELLOW}…${RESET} $1"
}

warn_msg() {
  echo -e "${YELLOW}⚠${RESET} $1"
}

error_msg() {
  echo -e "${RED}✗${RESET} $1"
}

section() {
  echo
  echo -e "${BOLD}${BLUE}$1${RESET}"
}

section "Stopping local Plane for COMPASS AI"

info "This script stops Plane without deleting Docker volumes."

if ! command -v docker >/dev/null 2>&1; then
  error_msg "Docker is not installed or not available in PATH."
  exit 1
fi

success "Docker CLI is available."

if ! docker info >/dev/null 2>&1; then
  success "Docker Desktop is not running. Nothing to stop."
  exit 0
fi

success "Docker Desktop is running."

if [ ! -d "${PLANE_DIR}" ]; then
  error_msg "Plane source directory not found: ${PLANE_DIR}"
  exit 1
fi

success "Plane source directory exists."

cd "${PLANE_DIR}"

section "Stopping containers"
docker compose stop
success "Docker Compose stop command completed."

section "Plane containers after stop"
docker compose ps

section "Checking Plane URL"

if curl -fsS -I "${PLANE_URL}" >/dev/null 2>&1; then
  warn_msg "${PLANE_URL} still responds."
  warn_msg "Another service may be using port 80, or one Plane container may still be running."
  echo
  echo "Check running containers:"
  echo "docker ps"
else
  success "Plane is stopped. ${PLANE_URL} is not available."
fi

section "Data safety"
success "Docker volumes were preserved."
success "Plane data was not deleted."
success "Safe stop completed."