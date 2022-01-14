import json
import re
import shutil
import socket
import struct
import os
import os.path
import time
import cv2

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QColor, QPixmap
from PyQt5.QtWidgets import QMessageBox
from pyqt5_plugins.examplebuttonplugin import QtGui

from Information import ShowInformation
from QDialog import TipUi
from PicLabel import PicLabel
from dialogue import Ui_WorkTimeChat
from handleFileWin import Show_UiFiles
from PIL import Image, ImageFont

_translate = QtCore.QCoreApplication.translate

BUFFER_SIZE = 1024

# picButton 点击次数
i = 0
# font_button 点击次数
font_but = 0

# 消息记录
CHAT_RECORD_DICT = {}

LAST_CLICKED = ""
FLAG = 0
EMOJI_LIST = ["!.jpg", "up.jpg", "question.jpg", "cry.jpg",
              "lovel.jpg", "leaf.jpg", "good.jpg", "lover.jpg"]
HEADSHOT_DICT = {}
N = 0  # 气泡消息显示至n行


def resize_pic(pic_name, dir):
    # 检查图片是否超大，是则缩小
    img_size = cv2.imread(dir + pic_name)
    sp = img_size.shape
    height = sp[0]
    width = sp[1]
    flag = 0
    if height > 250:  # 高
        width = width * 250 // height
        height = 250
        flag = 1
    if width > 420:  # 宽
        height = height * 420 // width
        width = 420
        flag = 1
    if flag:
        img = Image.open(dir + pic_name)  # pic_name是
        pic = img.resize((width, height))  # 重置大小 （长，宽）
        pic_name = "resize_" + pic_name
        pic.save(dir + pic_name)
    return dir + pic_name


def renew_msg_list(stuff, sender, rceviver, message, num):
    # num = 0 is message(string), num = 1 is message(emoji)
    global CHAT_RECORD_DICT

    if stuff in CHAT_RECORD_DICT:
        CHAT_RECORD_DICT[stuff].append([sender, rceviver, num, message])
    else:
        CHAT_RECORD_DICT[stuff] = [[sender, rceviver, num, message]]


def set_emoji(idx: int):
    global EMOJI_LIST
    pic_name = "emojiPic/" + EMOJI_LIST[idx]
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap(pic_name), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    return icon


