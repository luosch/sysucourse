# Copyright (c) 2014 lsich.com 罗思成
import os, sys, hashlib, time, re, parse, jwxt, db
from flask import Flask, request, g, make_response
from werkzeug.contrib.fixers import ProxyFix

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

token = "lsc"

# 微信公众号验证
def checkSignature(token, timestamp, nonce, signature):
    tmpStr = reduce(lambda x, y: x + y, sorted([token, timestamp, nonce]))
    return hashlib.sha1(tmpStr).hexdigest() == signature

# 课程时间
courseStartTime = ["nouse", "08:00", "08:55", "09:50", "10:45", "11:40", "12:35", "13:30", "14:25", "15:20", "16:15", "17:10", "18:05", "19:00", "19:55", "20:50"]
courseEndTime = ["nouse", "08:45", "09:40", "10:35", "11:30", "12:25", "13:20", "14:15", "15:10", "16:05", "17:00", "17:55", "18:50", "19:45", "20:40", "21:35"]

# 帮助指令
welcomeText = "欢迎关注中大课程助手\n已使用缓存提高速度\n"
errorText = "请输入正确的指令\n"
loginText = "请输入信息, 格式如下:\n学号 密码\n14441444 23333"
wrongText = "学号或密码错误, 请重新设置\n"
waitText = "多啦A梦正在开发新的功能\n"
helpText = "输入0: 设置您的学号和密码\n输入1-6: 获取星期一至星期六的课程\n输入9: 获取今日课程\n输入233: 未知功能"

@app.route('/', methods=['GET', 'POST'])
def weixin():
    # 验证信息
    if request.method == 'GET':
        signature = request.args.get('signature', '')
        timestamp = request.args.get('timestamp', '')
        nonce = request.args.get('nonce', '')
        echostr = request.args.get('echostr', '')

        if (signature == '' or timestamp == '' or nonce == '' or echostr == ''):
            return "error"
        else:
            if checkSignature(token, timestamp, nonce, signature):
                return echostr;
            else:
                return "error"

    # 读取用户信息
    elif request.method == 'POST':
        msg = parse.xml2obj(request.data)
        toUserName = msg['FromUserName']
        fromUserName = msg['ToUserName']

        # 关注
        if 'Event' in msg.keys():
            content = welcomeText+helpText
            if msg.get('Event') != 'subscribe':
                content = "bye~"
            data = parse.str2xml(toUserName, fromUserName, "text", content)
            response = make_response(data)
            response.content_type = 'application/xml'
            return response

        ask = msg['Content']
        content = ""
        data = ""
        try:
            if (ask == "0"):
                content = loginText
                data = parse.str2xml(toUserName, fromUserName, "text", content)

            elif (len(ask) == 1 and "1" <= ask <= "6" or ask == "9"):
                tmp = db.getUser(toUserName)
                content = wrongText+loginText
                if ask == "9":
                    ask = time.strftime("%w", time.localtime())
                if tmp:
                    firstLine = False
                    courses = jwxt.courseListOnDay(tmp["number"], tmp["password"], int(ask))
                    if courses != 0:
                        content = ""
                        if len(courses) == 0:
                            content = "今天没课哦"
                        else:
                            for item in courses:
                                if firstLine:
                                    content += "\n"
                                firstLine = True
                                content += item["courseName"] + "\n"
                                content += "老师: " + item["teacher"] + "\n"
                                content += "时间: " + courseStartTime[item["start"]] + "-"
                                content += courseEndTime[item["end"]] + "\n"
                                if item["position"]:
                                    content += item["position"] + "\n"
                        
                data = parse.str2xml(toUserName, fromUserName, "text", content)

            elif (ask == "233"):
                data = parse.str2xml(toUserName, fromUserName, "text", waitText)

            elif re.match(r"(\d+)(\s)(\w+)", ask):
                tmp = ask.split(" ")
                number = tmp[0]
                passwd = tmp[1]
                if jwxt.login(number, passwd):
                    exist = False
                    if db.getUser(toUserName):
                        exist = True
                        db.updateUser(toUserName, number, passwd)
                    else:
                        db.createUser(toUserName, number, passwd)

                    if db.getUser(toUserName):
                        if exist:
                            content = "修改成功"
                        else:
                            content = "注册成功"

                data = parse.str2xml(toUserName, fromUserName, "text", content)
            else:
                content = errorText+helpText
                data = parse.str2xml(toUserName, fromUserName, "text", content)

        except Exception as e:
            content = "工程师出去泡妞了，服务器崩溃了~"
            data = parse.str2xml(toUserName, fromUserName, "text", content)

        response = make_response(data)
        response.content_type = 'application/xml'
        return response

debug=False
if __name__ == '__main__':
    app.run(debug=debug, port=8000)
