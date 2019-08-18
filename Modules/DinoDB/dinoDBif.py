#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
@author: EFRI
Frihauge IT
"""
import logging
import mysql.connector
import os


class dinodbif():
    def __init__(self, log):
        self.logger = log
        self.mydb = None
        self.pcname = os.environ['COMPUTERNAME']
        self.FilePath = 'C:\\ProgramData\\DinoCoin\\DinoPrint\\'
       
        self.filename =self.FilePath+ self.pcname + '_prize.json'
        
        self.mysqlconnected = False
        self.network = False
        # self.createlocalfile()
        if self.connect():
            self.CreateTables()
            
    def connect(self):
        try:
            self.mydb = mysql.connector.connect(host="mysql4.gigahost.dk",user="frihaugedk",passwd="Thisisnot4u", database="frihaugedk_dc2019",connect_timeout=2)
        except Exception as e:
            self.logger.info("No database connection: " +str(e))
            self.network = False
            return False
        self.mysqlconnected = self.mydb.is_connected()
        if not self.mysqlconnected:
            self.network = False
            return False
        self.logger.info("-----------Network Connected------------")
        self.network = True
        return True

    def CreateTablesPayment(self):
        try:
            cur = self.mydb.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS Payment (id int(11) NOT NULL AUTO_INCREMENT, time TIMESTAMP, orderid varchar(45), Amount INT, PRIMARY KEY (id))")
            self.mydb.commit()
            print(self.mydb)
        except Exception as e:
              self.logger.error("Error after connect !! "+e)
              self.network = False
        return True