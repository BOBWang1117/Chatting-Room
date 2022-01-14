# -*- coding:utf-8 -*-
import os
import sys
import socket
import re
import json
import struct
from Admin import AdminWindow
from settings import Ui_Dialog
from PyQt5 import QtWidgets, QtGui, QtCore
from QDialog import TipUi
from ChattingMainWindow import DialogueWindow

try:
    import PyQt5
except ModuleNotFoundError:
    os.system("pip install PyQt5")
    from PyQt5.Qt import *
else:
    from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QLineEdit, QFrame, QMessageBox, QComboBox
    from PyQt5.QtGui import QIcon, QFont
    from PyQt5.QtCore import Qt

IP = "127.0.0.1"
PORT = 50007
buffSize = 1024


class Settings(QtWidgets.QWidget, Ui_Dialog):

    def __init__(self):
        super(Settings, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("Settings")


class MyWindow(QWidget):

    def __init__(self, username, password):
        super().__init__()
        self.icon = QIcon("./IMG/WorkTime_logo.png")
        self.setWindowTitle("  Login in")
        self.setFixedSize(1000, 800)
        self.settings_win = Settings()
        self.set_ui()
        self.username_edit.setText(username)
        self.password_edit.setText(password)

    def change_icon(self):
        """用来修改图像的图标"""
        self.setWindowIcon(self.icon)

    def set_ui(self):
        """设置界面"""
        self.set_background_image()  # 设置背景的图片
        self.change_icon()
        self.add_label()
        self.add_line_edit()
        self.add_button()

    def add_label(self):
        """添加相应的标签"""
        # 设置字体
        label_font = QFont()
        label_font.setFamily('Consolas')
        label_font.setPixelSize(30)

        # 创建文本标签
        self.username_label = QLabel(self)
        self.password_label = QLabel(self)

        # 设置标签中的文本
        self.username_label.setText("Username")
        self.password_label.setText("Password")
        self.username_label.setFont(QFont("Consolas", 23, QFont.Bold))
        self.password_label.setFont(QFont("Consolas", 23, QFont.Bold))

        # 设置标签的大小
        self.username_label.setFixedSize(240, 40)
        self.password_label.setFixedSize(240, 40)

        # 设置标签的位置
        self.username_label.move(260, 530)
        self.password_label.move(260, 600)

        # self.username_label.setFont(label_font)
        # self.password_label.setFont(label_font)

    def add_line_edit(self):
        """添加输入框"""
        line_edit_font = QFont()
        line_edit_font.setFamily('Consolas')
        line_edit_font.setPixelSize(30)

        # 创建
        self.username_edit = QLineEdit(self)
        self.password_edit = QLineEdit(self)

        # 设置密码格式
        self.password_edit.setEchoMode(QLineEdit.Password)

        # 设置字体
        self.username_edit.setFont(line_edit_font)
        self.password_edit.setFont(line_edit_font)

        # 设置占位符
        self.username_edit.setPlaceholderText("username")
        self.password_edit.setPlaceholderText("password")

        self.username_edit.setText("admin")
        self.password_edit.setText("admin123")

        # 设置大小
        self.username_edit.setFixedSize(270, 40)
        self.password_edit.setFixedSize(270, 40)

        # 设置位置
        self.username_edit.move(450, 530)
        self.password_edit.move(450, 600)

    def add_button(self):
        """添加按钮"""
        button_font = QFont()
        button_font.setFamily('Consolas')
        button_font.setPixelSize(30)

        # 创建按钮对象
        self.login_button = QPushButton("Login", self)

        # 修改大小且不可变
        self.login_button.setFixedSize(160, 50)

        # 设置字体
        self.login_button.setFont(button_font)

        # 设置位置
        self.login_button.move(420, 700)

        # 设置文本提示内容
        self.login_button.setText("Login in")
        self.login_button.setToolTip('If you are the admin, please login in with the specific account')

        # 实现功能，按钮点击之后执行的动作
        self.login_button.clicked.connect(self.login)
        self.login_button.setShortcut("Return")  # 设置快捷键
        # 设置设置键
        self.setting_but = QPushButton("Login", self)
        self.setting_but.setFixedSize(40, 40)
        button_font.setPixelSize(18)
        self.setting_but.setFont(button_font)
        self.setting_but.move(10, 10)
        self.setting_but.setText("")
        self.setting_but.clicked.connect(self.settings)
        icon = QtGui.QIcon()  # 新增
        icon.addPixmap(QtGui.QPixmap("buttonPic/settings.jpg"),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setting_but.setIcon(icon)
        self.setting_but.setIconSize(QtCore.QSize(40, 40))

    def set_background_image(self):
        """添加背景图片"""
        self.frame = QFrame(self)  # 这里采用 QFrame, 如果直接对self进行背景设置，似乎没有那么简单容易控制
        self.frame.resize(1000, 800)
        self.frame.move(0, 0)
        self.frame.setStyleSheet(
            'background-image: url("./IMG/Worktime.png"); background-repeat: no-repeat; text-align:center;')

    def settings(self):
        self.settings_win.show()
        self.settings_win.pushButton.clicked.connect(self.confirm)

    def confirm(self):
        global IP
        global PORT
        ip = self.settings_win.ip.text()
        check = ip.split(".")
        if not re.match(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}"
                        r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$", ip, 0):
            TipUi.show_tip('Wrong format for ip address! ')
            return
        port = self.settings_win.port.text()
        if int(port) < 1024 or int(port) > 65535:
            TipUi.show_tip('Wrong format for port! ')
            return
        IP = ip
        PORT = int(port)
        self.settings_win.close()

    def login(self):

        """登录功能实现"""
        print("Login: ", IP, PORT)
        username = self.username_edit.text()
        password = self.password_edit.text()
        s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = re.compile('^[a-zA-Z0-9_]+$')
        password_length = re.compile('^[a-zA-Z0-9_]{6,18}$')
        success = 1
        try:
            s1.connect((IP, PORT + 3))
        except socket.error:
            TipUi.show_tip('Socket error\nFail to conncet!',)
            success = -1

        if success == 1:
            if not username:
                TipUi.show_tip('Name type error\nUsername Empty!')
                s1.close()
                success = -1
            elif not password:
                TipUi.show_tip('Password type error\nPassword Empty!')
                s1.close()
                success = -1
            elif not result.match(username):
                TipUi.show_tip('Username: illegal characters\nAccept English Letters, Numbers and Underline')
                s1.close()
                success = -1
            elif not result.match(password):
                TipUi.show_tip('Password: illegal characters\nAccept English Letters, Numbers and Underline')
                s1.close()
                success = -1
            elif not password_length.match(password):
                TipUi.show_tip('Password: illegal length\nAccept Length: 6-18')
                s1.close()
                success = -1

        if success == 1:
            print('username: ' + username)
            print('password :' + password)
            pid = 1  # Protocol 1 is used for send username and password
            head = {
                'protocol': pid,
                'username': username,
                'password': password,
            }
            head_info = json.dumps(head)  # 将字典转换成字符串
            head_info_len = struct.pack('i', len(head_info))  # 将字符串的长度打包
            s1.send(head_info_len)  # 发送head_info的长度  # server: send3
            s1.send(head_info.encode('utf-8'))  # server: send4

            result = s1.recv(buffSize)
            success = int(result.decode())
            if success == -1:
                TipUi.show_tip('Password and Username is error')

        if success == 1:
            if username == 'admin':  # 如果是管理员，进入管理界面
                self.admin = AdminWindow(username, IP, PORT)
                self.admin.show()
                self.close()

            else:
                self.stuff = DialogueWindow(username, IP, PORT)
                self.stuff.show()
                self.close()

        s1.close()


def main(username: str = "", password: str = ""):
    app = QApplication(sys.argv)
    with open('Qss.qss', 'r') as f:
        app.setStyleSheet(f.read())
    my = MyWindow(username, password)
    my.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
