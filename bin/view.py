import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mBox
from tkinter.scrolledtext import ScrolledText
from tkinter import END
from PIL import Image, ImageTk
import threading
import os
import sys
import time
import random
import sqlite3
import json
import re
import webbrowser
from tkinter.filedialog import askdirectory, askopenfilename, asksaveasfilename
from tkinter.messagebox import *

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)
from conf import settings
from core.Mytools import resize, choice_img, calDate, changeStrToDate, remake_time_human

answer = {"问候": ['你好啊，今天怎么样啊？', '你好啊！', '嗨！'],
          "聊天": ['至少还有我陪着你', '加油，相信你', '嗯？', '嗯！', '平凡的脚步也可以走完伟大的行程']
          }  # 程序回复答案集

# 读取语料库
with open(settings.YULIAO_PATH, 'r', encoding="utf-8") as f:
    content = f.readlines()
    for item in content:
        answer["聊天"].append(item.strip())
    # print(answer)


class IndexFrame(tk.Frame):  # 继承Frame类
    def __init__(self, master=None):
        self.pwin = master  # 父容器对象引用，方便后面调用父容器实例方法
        tk.Frame.__init__(self, master.win)
        self.root = ttk.Frame(master.win)  # 定义内部变量root
        # self.root.pack()
        self.createPage()

    def createPage(self):
        msgFrame = ttk.Frame(self.root, width=600, height=300)  # 创建消息区
        sendFrame = ttk.Frame(self.root, width=600, height=100)  # 创建输入区
        buttunFrame = ttk.Frame(self.root, width=600, height=100)  # 按钮区

        f_right = ttk.Frame(self.root, width=200, height=600)  # 右侧区域
        f_info = ttk.Frame(f_right, width=200, height=100)  # 信息区域/ “robot与你相伴的第 x 个日夜”
        f_image = ttk.Frame(f_right, width=200, height=200)  # 图片区域
        f_greet = ttk.Frame(f_right, width=200, height=100)  # 问候信息区域
        f_option = ttk.Frame(f_right, width=200, height=200)  # 操作菜单区域
        self.txt_msgList = ScrolledText(msgFrame, height=31, wrap=tk.WORD)  # 消息列表分区中创建文本控件
        self.txt_msgList.tag_config("green", foreground="green")  # 消息列表分区中创建标签
        self.txt_msgSend = ScrolledText(sendFrame, height=12)

        msgFrame.grid(row=0, column=0)
        sendFrame.grid(row=1, column=0, pady=5)
        buttunFrame.grid(row=2, column=0)
        f_right.grid(row=0, column=1, rowspan=3)
        f_info.grid(row=0, column=0)  # 展示信息 "robot 与你相伴 x 个日夜"
        f_image.grid(row=1, column=0)  # 图片Frame为f_right的子容器
        f_greet.grid(row=2, column=0, sticky=tk.S)  # 图片Frame为f_right的子容器
        f_option.grid(row=3, column=0, sticky=tk.S)

        self.txt_msgList.grid()
        self.txt_msgSend.grid()
        self.txt_msgList.insert(tk.INSERT, "robot:  %s\n" % random.choice(answer["问候"]))  # 初始问候语

        ttk.Button(buttunFrame, text="清空输入框", command=self.emptyLog).grid(row=0, column=0)
        ttk.Button(buttunFrame, text="发送", command=self.sendMsg).grid(row=0, column=1)
        ttk.Button(f_option, text="背首古诗", command=self.readPoetry).grid(row=0, column=0)
        ttk.Button(f_option, text="查看聊天记录", command=self.pwin.recordData).grid(row=0, column=1)
        ttk.Button(f_option, text="诗词更新", command=self.pwin.poetryData).grid(row=1, column=0)
        ttk.Button(f_option, text="计时", command=self.pwin.timerData).grid(row=1, column=1)
        ttk.Button(f_option, text="提醒", command=self.pwin.tipData).grid(row=2, column=0)
        ttk.Button(f_option, text="备忘", command=self.pwin.noteData).grid(row=2, column=1)

        # 右侧信息区
        self.label_info = tk.Label(f_info, font=("华文行楷", 10), fg="green")  # 展示信息 "robot 与你相伴 x 个日夜"
        self.label_info.grid()
        self.label_timer_info = ttk.Label(f_info)
        self.label_tip_info = ttk.Label(f_info)
        self.label_timer_info.grid()
        self.label_tip_info.grid()

        self.photo = self.getImg()
        self.label_img = tk.Label(f_image, image=self.photo, width=200, height=200)
        self.label_img.grid()  # 用于展示图片
        self.label_greet = ttk.Label(f_greet)  # 用于展示问候语
        self.label_time = ttk.Label(f_greet)  # 用于展示时间
        self.label_greet.grid(row=1, column=0)
        self.label_time.grid(row=2, column=0)
        self.run_greet()  # 创建子线程用于显示问候以及时间
        self.txt_msgSend.bind("<Control-Return>", func=self.run_sendMsg)  # 绑定键盘事件 ctrl + enter为发送消息
        # self.txt_msgSend.bind("<Return>", func=self.run_sendMsg)

    def readPoetry(self):
        """念唐诗，匹配《念首唐诗》按钮"""
        conn = sqlite3.connect(settings.DB_PATH)
        c = conn.cursor()

        self.txt_msgList.config(state=tk.NORMAL)  # 消息区打开读写
        # 获取唐诗资源并输出到消息区
        c.execute("select count(*) from poetrys")
        poetry_num = c.fetchone()[0]   # (316,) 故取元组第一位
        poetry_id = random.choice(range(poetry_num))
        print("poetry_id：", poetry_id)
        c.execute("select id,title,author,content,remark from poetrys where id=?", (poetry_id,))
        # print(c.fetchone())
        self.txt_msgList.insert(END, "\nrobot %s \n" % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
        self.txt_msgList.insert(END, "id:%s\n\n%s\n%s\n\n%s\n\n备注:%s\n" % c.fetchone())  # 获取发送消息，添加文本到消息列表
        self.txt_msgList.see(END)  # 将滚动文本焦点设置到最新处
        self.txt_msgList.config(state=tk.DISABLED)  # 消息区设为只读 不可更改
        c.close()
        conn.close()

    def sendMsg(self):
        """实际发送消息函数"""
        # 链接数据库
        conn = sqlite3.connect(settings.DB_PATH)
        c = conn.cursor()
        self.txt_msgList.config(state=tk.NORMAL)  # 消息区打开读写
        send_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        msg = '\n我 %s \n' % send_time
        self.txt_msgList.insert(END, msg, 'green')  # 添加时间
        send_msg = self.txt_msgSend.get('0.0', END).strip()
        self.txt_msgList.insert(END, "%s\n" % send_msg)  # 获取发送消息，添加文本到消息列表
        self.txt_msgSend.delete('0.0', END)  # 清空发送消息
        if send_msg in ["念首唐诗", "再来一首"]:
            # 从json文件读取
            self.readPoetry()
        else:
            answer_msg = random.choice(answer["聊天"])
            print("robot:  %s" % answer_msg)
            answer_time =time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            self.txt_msgList.insert(END, "\nrobot %s \n" % answer_time)
            self.txt_msgList.insert(END, "%s\n" % answer_msg)
            local_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            c.execute("insert into talks (send_time, send_msg, receive_time, receive_msg) values (?,?,?,?)", (send_time, send_msg, answer_time, answer_msg))
            conn.commit()
            self.txt_msgList.see(END)
        self.txt_msgList.config(state=tk.DISABLED)  # 消息区设为只读 不可更改
        c.close()
        conn.close()

    def run_sendMsg(self, event=None):
        """用于解决GUI耗时阻塞问题"""
        t = threading.Thread(target=self.sendMsg)
        t.start()

    def insertToLog(self, str):
        self.txt_msgList.insert(END, str+'\n')
        self.txt_msgList.see(END)

    def emptyLog(self):
        self.txt_msgSend.delete(0.0, END)

    def getImg(self):
        """获取随机图片，并缩放到合适尺寸 """
        # resize函数使用过程：
        # ==================================================================
        w_box = 180  # 期望图像显示的大小（窗口大小）
        h_box = 180
        pil_image = Image.open(choice_img())  # 以一个PIL图像对象打开  【调整待转图片格式】
        pil_image_resized = resize(w_box, h_box, pil_image)  # 缩放图像让它保持比例，同时限制在一个矩形框范围内  【调用函数，返回整改后的图片】
        photo = ImageTk.PhotoImage(pil_image_resized)  # 把PIL图像对象转变为Tkinter的PhotoImage对象  【转换格式，方便在窗口展示】
        # ====================================================================
        return photo

    def changeImg(self):
        """修改图片，切换图片"""
        self.photo = self.getImg()
        # self.canvas_img.image=photo
        self.label_img.config(image=self.photo)

    def greet(self):
        """程序问候语，当前时间显示"""
        # 程序初始问候
        count = 0  # 用于计时刷新图片
        while True:
            local_hour = time.localtime().tm_hour  # 当前小时，用于判断上下午
            local_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  # 当前时间
            if local_hour in range(0, 6):
                msg = "这么晚了还不休息么？"
            elif local_hour in range(6, 12):
                msg = "上午好！"
            elif local_hour in range(12, 14):
                msg = "中午好！"
            elif local_hour in range(14, 19):
                msg = "下午好！"
            else:
                msg = "晚上好！"
            days_ago = calDate(settings.BIRTHDAY, local_time)  # robot程序诞生至今多少时间
            info = "robot 与你相伴 %s 个日夜！" % days_ago
            # 展示计时任务信息
            timer_num = len(self.pwin.timerPage.timer_active)
            if timer_num:
                self.label_timer_info.config(text="现在共有 %s 个计时器任务正在运行！" % timer_num)
            else:
                self.label_timer_info.config(text="")

            # 展示提醒任务信息
            tip_num = len(self.pwin.tipPage.timer_active)
            if tip_num:
                self.label_tip_info.config(text="现在共有 %s 个提醒任务正在运行！" % tip_num)
            else:
                self.label_tip_info.config(text="")

            self.label_info.config(text=info)  # 展示陪伴信息
            self.label_greet.config(text=msg)  # 问候语
            self.label_time.config(text=local_time)  # 当前时间
            time.sleep(0.5)
            count += 1
            if count == 20:  # 10秒切换一次图片
                count = 0
                self.changeImg()

    def run_greet(self):
        """用于创建子进程执行问候语以及时间显示操作，避免GUI耗时阻塞"""
        t = threading.Thread(target=self.greet)
        # 设置守护线程 避免主线程结束后子线程访问主线程资源报，RuntimeError: main thread is not in main loop
        # Tcl_AsyncDelete: async handler deleted by the wrong thread
        t.daemon = True
        t.start()


class PoetryFrame(tk.Frame):  # 继承Frame类
    # 创建诗词页面
    def __init__(self, master=None):
        tk.Frame.__init__(self, master.win)
        self.root = ttk.Frame(master.win)  # 定义内部变量root
        self.pwin = master  # 父容器对象的引用，方便后面调用父类方法
        # self.root.pack()
        self.select_id = tk.IntVar()  # 选中的id  ，用于定位修改的便签
        self.search_key = tk.StringVar()  # 搜索关键字
        self.search_mode = tk.StringVar()  # 搜索模式 text 标题  author 作者
        self.search_mode.set("title")
        self.new_title = tk.StringVar()  # 要修改的诗词标题，默认为原标题
        self.new_author = tk.StringVar()  # 要修改的诗词作者
        self.createPage()
        # 链接数据库
        self.conn = sqlite3.connect(settings.DB_PATH)
        self.c = self.conn.cursor()

    def createPage(self):
        f_top = ttk.Frame(self.root)
        f_title = ttk.Frame(self.root)
        f_content = ttk.Frame(self.root)
        f_bottom = ttk.Frame(self.root)
        f_top.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        f_bottom.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        f_title.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        f_content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # f_right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ttk.Label(f_top, text="修改诗词").pack(pady=10)
        ttk.Button(f_top, text="返回主页", command=self.pwin.returnIndex).pack(anchor=tk.NE, pady=2)
        ttk.Label(f_title, text="ID:").grid(row=0, column=0, padx=5)
        self.label_id = ttk.Label(f_title, text="")  # 显示当前诗歌id
        self.label_id.grid(row=0, column=1, padx=5, sticky=tk.W)
        ttk.Label(f_title, text="标题:").grid(row=1, column=0, padx=5)
        self.label_poetry_title = ttk.Entry(f_title, width=80, textvariable=self.new_title)
        self.label_poetry_title.grid(row=1, column=1)
        ttk.Label(f_title, text="作者:").grid(row=2, column=0, padx=5, pady=2)
        self.label_poetry_author = ttk.Entry(f_title, width=80, textvariable=self.new_author)
        self.label_poetry_author.grid(row=2, column=1)
        ttk.Label(f_content, text="正文").grid(row=0, column=0)
        ttk.Label(f_content, text="备注").grid(row=0, column=1)
        self.s_content = ScrolledText(f_content, wrap=tk.WORD, width=60, height=30)
        self.s_content.grid(row=1, column=0)
        self.s_remark = ScrolledText(f_content, wrap=tk.WORD, width=40, height=30)
        self.s_remark.grid(row=1, column=1)

        ttk.Label(f_bottom, text="查找诗词").grid(row=0, column=0)
        ttk.Radiobutton(f_bottom, text="根据标题", value="title", variable=self.search_mode).grid(row=0, column=1)
        ttk.Radiobutton(f_bottom, text="根据作者", value="author", variable=self.search_mode).grid(row=0, column=2)
        ttk.Entry(f_bottom, textvariable=self.search_key, width=50).grid(row=2, column=0, columnspan=4)
        ttk.Button(f_bottom, text="搜索", command=self.searchPoetry).grid(row=2, column=4)
        self.buttun_del = ttk.Button(f_bottom, text="删除", command=self.delPoetry, state=tk.DISABLED)
        self.buttun_del.grid(row=2, column=5, sticky=tk.E)
        self.buttun_update = ttk.Button(f_bottom, text="修改", command=self.updatePoetry, state='disabled')
        self.buttun_update.grid(row=2, column=6, sticky=tk.E)
        self.buttun_add = ttk.Button(f_bottom, text="新增", command=self.addPoetry)
        self.buttun_add.grid(row=2, column=7, sticky=tk.E)
        ttk.Label(f_bottom, text="定位编号:").grid(row=0, column=5)
        ttk.Entry(f_bottom, textvariable=self.select_id, width=12).grid(row=0, column=6)
        self.buttun_locate = ttk.Button(f_bottom, text="定位", command=self.showSelectPoetry)
        self.buttun_locate.grid(row=0, column=7, sticky=tk.E)

    def clearMsg(self):
        # 清空显示区
        self.new_title.set("")
        self.new_author.set("")
        self.s_content.delete("0.0", tk.END)
        self.s_remark.delete("0.0", tk.END)

    def searchPoetry(self):
        """搜索诗词"""
        # 清空内容
        # 搜索操作先锁定“修改”按钮，防止误操作引发数据出错
        # 清空显示区
        self.clearMsg()
        search_key = self.search_key.get()
        if self.search_mode == "title":
            sql = "select id,title,author,content,remark from poetrys where title like ?"
        else:
            sql = "select id,title,author,content,remark from poetrys where author like ?"
        self.c.execute(sql, ("%%%s%%" % search_key,))
        self.result = self.c.fetchall()  # ((xxx,xxx,x),)
        if len(self.result):
            if len(self.result) == 1:
                # 将原来的诗词数据填到对应区域
                self.new_title.set(self.result[0][1])
                self.new_author.set(self.result[0][2])
                self.s_content.insert(END, "%s" % self.result[0][3])
                self.s_remark.insert(END, "%s" % self.result[0][4])
            else:
                mBox.showinfo("多个搜索结果", "共搜索到%s个符合条件结果！" % len(self.result))
                for item in self.result:
                    self.s_content.insert(END, "编号: %s\n标题: %s\n作者: %s\n%s\n\n备注:\n%s\n\n" % item)
        else:
            self.s_content.insert(tk.INSERT, "未找到 %s 的诗词" % search_key)
        # 将定位以及修改诗词部分的控件置为最初状态，避免误操作
        self.select_id.set("")
        self.label_id.config(text="")
        self.buttun_del.config(state=tk.DISABLED)
        self.buttun_update.config(state=tk.DISABLED)

    def showSelectPoetry(self):
        """用于定位诗词"""
        # 清空显示区
        self.clearMsg()
        select_id = self.select_id.get()  # 定位编号
        # print(select_id)
        sql = "select id,title,author,content,remark from poetrys where id=?"
        self.c.execute(sql, (select_id,))
        poetry_item = self.c.fetchone()
        # print(poetry_item)
        if poetry_item:
            # 将修改按钮置为normal，使其可点击
            self.buttun_update.config(state=tk.NORMAL)
            self.buttun_del.config(state=tk.NORMAL)
            self.label_id.config(text=select_id)
            self.new_title.set(poetry_item[1])
            self.new_author.set(poetry_item[2])
            self.s_content.insert(END, "%s" % poetry_item[3])
            self.s_remark.insert(END, "%s" % poetry_item[4])

    def updatePoetry(self):
        """修改诗词内容"""
        poetry_id = self.select_id.get()
        new_title = self.new_title.get()
        new_author = self.new_author.get()
        new_content = self.s_content.get('0.0', END)
        new_remark = self.s_remark.get('0.0', END)
        # 修改诗词
        sql = "update poetrys set title=?,author=?,content=?,remark=? where id=?"
        self.c.execute(sql, (new_title, new_author, new_content, new_remark, poetry_id))
        self.conn.commit()
        # 清空状态防止后续操作数据出错
        self.result = None
        self.buttun_update.config(state=tk.DISABLED)
        self.buttun_del.config(state=tk.DISABLED)
        mBox.showinfo('诗词修改成功！', '编号为:%s 的诗词修改完成！' % poetry_id)

    def delPoetry(self):
        """删除诗词"""
        poetry_id = self.select_id.get()
        # 修改诗词
        sql = "delete from poetrys  where id=?"
        self.c.execute(sql, (poetry_id,))
        self.conn.commit()
        # 清空状态防止后续操作数据出错
        self.result = None
        self.buttun_update.config(state=tk.DISABLED)
        self.buttun_del.config(state=tk.DISABLED)
        mBox.showinfo('诗词删除成功！', '编号为:%s 的诗词删除完成！' % poetry_id)

    def addPoetry(self):
        """新增诗词"""
        new_title = self.new_title.get()
        new_author = self.new_author.get()
        new_content = self.s_content.get('0.0', END)
        new_remark = self.s_remark.get('0.0', END)
        # 修改诗词
        sql = "insert into poetrys(title,author,content,remark) values (?,?,?,?)"
        self.c.execute(sql, (new_title, new_author, new_content, new_remark))
        self.conn.commit()
        # 清空状态防止后续操作数据出错
        mBox.showinfo('诗词新增成功！', '标题为:%s 的诗词新增完成！' % new_title)


class RecordFrame(tk.Frame):  # 继承Frame类
    # 创建聊天记录查看页面
    def __init__(self, master=None):
        tk.Frame.__init__(self, master.win)
        self.root = ttk.Frame(master.win)  # 定义内部变量root
        self.pwin = master  # 父容器对象引用，方便后面调用父容器实例方法
        # self.root.pack()
        self.search_key = tk.StringVar()  # 搜索关键字
        self.search_mode = tk.StringVar()  # 搜索模式 content 文本内容  time 时间
        self.search_mode.set("content")
        self.createPage()
        self.conn = sqlite3.connect(settings.DB_PATH)
        self.c = self.conn.cursor()

    def createPage(self):
        f_top = ttk.Frame(self.root)
        f_content = ttk.Frame(self.root)
        f_bottom = ttk.Frame(self.root)
        f_top.pack(side=tk.TOP, fill=tk.BOTH)
        f_content.pack(side=tk.TOP, fill=tk.BOTH)
        f_bottom.pack(side=tk.BOTTOM, fill=tk.BOTH)

        ttk.Label(f_top, text="查看聊天记录").pack(pady=10)
        ttk.Button(f_top, text="返回主页", command=self.pwin.returnIndex).pack(anchor=tk.NE)
        self.txt_record = ScrolledText(f_content, wrap=tk.WORD, width=100, height=35)
        self.txt_record.pack(pady=5)
        ttk.Label(f_bottom, text="查找聊天记录").grid(row=0, column=0)
        ttk.Radiobutton(f_bottom, text="根据内容", value="content", variable=self.search_mode).grid(row=0, column=1)
        ttk.Radiobutton(f_bottom, text="根据时间", value="time", variable=self.search_mode).grid(row=0, column=2)
        ttk.Entry(f_bottom, textvariable=self.search_key, width=50).grid(row=2, column=0, columnspan=3)
        ttk.Button(f_bottom, text="搜索", command=self.serachRecord).grid(row=2, column=5)
        ttk.Button(f_bottom, text="查看所有聊天记录", command=self.showAllRecord).grid(row=2, column=6)

    def showAllRecord(self):
        # 清空消息记录区
        self.txt_record.delete("0.0", END)
        # 插入聊天记录数据
        sql = "select send_time,send_msg,receive_time,receive_msg from talks"
        self.c.execute(sql)
        content = self.c.fetchall()  # 从数据库获取所有聊天记录
        for item in content:
            self.txt_record.insert(END, "me %s\n%s\nrobot %s\n%s\n\n" % item)  # 消息时间
            self.txt_record.see(END)

    def serachRecord(self):
        """用于搜索聊天记录"""
        # 清空消息记录区
        self.txt_record.delete("0.0", END)
        # 获取要搜索的内容关键字
        search_key = self.search_key.get()
        # 根据聊天时间
        if self.search_mode.get() == "time":
            sql = "select send_time,send_msg,receive_time,receive_msg from talks where send_time like ? or receive_time like ?"
        else:
            # 根据聊天内容
            sql = "select send_time,send_msg,receive_time,receive_msg from talks where send_msg like ? or receive_msg like ?"
        self.c.execute(sql, ("%%%s%%" % search_key, "%%%s%%" % search_key))
        content = self.c.fetchall()
        for item in content:
            self.txt_record.insert(END, "me %s\n%s\nrobot %s\n%s\n\n" % item)  # 消息时间
            self.txt_record.see(END)


class TimerFrame(tk.Frame):  # 继承Frame类
    def __init__(self, master=None):
        tk.Frame.__init__(self, master.win)
        # 创建计时器页面
        self.root = ttk.Frame(master.win)  # 定义内部变量root
        self.pwin = master  # 父容器对象引用，方便后面调用父容器实例方法
        # self.root.pack()
        self.new_title = tk.StringVar()  # 新建计时器标题
        self.new_remark = tk.StringVar()  # 新建计时器备注
        self.timer_row = 2  # 用于布局显示label的行起始位置
        self.process_id = 0  # 计时器编号,方便程序控制，并非记录在数据库的id 因为有可能会存在某些时候不保存进数据库 为了避免程序id和数据库id冲突故两者隔离开
        self.timer_active = []  # 用于记录当前正在计时的计时器，配合停止button使用
        self.search_key = tk.StringVar()  # 用于在计时器记录界面搜索计时器，要搜索的计时器的关键字
        self.search_mode = tk.StringVar()  # 用于在计时器记录界面搜索计时器，要搜索的计时器的模式  “content”  内容  "time"  时间
        self.search_mode.set("content")
        # 链接数据库
        self.conn = sqlite3.connect(settings.DB_PATH)
        self.c = self.conn.cursor()
        self.createPage()

    def createPage(self):
        f_top = ttk.Frame(self.root)  # 显示标题
        f_top.pack(fill=tk.BOTH)
        f_option = ttk.Frame(self.root)  # 显示操作区
        f_option.pack()
        self.f_content = ttk.Frame(self.root)  # 记录显示区
        self.f_content.pack()
        ttk.Label(f_top, text="计时器").pack(pady=10)
        ttk.Button(f_top, text="返回主页", command=self.pwin.returnIndex).pack(anchor=tk.NE)
        ttk.Label(f_option, text="事项").grid(row=0, column=1)
        ttk.Label(f_option, text="备注").grid(row=0, column=2)
        ttk.Entry(f_option, textvariable=self.new_title, width=30).grid(row=1, column=1, padx=2)
        ttk.Entry(f_option, textvariable=self.new_remark, width=30).grid(row=1, column=2, padx=2)
        self.button_start = ttk.Button(f_option, text="创建", command=self.runNewJob)
        self.button_start.grid(row=1, column=3, padx=5)

        self.label_active = ttk.Label(self.f_content, text="当前共有 %s 个计时器任务！" % len(self.timer_active))  # 展示当前计时任务个数
        self.label_active.grid(row=0, column=0, columnspan=5, pady=5)
        ttk.Button(self.f_content, text="查看历史记录", command=self.show_record).grid(row=0, column=5, pady=5)
        ttk.Label(self.f_content, text="事项").grid(row=1, column=1, padx=5)
        ttk.Label(self.f_content, text="备注").grid(row=1, column=2, padx=5)
        ttk.Label(self.f_content, text="开始时间").grid(row=1, column=3, padx=5)
        ttk.Label(self.f_content, text="已计时长").grid(row=1, column=4, padx=5)

    def backPrePage(self):
        """从记录查询页面返回计时器操作页面"""
        self.root_new.pack_forget()
        self.root.pack()

    def show_record(self):
        """用于查看历史记录"""
        self.root_new = ttk.Frame(self.pwin.win)  # 记录查看页面Frame
        self.root_new.pack()
        self.root.pack_forget()  # 隐藏原root页面

        ttk.Label(self.root_new, text="计时器记录查看").grid(row=0, column=0, columnspan=3, pady=5)
        ttk.Button(self.root_new, text="返回上一页", command=self.backPrePage).grid(row=0, column=2)
        self.content = ScrolledText(self.root_new, height=35, width=95, wrap=tk.WORD)  # 创建记录展示区
        self.content.tag_config("green", foreground="green")  # 消息列表分区中创建标签
        self.content.grid(row=1, columnspan=3)
        ttk.Label(self.root_new, text="查找模式:").grid(row=2, column=0)
        ttk.Radiobutton(self.root_new, text="根据内容", value="content", variable=self.search_mode).grid(row=2, column=1)
        ttk.Radiobutton(self.root_new, text="根据时间", value="time", variable=self.search_mode).grid(row=2, column=2)

        ttk.Entry(self.root_new, textvariable=self.search_key, width=50).grid(row=3, column=0)
        ttk.Button(self.root_new, text="搜索", command=self.searchRecord).grid(row=3, column=1)
        ttk.Button(self.root_new, text="查看所有", command=self.showAll).grid(row=3, column=2, sticky=tk.EW)
        self.showAll()  # 显示所有信息

    def searchRecord(self):
        """用于搜索计时器记录"""
        # 清空数据区
        self.content.delete("0.0", tk.END)
        # 搜索匹配条件的记录
        search_key = self.search_key.get()
        if self.search_mode.get() == "time":
            sql = "select id,create_time,cal_time,title,remark from timers where create_time like ?"
            self.c.execute(sql, ("%%%s%%" % search_key,))
        else:
            sql = "select id,create_time,cal_time,title,remark from timers where title like ? or remark like?"
            self.c.execute(sql, ("%%%s%%" % search_key, "%%%s%%" % search_key))

        record = self.c.fetchall()
        if record and len(record):
            result_list = []  # 用于记录搜索到的计时信息，存储计时时长
            for item in record:
                msg = "编号:%s, 开始时间:%s, 计时时长:%s, 事项:%s, 备注:%s\n" % (
                item[0], item[1], remake_time_human(item[2]), item[3], item[4])
                result_list.append(item[2])  # 将匹配到的符合条件的计时时长信息添加到result_list中
                self.content.insert(tk.INSERT, msg)
            # 显示搜索统计信息
            sum_msg = sum(result_list)
            avg_msg = sum_msg / len(result_list)
            msg = "共找到 %s 条符合条件的计时任务信息，SUM: %s  ,MAX: %s  ,AVG: %s  ,MIN: %s  " % (len(result_list), remake_time_human(sum_msg), remake_time_human(max(result_list)), remake_time_human(avg_msg), remake_time_human(min(result_list)))
            self.content.insert(tk.INSERT, msg, "green")
        else:
            self.content.insert(tk.INSERT, "未找到符合条件的计时任务信息！", "green")

    def showAll(self):
        """用于显示所有计时器信息"""
        # 输出信息
        self.content.delete("0.0", tk.END)
        sql = "select id,create_time,cal_time,title,remark from timers"
        self.c.execute(sql)
        record = self.c.fetchall()
        if record and len(record):
            self.content.insert(tk.INSERT, "共有 %s 个计时器历史记录！\n" % len(record), "green")
            for item in record:
                msg = "编号:%s, 开始时间:%s, 计时时长:%s, 事项:%s, 备注:%s\n" % (item[0], item[1], remake_time_human(item[2]), item[3], item[4])
                self.content.insert(tk.INSERT, msg)
        else:
            self.content.insert(tk.INSERT, "当前没有计时器历史记录！\n", "green")

    def newJob(self):
        """用于开始计时器"""
        conn = sqlite3.connect(settings.DB_PATH)
        c = conn.cursor()
        process_id = self.process_id
        new_title = self.new_title.get()
        # 判断是否有输入内容,无内容输入则不创建计时器
        if (not new_title) or (not new_title.strip()):
            return
        new_remark = self.new_remark.get()
        self.timer_active.append(process_id)  # 将当前计时器的id添加到self.timer_active列表中
        # 计时器相关信息+1
        self.timer_row += 1  # 计时器布局行号+1
        self.process_id += 1  # 计时器编号+1
        self.label_active.config(text="当前共有 %s 个计时器任务正在计时！" % len(self.timer_active))
        time_start = time.time()  # 开始时间，时间戳
        time_start_write = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time_start))  # 开始时间，格式化
        cal_time = 0  # 已计时长

        # 设计布局
        label_title = ttk.Label(self.f_content, text=new_title)
        label_title.grid(row=self.timer_row, column=1, padx=5)
        label_remark = ttk.Label(self.f_content, text=new_remark)
        label_remark.grid(row=self.timer_row, column=2, padx=5)
        label_time_start = ttk.Label(self.f_content, text=time_start_write)
        label_time_start.grid(row=self.timer_row, column=3, padx=5)
        label_cal_time = ttk.Label(self.f_content, text=cal_time)
        label_cal_time.grid(row=self.timer_row, column=4, padx=5)
        button_stop = ttk.Button(self.f_content, text="停止", command=lambda: self.stopJob(process_id))
        button_stop.grid(row=self.timer_row, column=5, padx=5)

        # 循环计时
        while process_id in self.timer_active:
            cal_time = (time.time() - time_start)  # 计算时间差
            cal_time_msg = remake_time_human(cal_time)  # 本次煲机时长
            label_cal_time.config(text=cal_time_msg)
            time.sleep(1)

        # 将”停止“按钮置为不可点击
        button_stop.config(state=tk.DISABLED, text="已结束")
        # 将计时记录记录到数据库
        sql = "insert into timers (create_time,cal_time,title,remark) values (?,?,?,?)"
        c.execute(sql, (time_start_write, cal_time, new_title, new_remark))
        conn.commit()
        c.close()
        conn.close()

    def runNewJob(self):
        """创建子线程执行实际函数"""
        t = threading.Thread(target=self.newJob)
        t.daemon = True
        t.start()

    def stopJob(self, timer_id):
        """用于停止计时器"""
        if timer_id in self.timer_active:
            # 将该计时器id从timer_active列表中删除
            self.timer_active.remove(timer_id)
            print("计时器id：%s 结束计时！" % timer_id)
            # 刷新label_active
            self.label_active.config(text="当前共有 %s 个计时器任务正在计时！" % len(self.timer_active))


