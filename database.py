# -*- coding:utf-8 -*-
import os


def get_user_info(weixin_id):
    """
    :param weixin_id: string
    :return: a dict contains sno and password
    """
    file_name = 'user/{}.txt'.format(weixin_id)
    if not os.path.isfile(file_name):
        return None
    else:
        with open(file_name, mode='r') as f:
            data = f.read().strip('\n')

        sno, password = data[:data.find('#')], data[data.find('#') + 1:]
        return {
            'sno': sno,
            'password': password
        }


def create_user(weixin_id, sno, password):
    """
    :param weixin_id: string
    :param sno: string for student number
    :param password: string
    :return: void
    """
    file_name = 'user/{}.txt'.format(weixin_id)
    data = '{}#{}'.format(sno, password)

    with open(file_name, mode='w') as f:
        f.write(data)


def update_user(weixin_id, sno, password):
    """
    :param weixin_id: string
    :param sno: string for student number
    :param password: string
    :return: void
    """
    create_user(weixin_id, sno, password)


def set_session_id(weixin_id, jsessionid):
    """
    :param weixin_id: string
    :param jsessionid: string like 'FB10E88B6589AB7C2E78590838C6F2AC'
    :return: void
    """
    file_name = 'cache/{}.txt'.format(weixin_id)
    with open(file_name, mode='w') as f:
        f.write(jsessionid)


def get_session_id(weixin_id):
    """
    :param weixin_id: string
    :return: JSESSONID like 'FB10E88B6589AB7C2E78590838C6F2AC'
    """
    file_name = 'cache/{}.txt'.format(weixin_id)
    if not os.path.isfile(file_name):
        return None
    else:
        with open(file_name, mode='r') as f:
            data = f.read().strip('\n')

        return data
