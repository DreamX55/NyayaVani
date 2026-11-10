#!/usr/bin/env bash
# Launch NyayaVani (न्यायवाणी) Unified Web Application
# Framer Mondragon Entry Page + Claude Chat Interface
cd "$(dirname "$0")"
echo "Starting NyayaVani Server on http://localhost:8501..."
python3 -m uvicorn backend.server:app --host 127.0.0.1 --port 8501
