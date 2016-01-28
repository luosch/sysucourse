# -*- coding:utf-8 -*-
WEIXIN_TOKEN = 'bojscsa'
PORT = 8080

TPL_TEXT = u'<xml><ToUserName><![CDATA[{to_user_name}]]></ToUserName><FromUserName><![CDATA[{from_user_name}]]></FromUserName><CreateTime>{create_time}</CreateTime><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[{content}]]></Content><FuncFlag>0</FuncFlag></xml>'

# course time and date
COURSE_START_TIME = ['08:00', '08:55', '09:50', '10:45', '11:40', '12:35', '13:30', '14:25', '15:20', '16:15', '17:10', '18:05', '19:00', '19:55', '20:50']
COURSE_END_TIME = ['08:45', '09:40', '10:35', '11:30', '12:25', '13:20', '14:15', '15:10', '16:05', '17:00', '17:55', '18:50', '19:45', '20:40', '21:35']
WEEK_TIME = [u'星期一', u'星期二', u'星期三', u'星期四', u'星期五', u'星期六', u'星期日']
CURRENT_XND = '2015-2016'
CURRENT_XQ = '3'

# command introduction
WELCOME_TEXT = u'感谢您的关注\n'
ERROR_TEXT = u'操作失败, 可能是服务器崩溃或者密码错误\n'
LOGIN_TEXT = u'请输入信息, 格式如下:\n学号#密码\n14441444#23333'
WRONG_TEXT = u'学号或密码错误, 请重新设置\n'
HELP_TEXT = u'\n'.join([
    u'输入user: 设置学号和密码',
    u'输入login: 登陆教务系统',
    u'输入0: 获取本周的课程',
    u'输入1-7: 获取星期一至星期日的课程',
    u'输入8: 获取今日的课程',
    u'输入9: 获取明日的课程',
    u'-' * 20,
    u'输入cj#xnd#xq: 获取课程成绩, 例如cj#2015#1, 获取2015至2016学年第1学期各科成绩',
    u'输入gpa#xnd#xq: 获取平均绩点, 例如gpa#2015#1, 获取2015至2016学年第1学期平均绩点',
    u'-' * 20,
    u'输入gpa: 获取总平均绩点',
    u'输入credit: 获取总学分'
])
