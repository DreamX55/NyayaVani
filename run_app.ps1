Set-Location -LiteralPath $PSScriptRoot
python -m uvicorn backend.server:app --host 127.0.0.1 --port 8501
