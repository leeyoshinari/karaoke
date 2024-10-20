# 使用官方的 Python 镜像
FROM python:3.11.10-slim

# 设置工作目录
WORKDIR /usr/src/karaoke

# 复制 requirements.txt 文件到容器中的工作目录
COPY requirements.txt .

# 安装项目依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码到容器中
COPY . .

# 开放容器的端口
EXPOSE 15200

# 运行 Uvicorn 服务器
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "15200"]
