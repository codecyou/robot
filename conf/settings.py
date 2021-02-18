# 用于配置

import os
import json
from core import create_db

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, "db")  # 保存数据相关的目录
LOG_DIR = os.path.join(BASE_DIR, "log")  # 保存日志的目录
# configFile = os.path.join(BASE_DIR, 'conf', 'config.json')  # 配置文件路径

YULIAO_PATH = os.path.join(DB_DIR, "语料.txt")
RECORD_PATH = os.path.join(DB_DIR, "record.txt")
TANGSHI_PATH = os.path.join(DB_DIR, "唐诗.json")
IMAGES_PATH = os.path.join(BASE_DIR, "src/img")

BIRTHDAY = "2021-01-14 03:03:55"  # 程序诞生时间

DB_PATH = os.path.join(DB_DIR, "robot.db")

# 如果数据库文件不存在则创建数据库并初始化
if not os.path.exists(DB_PATH):
    create_db.create()
