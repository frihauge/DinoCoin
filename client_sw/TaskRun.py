import logging
import time

from PrizeModule import Prize
from AdamModule import adam



class TaskRun():
    
    
    def __init__(self, log, appsettings):
        self.Version = 1.0
        self.logger = log
        self.appsettings = appsettings
        self.adamhost = appsettings['AdamHost']
        self.Description = "Module TaskRun"
        self.pr = Prize(self.logger)
        self.logger.info("Connecting iomodule ip " + str(self.adamhost))
        self.iomodule = adam.adam6000(self.logger, str(self.adamhost))
        succes = self.iomodule.connect()

     
  
    def run1s(self):
        CounterInPort = 0
        stat = False
        cnt = self.iomodule.readcounter(CounterInPort)
        self.logger.log(logging.INFO,"Counter log: "+ str(cnt))
        if (cnt > 0 ):
            time.sleep(0.1) # If between 2 pulses
            cnt = self.iomodule.readcounter(CounterInPort)
            self.logger.log(logging.INFO,"Generateprize Type: "+ str(cnt))
            if cnt == 1:
                self.pr.newprize(1)
            elif cnt == 2:
                self.pr.newprize(2)
            stat = self.iomodule.ClearCounter(CounterInPort)
                    
    def run1m(self):
        self.logger.log(logging.INFO,"Update from google drive")
        self.pr.load_prizelist_to_local()
        
        
    def  TestGenPrize(pr_str):
        if pr_st == '1':
            self.iomodule.SetOutputbit(1,1)
            self.iomodule.SetOutputbit(1,0)
        elif pr_st == '2':
            self.iomodule.SetOutputbit(1,1)
            self.iomodule.SetOutputbit(1,0)
            self.iomodule.SetOutputbit(1,1)
            self.iomodule.SetOutputbit(1,0)
        else:
            Print ('Wrong entry'+ str(pr_str))
            
        
                