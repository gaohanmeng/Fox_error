# coding: UTF-8
__author__ = 'H7112589'

import os
# import time
import logging
from datetime import datetime
import pg8000
import hashlib
import math
# import middleware
# import xlrd
from flask import Flask, request, render_template, url_for, redirect, session
from flask_login import login_required, LoginManager, UserMixin, login_user

app = Flask(__name__)
# app.wsgi_app = middleware.PrefixMiddleware(app.wsgi_app, prefix='/F_errordb')
static_dir = os.path.join(os.path.dirname(__file__), 'static')
logging.basicConfig(level=logging.DEBUG, filename='flask.log')


class Debug(object):
    # DEBUG = False
    DEBUG = True
    SECRET_KEY = 'xxxxxxxxxxxxxxxxxxx'


app.config.from_object(Debug)


class UploadDb(object):
    """from excel get Ali_db data"""
    pass
    # i, j, x = 0, 0, 0
    # error_data = xlrd.open_workbook('C:\Users\H7112589\Desktop\CGECX0270-FC07Error_Code.xlsx')
    # table = error_data.sheet_by_index(i)
    #
    # conn = pg8000.connect(user='production_user', password='Foxconn123', database='test_db')
    #
    # cursor = conn.cursor()
    # cursor.execute('rollback;')
    # while True:
    #     try:
    #         dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #         row_type = table.cell(i + 1, 1)
    #         row_code = table.cell(j + 1, 3)
    #         row_detail = table.cell(x + 1, 4)
    #         md5 = hashlib.md5()
    #         desc = row_type.value
    #         md5.update(desc.strip())
    #         digest = md5.hexdigest()
    #         cursor.execute("INSERT INTO public.error_code_mapping (desc_md5, error_code, key_word, "
    #                        "fail_detail, code_time, code_update_time) VALUES (%s, %s, %s, %s, %s, %s)"
    #                        % ("'"+digest + "'", "'"+row_code.value+"'", "'"+row_type.value + "'",
    #                           "'"+row_detail.value+"'", "'"+dt+"'", "'"+dt+"'"))
    #         i += 1
    #         j += 1
    #         x += 1
    #         time.sleep(2)
    #     except IndexError:
    #         break
    #
    # conn.commit()


class QueryDb(object):
    conn = pg8000.connect(user='production_user', password='Foxconn123', database='test_db')
    cursor = conn.cursor()
    # cursor.execute('rollback;')
    # cursor.execute("SELECT desc_md5, error_code, key_word FROM public.error_code_mapping;")
    # key_list = cursor.fetchall()


class User(UserMixin):
    pass


def query_user(user_name):
    conn = pg8000.connect(user='production_user', password='Foxconn123', database='test_db')
    cursor = conn.cursor()
    cursor.execute("select * from public.error_code_users")
    users = cursor.fetchall()
    for user in users:
        if user_name in user:
            return user


app.secret_key = '23212123'
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'login_index'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    if query_user(user_id) is not None:
        user = User()
        user.name = user_id
        return user


@app.route('/')
def login_index():
    return render_template('login.html')


@app.route('/login/', methods=['POST', ])
def login():
    """登录验证"""
    user_name = request.form.get('user')
    user_password = request.form.get('password')
    if request.method == 'POST':
        user = query_user(user_name)
        if user is not None:
            if user_name in user:
                if user_password in user:
                    curr_user = User()
                    curr_user.id = user_name
                    curr_user.password = user_password
                    # login_user(curr_user, remember=True)
                    login_user(curr_user)
                    # print(load_user, session['_user_id'])
                    app.logger.info(u'账号:%s 密码:%s 登录时间:%s'
                                    % (curr_user.id, curr_user.password,
                                       str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))))
                    return redirect(url_for('index1'))
                else:
                    app.logger.info(u'账号%s 密码:%s 登录时间:%s'
                                    % (user_name, user_password, str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))))
                    return render_template('login_error.html')
            else:
                app.logger.info(u'账号%s 密码:%s 登录时间:%s'
                                % (user_name, user_password, str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))))
                return render_template('login_error.html')
        app.logger.info(u'账号%s 密码:%s 登录时间:%s'
                        % (user_name, user_password, str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))))
        return render_template('login_error.html')


