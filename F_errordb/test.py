# coding: UTF-8
__author__ = 'H7112589'

import pg8000


def query_user(user_name):
    conn = pg8000.connect(user='production_user', password='Foxconn123', database='test_db')
    cursor = conn.cursor()
    cursor.execute("select * from public.error_code_users")
    users = cursor.fetchall()
    for user in users:
        if user_name in user:
            return user


users = query_user("h7112589")
print(users)
