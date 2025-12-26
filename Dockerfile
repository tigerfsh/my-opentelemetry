# 使用Python 3.9基础镜像
FROM docker.1ms.run/python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    curl \
    default-libmysqlclient-dev \
    pkg-config \
    mariadb-client \
    && rm -rf /var/lib/apt/lists/*

# 安装uv包管理器
# RUN curl -LsSf https://astral.sh/uv/0.9.18/install.sh | sh
RUN pip install uv -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制项目依赖文件
COPY pyproject.toml uv.lock ./

# 安装项目依赖
# RUN uv pip install -r uv.lock
RUN uv sync --frozen

# 复制项目文件
COPY . .

# 暴露端口
EXPOSE 8000

# 收集静态文件（如果有的话）
RUN uv run python manage.py collectstatic --noinput || true

# 运行应用
CMD ["uv run python", "manage.py", "runserver", "0.0.0.0:8000"]