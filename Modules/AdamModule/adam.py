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

    def connect(self):
        self.client = ModbusClient(self.host)

    def PulsePort(self, pulsescnt, portnum, ms_pulsetime):
        stat = False
        for _ in range(pulsescnt):
            self.SetOutputbit(portnum, 1)
            time.sleep(ms_pulsetime / 1000)
            stat = self.SetOutputbit(portnum, 0)
            time.sleep(ms_pulsetime / 1000)
            stat = True
        return stat

    def SetOutputbit(self, num, stat):
        stat = self.client.write_coil(17 + int(num), stat)
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
        self.send('$01M\r')
        rawresult = self.receive()
        res = rawresult[4:4]
        return res

    def close(self):
        self.client.close()


if __name__ == '__main__':
    ad = adam6000(None, '192.168.50.15')
    ad.connect()
    print(ad.readcounter(1))
