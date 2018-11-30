#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
@author: EFRI
Frihauge IT
"""

import time


class custom():

    def __init__(self, host):
        self.Version = 1.0
        self.Description = "Setup Connection to customprinter"

    def connect(self):
        return True

    def send(self, tx):
       # self.hnd.sendto(tx, self.addr)
          
    def receive(self, tx):
        # indata, inaddr = self.hnd.recvfrom(self.buf)
        return indata
        
