import sqlite3


class Database:

    def __init__(self, db):
        self._database = db
        self.delete_table_by_username("Amy")

    def delete_table_by_username(self, username):
        """通过用户名称删除数据"""
        connect = sqlite3.connect(self._database)
        cursor = connect.cursor()
        sql = 'DELETE FROM data WHERE username=?'
        cursor.execute(sql, (username,))
        connect.commit()
        connect.close()


class DatabasePersonalInfo:

    def __init__(self, db):
        self._database = db
        self.delete_table_by_username("Amy")

    def delete_table_by_username(self, username):
        """通过用户名称删除数据"""
        connect = sqlite3.connect(self._database)
        cursor = connect.cursor()
        sql = 'DELETE FROM personal_info WHERE name=?'
        cursor.execute(sql, (username,))
        connect.commit()
        connect.close()


if __name__ == '__main__':
    dataUserInfo1 = DatabasePersonalInfo('./personal_info.db')
    dataUserInfo2 = Database('./data.db')