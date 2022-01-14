# -*- coding=utf-8 -*-

import sqlite3
import time


class Database:
    """为登录界面所提供数据库操作的类"""

    def __init__(self, db):
        self._database = db
        self.create_table()

    @property
    def database(self):
        return self._database

    @database.setter
    def database(self, db):
        self._database = db

    def create_table(self):
        """创建一个数据库"""
        connect = sqlite3.connect(self._database)
        cursor = connect.cursor()
        sql = "CREATE TABLE IF NOT EXISTS data(username TEXT, password TEXT, created_time TEXT)"
        cursor.execute(sql)
        if not self.is_has('admin'):  # 管理员的用户名一定为 admin ！
            created_time = self.get_time()
            default = "INSERT INTO data(username, password, created_time) VALUES('admin', 'admin123', ?)"  # 设置初始的账号密码
            cursor.execute(default, (created_time,))
        connect.commit()
        connect.close()

    def insert_table(self, username, password):
        """向数据库中插入元素"""
        connect = sqlite3.connect(self._database)
        cursor = connect.cursor()
        if self.is_has(username):
            # print("Already exits username {}".format(username))  # 测试使用
            return True  # 已经有该元素的时候返回一个 True 提供外界接口
        else:
            created_time = self.get_time()
            sql = 'INSERT INTO data (username, password, created_time) VALUES(?,?,?)'
            cursor.execute(sql, (username, password, created_time))
            connect.commit()
        connect.close()

    def read_table(self):
        """读取数据库中的所有元素"""
        connect = sqlite3.connect(self._database)
        cursor = connect.cursor()
        sql = 'SELECT * FROM data ORDER BY username'
        result = cursor.execute(sql)
        data = result.fetchall()
        connect.commit()
        connect.close()
        return data

    def update_table(self, username, password):
        """更新数据库中的数据"""
        connect = sqlite3.connect(self._database)
        cursor = connect.cursor()
        sql = 'UPDATE data SET password =? WHERE username=? '
        cursor.execute(sql, (password, username))
        connect.commit()
        connect.close()

    def find_password_by_username(self, username):
        """根据用户名来查找用户的密码"""
        connect = sqlite3.connect(self._database)
        cursor = connect.cursor()
        sql = 'SELECT password FROM data WHERE username=?'
        result = cursor.execute(sql, (username,))
        connect.commit()
        found_data = result.fetchall()
        connect.close()
        return found_data

    def delete_table_by_username(self, username):
        """通过用户名称删除数据"""
        connect = sqlite3.connect(self._database)
        cursor = connect.cursor()
        sql = 'DELETE FROM data WHERE  username=?'
        cursor.execute(sql, (username,))
        connect.commit()
        connect.close()

    def is_has(self, username):
        """判断数据库中是否包含用户名信息"""
        connect = sqlite3.connect(self._database)
        cursor = connect.cursor()
        sql = 'SELECT * FROM data WHERE username=?'
        result = cursor.execute(sql, (username,))
        connect.commit()
        all_data = result.fetchall()
        connect.close()
        if all_data:
            return True
        else:
            return False

    def clear(self):
        """清空所有的数据"""
        connect = sqlite3.connect(self._database)
        cursor = connect.cursor()
        sql = "DELETE FROM data"
        cursor.execute(sql)
        connect.commit()
        connect.close()

    @staticmethod
    def get_time():
        date = time.localtime()
        created_time = "{}-{}-{}-{}:{}:{}".format(date.tm_year, date.tm_mon,
                                                  date.tm_mday,
                                                  date.tm_hour, date.tm_min,
                                                  date.tm_sec)
        return created_time


