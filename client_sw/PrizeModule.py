import time
import logging
from db import dbif
from customprinter import custom 

class Prize():
    
    
    def __init__(self, log):
        self.Version = 1.0
        self.Description = "Module handlng prize"
        self._Prize = {0 : 'StdPrize', 1 : 'GoldPrize'}
        self.logger = log
        self.db = dbif.dbif(self.logger)
        self.prn = custom.custom( self.logger)

    def newprize(self, prizetype):
        db = dbif.dbif(self.logger)
        Winner_label = db.getRandomPrice(prizetype)   
        self.logger.log(logging.INFO,"Prize Found: "+ str(Winner_label)) 
        self.prn.printlabel(Winner_label)
        return Winner_label
    
    def load_prizelist_to_local(self):
        db = dbif.dbif(self.logger)
        db.download_file()