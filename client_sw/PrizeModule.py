import time
import logging
import threading
import queue
from db import dbif
from customprinter import custom 
prn_queue = queue.Queue()

class Prize(threading.Thread):
    
    def __init__(self, log, root, labeltype=0):
        threading.Thread.__init__(self)
        self.root = root
        self.Version = 1.0
        self.Description = "Module handlng prize"
        self._Prize = {0 : 'StdPrize', 1 : 'GoldPrize'}
        self._LabelType = labeltype
        self.logger = log
        self.stopthread = False
        self.lock = threading.Lock()
        self.db = dbif.dbif(self.logger,self.root)
        self.prn = custom.custom( self.logger,self.root)
        
    def worker(self,prn_queue):
        while not self.stopthread:
            try:
                item = prn_queue.get()
                # item = prn_queue.get(block=True, timeout=2)
                self.logger.log(logging.INFO,"Queue print: "+ str(item))
                if item is None:
                    break
                if item == 1 or item == 2:
                    self.newprize(item)
                elif item == 0 or item == 'loadloc':
                    self.load_prizelist_to_local()
                elif item == -1:
                    self.logger.info("Quit Printer queue")  
                    self.stopthread = True
                else:
                    self.logger.error("Wrong queue cmd:" + str(item))  
                prn_queue.task_done()
            except Exception as e:
                self.logger.error("Prize Module Worker exception:" +str(e))
            pass

    def newprize(self, prizetype):

        winnerprize =  self.db.getRandomPrice(prizetype)   
        self.logger.log(logging.INFO,"Prize Found: "+ str(winnerprize['Name']) + " DeliveryPoint: "+ winnerprize['delivery_point']) 
        self.prn.printlabel(winnerprize, self._LabelType)
        return winnerprize['Name']
    
    def load_prizelist_to_local(self):
        self.db.download_file(reconnecttry=True)
        self.db.db_mysql.updatetimestamp()