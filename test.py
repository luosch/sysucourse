# -*- coding:utf-8 -*-
import time
import requests

def main():
    user = raw_input('FromUserName: ')
    while(1):
        data = '<xml>'
        data += '<ToUserName><![CDATA[sysucc]]></ToUserName>'
        data += '<FromUserName><![CDATA[{}]]></FromUserName>'.format(user)
        data += '<CreateTime>{}</CreateTime>'.format(time.time())
        data += '<MsgType><![CDATA[text]]></MsgType>'
        data += '<Content><![CDATA[{}]]></Content>'.format(raw_input('Content: '))
        data += '<MsgId>1234567890123456</MsgId>'
        data += '</xml>'

        req = requests.post(
            url='http://127.0.0.1:8080',
            headers={'Content-type': 'text/xml'},
            data=data
        )
        print req.content.decode('utf-8')

if __name__ == '__main__':
    main()
