#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."

URL="http://127.0.0.1:8601/api/health"

python -c "import urllib.request; import json; payload=json.load(urllib.request.urlopen('$URL', timeout=5)); assert payload['status'] == 'ok'; print('Sandbox smoke test passed:', payload)"