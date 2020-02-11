#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
@author: EFRI
Frihauge IT
"""
import logging
import mysql
import mysql.connector
import time
import datetime
import os
import sys


class dinodbif():
    def __init__(self, root, log):
        self.logger = log
        self.mydb = None
        self.pcname = os.environ['COMPUTERNAME']
        self.FilePath = 'C:\\ProgramData\\DinoCoin\\DinoPrint\\'
        self.filename = self.FilePath + self.pcname + '_prize.json'
        self.rootversion = root.AppVersion
        self.mysqlconnected = False
        self.network = False
        self.clientid = None

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
        self.GetClientId()
        self.network = True
        return True
    
    def reconnect (self):
        try:
            if not self.mydb.is_connected():
                print("Mysql Reconneect")
                self.connect()
        except:
            self.connect()
            
    def GetAllRefund(self):
        try:
            self.reconnect()
            cur = self.mydb.cursor()
            ts = time.time()
            self.timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            refunddict = dict()
            sql = """SELECT PosId,
                            OrderId,
                            PaymentStatus,
                            Amount,
                            TransactionId,
                            Pulsecntstat,
                            RefundAmount,
                            Refund FROM Payments WHERE PaymentStatus=100 AND RefundAmount=0 AND Refund =1 AND ClientID = %s""" % (self.clientid)
            cur.execute(sql)
            rows = cur.fetchall()
            i = 0
            for row in rows:
                i = i+1
                refunddict[i] = {"PosId": row[0],
                                "OrderId": row[1],
                                "PaymentStatus": row[2],
                                "Amount": row[3],
                                "TransactionId": row[4],
                                "Pulsecntstat": row[5],
                                "RefundAmount": row[6],
                                "Refund": row[7]}
                
            self.mydb.commit()
            return refunddict
        except Exception as e:
            self.logger.error("Error GetAllRefund !! " + str(e))
            self.network = False
            self.printerrorlog(e)
            return None

    def InsertRefund(self, data):
        if data is None:
            self.logger.error("Data input is none!")
            return None
        try:

            self.reconnect()
            cur = self.mydb.cursor()
            ts = time.time()
            self.timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            sqldict = dict()
            sqldict['ClientId'] = self.clientid
            sqldict['Time'] = self.timestamp
            sqldict.update(data)
            sql = """INSERT INTO Payments (id,ClientId, Time, PosId, OrderId,TransactionId, Amount, RefundAmount,Refund) VALUES (%s, %s,%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE Time = VALUES(Time), Amount = VALUES(Amount), RefundAmount = VALUES(RefundAmount)"""
            val = (0,sqldict['ClientId'],
                   sqldict['Time'],
                   sqldict['PosId'],
                   sqldict['OrderId'],
                   sqldict['TransactionId'],
                   sqldict['Amount'],
                   sqldict['RefundAmount'],
                   sqldict['Refund'])
            cur.execute(sql, val)
            self.mydb.commit()
            return True
        except Exception as e:
            self.network = False           
            self.logger.error("Error after connect !! "+str(e))
            self.network = False
            self.printerrorlog(e)
            return None

    def InsertPayement(self, data):
        if data is None:
            self.logger.error("Data input is none!")
            return None
        try:
            
            self.reconnect()
            cur = self.mydb.cursor()
            ts = time.time()
            self.timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            sqldict = dict()
            sqldict['ClientId'] = self.clientid
            sqldict['Time'] = self.timestamp
            sqldict.update(data)
            sql = """INSERT INTO Payments (id,ClientId, Time,sysmode, PosId, PaymentStatus, OrderId,TransactionId, Amount,CustomerId,CustomerReceiptToken, Pulsecntstat, RefundAmount,Refund) VALUES (%s,%s,%s,%s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE Time = VALUES(Time), TransactionId = VALUES(TransactionId),PaymentStatus = VALUES(PaymentStatus),CustomerId = VALUES(CustomerId),CustomerReceiptToken = VALUES(CustomerReceiptToken),Pulsecntstat = VALUES(Pulsecntstat)"""
            val = (0,sqldict['ClientId'],
                   sqldict['Time'],
                   sqldict['sysmode'],
                   sqldict['PosId'],
                   sqldict['PaymentStatus'],
                   sqldict['OrderId'],
                   sqldict['TransactionId'],
                   sqldict['Amount'],
                   sqldict['CustomerId'],
                   sqldict['CustomerReceiptToken'],
                   sqldict['Pulsecntstat'],
                   sqldict['RefundAmount'],
                   sqldict['Refund'])
            cur.execute(sql, val)
            self.mydb.commit()
            return True
        except Exception as e:
            self.network = False           
            self.logger.error("Error after connect !! "+str(e))
            self.network = False
            self.printerrorlog(e)
            return None
        
    def GetClientId(self):
        try:
            cur = self.mydb.cursor()
            sql = ("SELECT Id FROM `Clients` WHERE `ClientName` = %s")
            val = (self.pcname,)
            cur.execute(sql, val)
            rv = cur.fetchall()
            self.clientid = int(rv[0][0])
        except Exception as e:
            self.logger.error("Error after connect !! "+e)
            self.network = False
            self.printerrorlog(e)
        
    def CreateTablesPayment(self):
        try:
            cur = self.mydb.cursor()
            sql = ("""CREATE TABLE IF NOT EXISTS Payments(
                                id int(11) NOT NULL AUTO_INCREMENT,
                                ClientId int(11),
                                Time TIMESTAMP,
                                sysmode int(8),
                                PosId varchar(45),
                                PaymentStatus INT,
                                OrderId varchar(45),
                                TransactionId varchar(45),
                                Amount INT,
                                CustomerId varchar(45),
                                CustomerToken varchar(45),
                                CustomerReceiptToken varchar(45),
                                Pulsecntstat INT,
                                RefundAmount INT,
                                Refund BOOLEAN,
                                FOREIGN KEY(ClientId) REFERENCES Clients(id), PRIMARY KEY (id),
                                UNIQUE KEY `id_order` (`ClientId`,`OrderId`,`Refund`))""")
            cur.execute(sql)
            cur.execute("CREATE TABLE IF NOT EXISTS PayApp_info (id int(11) NOT NULL AUTO_INCREMENT,clientname varchar(45),PC_Alias varchar(45),Version varchar(45),LastOnline TIMESTAMP, PRIMARY KEY (id), UNIQUE (clientname))")
            sql = "INSERT IGNORE INTO PayApp_info (clientname, Version) VALUES (%s,%s) on duplicate key update Version = %s"
            cur.execute(sql, (self.pcname, self.rootversion, self.rootversion))
        
            self.mydb.commit()
        except Exception as e:
            self.logger.error("Error after connect !! "+e)
            self.network = False
        return True
 
    def printerrorlog(self, e):
        print(e)
        self.logger.error("Error o exception:" +str(e))
        self.logger.error('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))  