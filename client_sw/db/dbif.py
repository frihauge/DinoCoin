#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
@author: EFRI
Frihauge IT
"""
import logging
import random
import mysql.connector
import os
#from . import googlefile as gf

class db_mysql():
    def __init__(self):
        self.mydb=None
        self.pcname = os.environ['COMPUTERNAME']
        self.mysqlconnected = False
        self.connect()
                
    def connect(self):
        self.mydb = mysql.connector.connect(host="mysql4.gigahost.dk",user="frihaugedk",passwd="Thisisnot4u", database="frihaugedk_dc2019")
        self.mysqlconnected = self.mydb.is_connected()
        if not self.mysqlconnected:
            return False
        cur = self.mydb.cursor()
  
# Select data from table using SQL query.
        cur.execute("CREATE TABLE IF NOT EXISTS Clients (id int(11) NOT NULL AUTO_INCREMENT,clientname varchar(45),PRIMARY KEY (id))")
        #cur.execute("CREATE TABLE IF NOT EXISTS Prizetype (id int(11) NOT NULL,PrizeName varchar(45),PRIMARY KEY (id))")
       
        sql = "INSERT IGNORE INTO Clients (clientname) VALUES (%s)"
        cur.execute(sql, (self.pcname,))
       
        self.mydb.commit()


        print(self.mydb)
           
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
    db = db_mysql()
      