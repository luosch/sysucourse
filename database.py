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
        data = open(file_name).read().strip('\n')
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
