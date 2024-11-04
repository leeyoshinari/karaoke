#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

import json
import os.path
import asyncio
import subprocess
import traceback
from typing import List
from urllib.parse import unquote
from tortoise.exceptions import DoesNotExist
from karaoke.results import Result
from karaoke.models import Files, History, FileList, HistoryList
from settings import logger, FILE_PATH, PAGE_SIZE, VIDEO_PATH


clients: List[asyncio.Queue] = []


async def broadcast_data(data: dict):
    for client in clients[:]:
        try:
            await client.put(json.dumps(data, ensure_ascii=False))
        except:
            logger.error(traceback.format_exc())


async def init_history():
    try:
        songs = await History.filter(is_sing=-1)
        for s in songs:
            s.is_sing = 1
            await s.save()
    except:
        logger.error(traceback.format_exc())


async def upload_file(query) -> Result:
    result = Result()
    query = await query.form()
    file_name = query['file'].filename
    data = query['file'].file
    try:
        file_path = os.path.join(FILE_PATH, file_name)
        song_name = file_name.replace('.mp4', '').replace('_vocals.mp3', '').replace('_accompaniment.mp3', '')
        try:
            file = await Files.get(name=song_name)
        except DoesNotExist:
            file = await Files.create(name=song_name, is_sing=0)
        with open(file_path, 'wb') as f:
            f.write(data.read())
        result.msg = f"{file_name} 上传成功"
        result.data = file.name
        logger.info(result.msg)
    except:
        result.code = 1
        result.data = file_name
        result.msg = "系统错误"
        logger.error(f"{file_name} 上传失败")
        logger.error(traceback.format_exc())
    return result


async def get_list(q: str, page: int) -> Result:
    result = Result()
    try:
        if q:
            files = await Files.filter(name__contains=q).order_by('-id').offset((page - 1) * PAGE_SIZE).limit(PAGE_SIZE)
            total_num = await Files.filter(name__contains=q).count()
        else:
            files = await Files.all().order_by('-id').offset((page - 1) * PAGE_SIZE).limit(PAGE_SIZE)
            total_num = await Files.all().count()
        file_list = [FileList.from_orm_format(f).dict() for f in files]
        result.data = file_list
        result.page = page
        result.total = len(result.data)
        result.totalPage = (total_num + PAGE_SIZE - 1) // PAGE_SIZE
        logger.info("查询歌曲列表成功 ~")
    except:
        logger.error(traceback.format_exc())
        result.code = 1
        result.msg = "系统错误"
    return result


async def delete_song(file_id: int) -> Result:
    result = Result()
    try:
        file = await Files.get(id=file_id)
        if os.path.exists(f"{FILE_PATH}/{file.name}.mp4"):
            os.remove(f"{FILE_PATH}/{file.name}.mp4")
        if os.path.exists(f"{FILE_PATH}/{file.name}_vocals.mp3"):
            os.remove(f'{FILE_PATH}/{file.name}_vocals.mp3')
        if os.path.exists(f"{FILE_PATH}/{file.name}_accompaniment.mp3"):
            os.remove(f'{FILE_PATH}/{file.name}_accompaniment.mp3')
        try:
            history = await History.get(id=file_id)
            await history.delete()
        except DoesNotExist:
            pass
        await file.delete()
        result.msg = f"{file.name} 删除成功"
        logger.info(result.msg)
    except:
        logger.error(traceback.format_exc())
        result.code = 1
        result.msg = "系统错误"
    return result


async def delete_history(file_id: int) -> Result:
    result = Result()
    try:
        history = await History.get(id=file_id)
        await history.delete()
        result.msg = f"{history.name} 播放记录删除成功"
        await broadcast_data({"code": 8})
        logger.info(result.msg)
    except:
        logger.error(traceback.format_exc())
        result.code = 1
        result.msg = "系统错误"
    return result


async def sing_song(file_id: int) -> Result:
    result = Result()
    try:
        msg_list = []
        file = await Files.get(id=file_id)
        if file.is_sing == 0:
            if not os.path.exists(f"{FILE_PATH}/{file.name}.mp4"):
                msg_list.append("视频文件不存在")
            if not os.path.exists(f"{FILE_PATH}/{file.name}_vocals.mp3"):
                msg_list.append("人声文件不存在")
            if not os.path.exists(f"{FILE_PATH}/{file.name}_accompaniment.mp3"):
                msg_list.append("伴奏文件不存在")
            if len(msg_list) > 0:
                result.code = 1
                result.msg = '，'.join(msg_list)
                return result
            else:
                file.is_sing = 1
                await file.save()
                _ = await History.create(id=file.id, name=file.name)
                await broadcast_data({"code": 8})
        else:
            try:
                history = await History.get(id=file.id)
                if history.is_sing == 1:
                    history.is_sing = 0
                    history.is_top = 0
                    await history.save()
            except DoesNotExist:
                _ = await History.create(id=file.id, name=file.name, is_sing=0, is_top=0)
            finally:
                await broadcast_data({"code": 8})
        result.msg = f"{file.name} 点歌成功"
        logger.info(result.msg)
    except:
        logger.error(traceback.format_exc())
        result.code = 1
        result.msg = "系统错误"
    return result


