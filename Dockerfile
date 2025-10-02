FROM python:3.10-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y curl build-essential && rm -rf /var/lib/apt/lists/*

# 安装 uv
RUN pip install --no-cache-dir uv

COPY pyproject.toml .
COPY . .

RUN uv pip install -r pyproject.toml --system

# 给 init.sh 添加执行权限
RUN chmod +x init.sh

EXPOSE 7777

CMD ["bash", "init.sh"]
