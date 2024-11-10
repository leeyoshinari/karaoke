# 官方的 Python 镜像
FROM python:3.11.10-slim
WORKDIR /karaoke/project
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN chmod +x init.sh
RUN mkdir /KTV
ENTRYPOINT ["./init.sh"]
EXPOSE 15210
CMD ["uvicorn", "main:agit pp", "--host", "0.0.0.0", "--port", "15210"]