async def history_list(query_type: str) -> Result:
    result = Result()
    try:
        if query_type == "history":
            songs = await History.filter(is_sing=1).order_by('-update_time').offset(0).limit(200)
            msg = "查询K歌历史列表成功"
        elif query_type == "usually":
            songs = await History.all().order_by('-times').offset(0).limit(200)
            msg = "查询经常K歌的歌曲列表成功"
        elif query_type == "pendingAll":
            songs = await History.filter(is_sing=-1)
            songs = songs + await History.filter(is_sing=0, is_top=1).order_by('-update_time')
            songs = songs + await History.filter(is_sing=0, is_top=0).order_by('update_time')
            msg = "查询已点列表的歌曲成功"
        else:
            songs = await History.filter(is_sing=-1)
            songs = songs + await History.filter(is_sing=0, is_top=1).order_by('-update_time')
            songs = songs + await History.filter(is_sing=0, is_top=0).order_by('update_time').offset(0).limit(4)
            msg = "查询已点列表最近的歌曲成功"
        song_list = [HistoryList.from_orm(f).dict() for f in songs]
        result.data = song_list
        result.total = len(result.data)
        logger.info(msg)
    except:
        logger.error(traceback.format_exc())
        result.code = 1
        result.msg = "系统错误"
    return result


async def set_top(file_id: int) -> Result:
    result = Result()
    try:
        history = await History.get(id=file_id)
        history.is_top = 1
        await history.save()
        result.msg = f"{history.name} 置顶成功"
        await broadcast_data({"code": 8})
        logger.info(result.msg)
    except:
        logger.error(traceback.format_exc())
        result.code = 1
        result.msg = "系统错误"
    return result


async def set_singing(file_id: int) -> Result:
    result = Result()
    try:
        history = await History.get(id=file_id)
        history.is_sing = -1
        history.is_top = 0
        await history.save()
        result.msg = f"{history.name} 设置-1成功"
        logger.info(result.msg)
    except:
        logger.error(traceback.format_exc())
        result.code = 1
        result.msg = "系统错误"
    return result


async def set_singed(file_id: int) -> Result:
    result = Result()
    try:
        history = await History.get(id=file_id)
        history.is_sing = 1
        history.is_top = 0
        history.times = history.times + 1
        await history.save()
        result.msg = f"{history.name} 设置1成功"
        await broadcast_data({"code": 8})
        logger.info(result.msg)
    except:
        logger.error(traceback.format_exc())
        result.code = 1
        result.msg = "系统错误"
    return result


async def upload_video(query) -> Result:
    result = Result()
    query = await query.form()
    file_name = query['file'].filename
    data = query['file'].file
    try:
        file_format = file_name.split(".")[-1]
        name = file_name.replace(f".{file_format}", "")
        file_path = os.path.join(VIDEO_PATH, f"{name}_origin.{file_format}")
        with open(file_path, 'wb') as f:
            f.write(data.read())
        result.msg = f"{file_name} 上传成功"
        result.data = file_name
        logger.info(result.msg)
    except:
        result.code = 1
        result.data = file_name
        result.msg = "系统错误"
        logger.error(f"{file_name} 上传失败")
        logger.error(traceback.format_exc())
    return result


async def deal_video(file_name: str) -> Result:
    result = Result()
    try:
        file_name = unquote(file_name)
        name = file_name.replace(".mp4", "")
        mp4_file = os.path.join(VIDEO_PATH, f"{name}_origin.mp4")
        mp3_file = os.path.join(VIDEO_PATH, f"{name}.mp3")
        cmd1 = ['ffmpeg', '-i', mp4_file, '-q:a', '0', '-map', 'a', mp3_file]
        subprocess.run(cmd1, check=True)
        no_voice_file = os.path.join(VIDEO_PATH, f"{name}_voice.mp4")
        cmd2 = ['ffmpeg', '-i', mp4_file, '-an', '-vcodec', 'copy', no_voice_file]
        subprocess.run(cmd2, check=True)
        video_file = os.path.join(VIDEO_PATH, f"{name}.mp4")
        cmd3 = ['ffmpeg', '-i', no_voice_file, '-map_metadata', '0', '-c:v', 'copy', '-c:a', 'copy', '-movflags', '+faststart', video_file]
        subprocess.run(cmd3, check=True)
        result.data = {"mp3": f"{name}.wav", "video": f"{name}.mp4"}
        logger.info(result.msg)
    except:
        logger.error(traceback.format_exc())
        result.code = 1
        result.msg = "系统错误"
    return result


async def convert_video(file_name: str) -> Result:
    result = Result()
    try:
        file_name = unquote(file_name)
        file_format = file_name.split(".")[-1]
        name = file_name.replace(f".{file_format}", "")
        audio_file = os.path.join(VIDEO_PATH, f"{name}_origin.{file_format}")
        mp4_file = os.path.join(VIDEO_PATH, f"{name}.mp4")
        cmd = ['ffmpeg', '-i', audio_file, '-c:v', 'libx264', '-c:a', 'aac', mp4_file]
        subprocess.run(cmd, check=True)
        result.data = {"mp4": f"{name}.mp4", "video": f"{name}.{file_format}"}
        logger.info(result.msg)
    except:
        logger.error(traceback.format_exc())
        result.code = 1
        result.msg = "系统错误"
    return result


async def convert_audio(file_name: str) -> Result:
    result = Result()
    try:
        file_name = unquote(file_name)
        file_format = file_name.split(".")[-1]
        name = file_name.replace(f".{file_format}", "")
        audio_file = os.path.join(VIDEO_PATH, f"{name}_origin.{file_format}")
        mp3_file = os.path.join(VIDEO_PATH, f"{name}.mp3")
        cmd = ['ffmpeg', '-i', audio_file, '-codec:a', 'libmp3lame', mp3_file]
        subprocess.run(cmd, check=True)
        result.data = {"mp3": f"{name}.mp3", "audio": f"{name}.{file_format}"}
        logger.info(result.msg)
    except:
        logger.error(traceback.format_exc())
        result.code = 1
        result.msg = "系统错误"
    return result
