#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
@author: EFRI
"""

import time
import threading

import paho.mqtt.client as pmqtt

from cgi import log


class MQTT(threading.Thread):

    def __init__(self, root, log, host):
        super().__init__()
        self.root = root
        self.log = log
        self.host = host
        self.mqtt = pmqtt
        self._stop_event = threading.Event()
        self.connect()
        self.pulsescnt = 0
        self.portnum = 0
        self.pulsetime_low = 100
        self.pulsetime_high = 100
        self.cyclicdata = []


    def connect(self):
        self.mqttc= self.mqtt.Client()
        self.mqttc.on_connect=self.on_connect
        self.mqttc.on_message=self.on_message

    def run(self):
        while not self._stop_event.is_set():
            self.mqttc.loop()
                    # print(item)
                except Exception as e:
                    AdamValueQueue.put(("No Connection",None))
                    print(e)
                    print("Queue Error")
                finally:
                    Adam_Set_Cmd.task_done()

            if len(self.cyclicdata) > 0:
                for portno in self.cyclicdata:
                    value = self.adam6050.readinputbit(int(portno))
                    AdamValueQueue.put(("IOValue_" + str(portno), value))

            time.sleep(0.3)

    def stop(self):
        self.stop = True
        self._stop_event.set()




if __name__ == '__main__':
    at = AdamThreadSendTask(None,None, '192.168.1.200')
    at.start()
    #ad = adam6000(None, '192.168.1.200')
    #ad.connect()
    #print(ad.readcounter(1))
    #ad.SetOutputbit(0, 0)
    #print(ad.readinputbit(1))