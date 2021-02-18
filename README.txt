robot 程序说明

目录结构
│  README.txt  # 说明文件
│  
├─bin
│      MainPage.py  # 程序视图
│      robot_GUI.py  # 程序入口
│      view.py  # 程序视图
│      
├─conf
│      settings.py  # 程序配置文件
│      
├─core
│      create_db.py  # 创建数据库
│      Mytools.py  # 通用工具类
│          
├─db
│      robot.db # 数据库
│      唐诗.json  
│      语料.txt
│          
└─src  # 程序图片文件夹，用于程序界面图片展示
     └─img
            1574152962320463_avatar.png
            20210115_17460633.png
            2198662272522315_avatar.png
            597724674398456_avatar.png
            60598898585_avatar.png
            92521689353_avatar.png
			
			
使用说明:
	运行方式 python robot_GUI.py

程序模块说明
view.py 类说明
IndexFrame  主页
PoetryFrame  诗词
RecordFrame  查看聊天记录
TimerFrame  计时器
TipFrame  提醒/倒计时
NoteFrame  便签/备忘录
