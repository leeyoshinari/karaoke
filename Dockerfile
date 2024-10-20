# 官方的 Python 镜像
FROM python:3.11.10-slim
WORKDIR /karaoke
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 15200
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "15200"]