@app.route('/ali', methods=['GET', 'POST'])
@login_required
def index1():
    conn = QueryDb.conn
    cursor = conn.cursor()
    cursor.execute("SELECT error_code, key_word, fail_detail FROM public.error_code_mapping "
                   "order by code_time desc limit 1")
    last_insert_key = cursor.fetchall()
    cursor.execute("SELECT error_code, key_word, fail_detail FROM public.error_code_mapping "
                   "order by code_update_time desc limit 1")
    last_update_key = cursor.fetchall()
    return render_template('alidb.html', insert_results=last_insert_key, update_results=last_update_key)


@app.route('/alichdb/')
@login_required
def index2():
    return render_template('changedb.html')


@app.route('/aliseadb/')
@login_required
def index3():
    return render_template('searchdb.html')


@app.route('/alidata/')
@login_required
def index4():
    keys = []
    if request.method == 'GET':
        conn = pg8000.connect(user='production_user', password='Foxconn123', database='test_db')
        cursor = conn.cursor()
        cursor.execute('rollback;')
        cursor.execute("SELECT error_code, key_word, fail_detail FROM public.error_code_mapping "
                       "order by error_code limit 10;")
        key_list = cursor.fetchall()
        for i in range(0, len(key_list)):
            db = (key_list[i][0], key_list[i][1], key_list[i][2])
            keys.append(db)
            i += 1
        # cursor.execute("SELECT desc_md5, error_code, key_word, fail_detail FROM public.error_code_mapping;")
        cursor.execute("SELECT count(*) FROM public.error_code_mapping;")
        key_li = cursor.fetchall()[0]
        # print(key_li, '*'*20)
        pages = int(math.ceil(key_li[0] / float(10)))
        # prv_page = 0
        return render_template('alialldata.html', keys=keys, pages=pages)


@app.route('/alideledb/')
@login_required
def index5():
    return render_template('deletedb.html')


@app.route('/alikeydb/<int:page_num>', methods=['GET', ])
@login_required
def get_keys_db(page_num):
    keys = []
    if request.method == 'GET':
        conn = QueryDb.conn
        cursor = conn.cursor()
        cursor.execute('rollback;')
        cursor.execute("SELECT error_code, key_word, fail_detail FROM public.error_code_mapping "
                       "order by error_code limit 10 offset %d;" % ((page_num - 1) * 10))
        key_list = cursor.fetchall()
        for i in range(0, len(key_list)):
            db = (key_list[i][0], key_list[i][1], key_list[i][2])
            keys.append(db)
            i += 1
        # cursor.execute("SELECT desc_md5, error_code, key_word, fail_detail FROM public.error_code_mapping;")
        cursor.execute("SELECT count(*) FROM public.error_code_mapping;")
        key_li = cursor.fetchall()[0]
        pages = int(math.ceil(key_li[0] / float(10)))
        return render_template('alialldata.html', keys=keys, pages=pages)


@app.route('/aliadddb/', methods=['POST', ])
@login_required
def add_keys_db():
    dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = QueryDb.conn
    cursor = conn.cursor()
    key_word = request.form.get('key2_word')
    # key_word = request.args.get('key2_word')
    error_code = request.form.get('error2_code')
    fail_detail = request.form.get('fail2_detail')
    get_new_data = []

    if request.method == 'POST':
        if key_word.strip() == '' or error_code.strip() == '' or fail_detail == '':
            return render_template('error.html')
        elif key_word and error_code and fail_detail:
            md5 = hashlib.md5()
            md5.update(key_word.strip())
            digest = md5.hexdigest()
            get_new_data.append(digest)
            get_new_data.append(error_code)
            get_new_data.append(key_word)
            get_new_data.append(fail_detail)
            cursor.execute("SELECT desc_md5, error_code, key_word, fail_detail FROM public.error_code_mapping")
            keys = cursor.fetchall()
            if get_new_data in keys:
                return render_template('error.html')
            elif [get_new_data[2] for get_new_data in keys if key_word in get_new_data]:
                return render_template('error.html')
            elif [get_new_data[1] for get_new_data in keys if error_code in get_new_data]:
                return render_template('error.html')
            elif [get_new_data[0] for get_new_data in keys if digest in get_new_data]:
                return render_template('error.html')
            elif [get_new_data[3] for get_new_data in keys if fail_detail in get_new_data]:
                return render_template('error.html')
            else:
                cursor.execute("INSERT INTO public.error_code_mapping (desc_md5, error_code, key_word, fail_detail,"
                               " code_time, code_update_time) VALUES (%s, %s, %s, %s, %s, %s);\
                            " % ("'" + digest + "'", "'" + error_code.strip() + "'", "'" + key_word.strip() + "'",
                                 "'" + fail_detail.strip() + "'", "'" + dt + "'", "'" + dt + "'"))
                conn.commit()
                cursor.execute("SELECT error_code, key_word, fail_detail FROM public.error_code_mapping order by"
                               " code_time desc limit 1")
                last_insert_key = cursor.fetchall()
                cursor.execute("SELECT error_code, key_word, fail_detail FROM public.error_code_mapping "
                               "order by code_update_time desc limit 1")
                last_update_key = cursor.fetchall()
                app.logger.info(u'账号:%s 登录时间:%s 添加数据:%s'
                                % (session['_user_id'], dt, last_insert_key))
                return render_template('alidb.html', insert_results=last_insert_key, update_results=last_update_key)
        else:
            return render_template('error.html')


