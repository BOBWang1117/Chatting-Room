import socket
import threading
import queue
import struct
import json  # json.dumps(some)打包   json.loads(some)解包
import time
import os
import os.path
import sys
from Database import Database, DatabasePersonalInfo

IP = '127.0.0.1'
PORT = 50007
que = queue.Queue()  # 用于存放客户端发送的信息的队列
users = []  # 用于存放在线用户的信息  [conn, user, addr]
lock = threading.Lock()  # 创建锁, 防止多个线程写入数据的顺序打乱
database = Database('./data.db')
databasePersonalInfo = DatabasePersonalInfo('./personal_info.db')
buffSize = 1024


# 将在线用户存入online列表并返回
def onlines():
    online = []
    for i in range(len(users)):
        online.append(users[i][1])  # users [conn, user, addr]
    return online


class JudgeServer(threading.Thread):
    def __init__(self, port):
        self.isAdmin = -1
        threading.Thread.__init__(self)
        self.ADDR = (IP, port)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def judge(self, conn, addr):
        # new code
        head_struct = conn.recv(4)
        if not head_struct:
            print('ERROR: Receive head_struct')
            exit(-1)
        head_len = struct.unpack('i', head_struct)[0]
        data = conn.recv(head_len)
        head_dir = json.loads(data.decode('utf-8'))
        protocol = head_dir['protocol']

        if protocol == 1:
            username = head_dir['username']
            password = head_dir['password']
            self.judgeLogin(conn, username, password)

        if protocol == 2:
            self.sendDatabase(conn)

        if protocol == 3:
            fileName = head_dir['fileName']
            fileSize = head_dir['fileSize']
            self.getDatabase(conn, fileName, fileSize)

        if protocol == 4:
            name = head_dir['name']
            self.ifExist(conn, name)

        if protocol == 5:
            name = head_dir['name']
            self.sendInformationFromDatabase(conn, name)

        if protocol == 6:
            occupation = head_dir['occupation']
            telephone = head_dir['telephone']
            email = head_dir['email']
            headshot = head_dir['headshot']
            name = head_dir['name']
            self.updataInformationToDatabase(occupation, telephone, email, headshot, name)
            d = onlines()
            self.recvFlash(addr, d, '', '', -1)

    def recvFlash(self, addr, data, sender, receiver, protocol):
        lock.acquire()
        try:
            que.put((addr, data, sender, receiver, protocol))
        finally:
            lock.release()

    @staticmethod
    def judgeLogin(conn, username, password):
        print('\nusername: ' + username)
        print('password: ' + password)
        data = database.find_password_by_username(username)  # 在数据库中查找数据
        result = '-1'
        if data:
            if str(data[0][0]) == password:
                result = '1'
        conn.send(result.encode())  # server: send3

    @staticmethod
    def sendDatabase(conn):
        fileMesg = 'data.db'
        fileSize = os.path.getsize(fileMesg)  # 得到文件的大小,字节
        fileName = 'new' + fileMesg
        dirc = {
            'fileName': fileName,
            'fileSize': fileSize,
        }
        head_info = json.dumps(dirc)  # 将字典转换成字符串
        head_info_len = struct.pack('i', len(head_info))  # 将字符串的长度打包
        conn.send(head_info_len)  # 发送head_info的长度  # server: send3
        conn.send(head_info.encode('utf-8'))  # server: send4
        #   发送real信息
        with open(fileMesg, 'rb') as f:
            data = f.read()
            conn.sendall(data)
        print('Successfully send database!')

    @staticmethod
    def ifExist(conn, name):
        data = database.is_has(name)
        if data is True:
            conn.send("True".encode())
            namelist = []
            namelist.append(name)
            piclist = databasePersonalInfo.find_headshot_by_name(namelist)
            if piclist[0] is not None:
                pic = piclist[0]
            else:
                pic = "headshot/default.jpeg"
            print(pic)
            conn.send(pic.encode())
        else:
            conn.send("False".encode())

    @staticmethod
    def getDatabase(conn, fileName, fileSize):
        recv_len = 0
        recv_mesg = b''
        old = time.time()
        f = open(fileName, 'wb')
        while recv_len < fileSize:

            if fileSize - recv_len > buffSize:
                recv_mesg = conn.recv(buffSize)
                f.write(recv_mesg)
                recv_len += len(recv_mesg)
            else:
                recv_mesg = conn.recv(fileSize - recv_len)
                recv_len += len(recv_mesg)
                f.write(recv_mesg)

        now = time.time()
        stamp = int(now - old)
        print("Successfully Receive Database! Spend time: %ds" %stamp)
        f.close()

    @staticmethod
    def sendInformationFromDatabase(conn, name):
        # search information form database by using name
        if not databasePersonalInfo.is_has_personal_info(name):
            databasePersonalInfo.insert_table_personal_info(name, None, None, None, None)

        result = databasePersonalInfo.find_personal_info_by_name(name)
        sid = result[0][0]
        name = result[0][1]
        occupation = result[0][2]
        telephone = result[0][3]
        email = result[0][4]
        headshot = result[0][5]
        head = {
            'sid': sid,
            'name': name,
            'occupation': occupation,
            'telephone': telephone,
            'email': email,
            'headshot': headshot,
        }
        head_info = json.dumps(head)  # 将字典转换成字符串
        head_info_len = struct.pack('i', len(head_info))  # 将字符串的长度打包
        conn.send(head_info_len)  # 发送head_info的长度  # server: send3
        conn.send(head_info.encode('utf-8'))  # server: send4

    @staticmethod
    def updataInformationToDatabase(occupation, telephone, email, headshot, name):
        databasePersonalInfo.update_table_personal_info(occupation, telephone, email, headshot, name)

    def run(self):
        self.s.bind(self.ADDR)
        self.s.listen(10)
        print('Judge server starts running...')
        while True:
            (conn, addr) = self.s.accept()
            t = threading.Thread(target=self.judge, args=(conn, addr))
            t.start()


