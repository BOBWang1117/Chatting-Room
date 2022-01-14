from PIL import ImageFont
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtCore import Qt, QTimer, QRect
import sys


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        global fm
        Dialog.setObjectName("Dialog")
        Dialog.resize(300, 100)
        Dialog.setStyleSheet("background: transparent;")
        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setGeometry(QtCore.QRect(0, 0, 200, 51))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("等线")
        font.setPointSize(11)
        #font.setBold(False)
        font.setWeight(40)
        self.pushButton.setFont(font)
        self.pushButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.pushButton.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.pushButton.setAutoFillBackground(False)
        #在这里设置气泡的stylesheet
        self.pushButton.setObjectName("pushButton")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.pushButton.setText(_translate("Dialog", "提示框"))

def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func

    return decorate


class TipUi(QDialog):
    def __init__(self, text: str, height: int, length: int, time: int, parent=None):
        # 设置ui
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        # 设置定时器，用于动态调节窗口透明度
        self.timer = QTimer()
        # 设置气泡在屏幕上的位置，水平居中，垂直屏幕80%位置
        desktop = QApplication.desktop()
        self.setGeometry(QRect(int(desktop.width() / 2 - 150), int(desktop.height() * 0.5), length, height))
        self.ui.pushButton.setGeometry(0, 0, length, height)
        self.ui.pushButton.setStyleSheet("background-color:rgb(111, 156, 207);\n"  # 0, 78, 161
                                      "border-style:none;\n"
                                      "padding:8px;\n"
                                      "border-radius:"+str(height//2)+"px;")
        # 显示的文本
        self.ui.pushButton.setText(text)
        # 设置隐藏标题栏、无边框、隐藏任务栏图标、始终置顶
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        # 设置窗口透明背景
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        # 窗口关闭自动退出，一定要加，否则无法退出
        self.setAttribute(Qt.WA_QuitOnClose, True)
        # 用来计数的参数
        self.windosAlpha = 0
        # 设置定时器25ms，1600ms记64个数
        self.timer.timeout.connect(self.hide_windows)
        self.timer.start(25)
        self.time = time

    # 槽函数
    def hide_windows(self):
        self.timer.start(25)
        # 前750ms设置透明度不变，后850ms透明度线性变化
        # print(self.time)
        if self.windosAlpha <= (30 + self.time):
            self.setWindowOpacity(1.0)
        else:
            self.setWindowOpacity(1.882 - 0.0294 * (self.windosAlpha - self.time))
        self.windosAlpha += 1
        # 差不多3秒自动退出
        if self.windosAlpha >= (63 + self.time):
            self.close()

        # 静态方法创建气泡提示
    @staticmethod

    @static_vars(tip=None)
    def show_tip(text):
        global fm
        label = QtWidgets.QLabel()
        font = QtGui.QFont()
        font.setFamily("等线")
        font.setPointSize(11)
        label.setFont(font)
        # 计算字符串长度
        fontfile = 'dengxian.ttf'
        font_cal = ImageFont.truetype(fontfile, 11)
        width, height = font_cal.getsize(text)
        segment = text.split("\n")
        width = 0
        for i in segment:
            l, height = font_cal.getsize(i)
            if l > width:
                width = l
        width += 220
        height = (len(segment)-1) * (height + 15) + 45
        len_text = len(text)
        TipUi.show_tip.tip = TipUi(text, height, width, len_text - 20)
        TipUi.show_tip.tip.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    strlen = "1793"
    end = "ABCD"
    TipUi.show_tip("Picture doesn't exist!")
    # Please choose who to chat with!
    # Please login first!
    # "ERROR\nMessage too long!'
    #                                 "\nThe maximum message length is 1792 letters. "
    #                                 "\nMessage After " + end +
    #                                 " is too long to be sent. "
    sys.exit(app.exec_())

