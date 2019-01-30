import time
import logging
import threading
import queue
from db import dbif
from customprinter import custom 
#prn_queue = queue.Queue()
class Prize(threading.Thread):
    
    
    def __init__(self, log):
        threading.Thread.__init__(self)
        self.Version = 1.0
        self.Description = "Module handlng prize"
        self._Prize = {0 : 'StdPrize', 1 : 'GoldPrize'}
        self.logger = log
        self.lock = threading.Lock()
        self.db = dbif.dbif(self.logger)
        self.prn = custom.custom( self.logger)
    def worker(self,prn_queue):
        while True:
            item = prn_queue.get()
            # item = prn_queue.get(block=True, timeout=2)
            if item is None:
                break
            self.newprize(item)
            prn_queue.task_done()

                    
    def newprize(self, prizetype):

        Winner_label =  self.db.getRandomPrice(prizetype)   
        self.logger.log(logging.INFO,"Prize Found: "+ str(Winner_label)) 
        self.prn.printlabel(Winner_label)
        return Winner_label
    
    def load_prizelist_to_local(self):
        self.db.download_file()