@app.route('/alideldb/', methods=['POST', ])
@login_required
def del_keys_db():
    conn = QueryDb.conn
    cursor = conn.cursor()
    delete_keys = request.form.get('delete_words')
    delete_codes = request.form.get('delete_codes')
    delete_detail = request.form.get('delete_details')

    if request.method == 'POST':
        if delete_keys.strip() == '' and delete_codes.strip() == '' and delete_detail.strip() == '':
            return render_template('error2.html')
        elif delete_keys:
            cursor.execute("SELECT error_code, key_word, fail_detail FROM public.error_code_mapping "
                           "where key_word=%s" % ("'" + delete_keys + "'"))
            delete_key = cursor.fetchall()
            if len(delete_key) == 0:
                return render_template('error2.html')
            cursor.execute("DELETE FROM error_code_mapping where key_word=%s" % ("'" + delete_keys + "'"))
            conn.commit()
            app.logger.info(u'账号:%s 登录时间:%s 删除数据:%s'
                            % (session['_user_id'], datetime.now().strftime('%Y:%m:%d %H:%M:%S'), delete_key))
            return render_template('deletedb.html', delete_results=delete_key)
        elif delete_codes:
            cursor.execute("SELECT error_code, key_word, fail_detail FROM public.error_code_mapping "
                           "where error_code=%s" % ("'" + delete_codes + "'"))
            delete_code = cursor.fetchall()
            if len(delete_code) == 0:
                return render_template('error2.html')
            cursor.execute("DELETE FROM error_code_mapping where error_code=%s" % ("'" + delete_codes + "'"))
            conn.commit()
            app.logger.info(u'账号:%s 登录时间:%s 删除数据:%s'
                            % (session['_user_id'], datetime.now().strftime('%Y:%m:%d %H:%M:%S'), delete_code))
            return render_template('deletedb.html', delete_results=delete_code)
        elif delete_detail:
            cursor.execute("SELECT error_code, key_word, fail_detail FROM public.error_code_mapping "
                           "where fail_detail=%s" % ("'" + delete_detail + "'"))
            delete_details = cursor.fetchall()
            if len(delete_details) == 0:
                return render_template('error2.html')
            cursor.execute("DELETE FROM error_code_mapping where fail_detail=%s" % ("'" + delete_detail + "'"))
            conn.commit()
            app.logger.info(u'账号:%s 登录时间:%s 删除数据:%s'
                            % (session['_user_id'], datetime.now().strftime('%Y:%m:%d %H:%M:%S'), delete_detail))
            return render_template('deletedb.html', delete_results=delete_details)


