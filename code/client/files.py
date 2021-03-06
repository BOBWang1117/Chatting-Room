# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'files.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_files(object):
    def setupUi(self, files):
        files.setObjectName("files")
        files.resize(581, 416)
        self.filesList = QtWidgets.QListWidget(files)
        self.filesList.setGeometry(QtCore.QRect(20, 50, 541, 301))
        self.filesList.setStyleSheet("height:20px;")
        self.filesList.setObjectName("filesList")
        self.label = QtWidgets.QLabel(files)
        self.label.setGeometry(QtCore.QRect(30, 20, 141, 16))
        self.label.setObjectName("label")
        self.currentPos = QtWidgets.QLabel(files)
        self.currentPos.setGeometry(QtCore.QRect(170, 20, 191, 16))
        self.currentPos.setText("")
        self.currentPos.setObjectName("currentPos")
        self.splitter = QtWidgets.QSplitter(files)
        self.splitter.setGeometry(QtCore.QRect(100, 370, 371, 28))
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setHandleWidth(170)
        self.splitter.setObjectName("splitter")
        self.uploadButton = QtWidgets.QPushButton(self.splitter)
        self.uploadButton.setObjectName("uploadButton")
        self.uploadButton_2 = QtWidgets.QPushButton(self.splitter)
        self.uploadButton_2.setObjectName("uploadButton_2")

        self.retranslateUi(files)
        self.uploadButton.clicked.connect(files.uploadFile)
        self.uploadButton_2.clicked.connect(files.downloadFile)
        self.filesList.itemDoubleClicked['QListWidgetItem*'].connect(files.itemDblClk)
        QtCore.QMetaObject.connectSlotsByName(files)

    def retranslateUi(self, files):
        _translate = QtCore.QCoreApplication.translate
        files.setWindowTitle(_translate("files", "Form"))
        self.label.setText(_translate("files", "Current position: "))
        self.uploadButton.setText(_translate("files", "Upload"))
        self.uploadButton_2.setText(_translate("files", "Download"))
