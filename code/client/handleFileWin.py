import json
import os
import struct
import time

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QKeySequence, QColor, QIcon
from PyQt5.QtWidgets import QFileDialog, QShortcut, QMessageBox

from files import Ui_files

_translate = QtCore.QCoreApplication.translate


class Show_UiFiles(QtWidgets.QWidget, Ui_files):
    def __init__(self):
        super(Show_UiFiles, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("Handle Files")
        self.icon = QIcon("./IMG/WorkTime_logo.png")
        self.setWindowIcon(self.icon)
        self.s = None   # file socket

    def cd(self, message):
        self.s.send(message.encode())
        return

    def itemDblClk(self):
        item = self.filesList.currentItem()
        if item is not None:
            name = item.text()
        else:
            return
        if name == 'Return to the previous dir':
            content = 'cd ..'
            self.cd(content)
            self.lab()
        elif '.' not in name:
            name = 'cd ' + name
            self.cd(name)
            self.lab()
        else:
            self.downloadFile()
        return

    def uploadFile(self):
        fileList, filetype = QFileDialog.getOpenFileNames(self, "Choose files", "C:/", "All Files (*);;Text Files (*.txt);;""Microsoft Edge PDF Document (*.pdf);;""Microsoft Word Document (*.docx);;""Microsoft PowerPoint Document (*.ppt);;""Microsoft Excel Worksheet (*.xlsx)")
        # 如果有选择文件才继续执行
        if fileList:
            for file in fileList:
                name = file.split('/')[-1]
                message = 'put ' + name
                print(message)
                self.s.send(message.encode())
                # fileName = r'./' + file
                fileSize = os.path.getsize(file)
                dirc = {
                    'filename': name,
                    'filesize_bytes': fileSize,
                }
                head_info = json.dumps(dirc)
                head_info_len = struct.pack('i', len(head_info))
                self.s.send(head_info_len)
                self.s.send(head_info.encode('utf-8'))
                print(fileSize)
                with open(file, 'rb') as f:
                    while True:
                        print("Start sending1")
                        a = f.read()
                        if not a:
                            break
                        self.s.sendall(a)
                    f.close()
                    print("Send over, waiting")
                    while True:
                        end=self.s.recv(1024)
                        if end == 'EOF'.encode():
                            print("Server recv over")
                            break
                     # time.sleep(0.1)
                     # self.s.send('EOF'.encode())

            QMessageBox.information(self, 'Message', 'Upload compeleted! ', QMessageBox.Ok )
        self.cd('cd same')
        self.lab()
        return

    def recvList(self, enter, lu):
        self.s.send(enter.encode())
        data = self.s.recv(4096)
        data = json.loads(data.decode())
        self.filesList.clear()
        lu = lu.split('\\')
        i = 0
        if len(lu) != 1:
            self.filesList.addItem('Return to the previous dir')
            self.filesList.item(i).setBackground(QColor(255, 236, 139))
            i += 1
        for j in range(len(data)):
            self.filesList.addItem(data[j])
            if '.' not in data[j]:
                self.filesList.item(i).setBackground(QColor(255, 236, 139))
            else:
                self.filesList.item(i).setBackground(QColor(255, 250, 205))
            i += 1
        return

    def lab(self):
        data = self.s.recv(1024)  # 接收目录
        lu = data.decode()
        try:
            self.currentPos.clear()
            self.currentPos.setText(lu)
        except:
            self.currentPos.setText(lu)
        self.recvList('dir', lu)
        return

    def downloadFile(self):
        item = self.filesList.currentItem()
        if item is not None:
            defaultName = item.text()
        else:
            return
        if '.' not in defaultName:
            QMessageBox.information(self, 'Warning', 'Download folder is not permitted! You can download fileself.s. ', QMessageBox.Ok)
            return
        fileDir, filetype = QFileDialog.getSaveFileName(self, "Save the file", defaultName,
                                                      "All Files (*);;Text Files (*.txt);;Microsoft Edge PDF Document (*.pdf);;Microsoft Word Document (*.docx);;Microsoft PowerPoint Document (*.ppt);;Microsoft Excel Worksheet (*.xlsx)")
        fileName = fileDir.split('/')[-1]
        message = 'get ' + defaultName
        if fileName:
            self.s.send(message.encode())
            head_struct=self.s.recv(4)
            if head_struct:
                print('已连接服务端,等待接收数据')
            head_len = struct.unpack('i', head_struct)[0]
            headdata = self.s.recv(head_len)
            head_dir = json.loads(headdata.decode('utf-8'))
            filesize_b = head_dir['filesize_bytes']
            filename = head_dir['filename']
            print(filesize_b)
            print(filename)
            recv_len = 0
            old = time.time()
            f = open(fileDir, 'wb')
            buffsize = 1024
            while recv_len < filesize_b:
                if filesize_b - recv_len > buffsize:
                    recv_mesg = self.s.recv(buffsize)
                    f.write(recv_mesg)
                    recv_len += len(recv_mesg)
                else:
                    recv_mesg = self.s.recv(filesize_b - recv_len)
                    recv_len += len(recv_mesg)
                    f.write(recv_mesg)
            print(recv_len, filesize_b)
            now = time.time()
            stamp = int(now - old)
            print('总共用时%ds' % stamp)
            QMessageBox.information(self, 'Message', 'Download compeleted! ', QMessageBox.Ok)
            f.close()
                #while True:
                  #  data = self.s.recv(1024)
                   # if data == 'EOF'.encode():
                    #    QMessageBox.information(self, 'Message', 'Download compeleted! ', QMessageBox.Ok )
                    #    break
                 #   f.write(data)
        else:
            QMessageBox.information(self, 'Error', 'File name is needed! ', QMessageBox.Ok)
        return