@app.route('/alichadb/', methods=['POST', 'GET'])
@login_required
def change_db():
    dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if request.method == 'POST':
        if request.form.get('row_keys'):
            row_word = request.form.get('row_keys')
            check_word = request.form.get('confirm_keys')
            change_word = request.form.get('change_keys')
            get_row_key = []
            conn = QueryDb.conn
            cursor = conn.cursor()
            cursor.execute("rollback;")
            if row_word is None:
                return render_template('error.html')
            elif row_word.strip() == '':
                return render_template('error.html')
            else:
                if check_word is None:
                    return render_template('error.html')
                elif row_word.strip() == '':
                    return render_template('error.html')
                elif check_word.strip() != row_word.strip():
                    return render_template('error.html')
                else:
                    try:
                        cursor.execute("SELECT desc_md5, error_code, fail_detail FROM public.error_code_mapping "
                                       "where key_word=%s;" % ("'" + row_word + "'"))
                        get_key = cursor.fetchone()
                        get_row_key.append(get_key[0])  # [1] desc_md5
                        get_row_key.append(get_key[1])  # [0] error_code
                        get_row_key.append(row_word)  # key_word
                        get_row_key.append(get_key[2])
                        cursor.execute("SELECT desc_md5, error_code, key_word, fail_detail FROM"
                                       " public.error_code_mapping;")
                        key_li = cursor.fetchall()
                        if get_row_key in key_li:
                            if change_word == get_row_key[3] or change_word == get_row_key[2] \
                                    or change_word == get_row_key[1] or change_word == get_row_key[0]:
                                return render_template('error.html')
                            elif [change_word for get_row_key in key_li if change_word in get_row_key]:
                                return render_template('error.html')
                            else:
                                cursor.execute("update public.error_code_mapping set key_word=%s, code_update_time=%s "
                                               "where error_code=%s;"
                                               % (
                                               "'" + change_word.strip() + "'", "'" + dt + "'", "'" + get_key[1] + "'"))
                                conn.commit()
                                cursor.execute("SELECT error_code, key_word, fail_detail FROM public.error_code_mapping"
                                               " where error_code=%s" % ("'" + get_key[1] + "'"))  # get_row_key[1]
                                update_keys = cursor.fetchall()
                                app.logger.info(u'账号:%s 登录时间:%s 修改数据:%s' %
                                                (session['_user_id'], dt, update_keys))
                                return render_template('changedb.html', update_keys=update_keys)
                        else:
                            return render_template('error.html')
                    except Exception as e:
                        # print e.message
                        return render_template('error.html')

        elif request.form.get('row_codes'):
            get_row_code = []
            conn = QueryDb.conn
            cursor = conn.cursor()
            cursor.execute("rollback")
            row_code = request.form.get('row_codes')
            check_code = request.form.get('confirm_codes')
            change_code = request.form.get('change_codes')
            if row_code is None:
                return render_template('error.html')
            elif row_code.strip() == '':
                return render_template('error.html')
            else:
                if check_code is None:
                    return render_template('error.html')
                elif row_code.strip() == '':
                    return render_template('error.html')
                elif check_code.strip() != row_code.strip():
                    return render_template('error.html')
                else:
                    try:
                        cursor.execute("SELECT desc_md5, key_word, fail_detail FROM public.error_code_mapping"
                                       " where error_code=%s;" % ("'" + row_code + "'"))
                        get_code = cursor.fetchall()[0]
                        get_row_code.append(get_code[0])  # get_code[1] desc_md5
                        get_row_code.append(row_code)
                        get_row_code.append(get_code[1])  # get_code[0] key_word
                        get_row_code.append(get_code[2])  # fail_detail
                        cursor.execute("SELECT desc_md5, error_code, key_word, fail_detail "
                                       "FROM public.error_code_mapping;")
                        code_li = cursor.fetchall()
                        if get_row_code in code_li:
                            if change_code == get_row_code[1] or change_code == get_row_code[2] \
                                    or change_code == get_row_code[3]:
                                return render_template('error.html')
                            elif [change_code for get_row_code in code_li if change_code in get_row_code]:
                                return render_template('error.html')
                            else:
                                cursor.execute("update public.error_code_mapping set error_code=%s, code_update_time=%s"
                                               " where key_word=%s;"
                                               % ("'" + change_code.strip() + "'", "'" + dt + "'",
                                                  "'" + get_code[1] + "'"))
                                conn.commit()
                                cursor.execute("SELECT error_code, key_word, fail_detail FROM public.error_code_mapping"
                                               " where key_word=%s;" % ("'" + get_code[1] + "'"))  # get_row_code[2]
                                update_keys = cursor.fetchall()
                                app.logger.info(u'账号:%s 登录时间:%s 修改数据:%s'
                                                % (session['_user_id'], dt, update_keys))
                                return render_template('changedb.html', update_keys=update_keys)
                        else:
                            return render_template('error.html')
                    except Exception as e:
                        # print e.message
                        return render_template('error.html')

        elif request.form.get('row_detail'):
            get_row_detail = []
            conn = QueryDb.conn
            cursor = conn.cursor()
            row_detail = request.form.get('row_detail')
            check_detail = request.form.get('confirm_detail')
            change_detail = request.form.get('new_detail')
            if row_detail is None:
                return render_template('error.html')
            elif row_detail.strip() == '':
                return render_template('error.html')
            else:
                if check_detail is None:
                    return render_template('error.html')
                elif check_detail.strip() == '':
                    return render_template('error.html')
                elif check_detail.strip() != row_detail.strip():
                    return render_template('error.html')
                else:
                    try:
                        cursor.execute("SELECT desc_md5, error_code, key_word, fail_detail FROM "
                                       "public.error_code_mapping where fail_detail=%s;" % ("'" + row_detail + "'"))
                        get_detail = cursor.fetchone()
                        get_row_detail.append(get_detail[0])  # desc_md5
                        get_row_detail.append(get_detail[1])  # error_code
                        get_row_detail.append(get_detail[2])  # key_word
                        get_row_detail.append(row_detail)
                        cursor.execute("SELECT desc_md5, error_code, key_word, fail_detail "
                                       "FROM public.error_code_mapping;")
                        detail_li = cursor.fetchall()
                        if get_row_detail in detail_li:
                            if change_detail == get_row_detail[3] or change_detail == get_row_detail[2] \
                                    or change_detail == get_row_detail[1]:
                                return render_template('error.html')
                            for get_row_detail in detail_li:
                                if change_detail in get_row_detail:
                                    return render_template('error.html')
                            else:
                                cursor.execute("UPDATE public.error_code_mapping set fail_detail=%s, "
                                               "code_update_time=%s where key_word=%s;"
                                               % ("'" + change_detail.strip() + "'", "'" + dt + "'",
                                                  "'" + get_detail[2] + "'"))
                                conn.commit()
                                cursor.execute("SELECT error_code, key_word, fail_detail FROM public.error_code_mapping"
                                               " where key_word=%s;" % ("'" + get_detail[2] + "'"))
                                update_keys = cursor.fetchall()
                                app.logger.info(u'账号:%s 登录时间:%s 修改数据:%s'
                                                % (session['_user_id'], dt, update_keys))
                                return render_template('changedb.html', update_keys=update_keys)
                        else:
                            return render_template('error.html')
                    except Exception as e:
                        # print e.message
                        return render_template('error.html')
        else:
            return render_template('error.html')


