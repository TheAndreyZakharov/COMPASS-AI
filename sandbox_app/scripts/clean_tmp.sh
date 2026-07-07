#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."

find sandbox_app -type d -name "__pycache__" -prune -exec rm -rf {} +
find sandbox_app -type f -name "*.pyc" -delete

echo "Sandbox temporary Python files cleaned."