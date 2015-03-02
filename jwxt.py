# Copyright (c) 2014 lsich.com 罗思成
import urllib.request, urllib.parse, urllib.error
import http.cookiejar
from html.parser import HTMLParser
import os, sys, time, operator

class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.is_td = False
        self.data = []
 
    def handle_starttag(self, tag, attrs):
        if tag == "td":
            self.is_td = True

    def handle_endtag(self, tag):
        if tag == "td":
            self.is_td = False

    def handle_data(self, data):
        if self.is_td == True:
            self.data.append(data)

# get the sid
loginUrl = "http://uems.sysu.edu.cn/elect/login"
def login(stuNum, stuPasswd):
    try:
        # set cookie
        cookie = http.cookiejar.CookieJar()
        cookieProc = urllib.request.HTTPCookieProcessor(cookie)
        # httpHandler = urllib.request.HTTPHandler(debuglevel=1)
        opener = urllib.request.build_opener(cookieProc)
        urllib.request.install_opener(opener)

        # login
        user = urllib.parse.urlencode({'username': stuNum, 'password': stuPasswd})
        req = urllib.request.Request(loginUrl, user.encode("utf-8"))
        res = urllib.request.urlopen(req)
        sid = res.geturl().replace('http://uems.sysu.edu.cn/elect/s/types?sid=', '')
        return sid

    except urllib.error.HTTPError as e:
        print(e)
        return False

# get the course list
courseUrl = 'http://uems.sysu.edu.cn/elect/s/courseAll?xnd=%s&xq=%s&sid=%s'
def getCourseList(sid, number):
    req = urllib.request.Request(courseUrl % ("2014-2015", "3", sid))
    res = urllib.request.urlopen(req)
    content = res.read().decode("utf-8")
    cut = content.find("toolbarTuitionMessage")

    tdList = MyHTMLParser()
    tdList.feed(content[cut:].replace("<td class='c'></td>", "<td class='c'>1</td>"))
    tdList.close()

    print(content[cut:].replace("<td class='c'></td>", "<td class='c'>1</td>"), file=open("cache/%s.html" % number, "w", encoding="utf-8"))

    courseList = []
    for index, item in enumerate(tdList.data):
        courseIndex = int(index / 14)
        if index % 14 == 3:
            courseList.append({'name': item})
        if index % 14 == 7:
            courseList[courseIndex]['time'] = item
        if index % 14 == 9:
            courseList[courseIndex]['teacher'] = item

    return courseList

# get the course list from cache
def getCourseListFromCache(rawHtml):
    tdList = MyHTMLParser()
    tdList.feed(rawHtml)
    tdList.close()

    courseList = []
    for index, item in enumerate(tdList.data):
        courseIndex = int(index / 14)
        if index % 14 == 3:
            courseList.append({'name': item})
        if index % 14 == 7:
            courseList[courseIndex]['time'] = item
        if index % 14 == 9:
            courseList[courseIndex]['teacher'] = item

    return courseList

# get the courses on exact day
weekDay = ["星期日", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六"]
def getCourseByDay(courseList, day):
    dayList = []
    for item in courseList:
        if item['time'].find(weekDay[day]) != -1:
            tmp = item["time"][4:item["time"].find("节")].replace(" ", "").split("-")
            pos = item["time"][item["time"].find("节")+1:].replace(":", "").replace("/", "").replace("：", "")

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

    return sorted(dayList, key = lambda x : x["start"])

# 外部接口
def courseListOnDay(number, passwd, day):
    if os.path.isfile("cache/%s.html" % number):
        rawHtml = open("cache/%s.html" % number, "r").read()
        return getCourseByDay(getCourseListFromCache(rawHtml), day)
    else:
        sid = login(number, passwd)
        if sid == 0:
            return False
        else:
            return getCourseByDay(getCourseList(sid, number), day)

