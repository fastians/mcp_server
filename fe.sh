#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if [[ ! -d "ui/node_modules" ]]; then
  echo "Installing UI dependencies..."
  npm --prefix ui install
fi

echo "Starting frontend dev server"
exec npm --prefix ui run dev
