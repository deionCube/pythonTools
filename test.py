#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File     : test.py
# @Author   : jade
# @Date     : 2023/3/15 14:59
# @Email    : jadehh@1ive.com
# @Software : Samples
# @Desc     :
from pyldk.pyldk import PyLdk
import time
import os
from jade import JadeLogging
JadeLog = JadeLogging()
def test_adapter():
    index = 0
    pyldk = PyLdk(JadeLog=JadeLog)
    haspStruct,feature_id,login_status = pyldk.login()
    while login_status:
        if pyldk.get_ldk(feature_id) is False:
            break
        else:
            index = index + 1
            JadeLog.INFO("加密狗正常,登录id为:{},index = {}".format(feature_id,index))
        time.sleep(1)
    print("结束")
def test_version():
    from pyldk import __version__
    print(__version__)

def test_login_multi_ldk():
    pyldk = PyLdk(JadeLog=JadeLog)
    haspStruct = pyldk.adapter.login(101)
    print(haspStruct.status)
    pyldk = PyLdk(JadeLog=JadeLog)
    haspStruct = pyldk.adapter.login(101)



if __name__ == '__main__':
    test_adapter()