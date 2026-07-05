#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="/Users/andrey/Documents/projects/COMPASS-AI"

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

success() {
  echo -e "${GREEN}✓${RESET} $1"
}

warn_msg() {
  echo -e "${YELLOW}⚠${RESET} $1"
}

error_msg() {
  echo -e "${RED}✗${RESET} $1"
}

section "Opening COMPASS AI local stack in VS Code"

cd "${PROJECT_ROOT}"

if ! command -v code >/dev/null 2>&1; then
  error_msg "VS Code CLI 'code' is not available."
  echo
  echo "Fix:"
  echo "1. Open VS Code"
  echo "2. Press Cmd+Shift+P"
  echo "3. Run: Shell Command: Install 'code' command in PATH"
  exit 1
fi

if [ ! -f ".vscode/tasks.json" ]; then
  error_msg ".vscode/tasks.json not found."
  exit 1
fi

success "VS Code CLI is available."
success "VS Code tasks file exists."

code -r "${PROJECT_ROOT}" --command workbench.action.tasks.runTask

section "Start stack from VS Code"

echo "In the VS Code task picker choose:"
echo
echo "COMPASS: start stack"
echo
echo "This will start:"
echo "- Plane in a VS Code terminal"
echo "- Ollama in a VS Code terminal"
echo "- FastAPI in a VS Code terminal"
echo "- Streamlit dashboard in a VS Code terminal"
echo
echo "Browser tabs will open for:"
echo "- Plane"
echo "- Dashboard"
echo

section "Stop stack"

echo "To stop everything, run VS Code task:"
echo
echo "COMPASS: stop stack"
echo
echo "or run:"
echo
echo "./scripts/stop_compass_stack.sh"

section "Data safety"

success "Start/stop scripts do not delete Docker volumes."
success "Plane data is preserved."
success "Docker Desktop may be started/stopped safely."