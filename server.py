# -*- coding:utf-8 -*-
import hashlib
from flask import Flask, request, make_response
from config import WEIXIN_TOKEN, PORT, WELCOME_TEXT, TPL_TEXT, LOGIN_TEXT, ERROR_TEXT, HELP_TEXT
from config import CURRENT_XQ, CURRENT_XND, COURSE_START_TIME, COURSE_END_TIME, WEEK_TIME
import xml.etree.ElementTree as eT
import time
import re
from datetime import date
import database as db
from jwxt import Jwxt

app = Flask(__name__)


def check_signature(timestamp, nonce, signature):
    """
    :param timestamp: time stamp
    :param nonce: random number
    :param signature: weixin encoded signature, combining WEIXIN_TOKEN, timestamp and nonce
    :return: True if signature is correct else False
    """
    tmp_str = reduce(lambda x, y: x + y, sorted([WEIXIN_TOKEN, timestamp, nonce]))
    return hashlib.sha1(tmp_str).hexdigest() == signature


def weixin_response(from_user_name, to_user_name, content):
    """
    :param from_user_name: string
    :param to_user_name: string
    :param content: string
    :return: weixin response in xml form
    """
    data = TPL_TEXT.format(
        from_user_name=from_user_name,
        to_user_name=to_user_name,
        content=content,
        create_time=int(time.time())
    )
    response = make_response(data)
    response.content_type = 'application/xml'
    return response


def check_user_status(msg):
    user_info = db.get_user_info(msg['FromUserName'])
    if not user_info:
        return {
            'status': 'user_not_exist',
            'response': weixin_response(
                from_user_name=msg['ToUserName'],
                to_user_name=msg['FromUserName'],
                content=LOGIN_TEXT
            )
        }

    jwxt = Jwxt(user_info['sno'], user_info['password'])

    if not jwxt.login():
        return {
            'status': 'jwxt_fail_login',
            'response': weixin_response(
                from_user_name=msg['ToUserName'],
                to_user_name=msg['FromUserName'],
                content=ERROR_TEXT
            )
        }

    return {
        'status': 'success',
        'instance': jwxt
    }


def check_user_session(msg):
    session_id = db.get_session_id(msg['FromUserName'])
    if not session_id:
        return {
            'status': 'session_id_not_exist',
            'response': weixin_response(
                from_user_name=msg['ToUserName'],
                to_user_name=msg['FromUserName'],
                content=u'请先输入 login 命令登陆'
            )
        }
    else:
        user_info = db.get_user_info(msg['FromUserName'])
        if not user_info:
            return {
                'status': 'user_not_exist',
                'response': weixin_response(
                    from_user_name=msg['ToUserName'],
                    to_user_name=msg['FromUserName'],
                    content=LOGIN_TEXT
                )
            }
        else:
            jwxt = Jwxt(user_info['sno'], user_info['password'])
            jwxt.cookies = {'JSESSIONID': session_id}

            return {
                'status': 'success',
                'instance': jwxt
            }


@app.route('/', methods=['GET'])
def index():
    """
    :return: echostr if signature is correct, else 'error'
    """
    signature = request.args.get('signature', '')
    timestamp = request.args.get('timestamp', '')
    nonce = request.args.get('nonce', '')
    echo_str = request.args.get('echostr', '')

    if signature == '' or timestamp == '' or nonce == '':
        return 'error'
    elif check_signature(timestamp, nonce, signature):
        return echo_str
    else:
        return 'error'