class TipFrame(tk.Frame):  # 继承Frame类
    def __init__(self, master=None):
        tk.Frame.__init__(self, master.win)
        # 创建计时器页面
        self.root = ttk.Frame(master.win)  # 定义内部变量root
        self.pwin = master  # 父容器对象引用，方便后面调用父容器实例方法
        # self.root.pack()
        self.new_title = tk.StringVar()  # 新建计时器标题
        self.new_remark = tk.StringVar()  # 新建计时器备注
        self.timer_row = 2  # 用于布局显示label的行起始位置
        self.process_id = 0  # 计时器编号,方便程序控制，并非记录在数据库的id 因为有可能会存在某些时候不保存进数据库 为了避免程序id和数据库id冲突故两者隔离开
        self.timer_active = []  # 用于记录当前正在计时的计时器，配合停止button使用
        self.end_time = tk.StringVar()  # 结束时间
        self.search_key = tk.StringVar()  # 用于在计时器记录界面搜索计时器，要搜索的计时器的关键字
        self.search_mode = tk.StringVar()  # 用于在计时器记录界面搜索计时器，要搜索的计时器的模式  “content”  内容  "time"  时间
        self.search_mode.set("content")
        # 链接数据库
        self.conn = sqlite3.connect(settings.DB_PATH)
        self.c = self.conn.cursor()
        self.createPage()

    def createPage(self):
        f_top = ttk.Frame(self.root)  # 显示标题
        f_top.pack(fill=tk.BOTH)
        f_option = ttk.Frame(self.root)  # 显示操作区
        f_option.pack()
        self.f_content = ttk.Frame(self.root)  # 记录显示区
        self.f_content.pack()
        ttk.Label(f_top, text="提醒").pack(pady=10)
        ttk.Button(f_top, text="返回主页", command=self.pwin.returnIndex).pack(anchor=tk.NE)
        ttk.Label(f_option, text="提醒时间").grid(row=0, column=1)
        ttk.Label(f_option, text="事项").grid(row=0, column=2)
        ttk.Label(f_option, text="备注").grid(row=0, column=3)
        ttk.Entry(f_option, textvariable=self.end_time, width=22).grid(row=1, column=1, padx=2)
        ttk.Entry(f_option, textvariable=self.new_title, width=30).grid(row=1, column=2, padx=2)
        ttk.Entry(f_option, textvariable=self.new_remark, width=35).grid(row=1, column=3, padx=2)
        self.button_start = ttk.Button(f_option, text="创建", command=self.runNewJob)
        self.button_start.grid(row=1, column=4, padx=2)

        self.label_active = ttk.Label(self.f_content, text="当前共有 %s 个提醒任务！" % len(self.timer_active))  # 展示当前计时任务个数
        self.label_active.grid(row=0, column=0, columnspan=5, pady=5)
        ttk.Button(self.f_content, text="查看已完成历史记录", command=self.show_record).grid(row=0, column=5, pady=5)
        ttk.Label(self.f_content, text="创建时间").grid(row=1, column=1, padx=5)
        ttk.Label(self.f_content, text="提醒时间").grid(row=1, column=2, padx=5)
        ttk.Label(self.f_content, text="事项").grid(row=1, column=3, padx=5)
        ttk.Label(self.f_content, text="备注").grid(row=1, column=4, padx=5)
        ttk.Label(self.f_content, text="倒计时").grid(row=1, column=5, padx=5)

        # 自动加载上次未完成的提醒任务
        self.c.execute("select count(*) from tips where state=0")
        count = self.c.fetchone()[0]
        print("当前进行中的提醒任务：", count)
        if not count:
            return
        if count > 1:
            self.c.execute("select * from tips where state=0")
            record = self.c.fetchall()
            print(record)
            for item in record:
                t = threading.Thread(target=self.renewJob, args=(item,))
                t.daemon = True
                t.start()
        else:
            self.c.execute("select * from tips where state=0")
            self.renewJob(self.c.fetchone())

    def renewJob(self, item):
        """用于恢复之前保存的待办任务
        tip_item为单条代办事项 即单个提醒
        """
        conn = sqlite3.connect(settings.DB_PATH)
        c = conn.cursor()
        timer_row = self.timer_row
        process_id = self.process_id
        self.timer_active.append(process_id)  # 将当前计时器的id添加到self.timer_active列表中
        # 计时器相关信息+1
        self.timer_row += 1  # 计时器布局行号+1
        self.process_id += 1  # 计时器编号+1
        self.label_active.config(text="当前共有 %s 个提醒(倒计时)任务正在计时！" % len(self.timer_active))
        cal_time = 0  # 倒计时长
        # 将输入的时间字符串转换成时间戳
        try:
            time_end = item[2]
            time_end_stamp = time.mktime(time.strptime(time_end, "%Y-%m-%d %H:%M:%S"))  # 将时间字符串转换为时间戳
        except Exception:
            mBox.showerror("输入格式有误！", message="请按照如下格式输入提醒时间：'%Y-%m-%d %H:%M:%S'")
            return

        # 设计布局
        label_time_start = ttk.Label(self.f_content, text=item[1])
        label_time_start.grid(row=timer_row, column=1, padx=5)
        label_time_end = ttk.Label(self.f_content, text=time_end)
        label_time_end.grid(row=timer_row, column=2, padx=5)
        label_title = ttk.Label(self.f_content, text=item[3])
        label_title.grid(row=timer_row, column=3, padx=5)
        label_remark = ttk.Label(self.f_content, text=item[4])
        label_remark.grid(row=timer_row, column=4, padx=5)

        label_cal_time = ttk.Label(self.f_content, text=cal_time)
        label_cal_time.grid(row=timer_row, column=5, padx=5)
        button_stop = ttk.Button(self.f_content, text="删除", command=lambda: self.stopJob(process_id))
        button_stop.grid(row=timer_row, column=6, padx=5)

        # 循环计时
        while process_id in self.timer_active:
            cal_time = (time_end_stamp - time.time())  # 计算倒计时 时间差
            if cal_time < 1:
                mBox.showinfo("提醒任务", message="现在是:%s  \n请完成:%s  \n备注:%s" % (time_end, item[3], item[4]))
                self.timer_active.remove(process_id)  # 从任务列表移除
                label_cal_time.config(text='0')
                break
            cal_time_msg = remake_time_human(cal_time)  # 倒计时时长，XX天XX小时
            label_cal_time.config(text=cal_time_msg)
            time.sleep(1)

        # 将”停止“按钮置为不可点击
        # 将计时记录写出到记数据库
        sql = "update tips set state=? where id=?"
        if time.time() >= time_end_stamp:
            button_stop.config(state=tk.DISABLED, text="已完成")
            self.label_active.config(text="当前共有 %s 个提醒(倒计时)任务正在计时！" % len(self.timer_active))
            c.execute(sql, (1, item[0]))  # 0,未完成 1,已完成 3,已删除
        else:
            # 手动删除任务而非任务完成
            button_stop.config(state=tk.DISABLED, text="已删除")
            c.execute(sql, (2, item[0]))  # 0,未完成 1,已完成 3,已删除
        conn.commit()
        c.close()
        conn.close()

    def backPrePage(self):
        """从记录查询页面返回计时器操作页面"""
        self.root_new.pack_forget()
        self.root.pack()

    def show_record(self):
        """用于查看历史记录"""
        self.root_new = ttk.Frame(self.pwin.win)  # 记录查看页面Frame
        self.root_new.pack()
        self.root.pack_forget()  # 隐藏原root页面

        ttk.Label(self.root_new, text="提醒/倒计时任务查看").grid(row=0, column=0, columnspan=3, pady=5)
        ttk.Button(self.root_new, text="返回上一页", command=self.backPrePage).grid(row=0, column=2, pady=5)
        self.content = ScrolledText(self.root_new, height=35, width=95, wrap=tk.WORD)  # 创建记录展示区
        self.content.tag_config("green", foreground="green")  # 消息列表分区中创建标签
        self.content.grid(row=1, columnspan=3)
        ttk.Label(self.root_new, text="查找模式:").grid(row=2, column=0)
        ttk.Radiobutton(self.root_new, text="根据内容", value="content", variable=self.search_mode).grid(row=2, column=1)
        ttk.Radiobutton(self.root_new, text="根据时间", value="time", variable=self.search_mode).grid(row=2, column=2)

        ttk.Entry(self.root_new, textvariable=self.search_key, width=50).grid(row=3, column=0)
        ttk.Button(self.root_new, text="搜索", command=self.searchRecord).grid(row=3, column=1)
        ttk.Button(self.root_new, text="查看所有", command=self.showAll).grid(row=3, column=2, sticky=tk.EW)
        self.showAll()  # 显示所有信息

    def searchRecord(self):
        """用于搜索已完成提醒任务历史记录"""
        # 清空数据区
        self.content.delete("0.0", tk.END)
        # 搜索匹配条件的记录
        search_key = self.search_key.get()
        if self.search_mode.get() == "time":
            sql = "select id,create_time,end_time,title,remark,state from tips where create_time like ?"
            self.c.execute(sql, ("%%%s%%" % search_key,))
        else:
            sql = "select id,create_time,end_time,title,remark,state from tips where title like ? or remark like?"
            self.c.execute(sql, ("%%%s%%" % search_key, "%%%s%%" % search_key))

        record = self.c.fetchall()
        if record and len(record):
            state_dict = {0: "状态:进行中\n", 1: "状态:已完成\n", 2: "状态:已取消\n"}
            for item in record:
                msg = "id:%s, 创建时间:%s, 结束时间:%s, 事项:%s, 备注:%s" % (
                item[0], item[1], item[2], item[3], item[4])
                msg += state_dict[item[5]]
                self.content.insert(tk.INSERT, msg)
            msg = "共找到 %s 条符合条件的计时任务信息!" % len(record)
            self.content.insert(tk.INSERT, msg, "green")
        else:
            self.content.insert(tk.INSERT, "未找到符合条件的计时任务信息！", "green")

    def showAll(self):
        """用于显示所有提醒任务"""
        # 输出信息
        self.content.delete("0.0", tk.END)
        sql = "select id,create_time,end_time,title,remark,state from tips"
        self.c.execute(sql)
        record = self.c.fetchall()
        if record and len(record):
            self.content.insert(tk.INSERT, "共有 %s 个提醒任务记录！\n" % len(record), "green")
            state_dict = {0: "状态:进行中\n", 1: "状态:已完成\n", 2: "状态:已取消\n"}
            for item in record:
                msg = "id:%s, 创建时间:%s, 结束时间:%s, 事项:%s, 备注:%s" % (
                item[0], item[1], item[2], item[3], item[4])
                msg += state_dict[item[5]]
                self.content.insert(tk.INSERT, msg)
        else:
            self.content.insert(tk.INSERT, "当前没有提醒任务记录！\n", "green")

    def newJob(self):
        """用于开始计时器"""
        conn = sqlite3.connect(settings.DB_PATH)
        c = conn.cursor()
        process_id = self.process_id
        new_title = self.new_title.get()
        # 判断是否有输入内容,无内容输入则不创建计时器
        if (not new_title) or (not new_title.strip()):
            return
        new_remark = self.new_remark.get()

        # 将输入的时间字符串转换成时间戳
        try:
            time_end = self.end_time.get()
            time_end_stamp = time.mktime(time.strptime(time_end, "%Y-%m-%d %H:%M:%S"))  # 将时间字符串转换为时间戳
        except Exception:
            mBox.showerror("时间格式有误！", message="请按照如下格式输入提醒时间：'%Y-%m-%d %H:%M:%S'")
            return

        if time_end_stamp <= time.time():
            mBox.showinfo("提醒时间已过", message="%s 已过！" % time_end)
            return

        self.timer_active.append(process_id)  # 将当前计时器的id添加到self.timer_active列表中
        # 计时器相关信息+1
        self.timer_row += 1  # 计时器布局行号+1
        self.process_id += 1  # 计时器编号+1
        time_start = time.time()  # 创建时间，时间戳
        time_start_write = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time_start))  # 开始时间，格式化
        cal_time = 0  # 倒计时长

        # 设计布局
        label_time_start = ttk.Label(self.f_content, text=time_start_write)
        label_time_start.grid(row=self.timer_row, column=1, padx=5)
        label_time_end = ttk.Label(self.f_content, text=time_end)
        label_time_end.grid(row=self.timer_row, column=2, padx=5)
        label_title = ttk.Label(self.f_content, text=new_title)
        label_title.grid(row=self.timer_row, column=3, padx=5)
        label_remark = ttk.Label(self.f_content, text=new_remark)
        label_remark.grid(row=self.timer_row, column=4, padx=5)
        label_cal_time = ttk.Label(self.f_content, text=cal_time)
        label_cal_time.grid(row=self.timer_row, column=5, padx=5)
        button_stop = ttk.Button(self.f_content, text="删除", command=lambda: self.stopJob(process_id))
        button_stop.grid(row=self.timer_row, column=6, padx=5)

        # 将计时记录写出到数据库
        sql = "insert into tips (create_time,end_time,title,remark) values (?,?,?,?)"
        c.execute(sql, (time_start_write, time_end, new_title, new_remark))
        conn.commit()
        # 循环计时
        while process_id in self.timer_active:
            cal_time = (time_end_stamp - time.time())  # 计算倒计时 时间差
            if cal_time < 1:
                mBox.showinfo("提醒任务", message="现在是:%s  \n请完成:%s  \n备注:%s" % (time_end, new_title, new_remark))
                self.timer_active.remove(process_id)  # 从任务列表移除
                label_cal_time.config(text='0')
                break
            cal_time_msg = remake_time_human(cal_time)  # 倒计时时长，XX天XX小时
            label_cal_time.config(text=cal_time_msg)
            time.sleep(1)

        # 将”停止“按钮置为不可点击
        # 将计时记录写出到记数据库
        sql = "update tips set state=? where create_time=? and end_time=? and title=? and remark=?"
        if time.time() >= time_end_stamp:
            button_stop.config(state=tk.DISABLED, text="已完成")
            self.label_active.config(text="当前共有 %s 个提醒(倒计时)任务正在计时！" % len(self.timer_active))
            c.execute(sql, (1, time_start_write, time_end, new_title, new_remark))  # 0,未完成 1,已完成 3,已删除
        else:
            # 手动删除任务而非任务完成
            button_stop.config(state=tk.DISABLED, text="已删除")
            c.execute(sql, (2, time_start_write, time_end, new_title, new_remark))  # 0,未完成 1,已完成 3,已删除
        conn.commit()
        c.close()
        conn.close()

    def runNewJob(self):
        """创建子线程执行实际函数"""
        t = threading.Thread(target=self.newJob)
        t.daemon = True
        t.start()

    def stopJob(self, timer_id):
        """用于停止计时器"""
        if timer_id in self.timer_active:
            # 将该计时器id从timer_active列表中删除
            self.timer_active.remove(timer_id)
            print("提醒任务id：%s 删除任务！" % timer_id)
            # 刷新label_active
            self.label_active.config(text="当前共有 %s 个计时器任务正在计时！" % len(self.timer_active))


