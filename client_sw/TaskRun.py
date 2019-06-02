import logging
import time
import threading
import queue
from PrizeModule import Prize
from AdamModule import adam
from symbol import except_clause
prn_queue = queue.Queue()


class TaskRun():
    
    
    def __init__(self, log, root):
        self.Version = 1.0
        self.root = root
        self.Description = "Module TaskRun"
        self.logger = log
        self.appsettings = self.root.appsettings
        self.timebetween_pulse = 0.001
        self.cnt = 0
        self.CounterInPort = 0
        try:
            set =  self.appsettings.get('Adam', {'Adam':[{'host':"192.168.1.200"}]})
            self.timebetween_pulse = self.appsettings.get('timebetween_pulse',1) * 0.001
            self.adamhost = set[0]['host']
        except Exception as e:
            self.logger.error("Main setup error"+ str(e)) 
            self.adamhost = "192.168.1.100"  
             
        self.logger.info("Connecting iomodule ip " + str(self.adamhost))
        self.iomodule = adam.adam6000(self.logger, str(self.adamhost))
        self.logger.info("WaitTime from 1 puls cnt to 2 is: " + str(self.timebetween_pulse))
        succes = self.iomodule.connect()
        self.pr = Prize(self.logger,self.root)
        self.t= threading.Thread(target=self.pr.worker, args=(prn_queue,))
        self.t.start()
        # start downloading file
        prn_queue.put(0)
    
    def stop(self):
        prn_queue.put(-1)

        
    def run10s(self):
        self.logger.log(logging.INFO,"Counter log: "+ str(self.cnt))
        if 'DigitalSignage' in self.appsettings:
            print("Check Digital Signage")
        # try:
        #     find_windows(best_match='YOURWINDOWNAMEHERE')

            
        # except:
        #     self.logger.log(logging.INFO,"No Browser open")
    
    def runfast(self):

        self.CounterInPort = 0
        stat = False
        self.cnt = self.iomodule.readcounter(self.CounterInPort)
        time.sleep(0.100)
        #time.sleep(1.100)
        # cnt = 1
        if self.cnt > 0 :
            time.sleep(self.timebetween_pulse) # If between 2 pulses
            self.cnt = self.iomodule.readcounter(self.CounterInPort)
            if self.cnt == 1 or self.cnt==2:
                prn_queue.put(self.cnt)
                self.logger.log(logging.INFO,"Generateprize Type: "+ str(self.cnt))
            #if self.cnt == 1:
               # self.pr#.newprize(1)
            #elif self.cnt == 2:
                #self.pr.newprize(2)
            if self.cnt > 2:
                self.logger.log(logging.WARN,"Counter > 2: "+ str(self.cnt) +" Igonore")    
            stat = self.iomodule.ClearCounter(self.CounterInPort)
                    
    def run1m(self):
        self.logger.log(logging.INFO,"Update from OnLine Database")
        prn_queue.put(0)

    def runtest(self):
        self.logger.log(logging.INFO,"Test Prize")
        prn_queue.put(1)
        
    def customcmd(self, cmd):
        if cmd == "cmd_1p":
            self.pr.newprize(1)
        if cmd == "cmd_2p":
            self.pr.newprize(2)
        if cmd == "q_1p":
            prn_queue.put(1)
        if cmd == "q_2p":
            prn_queue.put(2)
        if cmd == "q_loadloc":
            prn_queue.put('loadloc')
            
            
                