class DatabasePersonalInfo:
    def __init__(self, db):
        self._database = db
        self.create_table_personal_info()

    def create_table_personal_info(self):
        connect = sqlite3.connect(self._database)
        cursor = connect.cursor()
        sql = "CREATE TABLE IF NOT EXISTS personal_info(sid INTEGER, name TEXT, occupation TEXT, \
                        telephone TEXT, email TEXT, headshot TEXT)"
        cursor.execute(sql)
        if not self.is_has_personal_info('admin'):  # 管理员的用户名一定为 admin ！
            # created_time = self.get_time()
            sql = 'INSERT INTO personal_info (sid, name, occupation, telephone, email, headshot) VALUES(?,?,?,?,?,?)'
            cursor.execute(sql, (1, 'admin', None, None, None, None))
        connect.commit()
        connect.close()

    def find_personal_info_by_name(self, name):
        connect = sqlite3.connect(self._database)
        cursor = connect.cursor()
        sql = 'SELECT * FROM personal_info WHERE name=?'
        result = cursor.execute(sql, (name,))
        connect.commit()
        found_data = result.fetchall()
        connect.close()
        return found_data

    def find_headshot_by_name(self, namelist):
        piclist=[]
        for name in namelist:
            connect = sqlite3.connect(self._database)
            cursor = connect.cursor()
            sql = 'SELECT headshot FROM personal_info WHERE name=?'
            result = cursor.execute(sql, (name,))
            connect.commit()
            pic = result.fetchone()
            # print("pic[0]: ", pic[0])
            try:
                pic = pic[0]
            except:
                pic = "headshot/default.jpeg"

            piclist.append(pic)
            connect.close()
        return piclist

    def insert_table_personal_info(self, name, occupation, telephone, email, headshot):
        """向数据库中插入元素"""
        sid = self.next_id(self._database)
        connect = sqlite3.connect(self._database)
        cursor = connect.cursor()
        if self.is_has_personal_info(name):
            # print("Already exits username {}".format(name))  # 测试使用
            return True  # 已经有该元素的时候返回一个 True 提供外界接口
        else:
            # created_time = self.get_time()
            sql = 'INSERT INTO personal_info (sid, name, occupation, telephone, email, headshot) VALUES(?,?,?,?,?,?)'
            cursor.execute(sql, (sid, name, occupation, telephone, email, headshot))
        connect.commit()
        connect.close()

    def update_table_personal_info(self, occupation, telephone, email, headshot, name):
        """更新数据库中的数据"""
        connect = sqlite3.connect(self._database)
        cursor = connect.cursor()
        sql = 'UPDATE personal_info SET  occupation =?, telephone =?, email =?, headshot =? WHERE name=? '
        cursor.execute(sql, (occupation, telephone, email, headshot, name))
        connect.commit()
        connect.close()

    def is_has_personal_info(self, name):
        """判断数据库中是否包含用户名信息"""
        connect = sqlite3.connect(self._database)
        cursor = connect.cursor()
        sql = 'SELECT * FROM personal_info WHERE name=?'
        result = cursor.execute(sql, (name,))
        connect.commit()
        all_data = result.fetchall()
        connect.close()
        if all_data:
            return True
        else:
            return False

    @staticmethod
    def next_id(database):
        connect = sqlite3.connect(database)
        cursor = connect.cursor()
        sql = 'SELECT MAX(sid) FROM personal_info'
        result = cursor.execute(sql)
        data = result.fetchall()
        if not data[0][0]:
            nextid = 1
        else:
            nextid = data[0][0] + 1
        connect.commit()
        connect.close()
        return nextid

    def read_table(self):
        """读取数据库中的所有元素"""
        connect = sqlite3.connect(self._database)
        cursor = connect.cursor()
        sql = 'SELECT * FROM personal_info ORDER BY name'
        result = cursor.execute(sql)
        data = result.fetchall()
        connect.commit()
        connect.close()
        return data


if __name__ == '__main__':
    data = Database('./data.db')
    dataUserInfo = DatabasePersonalInfo('./personal_info.db')
    # data.insert_table('admin', 'password')

    data_ = data.read_table()
    data_UserInfo = dataUserInfo.read_table()

    print("data.db: \n", data_)
    print("\n\npersonal_info.db: \n", data_UserInfo)
