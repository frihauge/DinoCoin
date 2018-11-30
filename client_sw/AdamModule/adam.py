#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
@author: EFRI
"""

import time
import socket


class adam6000():

    def __init__(self, host):
        self.Version = 1.0
        self.Description = "Setup SocketConnection to adam module"
        self.host = host
        self.buf=1024
        self.port=5002
        self.addr = None
        self.hnd = None
        
    def connect(self):
        self.addr=(self.host, self.port)
        self.hnd=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.hnd.bind(self.addr)
        return True

    def send(self, tx):
        self.hnd.sendto(tx, self.addr)
          
    def receive(self, tx):
        indata, inaddr = self.hnd.recvfrom(self.buf)
        return indata
        
