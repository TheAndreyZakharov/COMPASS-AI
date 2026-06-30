#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="/Users/andrey/Documents/projects/COMPASS-AI"
PLANE_DIR="${PROJECT_ROOT}/plane/docker/plane-source"
PLANE_URL="http://localhost"
PLANE_WORKSPACE_URL="http://localhost/compass-ai-lab/"

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

error_msg() {
  echo -e "${RED}✗${RESET} $1"
}

section() {
  echo
  echo -e "${BOLD}${BLUE}$1${RESET}"
}

section "Starting local Plane for COMPASS AI"

if ! command -v docker >/dev/null 2>&1; then
  error_msg "Docker is not installed or not available in PATH."
  exit 1
fi

success "Docker CLI is available."

if ! docker info >/dev/null 2>&1; then
  error_msg "Docker Desktop is not running. Start Docker Desktop first."
  exit 1
fi

success "Docker Desktop is running."

if [ ! -d "${PLANE_DIR}" ]; then
  error_msg "Plane source directory not found: ${PLANE_DIR}"
  exit 1
fi

success "Plane source directory exists."

if [ ! -f "${PLANE_DIR}/docker-compose.yml" ]; then
  error_msg "docker-compose.yml not found in ${PLANE_DIR}"
  exit 1
fi

success "Plane docker-compose.yml exists."

if [ ! -f "${PLANE_DIR}/.env" ]; then
  error_msg "Missing Plane root .env file: ${PLANE_DIR}/.env"
  exit 1
fi

success "Plane root .env exists."

if [ ! -f "${PLANE_DIR}/apps/api/.env" ]; then
  error_msg "Missing Plane API .env file: ${PLANE_DIR}/apps/api/.env"
  exit 1
fi

success "Plane API .env exists."

cd "${PLANE_DIR}"

section "Validating Docker Compose"
docker compose config >/dev/null
success "Docker Compose configuration is valid."

section "Starting containers"
docker compose up -d
success "Docker Compose start command completed."

section "Current Plane containers"
docker compose ps

section "Waiting for frontend containers"

for attempt in {1..60}; do
  WEB_HEALTH="$(docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}no-healthcheck{{end}}' web 2>/dev/null || true)"
  ADMIN_HEALTH="$(docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}no-healthcheck{{end}}' admin 2>/dev/null || true)"
  SPACE_HEALTH="$(docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}no-healthcheck{{end}}' space 2>/dev/null || true)"

  if [ "${WEB_HEALTH}" = "healthy" ] && [ "${ADMIN_HEALTH}" = "healthy" ] && [ "${SPACE_HEALTH}" = "healthy" ]; then
    success "web container is healthy."
    success "admin container is healthy."
    success "space container is healthy."
    break
  fi

  wait_msg "Attempt ${attempt}/60: web=${WEB_HEALTH}, admin=${ADMIN_HEALTH}, space=${SPACE_HEALTH}"
  sleep 5

  if [ "${attempt}" = "60" ]; then
    error_msg "Plane frontend containers did not become healthy."
    docker compose ps
    echo
    echo "Run this command for logs:"
    echo "cd ${PLANE_DIR} && docker compose logs --tail=200"
    exit 1
  fi
done

section "Waiting for API"

for attempt in {1..60}; do
  API_RESPONSE="$(docker compose exec -T proxy wget -q -O- http://api:8000 2>/dev/null || true)"

  if [ "${API_RESPONSE}" = '{"status": "OK"}' ]; then
    success "Plane API returned {\"status\": \"OK\"}."
    break
  fi

  wait_msg "Attempt ${attempt}/60: API is not ready yet."
  sleep 5

  if [ "${attempt}" = "60" ]; then
    error_msg "Plane API did not become ready."
    docker compose logs api --tail=120
    exit 1
  fi
done

section "Waiting for main web URL"

for attempt in {1..60}; do
  if curl -fsS -I "${PLANE_URL}" >/dev/null 2>&1; then
    success "Plane main URL responds: ${PLANE_URL}"
    break
  fi

  wait_msg "Attempt ${attempt}/60: ${PLANE_URL} is not ready yet."
  sleep 5

  if [ "${attempt}" = "60" ]; then
    error_msg "Plane main URL did not become available."
    docker compose logs web --tail=120
    exit 1
  fi
done

section "Waiting for workspace route"

for attempt in {1..60}; do
  if curl -fsS -I "${PLANE_WORKSPACE_URL}" >/dev/null 2>&1; then
    success "Plane workspace route responds: ${PLANE_WORKSPACE_URL}"
    success "Plane is ready."
    open "${PLANE_WORKSPACE_URL}" >/dev/null 2>&1 || true
    exit 0
  fi

  wait_msg "Attempt ${attempt}/60: ${PLANE_WORKSPACE_URL} is not ready yet."
  sleep 5
done

wait_msg "Workspace route did not respond directly, opening main Plane URL instead."
success "Plane is available at ${PLANE_URL}"
open "${PLANE_URL}" >/dev/null 2>&1 || true