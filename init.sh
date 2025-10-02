#!/bin/bash
set -e

echo "[Init] 启动应用..."
exec uv run uvicorn app.api.server:app --host 0.0.0.0 --port 7777








