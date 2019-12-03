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
        self.filename = self.FilePath + self.pcname + '_prize.json'

        self.mysqlconnected = False
        self.network = False

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
    
    def CreateTablePrize(self):
        try:
            cur = self.mydb.cursor()

            cur.execute("CREATE TABLE IF NOT EXISTS Clients (id int(11) NOT NULL AUTO_INCREMENT,clientname varchar(45),PC_Alias varchar(45),Version varchar(45),LastOnline TIMESTAMP, PRIMARY KEY (id), UNIQUE (clientname))")
            cur.execute("CREATE TABLE IF NOT EXISTS Settings (id int(11) NOT NULL AUTO_INCREMENT,clientname varchar(45),Parameter varchar(45),Value varchar(128), PRIMARY KEY (id),UNIQUE (clientname, Parameter))")
            cur.execute("CREATE TABLE IF NOT EXISTS won_prizes (id int(11) NOT NULL AUTO_INCREMENT, client_id INT, prize_id INT,time TIMESTAMP, PRIMARY KEY (id))")

            sql = "INSERT IGNORE INTO Clients (clientname, Version) VALUES (%s,%s) on duplicate key update Version = %s"
            cur.execute(sql, (self.pcname, self.root.version, self.root.version))
            cur.execute("CREATE TABLE IF NOT EXISTS PrizeTypes (id int(11) NOT NULL AUTO_INCREMENT, PrizeType INT,PrizeTypeName varchar(45), PRIMARY KEY (id), UNIQUE(PrizeType))")
            sql = "INSERT IGNORE INTO Settings (clientname, Parameter, Value) VALUES (%s,%s,%s)"
            cur.execute(sql, (self.pcname, "Ad_URL", "http:\\helloWorld"))
            cur.execute("""INSERT IGNORE INTO PrizeTypes (PrizeType, PrizeTypeName) VALUES (1,"Standard_prize")""")
            cur.execute("""INSERT IGNORE INTO PrizeTypes (PrizeType, PrizeTypeName) VALUES (2,"Special_prize")""")
            self.mydb.commit()
            self.updatetimestamp()
            self.CreatePrizetableExist()
            print(self.mydb)
        except Exception as e:
              self.logger.error("Error after connect !! "+e)
              self.network = False
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