# -*- coding:utf-8 -*-
"""
默认的admin及默认密码 admin123
"""
import os
import sys
import socket
import struct
import time
import json  # json.dumps(some)打包   json.loads(some)解包
from Database import Database
from PyQt5.QtWidgets import QWidget, QApplication, QTableWidget, QAbstractItemView, QMessageBox, QTableWidgetItem, \
    QLineEdit, QPushButton, QHeaderView, QLabel, QCheckBox, QHBoxLayout
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt
from ChattingMainWindow import DialogueWindow


buffSize = 1024


class AdminWindow(QWidget):

    def __init__(self, name, IP, PORT):
        super().__init__()
        self.me = name
        self.IP = IP
        self.PORT = PORT
        self.table = QTableWidget(self)  # 添加表格对象
        self.getDatabase()
        self.database = Database('./newdata.db')
        self.check_list = []  # 保存所有的选择框
        self.show_password_flag = False  # 是否显示原密码
        self.select_all_flag = False  # 是否选择全部
        self.set_ui()

    def getDatabase(self):
        s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s1.connect((self.IP, self.PORT + 3))
        pid = 2  # Protocol 2 is used for admin client to get database
        head = {
            'protocol': pid,
        }
        head_info = json.dumps(head)  # 将字典转换成字符串
        head_info_len = struct.pack('i', len(head_info))  # 将字符串的长度打包
        s1.send(head_info_len)  # 发送head_info的长度  # server: send3
        s1.send(head_info.encode('utf-8'))  # server: send4
        while True:
            head_struct = s1.recv(4)  # 接收报头的长度, # client: recv3
            if not head_struct:
                print('ERROR: Receive head_struct ')
                exit(-1)
            head_len = struct.unpack('i', head_struct)[0]  # 解析出报头的字符串大小
            data = s1.recv(head_len)  # 接收长度为head_len的报头内容的信息 (包含文件大小,文件名的内容)  # client: recv4
            head_dir = json.loads(data.decode('utf-8'))
            fileSize = head_dir['fileSize']
            fileName = head_dir['fileName']
            #   接受真的文件内容
            recv_len = 0
            recv_mesg = b''
            old = time.time()
            f = open(fileName, 'wb')
            while recv_len < fileSize:
                if fileSize - recv_len > buffSize:
                    recv_mesg = s1.recv(buffSize)
                    f.write(recv_mesg)
                    recv_len += len(recv_mesg)
                else:
                    recv_mesg = s1.recv(fileSize - recv_len)
                    recv_len += len(recv_mesg)
                    f.write(recv_mesg)

            now = time.time()
            stamp = int(now - old)
            print("Successfully receive database! Spend time: %ds" %stamp)
            f.close()
            break
        s1.close()

    def editDatabase(self):
        s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s1.connect((self.IP, self.PORT + 3))
        pid = 3  # Protocol 3 is used for admin client to edit database
        fileMesg = 'newdata.db'
        fileSize = os.path.getsize(fileMesg)  # 得到文件的大小,字节
        fileName = 'data.db'
        head = {
            'protocol': pid,
            'fileName': fileName,
            'fileSize': fileSize,
        }
        head_info = json.dumps(head)  # 将字典转换成字符串
        head_info_len = struct.pack('i', len(head_info))  # 将字符串的长度打包
        s1.send(head_info_len)  # 发送head_info的长度  # server: send3
        s1.send(head_info.encode('utf-8'))  # server: send4
        #   发送real信息
        with open(fileMesg, 'rb') as f:
            data = f.read()
            s1.sendall(data)

        print('Successfully send database!')
        #s1.close()

    def set_ui(self):
        self.setWindowTitle("Management page")
        self.setFixedSize(1200, 900)
        self.font = QFont("Consolas")
        self.setFont(self.font)
        self.add_table()  # 添加数据表格
        self.get_all_user()  # add table 之后才有show
        self.add_line_edit()  # 添加输入框
        self.add_label()  # 添加标签
        self.add_button()  # 添加按钮并绑定事件
        self.icon = QIcon("./IMG/WorkTime_logo.png")
        self.setWindowIcon(self.icon)

    def add_table(self):
        """添加数据表格"""
        self.table.setFixedWidth(1020)  # 设置宽度
        self.table.setFixedHeight(600)  # 设置高度
        self.table.move(10, 30)  # 设置显示的位置
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 自动填充
        self.table.horizontalHeader().setFont(self.font)  # 设置一下字体
        # self.table.setSelectionMode(QAbstractItemView.SingleSelection)  # 只能单选
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)  # 只能选择整行
        self.table.setColumnCount(4)  # 设置列数
        self.table.setHorizontalHeaderLabels(["Choice", "username", "password", 'created_time'])  # 设置首行
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 表格中的内容设置为无法修改
        self.table.verticalHeader().hide()  # 把序号隐藏
        self.table.setSortingEnabled(False)  # 自动排序

    def get_all_user(self):
        """获取所有的用户信息"""
        data = self.database.read_table()  # 从数据库中获取用户信息，用户信息以 username, password, created_time 形式返回
        for user in data:
            self.add_row(user[0], user[1], user[2])

    def add_row(self, username, password, created_time):
        """在表格上添加一行新的内容"""
        row = self.table.rowCount()  # 表格的行数
        self.table.setRowCount(row + 1)  # 添加一行表格
        self.table.setItem(row, 1, QTableWidgetItem(str(username)))  # 将用户信息插入到表格中
        self.table.setItem(row, 2, QTableWidgetItem(str(password)))
        self.table.setItem(row, 3, QTableWidgetItem(str(created_time)))
        # 设置复选框
        widget = QWidget()
        check = QCheckBox()
        self.check_list.append(check)  # 添加到复选框列表中
        check_lay = QHBoxLayout()
        check_lay.addWidget(check)
        check_lay.setAlignment(Qt.AlignCenter)
        widget.setLayout(check_lay)
        self.table.setCellWidget(row, 0, widget)

    def add_line_edit(self):
        self.username_edit = QLineEdit(self)
        self.username_edit.setFixedSize(240, 40)
        self.username_edit.move(760, 700)
        self.username_edit.setPlaceholderText('username')

        self.password_edit = QLineEdit(self)
        self.password_edit.setFixedSize(240, 40)
        self.password_edit.move(760, 760)
        self.password_edit.setPlaceholderText('password')
        self.password_edit.setEchoMode(QLineEdit.Password)

        # 更新密码的输入框
        self.update_username_edit = QLineEdit(self)
        self.update_username_edit.setFixedSize(240, 40)
        self.update_username_edit.move(160, 700)
        self.update_username_edit.setPlaceholderText('username')

        self.update_password_edit = QLineEdit(self)
        self.update_password_edit.setFixedSize(240, 40)
        self.update_password_edit.move(160, 760)
        self.update_password_edit.setPlaceholderText('new password')

    def show_password(self):
        if self.show_password_flag:  # 如果是真，隐藏密码
            self.password_edit.setEchoMode(QLineEdit.Password)
            self.show_password_flag = False
            self.show_password_button.setText('Show')
        else:  # 否则显示密码
            self.password_edit.setEchoMode(QLineEdit.Normal)
            self.show_password_flag = True
            self.show_password_button.setText("Hide")

    def add_label(self):
        """添加界面上的标签控件"""
        self.username_label = QLabel(self)
        self.username_label.setFixedSize(160, 40)
        self.username_label.move(640, 700)
        self.username_label.setText('username')

        self.password_label = QLabel(self)
        self.password_label.setFixedSize(160, 40)
        self.password_label.move(640, 760)
        self.password_label.setText('password')

        # 更新密码的标签
        self.update_username_label = QLabel(self)
        self.update_username_label.setFixedSize(160, 40)
        self.update_username_label.move(40, 700)
        self.update_username_label.setText('username')

        self.update_password_label = QLabel(self)
        self.update_password_label.setFixedSize(160, 40)
        self.update_password_label.move(40, 760)
        self.update_password_label.setText('password')

    def add_button(self):
        """添加界面上的按钮控件"""
        # 创建按钮对象
        self.delete_button = QPushButton(self)
        self.update_button = QPushButton(self)
        self.add_button_ = QPushButton(self)
        self.show_password_button = QPushButton(self)
        self.clear_button = QPushButton(self)
        self.select_all_button = QPushButton(self)
        self.refresh_button = QPushButton(self)
        self.main_window_button = QPushButton(self)

        # 设置按钮上的文本
        self.delete_button.setText("Delete")
        self.update_button.setText("Update")
        self.add_button_.setText("Add")
        self.show_password_button.setText("Show")
        self.clear_button.setText("Clear")
        self.select_all_button.setText("Select All")
        self.refresh_button.setText("Refresh")
        self.main_window_button.setText("Main window")

        # 在按钮上设置提示信息
        self.delete_button.setToolTip("Delete the selected user, you can choose multiple users")
        self.clear_button.setToolTip("Clear all the users, including the super user, but the super user will be "
                                     "created later by default")
        self.select_all_button.setToolTip("Select all the users, including the super user")
        self.show_password_button.setToolTip("Show or hide the password")
        self.add_button_.setToolTip("Add a new user with the username and password in the input box")
        self.update_button.setToolTip("Update the password with the chosen username")
        self.refresh_button.setToolTip("Click here to refresh the table")
        self.main_window_button.setToolTip("Click here and you will go to the user interface")

        # 控制位置
        self.delete_button.move(1040, 340)
        self.select_all_button.move(1040, 280)
        self.clear_button.move(1040, 400)
        self.refresh_button.move(1040, 460)

        self.update_button.move(430, 700)
        self.add_button_.move(1020, 700)
        self.show_password_button.move(1020, 750)

        self.main_window_button.move(500, 820)

        # 绑定事件
        self.delete_button.clicked.connect(self.delete_user)
        self.select_all_button.clicked.connect(self.select_all)
        self.clear_button.clicked.connect(self.clear)
        self.show_password_button.clicked.connect(self.show_password)
        self.add_button_.clicked.connect(self.add_user)
        self.update_button.clicked.connect(self.update_password)
        self.refresh_button.clicked.connect(self.refresh)
        self.main_window_button.clicked.connect(self.show_main_window)
        self.main_window_button.setFixedSize(200, 40)
        self.select_all_button.setFixedSize(100, 30)
        self.clear_button.setFixedSize(100, 30)
        self.delete_button.setFixedSize(100, 30)
        self.refresh_button.setFixedSize(100, 30)

    def show_main_window(self):
        self.stuff = DialogueWindow(self.me, self.IP, self.PORT)
        self.stuff.show()
        self.close()

    def delete_user(self):
        choose_list = []
        for i in self.check_list:
            if i.isChecked():
                username = self.table.item(self.check_list.index(i), 1).text()
                if username == 'admin':
                    answer = QMessageBox.critical(self, 'Error',
                                                  'You are going to delete the super user, but it will be created later with the default password',
                                                  QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Cancel)
                    if answer == QMessageBox.Yes:
                        choose_list.append(i)
                        # self.editDatabase()
                    if answer == QMessageBox.Cancel:
                        return
                else:
                    choose_list.append(i)
                    # self.editDatabase()

        for i in choose_list:
            username = self.table.item(self.check_list.index(i), 1).text()
            self.database.delete_table_by_username(username)
            self.table.removeRow(self.check_list.index(i))
            self.check_list.remove(i)
        self.database.create_table()
        self.editDatabase()

    def select_all(self):
        """选择是否选择全部"""
        try:
            if not self.select_all_flag:
                for check in self.check_list:
                    check.setCheckState(2)  # 设置为选择状态
                self.select_all_button.setText("Unselect")
                self.select_all_flag = True
            else:
                for check in self.check_list:
                    check.setCheckState(0)  # 设置为未选状态
                self.select_all_button.setText("Select All")
                self.select_all_flag = False
        except:
            # 该错误是由于没有复选框引起
            pass

    def add_user(self):
        """一行一行的添加数据"""
        username = self.username_edit.text()
        password = self.password_edit.text()
        if all((username, password)):
            flag = self.database.insert_table(username, password)
            if flag:
                QMessageBox.critical(self, 'Error',
                                     'Already exists the username {}, please use another username'.format(username))
            else:
                self.add_row(username, password, self.database.get_time())
                self.editDatabase()
            self.username_edit.setText('')  # 清空输入的用户信息
            self.password_edit.setText('')
        else:
            QMessageBox.critical(self, 'Error', "Please fill in the blanks")

    def clear(self):
        """清空所有的数据，包括数据库和表格中的数据"""
        self.table.clearContents()  # 清空表格的内容
        self.table.setRowCount(0)  # 将表格的行数重置为0
        self.database.clear()  # 清空数据库数据
        self.editDatabase()

    def update_password(self):
        """更新密码"""
        username = self.update_username_edit.text()
        password = self.update_password_edit.text()
        if len(password) >= 6:
            self.database.update_table(username, password)
            self.change_table(username, password)
            self.update_password_edit.setText('')
            self.update_username_edit.setText('')
            self.editDatabase()

        else:
            QMessageBox.information(self, 'Error', 'Password is too short, at least 6 words', QMessageBox.Yes,
                                    QMessageBox.Yes)

    def change_table(self, username, password):
        """更新表格"""
        find_flag = False
        for row in range(self.table.rowCount()):
            username_find = self.table.item(row, 1).text()
            if username_find == username:
                self.table.item(row, 2).setText(password)
                find_flag = True
                break
        if not find_flag:  # 如果没有找到对应的用户名
            QMessageBox.information(self, 'prompt', 'Can not find the username {}'.format(username))

    def refresh(self):
        """重新加载数据库并显示"""
        self.table.clearContents()
        self.check_list.clear()
        self.table.setRowCount(0)
        self.database.create_table()
        self.get_all_user()
        # self.editDatabase()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    admin = AdminWindow("admin")
    admin.show()
    sys.exit(app.exec_())