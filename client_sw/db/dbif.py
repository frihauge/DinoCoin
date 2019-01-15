#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
@author: EFRI
Frihauge IT
"""
import logging
import random
from . import googlefile as gf


class dbif():

    def __init__(self, log):
        self.Version = 1.0
        self.Description = "Interface for database"
        self.data = None
        self.logger = log
        self.logger.info("Connecting Google")
        self.g = gf.googlefile(self.logger)



    def getRandomPrice(self, prizeType): # 1 or 2
        self.logger.info("Downloading local prize file")
        self.g.download_file()
        availbleprize = []
        data = self.g.ReadFile()
        if data is None:
            self.logger.error("Data from google drive is none!")
            return None
        prizeypecnt = 0
        prizecat = ('Prize_' + str(prizeType))
        prizeypecnt = len(data[prizecat]['prizes'])
        for i in data[prizecat]['prizes']:
            if i['Stock_cnt'] > 0:
                availbleprize.append(i)
        totalprizes = len(availbleprize)
        if totalprizes == 0: # No more stuck
            return None
        
        n = random.randint(0, totalprizes - 1)
        prize_id = availbleprize[n]['id']
        # Update data 
        data[prizecat]['prizes'][prize_id]['Stock_cnt']-=1
        data[prizecat]['prizes'][prize_id]['delivered']+=1
        winnerLabel = data[prizecat]['prizes'][prize_id]['Name']
        self.g.SaveFile(data)
        return winnerLabel
        
    def download_file(self):
        self.logger.info("Downloading local prize file")
        self.g.download_file()
           
    

         
if __name__ == '__main__':
    db = dbif(None)
    # db.g.download_file()
    #data = db.g.ReadFile()
    Winner_label = db.getRandomPrice(1)
    if Winner_label is not None:
        print(Winner_label)
    else:
        print('No more prizes')       