@app.route('/aliseardb/', methods=['POST'])
@login_required
def search_db():
    conn = QueryDb.conn
    cursor = conn.cursor()
    if request.method == 'POST':
        search_keys = request.form.get('search_keys')
        search_codes = request.form.get('search_codes')
        search_details = request.form.get('search_details')
        try:
            if search_keys.strip() == '':
                if search_codes.strip() == '':
                    if search_details.strip() == '':
                        return render_template('error.html')
                    else:
                        cursor.execute("SELECT error_code, key_word, fail_detail FROM public.error_code_mapping "
                                       "where fail_detail ilike %s" % ("'" + "%" + search_details.strip() + "%" + "'"))
                        key_result = cursor.fetchall()
                        if len(key_result) == 0:
                            return render_template('error2.html')
                        return render_template('searchdb.html', results=key_result)
                else:
                    cursor.execute("SELECT error_code, key_word, fail_detail FROM public.error_code_mapping"
                                   " where error_code ilike %s" % ("'" + "%" + search_codes.strip() + "%" + "'"))
                    key_result = cursor.fetchall()
                    if len(key_result) == 0:
                        return render_template('error2.html')
                    return render_template('searchdb.html', results=key_result)
            else:
                cursor.execute("SELECT error_code, key_word, fail_detail FROM public.error_code_mapping where "
                               "key_word ilike %s" % ("'" + "%" + search_keys.strip() + "%" + "'"))
                key_result = cursor.fetchall()
                if len(key_result) == 0:
                    return render_template('error2.html')
                return render_template('searchdb.html', results=key_result)
        except Exception as e:
            return render_template('error.html')


# app.run(host='0.0.0.0', port=5000)
if __name__ == '__main__':
    handler = logging.FileHandler(r'db.log')
    handler.setLevel = logging.DEBUG
    app.logger.addHandler(handler)
    app.run(host='10.67.71.132', port=35115)  # 8079
# UploadDb()
