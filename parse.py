# Copyright (c) 2014 lsich.com 罗思成
import xml.etree.ElementTree as ET
import time

textTpl = """
<xml>
<ToUserName><![CDATA[%s]]></ToUserName>
<FromUserName><![CDATA[%s]]></FromUserName>
<CreateTime>%s</CreateTime>
<MsgType><![CDATA[%s]]></MsgType>
<Content><![CDATA[%s]]></Content>
<FuncFlag>0</FuncFlag>
</xml>
"""

def str2xml(toUserName, fromUserName, msgType, content):
    return textTpl % (toUserName, fromUserName, str(int(time.time())), msgType, content)

def xml2obj(data):
    xml = ET.fromstring(data)
    child = list(xml)
    msgObj = {}
    for i in child:
        msgObj[i.tag] = i.text
    return msgObj