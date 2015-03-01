# Copyright (c) 2014 lsich.com 罗思成
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import cookielib
import os, sys, time, operator
from sgmllib import SGMLParser

# 解析HTML文档中的td类
class listName(SGMLParser):
    def __init__(self):
        SGMLParser.__init__(self)
        self.is_td = False
        self.tdList = []
    def start_td(self, attrs):
        self.is_td = True
    def end_td(self):
        self.is_td = False
    def handle_data(self, text):
        if self.is_td:
            self.tdList.append(text)

# get the sid
loginUrl = "http://uems.sysu.edu.cn/elect/login"
def login(stuNum, stuPasswd):
    try:
        # set cookie
        cookie = cookielib.CookieJar()
        cookieProc = urllib2.HTTPCookieProcessor(cookie)
        opener = urllib2.build_opener(cookieProc)
        urllib2.install_opener(opener)

        # login
        user = urllib.urlencode({'username': stuNum, 'password': stuPasswd})
        req = urllib2.Request(loginUrl, user)
        res = urllib2.urlopen(req)
        sid = res.geturl().replace('http://uems.sysu.edu.cn/elect/s/types?sid=', '')
        return sid

    except urllib2.HTTPError, e:
        return 0

# get the course list
courseUrl = 'http://uems.sysu.edu.cn/elect/s/courseAll?xnd=%s&xq=%s&sid=%s'
def getCourseList(sid, number):
    req = urllib2.Request(courseUrl % ("2014-2015", "2", sid))
    res = urllib2.urlopen(req)
    content = res.read()
    cut = content.find("toolbarTuitionMessage")
    data = listName()
    data.feed(content[cut:].replace("<td class='c'></td>", "<td class='c'>1</td>"))

    if not os.path.isfile("cache/%s.html" % number):
        print >> open("cache/%s.html" % number, "w"), content[cut:].replace("<td class='c'></td>", "<td class='c'>1</td>")

    courseList = []
    for index, item in enumerate(data.tdList):
        courseIndex = index / 14
        if index % 14 == 3:
            courseList.append({'name': item.decode("utf-8").encode("gbk")})
        if index % 14 == 7:
            courseList[courseIndex]['time'] = item.decode("utf-8").encode("gbk")
        if index % 14 == 9:
            courseList[courseIndex]['teacher'] = item.decode("utf-8").encode("gbk")
    return courseList

# get the course list from cache
def getCourseListFromCache(rawHtml):
    data = listName()
    data.feed(rawHtml)
    courseList = []
    for index, item in enumerate(data.tdList):
        courseIndex = index / 14
        if index % 14 == 3:
            courseList.append({'name': item.decode("utf-8").encode("gbk")})
        if index % 14 == 7:
            courseList[courseIndex]['time'] = item.decode("utf-8").encode("gbk")
        if index % 14 == 9:
            courseList[courseIndex]['teacher'] = item.decode("utf-8").encode("gbk")
    return courseList

# get the courses on exact day
weekDay = \
    [
        "星期日".decode("utf-8").encode("gbk"),
        "星期一".decode("utf-8").encode("gbk"),
        "星期二".decode("utf-8").encode("gbk"),
        "星期三".decode("utf-8").encode("gbk"),
        "星期四".decode("utf-8").encode("gbk"),
        "星期五".decode("utf-8").encode("gbk"),
        "星期六".decode("utf-8").encode("gbk")
    ]

jie = "节".decode("utf-8").encode("gbk")
dun = "：".decode("utf-8").encode("gbk")

def getCourseByDay(courseList, day):
    dayList = []

    for item in courseList:
        if item['time'].find(weekDay[day]) != -1:
            tmp = item["time"][6:item["time"].find(jie)].replace(" ", "").split("-")
            pos = item["time"][item["time"].find(jie)+2:].replace(":", "").replace("/", "").replace(dun, "")
            if (pos[0] == '('):
                position = None
            else:
                position = pos

            dayList.append({
                "courseName": item["name"],
                "teacher": item["teacher"],
                "start": int(tmp[0]),
                "end": int(tmp[1]),
                "position": position,
            })

    return sorted(dayList, key=lambda x : x["start"])

# 外部接口
def courseListOnDay(number, passwd, day):
    if os.path.isfile("cache/%s.html" % number):
        rawHtml = open("cache/%s.html" % number, "r").read()
        return getCourseByDay(getCourseListFromCache(rawHtml), day)
    else:
        sid = login(number, passwd)
        if sid == 0:
            return 0
        else:
            return getCourseByDay(getCourseList(sid, number), day)
