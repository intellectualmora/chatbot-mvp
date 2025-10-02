#!/bin/bash
set -e

echo "[Init] 拉取模型..."
uv run python init.py --download-models

echo "[Init] 初始化数据库并构建向量索引..."
uv run python init.py --build-index

echo "[Init] 启动应用..."
exec uv run uvicorn app.api.server:app --host 0.0.0.0 --port 7777