# This class is used to chatting and sending emoji
class ChatServer(threading.Thread):
    global users, que, lock

    def __init__(self, port):
        threading.Thread.__init__(self)
        self.ADDR = (IP, port)
        os.chdir(sys.path[0])
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 用于接收所有客户端发送信息的函数
    def tcp_connect(self, conn, addr):
        # 连接后将用户信息添加到users列表
        user = conn.recv(buffSize)  # 接收用户名
        user = user.decode()

        for i in range(len(users)):
            if user == users[i][1]:
                print('User already exist')
                user = '' + user + '_2'

        users.append((conn, user, addr))
        print(' New connection:', addr, ':', user, end='\n')  # 打印用户名
        d = onlines()  # 有新连接则刷新客户端的在线用户显示
        self.recvFlash(addr, d, '', '', -1)
        try:
            while True:
                head_struct = conn.recv(4)  # 接收报头的长度, # client: recv3
                if not head_struct:
                    print('ERROR: Receive head_struct ')
                    exit(-1)
                head_len = struct.unpack('i', head_struct)[0]  # 解析出报头的字符串大小
                data = conn.recv(head_len)  # 接收长度为head_len的报头内容的信息 (包含文件大小,文件名的内容)  # client: recv4
                head_dir = json.loads(data.decode('utf-8'))
                protocol = head_dir['protocol']
                if protocol == 1 or protocol == 2:
                    message = head_dir['message']
                    sender = head_dir['sender']
                    receiver = head_dir['receiver']
                    if sender != receiver:
                        self.recvFlash(addr, message, sender, receiver, protocol)
                # if protocol == 3:
                #     new = onlines()
                #     self.recvFlash(addr, new, '', '', -1)

        except:
            print(user + ' Connection lose')
            self.delUsers(conn, addr)  # 将断开用户移出users
            conn.close()

    # 判断断开用户在users中是第几位并移出列表, 刷新客户端的在线用户显示
    def delUsers(self, conn, addr):
        a = 0
        for i in users:
            if i[0] == conn:
                users.pop(a)
                print(' Remaining online users: ', end='')  # 打印剩余在线用户(conn)
                d = onlines()
                self.recvFlash(addr, d, '', '', -1)
                print(d)
                break
            a += 1

    # 将接收到的信息(ip,端口以及发送的信息)存入que队列
    def recvFlash(self, addr, data, sender, receiver, protocol):
        lock.acquire()
        try:
            que.put((addr, data, sender, receiver, protocol))
        finally:
            lock.release()

    # 将队列que中的消息发送给所有连接到的用户
    def sendData(self):
        while True:
            time.sleep(0.01)
            if not que.empty():
                message = que.get()  # 取出队列第一个元素
                if isinstance(message[1], str): # is a message(string)
                    for i in range(len(users)):         # users = []   用于存放在线用户的信息  [conn, user, addr]
                        if users[i][1] == message[3]:
                            pid = -1
                            if message[4] == 1:
                                pid = 1  # Protocol 1 is used for server to send message(string) to client in PORT 50007
                            elif message[4] == 2:
                                pid = 2  # Protocol 2 is used for server to send message(emoji) to client in PORT 50007
                            head = {
                                'protocol': pid,
                                'message': message[1],
                                'sender': message[2],
                                'receiver': message[3],
                            }
                            head_info = json.dumps(head)  # 将字典转换成字符串
                            head_info_len = struct.pack('i', len(head_info))  # 将字符串的长度打包
                            users[i][0].send(head_info_len)  # 发送head_info的长度  # server: send3
                            users[i][0].send(head_info.encode('utf-8'))  # server: send4

                if isinstance(message[1], list):  # 同上
                    # 如果是list则打包后直接发送
                    pid = 3     # Protocol 3 is used for server to send online stuff information to client in PORT 50007
                    print("mess: ", message[1])
                    headshotlist = databasePersonalInfo.find_headshot_by_name(message[1])
                    head = {
                        'protocol': pid,
                        'online': message[1],
                        'headshot': headshotlist,
                    }
                    head_info = json.dumps(head)  # 将字典转换成字符串
                    head_info_len = struct.pack('i', len(head_info))  # 将字符串的长度打包
                    for i in range(len(users)):
                        try:
                            users[i][0].send(head_info_len)  # 发送head_info的长度  # server: send3
                            users[i][0].send(head_info.encode('utf-8'))  # server: send4
                        except:
                            pass

    def run(self):
        self.s.bind(self.ADDR)
        self.s.listen(5)
        print('Chat server starts running...')
        q = threading.Thread(target=self.sendData)
        q.start()

        while True:
            (conn, addr) = self.s.accept()
            t = threading.Thread(target=self.tcp_connect, args=(conn, addr))
            t.start()


