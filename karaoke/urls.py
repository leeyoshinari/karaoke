#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

import json
import asyncio
import traceback
from fastapi import APIRouter, Request
from sse_starlette import EventSourceResponse
import karaoke.views as views
from karaoke.results import Result
from settings import logger


router = APIRouter(prefix='/song', tags=['歌曲'], responses={404: {'description': 'Not found'}})


@router.on_event('startup')
async def startup_event():
    await views.init_history()


@router.post('/upload', summary="上传歌曲")
async def upload_file(query: Request):
    result = await views.upload_file(query)
    return result


@router.get("/list", summary="歌曲列表")
async def song_list(q: str = "", page: int = 1):
    result = await views.get_list(q, page)
    return result


@router.get("/delete/{file_id}", summary="删除歌曲")
async def delete_song(file_id: int):
    result = await views.delete_song(file_id)
    return result


@router.get("/deleteHistory/{file_id}", summary="删除点歌历史记录")
async def delete_history(file_id: int):
    result = await views.delete_history(file_id)
    return result


@router.get("/sing/{file_id}", summary="点歌")
async def song_sing(file_id: int):
    result = await views.sing_song(file_id)
    return result


@router.get("/singHistory/{query_type}", summary="点歌历史纪录列表")
async def history_list(query_type: str):
    result = await views.history_list(query_type)
    return result


@router.get("/setTop/{file_id}", summary="置顶")
async def set_top(file_id: int):
    result = await views.set_top(file_id)
    return result


@router.get("/setSinged/{file_id}", summary="设置已经播放过")
async def set_singed(file_id: int):
    result = await views.set_singed(file_id)
    return result


@router.get("/setSinging/{file_id}", summary="设置正在播放")
async def set_dinging(file_id: int):
    result = await views.set_singing(file_id)
    return result


@router.post('/upload/video', summary="上传视频")
async def upload_video_file(query: Request):
    result = await views.upload_video(query)
    return result


@router.get('/deal/video/{file_name}', summary="处理视频")
async def deal_video(file_name: str, query: Request):
    result = await views.deal_video(file_name)
    return result


@router.get('/convert/audio/{file_name}', summary="处理音频")
async def convert_audio(file_name: str, query: Request):
    result = await views.convert_audio(file_name)
    return result


@router.get('/convert/video/{file_name}', summary="处理视频")
async def convert_video(file_name: str, query: Request):
    result = await views.convert_video(file_name)
    return result


@router.get('/local/import/{local_path}', summary="从本地路径导入歌曲文件")
async def import_local(local_path: str, query: Request):
    result = await views.convert_video(local_path)
    return result


@router.get("/events", summary="SSE")
async def get_events(request: Request):
    client_queue = asyncio.Queue()
    views.clients.append(client_queue)

    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    break
                message = await client_queue.get()
                yield message
        except:
            logger.error(traceback.format_exc())
        finally:
            views.clients.remove(client_queue)

    return EventSourceResponse(event_generator())


@router.get("/send/event", summary="发送数据")
async def send_event(code: int, data, request: Request):
    data = json.dumps({'code': code, 'data': data})
    for client in views.clients:
        await client.put(data)
    return Result()


# SSE功能对应的消息格式为 {"code": 0, "data": 1}
# code = 0: 无实际含义，可用于心跳检测
# code = 1: 开始/暂停K歌，data = 0 暂停，data = 1 开始，data = 3 已经开始播放，data = 4 已经停止播放，data = 5 第一次播放
# code = 2: 重唱
# code = 3: 切歌，下一首
# code = 4: 切换原唱/伴奏，data = 0 原唱，data = 1 伴奏
# code = 5: 调整原唱音量，data 为音量值
# code = 6: 调整伴奏音量，data 为音量值
# code = 7: 互动，data 为互动方式
# code = 8: 查询已点歌曲列表
