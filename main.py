from qfluentwidgets import NavigationItemPosition, FluentWindow, SubtitleLabel, setFont
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from PyQt5 import QtCore
import sys
from sync import FileSyncTool  # 引入 FileSyncTool 类

from qfluentwidgets import (
    NavigationItemPosition,
    MessageBox,
    setTheme,
    Theme,
    MSFluentWindow,
    NavigationAvatarWidget,
    qrouter,
    SubtitleLabel,
    setFont,
)
from qfluentwidgets import FluentIcon as FIF


class Window(MSFluentWindow):

    def __init__(self):
        super().__init__()

        # create sub interface
        self.homeInterface = FileSyncTool()
        self.homeInterface.setObjectName("homeInterface")  # 设置对象名

        self.initNavigation()
        self.initWindow()

    def initNavigation(self):
        self.addSubInterface(self.homeInterface, FIF.HOME, "主页", FIF.HOME_FILL)
        # self.addSubInterface(self.appInterface, FIF.APPLICATION, "应用")
        # self.addSubInterface(self.videoInterface, FIF.VIDEO, "视频")

        # self.addSubInterface(
        #     self.libraryInterface,
        #     FIF.BOOK_SHELF,
        #     "库",
        #     FIF.LIBRARY_FILL,
        #     NavigationItemPosition.BOTTOM,
        # )

        # 添加自定义导航组件
        self.navigationInterface.addItem(
            routeKey="Help",
            icon=FIF.HELP,
            text="帮助",
            onClick=self.showMessageBox,
            selectable=False,
            position=NavigationItemPosition.BOTTOM,
        )

        self.navigationInterface.setCurrentItem(self.homeInterface.objectName())

    def initWindow(self):
        self.resize(900, 700)
        # self.setWindowIcon(QIcon(":/qfluentwidgets/images/logo.png"))
        self.setWindowTitle("EasySyncTools - 文件同步工具")

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Window()
    w.show()
    app.exec()
