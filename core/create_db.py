# 用于创建数据库 及表结构

import sqlite3
import os
import json
from conf import settings

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def create(conn=None):
    """用于创建数据库文件，并初始化"""

    if conn is None:
        conn = sqlite3.connect(settings.DB_PATH)
    c = conn.cursor()
    # 创建表结构

    # 聊天记录表
    talk_table = '''CREATE TABLE talks(
            id INTEGER PRIMARY KEY   AUTOINCREMENT NOT NULL,
            send_time TEXT NOT NULL,
            send_msg TEXT NOT NULL,
            receive_time TEXT NOT NULL,
            receive_msg TEXT NOT NULL
            );'''

    # 计时器表
    timer_table = '''CREATE TABLE timers(
             id INTEGER PRIMARY KEY   AUTOINCREMENT NOT NULL,
             create_time TEXT NOT NULL,
             cal_time FLOAT NOT NULL,
             title VARCHAR(50) NOT NULL,
             remark VARCHAR(100)
             );'''

    # 提醒任务表/倒计时表
    tip_table = '''CREATE TABLE tips(
             id INTEGER PRIMARY KEY   AUTOINCREMENT NOT NULL,
             create_time TEXT NOT NULL,
             end_time TEXT NOT NULL,
             title VARCHAR(50) NOT NULL,
             remark VARCHAR(100),
             state TINYINT default 0  -- 0,未完成 1,已完成 3,已删除
             );'''

    # 便签表
    note_table = '''CREATE TABLE notes(
             id INTEGER PRIMARY KEY   AUTOINCREMENT NOT NULL,
             create_time TEXT NOT NULL,
             modify_time TEXT NOT NULL,
             note_date TEXT NOT NULL,
             title VARCHAR(50) NOT NULL,
             remark VARCHAR(100)
             );'''

    # 诗词表
    poetry_table = '''CREATE TABLE poetrys(
             id INTEGER PRIMARY KEY   AUTOINCREMENT NOT NULL,
             title VARCHAR(50) NOT NULL,
             author VARCHAR(30) NOT NULL,
             content TEXT NOT NULL,
             remark TEXT
             );'''

    tables = [talk_table, timer_table, tip_table, note_table, poetry_table]
    for item in tables:
        cursor = c.execute(item)

    conn.commit()

    # 往数据库中插入诗词数据
    # 将json中的数据存入数据库
    with open(settings.TANGSHI_PATH, 'r', encoding="utf-8") as f:
        tangshi_json = json.load(f)
    for item in tangshi_json:
        title = item
        author = item
        content = tangshi_json[item]
        c.execute("insert into poetrys (title, author, content ) values (?, ?, ?)", (title, author, content))

    conn.commit()
    c.close()
    conn.close()


if __name__ == '__main__':
    db_dir = os.path.join(base_dir, "db")
    conn = sqlite3.connect(os.path.join(db_dir, "robot.db"))
    print("Opened database successfully")
    create(conn)