################################################################


class FileServer(threading.Thread):
    def __init__(self, port):
        threading.Thread.__init__(self)
        self.ADDR = (IP, port)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.first = './resources'
        os.chdir(self.first)  # 把first设为当前工作路径

    def tcp_connect(self, conn, addr):
        print(' Connected by: ', addr)

        while True:
            data = conn.recv(1024)
            data = data.decode()
            if data == 'quit':
                print('Disconnected from {0}'.format(addr))
                break
            order = data.split(' ')[0]  # 获取动作
            self.recv_func(order, data, conn)

        conn.close()

    # 传输当前目录列表
    def sendList(self, conn):
        listdir = os.listdir(os.getcwd())
        listdir = json.dumps(listdir)
        conn.sendall(listdir.encode())

    # 发送文件函数
    def sendFile(self, message, conn):
        name = message.split()[1]  # 获取第二个参数(文件名)
        fileName = r'./' + name
        fileSize=os.path.getsize(fileName)
        dirc={
            'filename': fileName,
            'filesize_bytes': fileSize,
        }
        head_info = json.dumps(dirc)
        head_info_len = struct.pack('i', len(head_info))
        conn.send(head_info_len)
        conn.send(head_info.encode('utf-8'))
        with open(fileName, 'rb') as f:
            a = f.read()
            conn.sendall(a)
        print('Successfully send!')

        f.close()
        #time.sleep(0.1)  # 延时确保文件发送完整
        # conn.send('EOF'.encode())

    # 保存上传的文件到当前工作目录
    def recvFile(self, message, conn):
        name = message.split(" ", 1)[1]  # 获取文件名
        fileName = r'./' + name
        head_struct = conn.recv(4)
        if head_struct:
            print('已连接客户,等待接收数据')
        head_len = struct.unpack('i', head_struct)[0]
        headdata = conn.recv(head_len)
        head_dir = json.loads(headdata.decode('utf-8'))
        filesize_b = head_dir['filesize_bytes']
        filename = head_dir['filename']
        recv_len = 0
        old = time.time()
        f = open(fileName, 'wb')
        buffsize = 4096
        while recv_len < filesize_b:
            if filesize_b - recv_len > buffsize:
                recv_mesg = conn.recv(buffsize)
                f.write(recv_mesg)
                recv_len += len(recv_mesg)
            else:
                recv_mesg = conn.recv(filesize_b - recv_len)
                recv_len += len(recv_mesg)
                f.write(recv_mesg)

        now = time.time()
        stamp = int(now - old)
        print('总共用时%ds' % stamp)
        conn.send('EOF'.encode())
        f.close()
        # with open(fileName, 'wb') as f:
        #     while True:
        #         data = conn.recv(1024)
        #         if data == 'EOF'.encode():
        #             break
        #         f.write(data)
        print("Successfully recv")

    # 切换工作目录
    def cd(self, message, conn):
        print("!ERROR: ", message, conn)
        message = message.split(" ", 1)[1]  # 截取目录名
        # 如果是新连接或者下载上传文件后的发送则 不切换 只将当前工作目录发送过去
        if message != 'same':
            f = r'./' + message
            os.chdir(f)
        # path = ''

        path = os.getcwd().split('\\')  # 当前工作目录
        # os.path.dirname()
        for i in range(len(path)):
            if path[i] == 'resources':
                break

        pat = ''
        for j in range(i, len(path)):
            pat = pat + path[j] + ' '
        pat = '\\'.join(pat.split())
        # 如果切换目录超出范围则退回切换前目录
        if 'resources' not in path:
            f = r'./resources'
            os.chdir(f)
            pat = 'resources'
        conn.send(pat.encode())

    # 判断输入的命令并执行对应的函数
    def recv_func(self, order, message, conn):

        if order == 'get':
            return self.sendFile(message, conn)

        elif order == 'put':
            return self.recvFile(message, conn)

        elif order == 'dir':
            return self.sendList(conn)

        elif order == 'cd':
            return self.cd(message, conn)

    def run(self):
        print('File server starts running...')
        self.s.bind(self.ADDR)
        self.s.listen(3)
        while True:
            conn, addr = self.s.accept()
            t = threading.Thread(target=self.tcp_connect, args=(conn, addr))
            t.start()


