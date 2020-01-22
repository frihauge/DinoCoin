#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
@author: EFRI
"""

import time
import threading
import queue

from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from cgi import log


class AdamThreadSendTask(threading.Thread):

    def __init__(self, root, log, host, Adam_Set_Cmd, AdamValueQueue, AdamPulseQueue):
        super().__init__()
        self.root = root
        self.log = log
        self.host = host
        self.adam6050 = None
        self.Adam_Set_Cmd = Adam_Set_Cmd
        self.AdamValueQueue = AdamValueQueue
        self.AdamPulseQueue = AdamPulseQueue
        self._stop_event = threading.Event()
        self.connectadam6050()
        self.pulsescnt = 0
        self.portnum = 0
        self.pulsetime_low = 100
        self.pulsetime_high = 100
        self.cyclicdata = []

    def setcyclicdata(self, ports):
        self.cyclicdata = ports.split(",")

    def PulsePortConf(self, portnum, pulsetime_low, pulsetime_high):
        self.portnum = portnum
        self.pulsetime_low = pulsetime_low
        self.pulsetime_high = pulsetime_high

    def connectadam6050(self):
        self.adam6050 = adam6000(self.log, self.host)
        self.adam6050.connect()

    def run(self):
        while not self._stop_event.is_set():
            if not self.Adam_Set_Cmd.empty():
                try:
                    item = self.Adam_Set_Cmd.get(block=True, timeout=2)
                    if item[0] == "Pulse":
                        pulsescnt = item[1]
                        stat=False
                        stat = self.adam6050.PulsePort(pulsescnt, self.portnum, self.pulsetime_low, self.pulsetime_high)
                        self.AdamPulseQueue.put(("Pulse_stat", stat))
                    if item[0] == "readport":
                        portno = item[1]
                        val = self.adam6050.readinputbit(portno)
                        self.AdamValueQueue.put(("IOValue_" + str(portno), val))
                    # print(item)
                except Exception as e:
                    self.AdamValueQueue.put(("No Connection",None))
                    print(e)
                    print("Queue Error")
                finally:
                    self.Adam_Set_Cmd.task_done()

            if len(self.cyclicdata) > 0:
                for portno in self.cyclicdata:
                    value = self.adam6050.readinputbit(int(portno))
                    self.AdamValueQueue.put(("IOValue_" + str(portno), value))

            time.sleep(0.3)

    def stop(self):
        self.stop = True
        self._stop_event.set()


class adam6000():

    def __init__(self, log, host):
        self.Version = 1.0
        self.Description = "Setup SocketConnection to adam module"
        self.logger = log
        self.host = host
        self.client = None

    def connect(self):
        self.client = ModbusClient(self.host)
        stat = self.client is not None
        return stat, stat

    def PulsePort(self, pulsescnt, portnum, pulsetime_low, pulsetime_high):
        stat = False
        if pulsescnt == 0:
            return True
        try:
            for _ in range(pulsescnt):
                self.SetOutputbit(portnum, 1)
                time.sleep(pulsetime_high / 1000)
                stat = self.SetOutputbit(portnum, 0)
                time.sleep(pulsetime_low / 1000)
                stat = True
        except Exception as e:
            print(e)
        finally:
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
            rr = self.client.read_input_registers(0, 18)
            # not using highbyte in this setup
            # idxlow = num*2
            # highbyte = rr.registers[idxlow+1] 
            cnt = rr.registers[num * 2]
        except Exception as e:
            print(e)
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
    at = AdamThreadSendTask(None,None, '192.168.1.200')
    at.start()
    #ad = adam6000(None, '192.168.1.200')
    #ad.connect()
    #print(ad.readcounter(1))
    #ad.SetOutputbit(0, 0)
    #print(ad.readinputbit(1))