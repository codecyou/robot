from bin.view import *   # 菜单栏对应的各个子页面


class MainPage(object):
    def __init__(self, master=None):
        self.win = master  # 定义内部变量root
        self.win.protocol('WM_DELETE_WINDOW', self.closeWindow)  # 绑定窗口关闭事件，防止计时器正在工作导致数据丢失

        # 设置窗口大小
        winWidth = 790
        winHeight = 620
        # 获取屏幕分辨率
        screenWidth = self.win.winfo_screenwidth()
        screenHeight = self.win.winfo_screenheight()

        x = int((screenWidth - winWidth) / 2)
        y = int((screenHeight - winHeight) / 2)

        # 设置窗口初始位置在屏幕居中
        self.win.geometry("%sx%s+%s+%s" % (winWidth, winHeight, x, y))
        self.page = None  # 用于标记功能界面
        self.createPage()

    def createPage(self):
        # 创建不同Frame
        self.poetryPage = PoetryFrame(self)  # 修改诗词页面
        self.recordPage = RecordFrame(self)  # 查看聊天记录页面
        self.timerPage = TimerFrame(self)  # 计时页面
        self.tipPage = TipFrame(self)  # 提醒页面
        self.notePage = NoteFrame(self)  # 备忘录/记事本
        self.indexPage = IndexFrame(self)  # 主页

        self.pages = [self.indexPage, self.poetryPage, self.recordPage, self.timerPage, self.tipPage, self.notePage]
        self.indexPage.root.pack()

    def display(self, page):
        """用于展示当前页面"""
        print("现有Frame：", self.win.pack_slaves())
        for item in self.pages:
            if item == page:
                page.root.pack()
                continue
            item.root.pack_forget()

    def returnIndex(self):
        """返回主页"""
        print("跳转到主页现有Frame：", self.win.pack_slaves())
        frame_list = self.win.pack_slaves()
        for item in frame_list:
            item.pack_forget()
        self.indexPage.root.pack()

    def closeWindow(self):
        """用来处理关闭窗口按钮在退出系统前的询问"""
        active_num = len(self.timerPage.timer_active)  # 当前正在进行的计时器数
        # print(active_num)
        if active_num:
            ans = mBox.askyesno(title="Warning", message="当前还有 %s 个计时器正在工作，数据尚未保存，是否退出？" % active_num)
            if not ans:
                # 选择否/no 不退出
                return
        # 退出程序
        self.win.destroy()

    def indexData(self):
        self.display(self.indexPage)

    def poetryData(self):
        self.display(self.poetryPage)

    def recordData(self):
        self.display(self.recordPage)

    def timerData(self):
        self.display(self.timerPage)

    def tipData(self):
        self.display(self.tipPage)

    def noteData(self):
        self.display(self.notePage)