#############################################################################


class PictureServer(threading.Thread):

    def __init__(self, port):
        threading.Thread.__init__(self)
        self.ADDR = (IP, port)
        self.PictureServerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        os.chdir(sys.path[0])
        self.folder = '.\\Server_image_cache\\'  # 图片的保存文件夹

    def tcp_connect(self, conn, addr):

        head_struct = conn.recv(4)  # 接收报头的长度, # client: recv3
        if not head_struct:
            print('ERROR: Receive head_struct ')
            exit(-1)
        head_len = struct.unpack('i', head_struct)[0]  # 解析出报头的字符串大小
        data = conn.recv(head_len)  # 接收长度为head_len的报头内容的信息 (包含文件大小,文件名的内容)  # client: recv4
        head_dir = json.loads(data.decode('utf-8'))

        pid = head_dir['protocol']
        sender = head_dir['sender']
        receiver = head_dir['receiver']
        picSize = head_dir['picSize']
        picName = head_dir['picName']

        self.recvPic(conn, sender, receiver, picSize, picName)
        receiverConn = ''
        for i in range(len(users)):            # user [conn, user, addr]
            if receiver == users[i][1]:
                receiverConn = users[i][0]
                break
        if sender != receiver:
            self.sendPic(receiverConn, sender, receiver, picSize, picName)
        picNameInServer = './cache/' + sender + "_send_to_" + receiver + "_a_" + picName
        os.remove(picNameInServer)
        conn.close()

    @staticmethod
    # 保存上传的文件到当前工作目录
    def recvPic(conn, sender, receiver, picSize, picName):
        #  recv picture
        picName = "./cache/" + sender + "_send_to_" + receiver + "_a_" + picName
        recv_len = 0
        recv_mesg = b''
        old = time.time()
        f = open(picName, 'wb')
        # while True:
        #     recv_mesg = conn.recv(buffSize)
        #     if len(recv_mesg) == 0:
        #         print("recv all!")
        #         break
        #     f.write(recv_mesg)
        # time.sleep(0.01)

        while recv_len < picSize:
            if picSize - recv_len > buffSize:
                recv_mesg = conn.recv(buffSize)
                f.write(recv_mesg)
                recv_len += len(recv_mesg)
            else:
                recv_mesg = conn.recv(picSize - recv_len)
                recv_len += len(recv_mesg)
                f.write(recv_mesg)

        time.sleep(0.01)
        f.close()
        now = time.time()
        stamp = int(now - old)
        print("Successfully receive picture! Spend time: %ds" % stamp)
        conn.close()

    @staticmethod
    # 发送文件函数
    def sendPic(receiverConn, sender, receiver, picSize, picName):
        pid = 4  # Protocol 4 is used for server send picture to client in PORT 50007
        head = {
            'protocol': pid,
            'sender': sender,
            'receiver': receiver,
            'picName': picName,
            'picSize': picSize,
        }
        head_info = json.dumps(head)  # 将字典转换成字符串
        head_info_len = struct.pack('i', len(head_info))  # 将字符串的长度打包
        receiverConn.send(head_info_len)  # 发送head_info的长度
        receiverConn.send(head_info.encode('utf-8'))
        picNameInServer = './cache/' + sender + "_send_to_" + receiver + "_a_" + picName
        with open(picNameInServer, 'rb') as p:
            picture = p.read()
            receiverConn.sendall(picture)
        p.close()


    def run(self):
        self.PictureServerSock.bind(self.ADDR)
        self.PictureServerSock.listen(5)
        print('Picture server starts running...')
        while True:
            conn, addr = self.PictureServerSock.accept()
            t = threading.Thread(target=self.tcp_connect, args=(conn, addr))
            t.start()


####################################################################################


if __name__ == '__main__':
    cserver = ChatServer(PORT)
    fserver = FileServer(PORT + 1)
    pserver = PictureServer(PORT + 2)
    jserver = JudgeServer(PORT + 3)
    cserver.start()
    fserver.start()
    pserver.start()
    jserver.start()
    while True:
        time.sleep(1)
        if not jserver.is_alive():
            print("judge connection lost...")
            sys.exit(0)
        if not cserver.is_alive():
            print("Chat connection lost...")
            sys.exit(0)
        if not fserver.is_alive():
            print("File connection lost...")
            sys.exit(0)
        if not pserver.is_alive():
            print("Picture connection lost...")
            sys.exit(0)


