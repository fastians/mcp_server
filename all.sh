#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

LOG_DIR="$ROOT_DIR/.run_logs"
mkdir -p "$LOG_DIR"

echo "Starting backend, frontend, and MCP server..."

"$ROOT_DIR/be.sh" > "$LOG_DIR/backend.log" 2>&1 &
BE_PID=$!

"$ROOT_DIR/fe.sh" > "$LOG_DIR/frontend.log" 2>&1 &
FE_PID=$!

"$ROOT_DIR/mcp.sh" > "$LOG_DIR/mcp.log" 2>&1 &
MCP_PID=$!

cleanup() {
  echo
  echo "Stopping all services..."
  kill "$BE_PID" "$FE_PID" "$MCP_PID" 2>/dev/null || true
}

trap cleanup EXIT INT TERM

echo "Backend PID:  $BE_PID (log: .run_logs/backend.log)"
echo "Frontend PID: $FE_PID (log: .run_logs/frontend.log)"
echo "MCP PID:      $MCP_PID (log: .run_logs/mcp.log)"
echo "Tip: run smoke test in another terminal -> PYTHONPATH=. python scripts/smoke_test.py"
echo "Press Ctrl+C to stop all."

wait "$BE_PID" "$FE_PID" "$MCP_PID"
