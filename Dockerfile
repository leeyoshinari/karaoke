# 官方的 Python 镜像
FROM python:3.11.10-slim
WORKDIR /karaoke/project
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN ln -s /usr/bin/ffmpeg /karaoke/ffmpeg
RUN mkdir /karaoke/data
EXPOSE 15200
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "15200"]
CMD ["sh", "-c", "cp -n /karaoke/project/sqlite3.db /karaoke/ && uvicorn main:app --host 0.0.0.0 --port 15200"]
