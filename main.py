#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

import os
import socket
import traceback
from urllib.parse import unquote
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from tortoise.contrib.fastapi import register_tortoise
import settings
from karaoke.responses import StreamResponse
from karaoke.results import Result
import karaoke.urls as my_urls


prefix = '/hhh'  # url prefix, url的前缀
app = FastAPI()
register_tortoise(app=app, config=settings.TORTOISE_ORM)
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


def get_local_ip():
    host = "0.0.0.0"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("114.114.114.114", 80))
        host = s.getsockname()[0]
    finally:
        s.close()
    return host


async def read_file(file_path, start_index=0):
    with open(file_path, 'rb') as f:
        f.seek(start_index)
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            yield chunk


@app.get(prefix + "/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "prefix": prefix})


@app.get(prefix + "/dealVideo")
async def index(request: Request):
    return templates.TemplateResponse("tool.html", {"request": request, "prefix": prefix})


@app.get(prefix + "/sing")
async def play(request: Request):
    return templates.TemplateResponse("playing.html", {"request": request, "prefix": prefix})


@app.get(prefix + "/song")
async def index(request: Request):
    return templates.TemplateResponse("client.html", {"request": request, "prefix": prefix})


@app.get(prefix + "/download/{file_name}", summary="Download file (获取文件)")
async def download_file(file_name: str):
    try:
        file_name = unquote(file_name)
        file_path = os.path.join(settings.FILE_PATH, file_name)
        file_format = file_name.split('.')[-1]
        headers = {'Accept-Ranges': 'bytes', 'Content-Length': str(os.path.getsize(file_path)),
                   'Content-Disposition': f'inline;filename="{file_name}"'}
        return StreamResponse(read_file(file_path), media_type=settings.CONTENT_TYPE.get(file_format, 'application/octet-stream'), headers=headers)
    except:
        print(traceback.format_exc())
        return Result(code=1, msg="System Error")

app.include_router(my_urls.router, prefix=prefix)


if __name__ == "__main__":
    import uvicorn
    local_ip = settings.get_config('host')
    if not local_ip:
        local_ip = get_local_ip()
    uvicorn.run(app="main:app", host=local_ip, port=int(settings.get_config('port')), reload=False)
