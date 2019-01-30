import logging
import time
import threading
import queue
from PrizeModule import Prize
from AdamModule import adam
from symbol import except_clause
prn_queue = queue.Queue()


class TaskRun():
    
    
    def __init__(self, log, appsettings):
        self.Version = 1.0
        self.Description = "Module TaskRun"
        self.logger = log
        self.appsettings = appsettings
        self.timebetween_pulse = 0.001
        self.cnt = 0
        self.CounterInPort = 0
        try:
            self.adamhost = appsettings['Adam'][0]['host']
        except Exception as e:
            self.logger.error("Main setup error"+ str(e)) 
            self.adamhost = "192.168.1.100"  
             
        self.logger.info("Connecting iomodule ip " + str(self.adamhost))
        self.iomodule = adam.adam6000(self.logger, str(self.adamhost))
        succes = self.iomodule.connect()
        self.pr = Prize(self.logger)
        t= threading.Thread(target=self.pr.worker, args=(prn_queue,))
        t.start()
        # start downloading file
        prn_queue.put(0)

    def run1s(self):
        self.logger.log(logging.INFO,"Counter log: "+ str(self.cnt))
    def runfast(self):

        self.CounterInPort = 0
        stat = False
        self.cnt = self.iomodule.readcounter(self.CounterInPort)
        time.sleep(0.100)
        # cnt = 1
        if (self.cnt > 0 ):
            time.sleep(self.timebetween_pulse) # If between 2 pulses
            self.cnt = self.iomodule.readcounter(self.CounterInPort)
            self.logger.log(logging.INFO,"Generateprize Type: "+ str(self.cnt))
            prn_queue.put(self.cnt)
            #if self.cnt == 1:
               # self.pr#.newprize(1)
            #elif self.cnt == 2:
                #self.pr.newprize(2)
            stat = self.iomodule.ClearCounter(self.CounterInPort)
                    
    def run1m(self):
        self.logger.log(logging.INFO,"Update from OnLine Database")
        prn_queue.put(0)
        #self.pr.load_prizelist_to_local()
        
    def customcmd(self, cmd):
        if cmd == "cmd_1p":
            self.pr.newprize(1)
        if cmd == "cmd_2p":
            self.pr.newprize(2)
        if cmd == "q_1p":
            prn_queue.put(1)
        if cmd == "q_2p":
            prn_queue.put(2)
            
            
                