# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 20:49:32 2019
@author: Tiny
"""
# =============================================================================
from PyQt5.QtGui import QPixmap, QImage

''' 鼠标事件，各动作响应事件可以随意自定义'''

''' 参考: 1. https://blog.csdn.net/richenyunqi/article/details/80554257
             pyqt判断鼠标点击事件——左键按下、中键按下、右键按下、左右键同时按下等等;
          2. https://fennbk.com/8065
             Pyqt5 之 鼠标 (事件与方法介绍)
          3. https://blog.csdn.net/leemboy/article/details/80462632
             PyQt5编程-鼠标事件
          4. https://doc.qt.io/qtforpython/PySide2/QtGui/QWheelEvent.html#PySide2.QtGui.PySide2.QtGui.QWheelEvent.delta
             QWheelEvent'''
# =============================================================================
# =============================================================================
''' PyQt4 和 PyQt5区别：'''
#   PySide2.QtGui.QWheelEvent.delta()
#   Return type:	int
#   This function has been deprecated, use pixelDelta() or angleDelta() instead.
# =============================================================================
from PyQt5 import QtWidgets
import sys

'''自定义的QLabel类'''


class myImgLabel(QtWidgets.QLabel):
    def __init__(self, parent=None):
        super(myImgLabel, self).__init__(parent)

    '''重载一下鼠标双击事件'''

    def mouseDoubleClickEvent(self, event):
        print("mouseDoubleClickEvent")


'''定义主窗口'''


class MyWindow(QtWidgets.QWidget):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.imgLabel = myImgLabel()  # 声明imgLabel
        self.image = QImage()  # 声明新img
        if self.image.load("headshot/5.jpg"):  # 如果载入图片,则
            self.imgLabel.setPixmap(QPixmap.fromImage(self.image))  # 显示图片
        self.gridLayout = QtWidgets.QGridLayout(self)  # 布局设置
        self.gridLayout.addWidget(self.imgLabel, 0, 0, 1, 1)  # 注释掉这两句,则不显示图片


'''主函数'''
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myshow = MyWindow()
    myshow.show()
    sys.exit(app.exec_())