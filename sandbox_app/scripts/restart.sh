#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."

bash sandbox_app/scripts/stop.sh
bash sandbox_app/scripts/start.sh