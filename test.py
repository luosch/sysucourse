# coding=utf-8
# Copyright (c) 2014 lsich.com 罗思成
import urllib2, time, parse

url = "http://localhost:8000"

if __name__ == "__main__":
    while(1):
        data = "<xml>"
        data += "<ToUserName><![CDATA[sysucc]]></ToUserName>" # % raw_input("ToUserName: ")
        data += "<FromUserName><![CDATA[%s]]></FromUserName>" % raw_input("FromUserName: ")
        data += "<CreateTime>%s</CreateTime>" % str(int(time.time()))
        data += "<MsgType><![CDATA[text]]></MsgType>"
        data += "<Content><![CDATA[%s]]></Content>" % raw_input("Content: ")
        data += "<MsgId>1234567890123456</MsgId>"
        data += "</xml>"

        req = urllib2.Request(url, data, {"Content-type" : "text/xml"})
        res = urllib2.urlopen(req)

        print res.read().decode("utf-8").encode("gbk")
