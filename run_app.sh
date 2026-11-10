#!/usr/bin/env bash
# Launch NyayaVani (न्यायवाणी) Unified Web Application
# Framer Mondragon Entry Page + Claude Chat Interface
cd "$(dirname "$0")"
PYTHON_CMD="python3"
if [ -x "/usr/local/bin/python3" ]; then
    PYTHON_CMD="/usr/local/bin/python3"
fi
echo "Starting NyayaVani Server on http://localhost:8501..."
$PYTHON_CMD -m uvicorn backend.server:app --host 127.0.0.1 --port 8501 --reload
