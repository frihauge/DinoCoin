#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
@author: EFRI
"""

import time
import socket
import logging
from pymodbus.client.sync import ModbusTcpClient as ModbusClient

class adam6000():
    
    

     
    def __init__(self, log, host):
        self.Version = 1.0
        self.Description = "Setup SocketConnection to adam module"
        self.logger = log
        self.host = host
        self.port=1025

        

    def connect(self):
        self.client = ModbusClient(self.host)

     
    def SetOutputbit(self, num, stat):
        stat = self.client.write_coil(17+int(num),stat)
        return stat 
    
    def ClearCounter(self, num):
        adr = 33,37,41,45,49,53,57,61,65
        self.client.write_coils(adr[num],1)
        if self.readcounter(num) ==0:
            return True
        else:
            return False
        
        return stat 
    
    def readcounter(self, num):
        try:
            rr = self.client.read_input_registers(1,8)
            cnt = rr.registers[num]
        except:
            cnt = -1
        return cnt
        
    def readinputbit(self, num):
        stat = client.read_coils(0,8).bits[num]
        return stat 
         


    def readmodulename (self):
        self.send('$01M\r')
        rawresult = self.receive()
        res = rawresult[4:4]
        return res
    



    
    def close(self):
        self.client.close()

if __name__ == '__main__':
    ad = adam6000(None, '192.168.50.15')
    ad.connect()
    cnt = ad.readcounter(1)