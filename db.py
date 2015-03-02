# Copyright (c) 2014 lsich.com 罗思成
import os

# 返回学号和密码
def getUser(name):
    if not os.path.isfile("user/%s.txt" % name):
        return False
    else:
        data = open("user/%s.txt" % name, "r").read().split("+")
        print(data)
        result = {"number": data[0], "password": data[1]}
        return result

# 创建用户
def createUser(name, number, password):
    data = "%s+%s" % (number, password)
    print(data, file=(open("user/%s.txt" % name, "w", encoding="utf-8")))

# 更新用户
def updateUser(name, number, password):
    data = "%s+%s" % (number, password)
    print(data, file=(open("user/%s.txt" % name, "w", encoding="utf-8")))
