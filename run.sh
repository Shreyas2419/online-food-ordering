#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

# Locate Python environment
if [ -f "$DIR/.venv/bin/python" ]; then
    PYTHON="$DIR/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON="python"
else
    echo "❌ Error: Python 3 not found. Please install Python or set up .venv"
    exit 1
fi

export PYTHONPATH="$DIR"

# Handle test runner argument
if [ "$1" = "test" ] || [ "$1" = "--test" ]; then
    echo "🧪 Running Zero-G Kitchen System Tests..."
    "$PYTHON" tests/test_system.py
    exit $?
fi

# Server Configuration (configurable via env vars or CLI flags)
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"

while [[ $# -gt 0 ]]; do
  case $1 in
    -p|--port)
      PORT="$2"
      shift 2
      ;;
    -h|--host)
      HOST="$2"
      shift 2
      ;;
    *)
      shift
      ;;
  esac
done

# Clean up any lingering process on the target port if necessary
if lsof -ti:"$PORT" >/dev/null 2>&1; then
    echo "⚠️  Port $PORT is already in use by process $(lsof -ti:"$PORT"). Cleaning up..."
    kill -9 $(lsof -ti:"$PORT") 2>/dev/null || true
    sleep 1
fi

echo "============================================================"
echo " 🛸 ZERO-G KITCHEN: Anti-Gravity Food Ordering Engine"
echo "============================================================"
echo " 📍 Local:    http://localhost:${PORT}/"
echo " 🌐 Network:  http://${HOST}:${PORT}/"
echo " 📖 Swagger:  http://localhost:${PORT}/docs"
echo " ✨ Features: Table Reservations | Coupons | Bournet Gourmet"
echo "============================================================"
echo "🚀 Starting server with live auto-reload (Press Ctrl+C to stop)..."
echo ""

exec "$PYTHON" -m uvicorn app.main:app --host "$HOST" --port "$PORT" --reload
