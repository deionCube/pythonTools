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
    while True:
        pyldk = PyLdk(JadeLog=JadeLog)
        if pyldk.get_ldk() is False:
            break
        else:
            index = index + 1
            JadeLog.INFO("加密狗正常,index = {}".format(index))
        time.sleep(5*60)

if __name__ == '__main__':
    test_adapter()