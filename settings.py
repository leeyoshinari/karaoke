#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

import os
import shutil
import sys
import configparser
import logging.handlers

if hasattr(sys, 'frozen'):
    path = os.path.dirname(sys.executable)
else:
    path = os.path.dirname(os.path.abspath(__file__))
cfg = configparser.ConfigParser()
config_path = os.path.join(path, 'config.conf')
cfg.read(config_path, encoding='utf-8')
PAGE_SIZE = 20


def get_config(key):
    return cfg.get('default', key, fallback=None)


FILE_PATH = get_config("path")
if not os.path.exists(FILE_PATH):
    raise FileNotFoundError(FILE_PATH)

TORTOISE_ORM = {
    "connections": {"default": f"sqlite://{FILE_PATH}/sqlite3.db"},
    "apps": {
        "models": {
            "models": ["karaoke.models", "aerich.models"],
            "default_connection": "default"
        }
    },
    "timezone": "Asia/Shanghai"
}

CONTENT_TYPE = {'mp4': 'video/mp4', 'mp3': 'audio/mpeg'}

VIDEO_PATH = os.path.join(path, 'static', 'videos')
if os.path.exists(VIDEO_PATH):
    shutil.rmtree(VIDEO_PATH)
os.mkdir(VIDEO_PATH)

log_path = os.path.join(path, 'logs')
if not os.path.exists(log_path):
    os.mkdir(log_path)

log_level = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

logger = logging.getLogger()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(threadName)s - %(filename)s[line:%(lineno)d] - %(message)s')
logger.setLevel(level=log_level.get(get_config("level")))

file_handler = logging.handlers.TimedRotatingFileHandler(os.path.join(log_path, 'access.log'), when='midnight', interval=1, backupCount=7)
file_handler.suffix = '%Y-%m-%d'
# file_handler = logging.StreamHandler()
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
