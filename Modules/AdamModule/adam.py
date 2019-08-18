#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
@author: EFRI
"""

import time
import random

from pymodbus.client.sync import ModbusTcpClient as ModbusClient


class adam6000():

    def __init__(self, log, host):
        self.Version = 1.0
        self.Description = "Setup SocketConnection to adam module"
        self.logger = log
        self.host = host
        self.port = 1025
        self.client = None

    def connect(self):
        self.client = ModbusClient(self.host)
        stat = self.client is not None
        return stat, stat

    def PulsePort(self, pulsescnt, portnum, pulsetime_low, pulsetime_high):
        stat = False
        if pulsescnt == 0:
            return True
        for _ in range(pulsescnt):
            self.SetOutputbit(portnum, 1)
            time.sleep(pulsetime_high / 1000)
            stat = self.SetOutputbit(portnum, 0)
            time.sleep(pulsetime_low / 1000)
            stat = True
        return stat

    def SetOutputbit(self, num, stat):
        stat = self.client.write_coil(16 + int(num), stat)
        return stat 
    
    def ClearCounter(self, num):
        adr = 33, 37, 41, 45, 49, 53, 57, 61, 65
        try:
            self.client.write_coils(adr[num], 1)
        except:
            return False
        if self.readcounter(num) == 0:
            return True
        else:
            return False
    
    def readcounter(self, num):
        try:
            rr = self.client.read_input_registers(0, 7)
            cnt = rr.registers[num]
            if False:
                cnt = random.randint(0, 20)

        except:
            self.logger.error("No connection to ADAM on ip: " + str(self.host))
            cnt = -1
        return cnt

    def readinputbit(self, num):
        stat = self.client.read_coils(0, 8).bits[num]
        return stat

    def readmodulename(self):
        stat = False
        try:
            sendstr ='$01M\r'
            self.client.send(sendstr.encode())
            rawresult = self.client.receive()
            res = rawresult[4:4]
            stat = True
            return (stat, res)
        except:
            self.logger.error("No connection to ADAM on ip: " + str(self.host))
        return (False, '')

    def close(self):
        self.client.close()


if __name__ == '__main__':
    ad = adam6000(None, '192.168.1.200')
    ad.connect()
    print(ad.readcounter(1))
    ad.SetOutputbit(0, 0)
    print(ad.readinputbit(1))