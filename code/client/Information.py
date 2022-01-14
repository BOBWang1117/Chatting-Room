import re

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from QDialog import TipUi
from showInformation import Ui_ClgInfo
from chooseHeadShot import Ui_Form
_translate = QtCore.QCoreApplication.translate

headshot = ["headshot/1.png", "headshot/2.png", "headshot/3.jpg",
            "headshot/4.jpeg", "headshot/5.jpg", "headshot/6.jpg"]

def set_emoji(j):
    global headshot
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap(headshot[j]), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    return icon

class ChooseHeadshot(QtWidgets.QWidget, Ui_Form):
    def __init__(self):
        super(ChooseHeadshot, self).__init__()
        self.setupUi(self)
        self.potential_name = None
        self.groupBox.setVisible(False)
        self.setWindowTitle("Choose Headshot")
        self.icon = QIcon("./IMG/WorkTime_logo.png")
        self.setWindowIcon(self.icon)
        btns = [
            self.but1,
            self.but2,
            self.but3,
            self.but4,
            self.but5,
            self.but6
        ]
        for j in range(6):
            icon = set_emoji(j)
            btns[j].setIcon(icon)
            btns[j].setIconSize(QtCore.QSize(81, 81))

    def choose(self):
        global headshot
        sender = self.sender().objectName()
        self.groupBox.setVisible(True)
        if sender == "but1":
            self.groupBox.setGeometry(QtCore.QRect(20, 10, 101, 111))
            self.potential_name = headshot[0]
        elif sender == "but2":
            self.groupBox.setGeometry(QtCore.QRect(140, 10, 101, 111))
            self.potential_name = headshot[1]
        elif sender == "but3":
            self.groupBox.setGeometry(QtCore.QRect(260, 10, 101, 111))
            self.potential_name = headshot[2]
        elif sender == "but4":
            self.groupBox.setGeometry(QtCore.QRect(20, 130, 101, 111))
            self.potential_name = headshot[3]
        elif sender == "but5":
            self.groupBox.setGeometry(QtCore.QRect(140, 130, 101, 111))
            self.potential_name = headshot[4]
        elif sender == "but6":
            self.groupBox.setGeometry(QtCore.QRect(260, 130, 101, 111))
            self.potential_name = headshot[5]
        return



class ShowInformation(QtWidgets.QWidget, Ui_ClgInfo):
    def __init__(self, data, edit):
        super(ShowInformation, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("Colleague Information")
        self.icon = QIcon("./IMG/WorkTime_logo.png")
        self.setWindowIcon(self.icon)
        self.tel_edit.setVisible(False)
        self.email_edit.setVisible(False)
        self.post_edit.setVisible(False)
        self.confirm_button.setVisible(False)
        self.headshot_win = ChooseHeadshot()
        self.data = data        # id name post tel email headshot
        self.editting = 0  # 看是否正在编辑中
        self.set_headshot()
        if data[1] is None:
            self.post.setText(_translate("ClgInfo", "Staff"))
        else:
            self.post.setText(_translate("ClgInfo", data[2]))
        self.telephone.setText(_translate("ClgInfo", data[3]))
        self.name.setText(_translate("ClgInfo", data[1]))
        self.email.setText(_translate("ClgInfo", data[4]))
        self.number.setText(_translate("ClgInfo", str(data[0])))
        self.edit = edit  # 看是否可以进行编辑
        if not edit:
            self.edit_button.setVisible(False)

    def set_headshot(self):
        global headshot
        icon = QtGui.QIcon()
        if self.data[5] is None:
            icon.addPixmap(QtGui.QPixmap("headshot/default.jpeg"),
                           QtGui.QIcon.Normal, QtGui.QIcon.Off)
        else:
            icon.addPixmap(QtGui.QPixmap(self.data[5]),
                           QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton.setIcon(icon)
        self.pushButton.setIconSize(QtCore.QSize(111, 111))


    def edit(self):
        posts = ["Product Manager", "Scrum Master", "Developer"]
        self.post_edit.clear()
        self.post_edit.addItems(posts)
        if self.data[2] is not None:
            self.post_edit.setCurrentIndex(posts.index(self.data[2]))
        else:
            self.post_edit.setCurrentIndex(0)
        self.setWindowModality(Qt.ApplicationModal)
        self.editting = 1
        self.tel_edit.setText(self.data[3])
        self.email_edit.setText(self.data[4])
        self.confirm_button.setVisible(True)
        self.post.setVisible(False)
        self.telephone.setVisible(False)
        self.email.setVisible(False)
        self.edit_button.setVisible(False)
        self.post_edit.setVisible(True)
        self.tel_edit.setVisible(True)
        self.email_edit.setVisible(True)


    def head_shot(self):
        if self.edit and self.editting:
            self.hide()
            self.headshot_win.setWindowModality(Qt.ApplicationModal)
            self.headshot_win.show()
            #self.headshot_win.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
            self.headshot_win.pushButton.clicked.connect(self.confirm)

    def confirm(self):   # 这是头像选择页面的confirm，编辑信息的confirm在ChattingMainWindow.py

        if self.headshot_win.potential_name:
            self.data[5] = self.headshot_win.potential_name
        self.set_headshot()
        self.show()
        self.headshot_win.close()
        return

    def save_change(self):
        telephone = self.tel_edit.text()
        email = self.email_edit.text()
        if not telephone.isdigit():
            TipUi.show_tip('Invalid telephone number!\n'
                           'Characters except numbers are not allowed!')
            return
        if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email, 0):
            TipUi.show_tip('Invalid E-mail! ')
            return
        self.data[2] = self.post_edit.currentText()
        self.data[3] = telephone
        self.data[4] = email

