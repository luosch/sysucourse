# Copyright (c) 2014 lsich.com 罗思成
import urllib.request, time, parse

url = "http://localhost:8000"

if __name__ == "__main__":
    user = str(input("FromUserName: "))
    while(1):
        data = "<xml>"
        data += "<ToUserName><![CDATA[sysucc]]></ToUserName>" # % raw_input("ToUserName: ")
        data += "<FromUserName><![CDATA[%s]]></FromUserName>" % user
        data += "<CreateTime>%s</CreateTime>" % str(int(time.time()))
        data += "<MsgType><![CDATA[text]]></MsgType>"
        data += "<Content><![CDATA[%s]]></Content>" % str(input("Content: "))
        data += "<MsgId>1234567890123456</MsgId>"
        data += "</xml>"

        req = urllib.request.Request(url, data.encode("utf-8"), {"Content-type" : "text/xml"})
        res = urllib.request.urlopen(req)

        print(res.read().decode("utf-8"))
