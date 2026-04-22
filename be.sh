#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if [[ -d ".venv" ]]; then
  # shellcheck disable=SC1091
  source ".venv/bin/activate"
fi

export PYTHONPATH="${PYTHONPATH:-.}"
HOST="${HOST:-127.0.0.1}"
PORT="${BE_PORT:-8000}"

echo "Starting backend API on http://${HOST}:${PORT}"
exec uvicorn application.test_api:app --reload --host "$HOST" --port "$PORT"
