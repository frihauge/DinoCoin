#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
@author: EFRI
Frihauge IT
"""
import urllib.request
import time
from numpy.distutils.fcompiler import none


def PingDinoCoinWeb(ping_adress='http://www.dinocoin.frihauge.dk/connecttest.txt', timeout=3):
    try:
        f = None
        for i in range(2):
            try:
                req = urllib.request.Request(ping_adress)
                f = urllib.request.urlopen(req, timeout=timeout)
                break
            except:
                time.sleep(0.5)
                pass
        html = f.read().decode('utf-8')
        if len(html) != 8:
            return False
        if 'ALL PASS' in html:
            return True
        else:
            return False
    except:
        return False
    return False
