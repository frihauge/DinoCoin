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
        self.port=1025
        self.addr = None
        self.hnd = None
        self._CMDLIST = {0 : '0', 1 : '1', 2 : '2', 3 : '3', 4 : '4',
         5 : '5', 6 : '6', 7 : '7', 8 : '8', 9 : '9',
          10 : 'A', 11 : 'B', 12 : 'C', 13 : 'D', 14 : 'E', 15 : 'F'}
     
    
    def connect(self):
        self.addr=(self.host, self.port)
        self.hnd=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.hnd.connect((self.host, self.port))
        self.hnd.settimeout(5)
        #self.hnd.bind((self.host, self.port))
        #self.hnd.bind(self.addr)
        return True

    def send(self, tx):
        # self.hnd.sendto(tx, self.addr)
        self.hnd.send(tx.encode('utf-8'))
          
    def receive(self):
        try:
            indata, inaddr = self.hnd.recvfrom(self.buf)
        except errormsg:
            print ("Error")
            indata = -1
        return indata
    
    def readinput (self):
        self.send('$016\r')
        rawresult = self.receive()
        if rawresult != -1:
            res = int(rawresult[6:9], 16)
        else:
            res = -1
        return res
    
    def readinputno (self, in_num):
        portdata = self.readinput()
        mask = 1 << in_num
        res = (portdata & mask) >> in_num
        return res
    
    def writepoutputport(self, port, state):
        self.send('#011'+self._CMDLIST[port]+'0'+str(int(state))+'\r')
        rx = self.receive()
        if str(rx).find('>') != -1:
            return True
        return False
        
    def readmodulename (self):
        self.send('$01M\r')
        rawresult = self.receive()
        res = rawresult[4:4]
        return res
    
    def ClearLatchAlarm (self,port,Lowhigh= "Low" ):
        if CLHL == "High":
            self.send('#01C'+self._CMDLIST[port]+'HL\r')
        else:
            self.send('#01C'+self._CMDLIST[port]+'CL\r')
    
        rx = self.receive()
        if str(rx).find('>') != -1:
            return True
        return False
    
    def EnableLatchAlarm (self,port,Lowhigh= "Low"):
        
        if CLHL == "High":
            self.send('#01C'+self._CMDLIST[port]+'AHE1\r')
        else:
            self.send('#01C'+self._CMDLIST[port]+'ALE1\r')
    
    
        rx = self.receive()
        if str(rx).find('>') != -1:
            return True
        return False
    
    def DisableLatchAlarm (self,port,Lowhigh= "Low"):
        
        if CLHL == "High":
            self.send('#01C'+self._CMDLIST[port]+'AHE0\r')
        else:
            self.send('#01C'+self._CMDLIST[port]+'ALE0\r')
    
    
        rx = self.receive()
        if str(rx).find('>') != -1:
            return True
        return False
    
    def close(self):
        self.hnd.close()
    