#!/usr/bin/env bash
# Launch NyayaVani (न्यायवाणी) Unified Web Application
# Framer Mondragon Entry Page + Claude Chat Interface
cd "$(dirname "$0")"
echo "Starting NyayaVani Server on http://localhost:8501..."
/usr/local/bin/python3 -m uvicorn backend.server:app --host 0.0.0.0 --port 8501 --reload
