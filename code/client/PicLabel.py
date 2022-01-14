import os

from PyQt5 import QtWidgets, QtCore

from QDialog import TipUi


class PicLabel(QtWidgets.QLabel):
    def __init__(self, parent=None):
        super(PicLabel, self).__init__(parent)

    '''重载一下鼠标双击事件'''

    def mouseDoubleClickEvent(self, event):
        print("mouseDoubleClickEvent")
        # return
        # pic_name = self.pic_bubbles[self.sender()]
        pic_name = "hacker.jpg"
        if pic_name[0:7:1] == "resize_":
            new_name = pic_name.split("resize_", 1)[1]
            if os.path.isfile("IMG/cache/" + new_name):
                pic_name = "IMG/cache/" + new_name
                os.system('start ' + pic_name)
            else:
                TipUi.show_tip("Picture doesn't exist!")
        else:
            if os.path.isfile("IMG/cache/" + pic_name):
                pic_name = "IMG/cache/" + pic_name
                os.system('start ' + pic_name)
            else:
                TipUi.show_tip("Picture doesn't exist!")
        return

# class PicLabel(QtWidgets.QLabel):
#     # 自定义信号, 注意信号必须为类属性
#     DoubleClicked = QtCore.pyqtSignal()
#
#     def __init__(self, parent=None):
#         super(PicLabel, self).__init__(parent)
#
#
#
#     def mouseDoubleClickEvent(self, event):
#         print("mouseDoubleClickEvent")

    # def connect_customized_slot(self, func):
    #     self.DoubleClicked.connect(func)