@app.route('/', methods=['POST'])
def weixin():
    # parse xml to dict obj
    xml = eT.fromstring(request.data)
    msg = dict()
    for ele in list(xml):
        msg[ele.tag] = ele.text

    # subscribe or unsubscribe
    if 'Event' in msg.keys():
        return weixin_response(
            from_user_name=msg['ToUserName'],
            to_user_name=msg['FromUserName'],
            content=WELCOME_TEXT
        )

    # normal command
    ask = msg['Content']
    if ask == 'user':
        # prompt user to set their sno and password
        return weixin_response(
            from_user_name=msg['ToUserName'],
            to_user_name=msg['FromUserName'],
            content=LOGIN_TEXT
        )
    elif ask == 'login':
        # prompt user to login
        check = check_user_status(msg)
        if check['status'] != 'success':
            return check['response']
        else:
            jwxt = check['instance']
            db.set_session_id(msg['FromUserName'], jwxt.cookies['JSESSIONID'])
            return weixin_response(
                from_user_name=msg['ToUserName'],
                to_user_name=msg['FromUserName'],
                content=u'已尝试登陆'
            )
    elif re.match(r'^\d+#.+$', ask):
        # set sno and password
        sno, password = ask[:ask.find('#')], ask[ask.find('#') + 1:]
        user_info = db.get_user_info(msg['FromUserName'])

        if user_info:
            db.update_user(msg['FromUserName'], sno, password)
        else:
            db.create_user(msg['FromUserName'], sno, password)

        return weixin_response(
            from_user_name=msg['ToUserName'],
            to_user_name=msg['FromUserName'],
            content=u'创建成功' if not user_info else u'修改成功'
        )
    elif ask in [str(i) for i in range(10)]:
        # query course from day 0-7, 0 stand for all, 1-7 stand for Monday to Sunday
        check = check_user_session(msg)
        if check['status'] != 'success':
            return check['response']
        else:
            jwxt = check['instance']

        try:
            # get today or tomorrow course (ask = 8, ask = 9)
            if ask == '8':
                ask = str(date.today().weekday() + 1)
            elif ask == '9':
                ask = str(date.today().weekday() + 2)

            course_list = jwxt.get_course_list(CURRENT_XND, CURRENT_XQ)
            course_list.sort(key=lambda x: int(x['day']) * 100 + int(x['start_time']))
            output_list = []
            for course in [course for course in course_list if ask == '0' or course['day'] == int(ask)]:
                course['start_time'] = COURSE_START_TIME[int(course['start_time']) - 1]
                course['end_time'] = COURSE_END_TIME[int(course['end_time']) - 1]
                course['date'] = WEEK_TIME[int(course['day']) - 1]

                output = u'{course_name}\n{date} {start_time}-{end_time}\n{location}{duration}'.format(**course)
                output_list.append(output)

            if not output_list:
                output_list.append(u'此期间没有课程')

            return weixin_response(
                from_user_name=msg['ToUserName'],
                to_user_name=msg['FromUserName'],
                content=('\n' + '-' * 20 + '\n').join(output_list)
            )
        except:
            return weixin_response(
                from_user_name=msg['ToUserName'],
                to_user_name=msg['FromUserName'],
                content=u'会话过期, 请重新输入 login 命令登陆'
            )

    elif re.match(r'^(cj#)(\d+#\d+)$', ask):
        # query score by xnd(year-year+1) and xq[0(all), 1, 2, 3]
        check = check_user_session(msg)
        if check['status'] != 'success':
            return check['response']
        else:
            jwxt = check['instance']

        try:
            tmp = ask.split('#')
            xnd, xq = u'{}-{}'.format(int(tmp[1]), int(tmp[1]) + 1), tmp[2]
            if xq in ['0', '1', '2', '3']:
                if xq == '0':
                    score_list = reduce(lambda x, y: x + y, [jwxt.get_score_list(xnd, str(i)) for i in range(1, 4)])
                else:
                    score_list = jwxt.get_score_list(xnd, xq)

                output_list = []
                for score in score_list:
                    if len(score.get('jxbpm', '')) > 1:
                        output = u'{kcmc}\n成绩: {zpcj}\n排名: {jxbpm}'.format(**score)
                    else:
                        output = u'{kcmc}\n成绩: {zpcj}'.format(**score)
                    output_list.append(output)

                if not output_list:
                    output_list.append(u'此期间没有成绩')

                return weixin_response(
                    from_user_name=msg['ToUserName'],
                    to_user_name=msg['FromUserName'],
                    content=('\n' + '-' * 20 + '\n').join(output_list)
                )
            else:
                return weixin_response(
                    from_user_name=msg['ToUserName'],
                    to_user_name=msg['FromUserName'],
                    content=u'请输入正确的查询格式'
                )
        except:
            return weixin_response(
                from_user_name=msg['ToUserName'],
                to_user_name=msg['FromUserName'],
                content=u'会话过期, 请重新输入 login 命令登陆'
            )
    elif re.match(r'^gpa(#\d+#\d+)?$', ask):
        # query gpa by xnd(year-year+1) and xq[0(all), 1, 2, 3] or all gpa
        check = check_user_session(msg)
        if check['status'] != 'success':
            return check['response']
        else:
            jwxt = check['instance']

        try:
            output_list = []
            tmp = ask.split('#')
            if len(tmp) == 1:
                gpa_list = jwxt.get_all_gpa()
            else:
                xnd, xq = '{}-{}'.format(int(tmp[1]), int(tmp[1]) + 1), tmp[2]
                if xq not in ['1', '2', '3']:
                    return weixin_response(
                        from_user_name=msg['ToUserName'],
                        to_user_name=msg['FromUserName'],
                        content=u'请输入正确的查询格式'
                    )
                gpa_list = jwxt.get_gpa(xnd, xq)

            for gpa in gpa_list:
                output = u'{oneColumn}: {twoColumn}'.format(**gpa)
                output_list.append(output)

            if not output_list:
                output_list.append(u'此期间没有绩点')

            return weixin_response(
                from_user_name=msg['ToUserName'],
                to_user_name=msg['FromUserName'],
                content='\n'.join(output_list)
            )
        except:
            return weixin_response(
                from_user_name=msg['ToUserName'],
                to_user_name=msg['FromUserName'],
                content=u'会话过期, 请重新输入 login 命令登陆'
            )
    elif ask == 'credit':
        check = check_user_session(msg)
        if check['status'] != 'success':
            return check['response']
        else:
            jwxt = check['instance']
            count = 3
            while not jwxt.tno and count >= 0:
                count -= 1
                jwxt.get_info()

        try:
            output_list = [u'已获得的学分:']
            for credit in jwxt.get_credit():
                output = u'{oneColumn}: {twoColumn}'.format(**credit)
                output_list.append(output)

            output_list.append(u'-' * 20)
            output_list.append(u'毕业所需学分:')
            for credit in jwxt.get_total_credit():
                output = u'{oneColumn}: {twoColumn}'.format(**credit)
                output_list.append(output)

            return weixin_response(
                from_user_name=msg['ToUserName'],
                to_user_name=msg['FromUserName'],
                content='\n'.join(output_list)
            )
        except:
            return weixin_response(
                from_user_name=msg['ToUserName'],
                to_user_name=msg['FromUserName'],
                content=u'会话过期, 请重新输入 login 命令登陆'
            )
    else:
        # prompt user help information
        return weixin_response(
            from_user_name=msg['ToUserName'],
            to_user_name=msg['FromUserName'],
            content=HELP_TEXT
        )


if __name__ == '__main__':
    app.run(port=PORT, debug=True)