class DialogueWindow(QtWidgets.QWidget, Ui_WorkTimeChat):
    def __init__(self, name, IP, PORT):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Work Time Chat" + "(Username:" + name + ")")
        self.icon = QIcon("./IMG/WorkTime_logo.png")
        self.setWindowIcon(self.icon)
        self.showClgInfo = None
        self.fileWin = Show_UiFiles()
        self.me = name
        self.IP = IP
        self.PORT = PORT
        self.font = ["等线", 11]
        self.widget.setVisible(False)
        self.font_widget.setVisible(False)
        self.button_init()
        self.palette1 = QtGui.QPalette()
        self.palette1.setColor(self.backgroundRole(), QColor(224, 238, 255))
        self.font_box.activated.connect(self.font_box_changed)
        self.font_size.activated.connect(self.font_size_changed)

        self.gridLayout = QtWidgets.QGridLayout(self.widget_showText)
        self.groupBox = QtWidgets.QGroupBox(self.widget_showText)
        self.groupBox.setLayout(self.gridLayout)
        self.scroll = QtWidgets.QScrollArea(self.widget_showText)
        self.scroll.setWidget(self.groupBox)
        self.scroll.setWidgetResizable(True)
        self.scrollBar = self.scroll.verticalScrollBar()
        self.layout = QtWidgets.QVBoxLayout(self.widget_showText)
        self.layout.addWidget(self.scroll)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.groupBox.setStyleSheet("background-color:rgb(224, 238, 255);")
        self.groupBox.setMaximumSize(QtCore.QSize(680, 999999))
        self.scroll.setMaximumSize(QtCore.QSize(680, 999999))
        self.gridLayout.addWidget(self.set_label_bubble(
            "Welcome!", 1), 0, 1, 1, 1, QtCore.Qt.AlignCenter)
        self.gridLayout.setColumnMinimumWidth(0, 40)  # 第0列 最小 40
        self.gridLayout.setColumnMinimumWidth(1, 555)  # 第1列 最小 600
        self.gridLayout.setColumnMinimumWidth(2, 40)
        '''
        # self.gridLayout.setRowMinimumHeight(i, 20)    # 第0行 最小 20
        '''
        self.client_thread = ClientThread(name, IP, PORT)  # 登录后的聊天主页面
        self.client_thread.signal_add_msg.connect(self.add_msg)
        self.client_thread.signal_add_pic.connect(self.add_pic)
        self.client_thread.signal_clear_online_list.connect(self.clear_online_list)
        self.client_thread.signal_add_online_item.connect(self.add_online_item)
        self.client_thread.start()

    @QtCore.pyqtSlot(str, str)
    def add_online_item(self, name: str, head: str):
        self.onlineList.blockSignals(True)
        item = QtWidgets.QListWidgetItem(QtGui.QIcon(head), name)
        self.onlineList.addItem(item)
        self.onlineList.blockSignals(False)

    @QtCore.pyqtSlot()
    def clear_online_list(self):
        self.onlineList.blockSignals(True)
        self.onlineList.clear()
        self.onlineList.blockSignals(False)

    @QtCore.pyqtSlot(str, str)
    def add_msg(self, sender: str, msg: str):
        print("New Message:", sender, msg)
        pass
        self.show_msg(sender, msg)

    @QtCore.pyqtSlot(str, str)
    def add_pic(self, sender: str, pic_name: str):
        print("New Emoji:", sender, pic_name)
        pass
        self.show_emoji(sender, pic_name)

    def font_box_changed(self):
        self.font[0] = self.font_box.currentText()
        self.inputText.setStyleSheet("font: " + str(self.font[1]) + "pt \""
                                     + self.font[0] + "\";")

    def font_size_changed(self):

        self.font[1] = int(self.font_size.currentText())
        self.inputText.setStyleSheet("font: " + str(self.font[1]) + "pt \""
                                     + self.font[0] + "\";")

    def font_change(self):
        global font_but
        if font_but % 2 == 0:
            self.font_widget.setVisible(True)
            fonts = ["等线", "Bodoni MT", "Consolas", "Times New Roman"]
            self.font_box.clear()
            self.font_box.addItems(fonts)
            self.font_box.setCurrentIndex(fonts.index(self.font[0]))
            fonts_size = ['5', '7', '9', '11', '13', '15', '17', '19', '21', '23',
                          '25', '27', '29', '31']
            self.font_size.clear()
            self.font_size.addItems(fonts_size)
            self.font_size.setCurrentIndex(fonts_size.index(str(self.font[1])))
        else:
            self.font_widget.setVisible(False)
        font_but += 1
        return

    def button_init(self):
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("buttonPic/search_960_720.png"),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.searchButton.setIcon(icon)
        self.searchButton.setIconSize(QtCore.QSize(35, 35))
        self.searchButton.setAutoRepeatDelay(200)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("buttonPic/picButton.png"),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.picButton.setIcon(icon)
        self.picButton.setIconSize(QtCore.QSize(37, 37))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("buttonPic/fileButton.png"),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.fileButton.setIcon(icon)
        self.fileButton.setIconSize(QtCore.QSize(35, 35))
        return

    def set_head_shot_bubble(self, address):
        address = address.split(".")
        address = address[0] + "_smaller." + address[1]
        self.label = QtWidgets.QLabel()
        self.label.setPixmap(QPixmap(address))
        # label.setScaledContents(True)  # 自适应QLabel大小
        self.label.setStyleSheet("background-color: transparent")
        return self.label

    def set_label_bubble(self, content, self_or_not):
        self.label = QtWidgets.QLabel()
        font = QtGui.QFont()
        font.setFamily(self.font[0])
        font.setPointSize(self.font[1])
        self.label.setFont(font)
        # 计算字符串长度
        if self.font[0] == "等线":
            font_cal = ImageFont.truetype("dengxian.ttf", self.font[1])
        else:
            font_cal = ImageFont.truetype(self.font[0] + '.ttf', self.font[1])
        width, height = font_cal.getsize(content)
        segment = content.split(" ")
        content_show = ""
        line_width = 0
        if width > 400:
            for j in range(len(segment)):
                width, height = font_cal.getsize(segment[0] + " ")
                if line_width + width < 401:
                    line_width += width
                    content_show = content_show + segment[0] + " "
                else:
                    line_width = width
                    content_show = content_show + "\n" + segment[0] + " "
                del segment[0]
            self.label.setText(content_show)
        else:
            self.label.setText(content)
        if self_or_not:
            self.label.setStyleSheet("background-color:rgb(111, 156, 207);\n"
                                     "color:rgb(255, 255, 255);\nborder-style:none;\n"
                                     "padding:8px;\nborder-radius: 12px;")
        else:
            self.label.setStyleSheet("background-color:rgb(250, 250, 250);\n"
                                     "border-style:none;\npadding:8px;\nborder-radius: 12px;")
        return self.label

    def set_pic_bubble(self, address, height, width):
        self.label = PicLabel()
        self.label.resize(width, height)
        self.label.setPixmap(QPixmap(address))
        self.label.setScaledContents(True)
        self.label.setStyleSheet("background-color: transparent")
        return self.label

    def emoji_init(self):  # 初始化表情包界面
        global i
        btns = [
            self.pushButton_3,
            self.pushButton_4,
            self.pushButton_5,
            self.pushButton_6,
            self.pushButton_7,
            self.pushButton_8,
            self.pushButton_9,
            self.pushButton_10,
        ]
        if i % 2 == 0:
            self.widget.setVisible(True)
            for j in range(8):
                icon = set_emoji(j)
                btns[j].setIcon(icon)
                btns[j].setIconSize(QtCore.QSize(50, 50))
        else:
            self.widget.setVisible(False)
        i += 1
        return

    def push_but3(self):
        pic_name = "./emojiPic/" + EMOJI_LIST[0]
        self.send_emoji(pic_name)

    def push_but4(self):
        pic_name = "./emojiPic/" + EMOJI_LIST[1]
        self.send_emoji(pic_name)

    def push_but5(self):
        pic_name = "./emojiPic/" + EMOJI_LIST[2]
        self.send_emoji(pic_name)

    def push_but6(self):
        pic_name = "./emojiPic/" + EMOJI_LIST[3]
        self.send_emoji(pic_name)

    def push_but7(self):
        pic_name = "./emojiPic/" + EMOJI_LIST[4]
        self.send_emoji(pic_name)

    def push_but8(self):
        pic_name = "./emojiPic/" + EMOJI_LIST[5]
        self.send_emoji(pic_name)

    def push_but9(self):
        pic_name = "./emojiPic/" + EMOJI_LIST[6]
        self.send_emoji(pic_name)

    def push_but10(self):
        pic_name = "./emojiPic/" + EMOJI_LIST[7]
        self.send_emoji(pic_name)

    def send_emoji(self, pic_name):
        global i
        global LSAT_CLICKED
        self.show_emoji(self.me, pic_name)
        pid = 2  # Protocol 2 is used for client to send message(emoji) to server in PORT 50007
        head = {
            'protocol': pid,
            'message': pic_name,
            'sender': self.me,
            'receiver': LAST_CLICKED,
        }
        head_info = json.dumps(head)  # 将字典转换成字符串
        head_info_len = struct.pack('i', len(head_info))  # 将字符串的长度打包
        CHAT_SOCK.send(head_info_len)  # 发送head_info的长度  # server: send3
        CHAT_SOCK.send(head_info.encode('utf-8'))  # server: send4
        renew_msg_list(LAST_CLICKED, self.me, LAST_CLICKED, pic_name, 1)
        self.widget.setVisible(False)
        i += 1
        return

    def scroll_bar_set(self):
        print("SCROLL", self.scrollBar.value(), self.scrollBar.maximum())
        if self.scrollBar.value() > self.scrollBar.maximum() - 40:
            self.scrollBar.setValue(self.scrollBar.maximum()-1)
            print("SCROLL SET", self.scrollBar.value(), self.scrollBar.maximum())
        return

    def show_emoji(self, sender, pic_name):
        global HEADSHOT_DICT
        global N
        img_size = cv2.imread(pic_name)
        sp = img_size.shape
        height = sp[0]
        width = sp[1]
        if sender == self.me:
            self.gridLayout.addWidget(self.set_head_shot_bubble(HEADSHOT_DICT[sender]),
                                      N, 2, 1, 1, QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)
            self.gridLayout.addWidget(self.set_pic_bubble(pic_name, height, width),
                                      N, 1, 1, 1, QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)
        else:
            self.gridLayout.addWidget(self.set_head_shot_bubble(HEADSHOT_DICT[sender]),
                                      N, 0, 1, 1, QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
            self.gridLayout.addWidget(self.set_pic_bubble(pic_name, height, width),
                                      N, 1, 1, 1, QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.gridLayout.setRowMinimumHeight(N, 50)
        N += 1
        self.scroll_bar_set()
        return

    def sendPicture(self):
        global LAST_CLICKED
        content = self.inputText.toPlainText()
        if not LAST_CLICKED:
            TipUi.show_tip("Please choose a person you want to chat with!")
            LAST_CLICKED = self.me
            self.gridLayout.itemAt(0).widget().deleteLater()
            self.name.setText(LAST_CLICKED)
            return

        # content[0]是用户原本的输入，content[1]及以后都是文件路径
        if "file:///" in content:
            content = content.split("file:///")
            self.inputText.setPlainText(content[0])
            if content[1] == "":
                TipUi.show_tip("\"file:///\" is an illeagal string!")
                return
            file_list = ""
            for j in range(1, len(content)):
                file_list += "[File] " + content[j].split("/")[-1]
            reply = QMessageBox.information(self, 'Send to: ' + LAST_CLICKED, file_list,
                                            QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
            if reply == QMessageBox.Cancel:
                return
            show_msg = ''
            for j in range(1, len(content)):
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sendPicSock:
                    sendPicSock.connect((self.IP, self.PORT + 2))
                    content[j] = content[j].split("\n")[0]
                    picSize = os.path.getsize(content[j])  # 得到文件的大小,字节
                    pic_name = content[j].split('/')[-1]
                    pid = 1  # Protocol 1 is used for admin client to send picture in PORT 50009
                    head = {
                        'protocol': pid,
                        'sender': self.me,
                        'receiver': LAST_CLICKED,
                        'picName': pic_name,
                        'picSize': picSize,
                    }
                    head_info = json.dumps(head)  # 将字典转换成字符串
                    head_info_len = struct.pack('i', len(head_info))  # 将字符串的长度打包
                    sendPicSock.send(head_info_len)  # 发送head_info的长度  # server: send3
                    sendPicSock.send(head_info.encode('utf-8'))  # server: send4

                    with open(content[j], 'rb') as p:
                        picture = p.read()
                        sendPicSock.sendall(picture)

                    shutil.copyfile(content[j], './IMG/' + pic_name)
                    if pic_name.endswith(('.bmp', '.dib', '.png', '.jpg', '.jpeg',
                                          '.pbm', '.pgm', '.ppm', '.tif', '.tiff')):
                        pic_name = resize_pic(pic_name, "IMG/")
                        self.show_emoji(self.me, pic_name)
                        renew_msg_list(LAST_CLICKED, self.me, LAST_CLICKED, pic_name, 1)
                    else:
                        show_msg += pic_name + ' transmitted successfully \n'
                        # 使超大图片缩小
                    sendPicSock.close()
            show_msg = show_msg.strip()
            if show_msg:
                TipUi.show_tip('File(s) transmitted successfully!')
                renew_msg_list(LAST_CLICKED, self.me, LAST_CLICKED, show_msg, 0)
        elif "\n" in content:
            self.send_msg()
            return

    def open_file_win(self):
        files = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        files.connect((self.IP, self.PORT + 1))
        self.fileWin.s = files
        self.fileWin.show()
        self.fileWin.cd('cd same')
        self.fileWin.lab()
        return

    def send_msg(self):
        global LAST_CLICKED
        global FLAG
        if self.me == "":  # user can't chat if he/she didn't login
            TipUi.show_tip('Please login first!')  # show it in showText
            return

        # 提取输入框内容并删除右面的空格
        content = self.inputText.toPlainText().rstrip()  # get what user input and store in content
        if content:  # has content
            # 检查“不可以为空输入”提示是否存在
            if FLAG:
                FLAG = 0
                self.inputText.setPlaceholderText("")
            # 检查输入内容是否过长
            strlen = len(content)
            if strlen > 1792:
                end = content[1787:1792:1]
                TipUi.show_tip("ERROR\nMessage too long!\nMessage After " + end +
                               " is too long to be sent. ")
                return
        else:
            self.inputText.setPlaceholderText("Empty message is not permitted!   ")
            FLAG = 1  # 这个flag是用来看“空消息是不允许的”这条提示有没有出现，如果有这条提示，并且用户正确输入了，就取消这个提示
            self.inputText.clear()
            return

        self.show_msg(self.me, content)
        renew_msg_list(LAST_CLICKED, self.me, LAST_CLICKED, content, 0)

        pid = 1  # Protocol 1 is used for client to send message to srever in PORT 50007
        head = {
            'protocol': pid,
            'message': content,
            'sender': self.me,
            'receiver': LAST_CLICKED,
        }
        head_info = json.dumps(head)  # 将字典转换成字符串
        head_info_len = struct.pack('i', len(head_info))  # 将字符串的长度打包
        CHAT_SOCK.send(head_info_len)  # 发送head_info的长度  # server: send3
        CHAT_SOCK.send(head_info.encode('utf-8'))  # server: send4
        self.inputText.clear()

    def show_msg(self, sender: str, content: str):
        global HEADSHOT_DICT
        global N


        if sender == self.me:
            self.gridLayout.addWidget(self.set_head_shot_bubble(HEADSHOT_DICT[sender]),
                                      N, 2, 1, 1, QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)
            self.gridLayout.addWidget(self.set_label_bubble(content, 1),
                                      N, 1, 1, 1, QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)
        else:
            self.gridLayout.addWidget(self.set_head_shot_bubble(HEADSHOT_DICT[sender]),
                                      N, 0, 1, 1, QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
            self.gridLayout.addWidget(self.set_label_bubble(content, 0),
                                      N, 1, 1, 1, QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.gridLayout.setRowMinimumHeight(N, 50)
        N += 1
        self.scroll_bar_set()
        return

    def show_msg_rcd(self, rcevName):
        global CHAT_RECORD_DICT
        global N

        # 清空聊天记录
        for j in range(self.gridLayout.count()):
            self.gridLayout.itemAt(j).widget().deleteLater()

        N = 0
        self.name.setText(rcevName)
        if rcevName not in CHAT_RECORD_DICT:
            return

        for msg in CHAT_RECORD_DICT[rcevName]:
            # 判断是否为文字
            if msg[2] == 0:
                self.show_msg(msg[0], msg[3])

            # 判断是否为图片
            else:
                self.show_emoji(msg[0], msg[3])
        return

    def show_info_clg(self):
        item = None
        if self.onlineList.count() != 0:
            item = self.onlineList.currentItem()
        if item is not None:
            name = item.text()  # get who user chat with and store in name
            userInfoSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            userInfoSock.connect((self.IP, self.PORT + 3))  # PORT = 50007
            pid = 5  # Protocol 5 is used for
            head = {
                'protocol': pid,
                'name': name,
            }
            head_info = json.dumps(head)  # 将字典转换成字符串
            head_info_len = struct.pack('i', len(head_info))  # 将字符串的长度打包
            userInfoSock.send(head_info_len)  # 发送head_info的长度  # server: send3
            userInfoSock.send(head_info.encode('utf-8'))  # server: send4

            head_struct = userInfoSock.recv(4)  # 接收报头的长度, # client: recv3
            if not head_struct:
                print('ERROR: Receive head_struct ')
                exit(-1)
            head_len = struct.unpack('i', head_struct)[0]  # 解析出报头的字符串大小
            data = userInfoSock.recv(head_len)  # 接收长度为head_len的报头内容的信息 (包含文件大小,文件名的内容)
            # client: recv4
            head_dir = json.loads(data.decode('utf-8'))
            sid = head_dir['sid']
            name = head_dir['name']
            occupation = head_dir['occupation']
            telephone = head_dir['telephone']
            email = head_dir['email']
            headshot = head_dir['headshot']
            data = [sid, name, occupation, telephone, email, headshot]
            # 编号 姓名 职位，电话 邮箱 头像

            if name == self.me:
                self.showClgInfo = ShowInformation(data, 1)
            else:
                self.showClgInfo = ShowInformation(data, 0)
            self.showClgInfo.confirm_button.clicked.connect(self.confirm)
            self.showClgInfo.show()

            userInfoSock.close()
        return

    def srch_show_info(self):
        item = self.searchResList.currentItem()
        if item is not None:
            name = item.text()  # get who user chat with and store in name
            if name == "Search on the top!":
                return
            else:
                name, name2 = name.split('(')

            userInfoSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            userInfoSock.connect((self.IP, self.PORT + 3))  # PORT = 50007
            pid = 5  # Protocol 5 is used for
            head = {
                'protocol': pid,
                'name': name,
            }
            head_info = json.dumps(head)  # 将字典转换成字符串
            head_info_len = struct.pack('i', len(head_info))  # 将字符串的长度打包
            userInfoSock.send(head_info_len)  # 发送head_info的长度  # server: send3
            userInfoSock.send(head_info.encode('utf-8'))  # server: send4

            head_struct = userInfoSock.recv(4)  # 接收报头的长度, # client: recv3
            if not head_struct:
                print('ERROR: Receive head_struct ')
                exit(-1)
            head_len = struct.unpack('i', head_struct)[0]  # 解析出报头的字符串大小
            data = userInfoSock.recv(head_len)  # 接收长度为head_len的报头内容的信息 (包含文件大小,文件名的内容)
            # client: recv4
            head_dir = json.loads(data.decode('utf-8'))
            sid = head_dir['sid']
            name = head_dir['name']
            occupation = head_dir['occupation']
            telephone = head_dir['telephone']
            email = head_dir['email']
            headshot = head_dir['headshot']
            data = [sid, name, occupation, telephone, email, headshot]
            # 编号 姓名 职位，电话 邮箱 头像

            if name == self.me:
                self.showClgInfo = ShowInformation(data, 1)
            else:
                self.showClgInfo = ShowInformation(data, 0)
            self.showClgInfo.confirm_button.clicked.connect(self.confirm)
            self.showClgInfo.show()

            userInfoSock.close()
        return

    def confirm(self):
        name = self.me
        headshot = self.showClgInfo.data[5]
        post = self.showClgInfo.post_edit.currentText()  # 新增
        telephone = self.showClgInfo.tel_edit.text()
        email = self.showClgInfo.email_edit.text()
        if not telephone.isdigit():
            return

        if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email, 0):
            return
        self.showClgInfo.post_edit.setVisible(False)  # 新增
        self.showClgInfo.tel_edit.setVisible(False)
        self.showClgInfo.email_edit.setVisible(False)
        self.showClgInfo.confirm_button.setVisible(False)
        self.showClgInfo.edit_button.setVisible(True)
        self.showClgInfo.post.setVisible(True)  # 新增
        self.showClgInfo.email.setVisible(True)
        self.showClgInfo.telephone.setVisible(True)
        self.showClgInfo.post.setText(post)  # 新增
        self.showClgInfo.email.setText(email)
        self.showClgInfo.telephone.setText(telephone)
        self.showClgInfo.editting = 0

        updataInfoSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        updataInfoSock.connect((self.IP, self.PORT + 3))  # PORT = 50007
        pid = 6  # Protocol 6 is used for
        head = {
            'protocol': pid,
            'name': name,
            'occupation': post,
            'headshot': headshot,
            'telephone': telephone,
            'email': email,
        }
        head_info = json.dumps(head)  # 将字典转换成字符串
        head_info_len = struct.pack('i', len(head_info))  # 将字符串的长度打包
        updataInfoSock.send(head_info_len)  # 发送head_info的长度  # server: send3
        updataInfoSock.send(head_info.encode('utf-8'))  # server: send4

        updataInfoSock.close()

        # userlistSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # userlistSock.connect((self.IP, self.PORT))
        # head = {
        #     'protocol': 3
        # }
        # head_info = json.dumps(head)  # 将字典转换成字符串
        # head_info_len = struct.pack('i', len(head_info))  # 将字符串的长度打包
        # userlistSock.send(head_info_len)
        # userlistSock.send(head_info.encode('utf-8'))
        # userlistSock.close()

    def text_chat(self):
        global LAST_CLICKED
        global N
        item = None
        if self.onlineList.count() != 0:
            item = self.onlineList.currentItem()
        print("item", item)
        if item is not None:
            name = item.text()  # get who user chat with and store in name
            if LAST_CLICKED == name:  # user click the chat list but didn't change object to chat
                return
            LAST_CLICKED = name
            print("chat", LAST_CLICKED)
            self.show_msg_rcd(LAST_CLICKED)
        return

    def srch_text_chat(self):
        global LAST_CLICKED
        global N
        item = self.searchResList.currentItem()
        if item is not None:
            name = item.text()  # get who user chat with and store in name
            if name == "Search on the top!":
                return
            if LAST_CLICKED == name:  # user click the chat list but didn't change object to chat
                return
            LAST_CLICKED = name
            print("search", LAST_CLICKED)
            self.show_msg_rcd(LAST_CLICKED)
        return

    def search(self):
        target = self.searchLine.text()  # get what user want to search and store in target
        s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s1.connect((self.IP, self.PORT + 3))

        pid = 4  # Protocol 4 is used for search stuff in the database in PORT 50010
        head = {
            'protocol': pid,
            'name': target,
        }
        head_info = json.dumps(head)  # 将字典转换成字符串
        head_info_len = struct.pack('i', len(head_info))  # 将字符串的长度打包
        s1.send(head_info_len)  # 发送head_info的长度  # server: send3
        s1.send(head_info.encode('utf-8'))  # server: send4

        result2 = s1.recv(1024)
        result2 = result2.decode()
        if result2 == 'True':
            self.searchResList.clear()
            item = self.onlineList.findItems(target, QtCore.Qt.MatchExactly)
            size = len(item)
            headaddr = s1.recv(1024)
            headaddr = headaddr.decode()
            if size == 0:
                item = QtWidgets.QListWidgetItem(QtGui.QIcon(headaddr), target + "(offline)")
                self.searchResList.addItem(item)
            else:
                item = QtWidgets.QListWidgetItem(QtGui.QIcon(headaddr), target + "(online)")
                self.searchResList.addItem(item)
            self.chatList.setCurrentIndex(1)
        else:
            TipUi.show_tip('Search error\nThe user does not exist!')
        self.searchLine.clear()
        s1.close()
        return


class ClientThread(QtCore.QThread):
    """
    用来接收数据的线程
    """

    signal_add_msg = QtCore.pyqtSignal(str, str)
    signal_add_pic = QtCore.pyqtSignal(str, str)
    signal_clear_online_list = QtCore.pyqtSignal()
    signal_add_online_item = QtCore.pyqtSignal(str, str)

    def __init__(self, name, IP, PORT):
        super().__init__()
        self.name = name
        self.IP = IP
        self.PORT = PORT

    def run(self):
        try:
            global CHAT_SOCK
            CHAT_SOCK = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            CHAT_SOCK.connect((self.IP, self.PORT))  # PORT = 50007
            CHAT_SOCK.send(self.name.encode())
            while True:
                head_struct = CHAT_SOCK.recv(4)
                if not head_struct:
                    print('ERROR: Receive head_struct ')
                    exit(-1)
                print(">>> Trying to unpack")
                head_len = struct.unpack('i', head_struct)[0]
                data = CHAT_SOCK.recv(head_len)
                head_dir = json.loads(data.decode('utf-8'))
                print(">>> Json load finished")
                protocol = head_dir['protocol']
                print(">>> Received protocol", protocol)
                if protocol == 1:
                    # 文字消息
                    message = head_dir['message']
                    sender = head_dir['sender']
                    receiver = head_dir['receiver']
                    renew_msg_list(sender, sender, receiver, message, 0)
                    if sender == LAST_CLICKED:
                        print(sender, message)
                        self.signal_add_msg.emit(sender, message)

                elif protocol == 2:
                    # 表情包
                    message = head_dir['message']
                    sender = head_dir['sender']
                    receiver = head_dir['receiver']
                    renew_msg_list(sender, sender, receiver, message, 1)
                    if sender == LAST_CLICKED:
                        print(sender, message)
                        self.signal_add_pic.emit(sender, message)
                elif protocol == 3:
                    # 刷新在线列表
                    self.signal_clear_online_list.emit()

                    online = head_dir['online']
                    print(head_dir)
                    print(">>> online users", online)
                    headshotnum = 0
                    addresslist = head_dir['headshot']  # 头像图片地址
                    for user in online:
                        address = addresslist[headshotnum]
                        headshotnum = headshotnum + 1
                        if address is None:
                            address = "headshot/default.jpeg"

                        HEADSHOT_DICT[user] = address

                        self.signal_add_online_item.emit(user, address)

                    print("Done protocol 3")
                elif protocol == 4:
                    # 接收图片或文件
                    sender = head_dir['sender']
                    receiver = head_dir['receiver']
                    name = head_dir['picName']
                    picSize = head_dir['picSize']

                    recv_len = 0
                    old = time.time()
                    picName = "./IMG/cache/" + name
                    f = open(picName, 'wb')
                    while recv_len < picSize:
                        if picSize - recv_len > BUFFER_SIZE:
                            recv_mesg = CHAT_SOCK.recv(BUFFER_SIZE)
                        else:
                            recv_mesg = CHAT_SOCK.recv(picSize - recv_len)
                        f.write(recv_mesg)
                        recv_len += len(recv_mesg)

                    time.sleep(0.01)
                    f.close()
                    now = time.time()
                    stamp = int(now - old)
                    print("Successfully received the picture! Spend time: %ds" % stamp)

                    if name.endswith(('.bmp', '.dib', '.png', '.jpg', '.jpeg',
                                      '.pbm', '.pgm', '.ppm', '.tif', '.tiff')):
                        name = resize_pic(name, "./IMG/cache/")
                        renew_msg_list(sender, sender, receiver, name, 1)
                        if sender == LAST_CLICKED:
                            self.signal_add_pic.emit(sender, name)
                    else:
                        show_msg = name + ' transmitted successfully'
                        renew_msg_list(sender, sender, receiver, show_msg, 0)
                        if sender == LAST_CLICKED:
                            self.signal_add_msg.emit(sender, show_msg)
        except Exception as e:
            print(e)
        print("Thread quit")