class NoteFrame(tk.Frame):  # 继承Frame类
    def __init__(self, master=None):
        tk.Frame.__init__(self, master.win)
        # 创建聊天记录查看页面
        self.root = ttk.Frame(master.win)  # 定义内部变量root
        self.pwin = master  # 父容器对象引用，方便后面调用父容器实例方法
        # self.root.pack()
        self.select_id = tk.IntVar()  # 选中的id  ，用于定位修改的便签
        self.add_flag = True  # 用于标记是否是新增便签还是修改便签 True 新增 False 修改
        # 链接数据库
        self.conn = sqlite3.connect(settings.DB_PATH)
        self.c = self.conn.cursor()
        self.createPage()

    def createPage(self):
        f_top = ttk.Frame(self.root)
        f_title = ttk.Frame(self.root)
        f_content = ttk.Frame(self.root)
        f_bottom = ttk.Frame(self.root)
        f_top.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        f_bottom.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        f_title.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        f_content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ttk.Label(f_top, text="便签").pack(pady=10)
        ttk.Button(f_top, text="返回主页", command=self.pwin.returnIndex).pack(anchor=tk.NE)
        self.search_key = tk.StringVar()  # 搜索关键字
        self.search_mode = tk.StringVar()  # 搜索模式 content 标题  time 时间
        self.search_mode.set("content")
        ttk.Label(f_title, text="事项").grid(row=0, column=1)
        ttk.Label(f_title, text="时间").grid(row=0, column=2)  # 格式：'%Y-%m-%d %H:%M:%S'
        ttk.Label(f_title, text="备注").grid(row=0, column=3)

        # self.label_id = ttk.Label(f_title)
        # self.label_id.grid(row=1, column=0, padx=2)
        self.new_note = tk.StringVar()  # 便签内容
        self.entry_title = ttk.Entry(f_title, textvariable=self.new_note, width=20)
        self.entry_title.grid(row=1, column=1, padx=2)
        self.new_note_date = tk.StringVar()  # 时间
        self.entry_date = ttk.Entry(f_title, textvariable=self.new_note_date, width=20)  # 输入事项框
        self.entry_date.grid(row=1, column=2, padx=2)
        self.new_note_remark = tk.StringVar()  # 备注
        self.entry_remark = ttk.Entry(f_title, textvariable=self.new_note_remark, width=40)  # 输入备注框
        self.entry_remark.grid(row=1, column=3, padx=2)
        self.buttun_create_note = ttk.Button(f_title, text="创建", command=self.addNote)  # 创建便签 按钮
        self.buttun_create_note.grid(row=1, column=4, padx=2)

        self.label_notes_info = ttk.Label(f_content)  # 所有便签总数信息
        self.label_notes_info.pack()
        self.txt_note = ScrolledText(f_content, wrap=tk.WORD, width=100, height=30)
        self.txt_note.pack(pady=5)

        ttk.Label(f_bottom, text="查找便签:").grid(row=0, column=0)
        ttk.Radiobutton(f_bottom, text="根据内容", value="content", variable=self.search_mode).grid(row=0, column=1)
        ttk.Radiobutton(f_bottom, text="根据时间", value="time", variable=self.search_mode).grid(row=0, column=2)
        ttk.Label(f_bottom, text="定位编号:").grid(row=0, column=4)
        ttk.Entry(f_bottom, textvariable=self.select_id).grid(row=0, column=5)
        self.buttun_locate = ttk.Button(f_bottom, text="定位", command=self.locateNote)
        self.buttun_locate.grid(row=0, column=6, sticky=tk.E)
        ttk.Entry(f_bottom, textvariable=self.search_key, width=50).grid(row=2, column=0, columnspan=4)
        ttk.Button(f_bottom, text="搜索", command=self.searchNotes).grid(row=2, column=4)
        ttk.Button(f_bottom, text="查看所有便签", command=self.showNotes).grid(row=2, column=5, sticky=tk.EW)
        self.buttun_cancel = ttk.Button(f_bottom, text="取消修改", command=self.cancelUpdate)
        self.buttun_cancel.grid(row=2, column=6, sticky=tk.E)
        self.showNotes()

    def addNote(self):
        """新增便签记录"""
        new_note_title = self.new_note.get()
        new_note_date = self.new_note_date.get()
        new_note_remark = self.new_note_remark.get()
        select_id = self.select_id.get()
        if new_note_title:
            # if new_note_date.strip() == '':
            #     new_note_date = time.strftime('%Y-%m-%d', time.localtime())
            if new_note_remark.strip() == '':
                new_note_remark = ''
            # 匹配时间 三种时间格式20210201,2021.2.1,2021-2-1
            new_note_date = changeStrToDate(new_note_date)
            if not new_note_date:
                new_note_date = time.strftime('%Y-%m-%d', time.localtime())
            create_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  # 该便签创建时间
            if self.add_flag is True:
                sql = "insert into notes (create_time,modify_time,note_date,title,remark) values (?,?,?,?,?)"
                self.c.execute(sql, (create_time, create_time, new_note_date, new_note_title, new_note_remark))
                self.conn.commit()
                mBox.showinfo("添加完成", "添加新便签完成！")
            else:
                sql = "update notes set modify_time=?,note_date=?,title=?,remark=? where id=?"
                self.c.execute(sql, (create_time, new_note_date, new_note_title, new_note_remark, select_id))
                self.conn.commit()
                mBox.showinfo("修改完成", "修改编号为:%s 便签完成！" % select_id)
                self.cancelUpdate()
            self.showNotes()

    def showNotes(self):
        """展示所有便签"""
        self.c.execute("select count(*) from notes")
        notes_count = self.c.fetchone()[0]  # 便签数量
        if not notes_count:
            notes_count = 0
        self.label_notes_info.config(text="当前共有 %s 条便签！" % notes_count)
        self.txt_note.delete("0.0", END)
        if notes_count:
            sql = "select id,create_time,modify_time,note_date,title,remark from notes"
            self.c.execute(sql)
            record = self.c.fetchall()  # [(xxx,xx),]
            # print(record)
            for item in record:
                msg = "编号:%s , 创建时间:%s, 最近修改:%s, 记录日期:%s, 记录事项:%s, 备注:%s\n" % item
                self.txt_note.insert(tk.INSERT, msg)

    def searchNotes(self):
        """用于搜索便签"""
        # 获取搜索关键字
        search_key = self.search_key.get()  # 搜索词
        search_mode = self.search_mode.get()  # 搜索模式  “content” 事项和备注 “time” 时间
        self.txt_note.delete("0.0", END)
        if search_mode == "content":
            sql = "select id,create_time,modify_time,note_date,title,remark from notes where title like ? or remark like ?"
            self.c.execute(sql, ("%%%s%%" % search_key, "%%%s%%" % search_key))
        else:  # 按时间搜索
            sql = "select id,create_time,modify_time,note_date,title,remark from notes where create_time like ? or modify_time like ? or note_date like ?"
            self.c.execute(sql, ("%%%s%%" % search_key, "%%%s%%" % search_key, "%%%s%%" % search_key))
        record = self.c.fetchall()
        if not record:  # 没有搜索到结果
            self.label_notes_info.config(text="未搜索到符合条件的 便签！")
        else:
            self.label_notes_info.config(text="共搜索到符合条件的 %s 条便签！" % len(record))  # 显示找到多少条
            for item in record:
                msg = "编号:%s , 创建时间:%s, 最近修改:%s, 记录日期:%s, 记录事项:%s, 备注:%s\n" % item
                self.txt_note.insert(tk.INSERT, msg)

    def locateNote(self):
        """用于通过id定位便签并将其填充到对应控件内"""
        # 定位要修改的便签
        select_id = self.select_id.get()
        # print("select_id:", select_id)
        sql = "select id,create_time,modify_time,note_date,title,remark from notes where id=?"
        self.c.execute(sql, (select_id,))
        note_item = self.c.fetchone()
        # print("note_item:", note_item)
        if note_item:
            # self.label_id.config(text=select_id)
            self.new_note.set(note_item[4])
            self.new_note_date.set(note_item[3])
            self.new_note_remark.set(note_item[5])
            self.buttun_create_note.config(text="修改")
            self.add_flag = False  # 将便签操作标志位置为False 为修改便签
            self.label_notes_info.config(text="正在修改id为%s的便签！" % select_id)
        else:
            self.new_note.set("")
            self.new_note_date.set("")
            self.new_note_remark.set("")
            self.txt_note.delete("0.0", END)
            self.label_notes_info.config(text="数据库中未找到id为:%s的便签！" % select_id)

    def cancelUpdate(self):
        """用于取消修改便签内容操作"""
        # 还原标签状态为新增便签
        # self.label_id.config(text=self.note_id)
        self.new_note.set("")
        self.new_note_date.set("")
        self.new_note_remark.set("")
        self.buttun_create_note.config(text="创建")
        self.label_notes_info.config(text="")
        self.add_flag = True  # 将便签操作标志位置为False 为修改便签

