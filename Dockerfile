# 官方的 Python 镜像
FROM python:3.11.10-slim
WORKDIR /myKaraoke/project
COPY requirements.txt .
COPY init.sh /init.sh
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN chmod +x /init.sh
RUN mkdir /KTV
RUN mkdir /karaoke
ENTRYPOINT ["/init.sh"]
EXPOSE 15210
CMD ["uvicorn", "main:app",  "--host", "0.0.0.0", "--port", "15210"]