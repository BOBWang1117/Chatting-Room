import sys
import time
import random
from PyQt5 import QtCore, QtWidgets


class Example(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        lay = QtWidgets.QVBoxLayout(self)

        self.table = QtWidgets.QTableWidget(10, 10)
        lay.addWidget(self.table)

        self.myclass2 = myclass2()
        self.myclass2.new_signal.connect(self.some_function)
        self.myclass2.start()

    @QtCore.pyqtSlot(int, int, str)
    def some_function(self, r, c, text):
        it = self.table.item(r, c)
        if it:
            it.setText(text)
        else:
            it = QtWidgets.QTableWidgetItem(text)
            self.table.setItem(r, c, it)


class myclass2(QtCore.QThread):
    new_signal = QtCore.pyqtSignal(int, int, str)

    def run(self):
        while True:
            time.sleep(.1)
            r = random.randint(0, 9)
            c = random.randint(0, 9)
            text = "some_text: {}".format(random.randint(0, 9))
            self.new_signal.emit(r, c, text)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = Example()
    ex.showMaximized()
    sys.exit(app.exec_())
