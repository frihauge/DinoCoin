#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
@author: EFRI
Frihauge IT
"""
import logging
import random
import sys
import os
import time
import datetime
import json
import io
sys.path.append('../Modules')
from DinoDB import dinoDBif
import queue
import threading


dbOutQueuedbinQueue = queue.Queue()
    
class dbpayifthread(threading.Thread):
    def __init__(self, log, root,dbinQueue,dboutQueue):
        super().__init__()
        self.root = root
        self.log = log
        self.mydb=None
        self.connection_pool = None
        self.pcname = os.environ['COMPUTERNAME']
        self.mysqlconnected = False
        self.network = False
        self.dbpay = None
        self.dbinQueue = dbinQueue
        self.dboutQueue= dboutQueue
        self._stop_event = threading.Event()
        
       # self.createlocalfile()
                 #  self.Download_to_local_json()

        
    def run(self):
        while not self._stop_event.is_set():
            if not self.dbinQueue.empty():
                try:
                    item = self.dbinQueue.get(block=True, timeout=2)
                    print("DB IN CMD Received: "+ item[1])
                    self.log.info(str("DB IN CMD Received: "+ item[1]))
                    if item[1] == "PAY":
                        if self.dbpay.InsertPayement(item[0]):    
                            self.dboutQueue.put(("DB_OK", ))
                            print("OK dboutQueue")
                        else:
                            print("""self.dboutQueue.put(("error", ))""")
                            self.dboutQueue.put(("error", ))
                    elif item[1] =="REFUND":
                       refunddata = self.dbpay.GetAllRefund()
                       if len(refunddata):
                           self.dboutQueue.put(("REFUND DATA", refunddata))
                           self.root.processrefund(refunddata)   

                    # print(item)
                except Exception as e:
                    print(e)
                    print("Queue Error")
                    self.printerrorlog(e)
                finally:
                    self.dbinQueue.task_done()


            time.sleep(0.3)
                      
    def connect(self):
        try:
            self.dbpay = dinoDBif.dinodbif(self.log)
            self.dbpay.connect();
            self.dbpay.CreateTablesPayment()          
        except Exception as e:
            self.printerrorlog(e)
            
    

    
    def DoesTablesExist(self):
        cur = self.mydb.cursor()
        cur.execute("SHOW TABLES")
        rv = cur.fetchall()
        for x in rv:
            print(x)
            

        
    def writepayment(self, data):
        item = (data, True)
        dbinQueue.put(item, block=True, timeout=None)
        dbinQueue.join()       
   
    def createlocalfile(self):
        if not os.path.exists(os.path.dirname(self.filename)):
            try:
                os.makedirs(os.path.dirname(self.filename))
            except OSError as exc: 
                if exc.errno != errno.EEXIST:
                    raise

        if os.path.isfile(self.filename) and os.access(self.filename, os.R_OK):
            print ("Local file exists and is readable")
        else:
            with io.open(self.filename, 'w') as db_file:
                db_file.write(json.dumps({"StationName": self.pcname}))
  
    def Download_to_local_json(self, reconnecttry = True):
        if not self.network and reconnecttry:
            self.logger.info("No DB connection tring to reconnect ")
            if not self.connect():
                return False
             
        try:
            self.mydb.cmd_ping()
            cur = self.mydb.cursor()
        except Exception as e:
            self.logger.info("No Database connection Using local file" +str(e))
            self.network = False
            
            
        try:
            self.logger.info("Check if local file need to be uploaded")
            data = self.ReadFile()
            if True: # put ind hvis der skal chekkes localt data:
                if 'Networkstatus' in data:
                    if data['Networkstatus'] == False:
                        self.logger.info("Upload local data before getting server data")
                        self.Update_Values_LocalJsonTodb()
        except Exception as e:
            self.logger.error("Error checkking for networkstatus in local file" +str(e))
            return False
        
        self.logger.info("Downloading new prizefile")
        sql = """SELECT id,  PrizeType, Name, Name_arab, Stock_cnt, delivered, PrizeTypeDescription, delivery_point, delivery_point_arab FROM `Prizes` WHERE `ClientName` = %s"""
        val = (self.pcname,)
        
        try:
            cur.execute(sql, val)
            row_headers=[x[0] for x in cur.description] #this will extract row headers
            rv = cur.fetchall()
            json_data=[]
            if not len(rv):
                return False
            for result in rv:
                json_data.append(dict(zip(row_headers,result)))
            self.SaveFile(json_data)
        except Exception as e:
            self.network = False
            return False     
        return True
    

            
    def Update_Values_LocalJsonTodb(self):
        data = self.ReadFile()
        if data is None:
            self.logger.error("Data input is none!")
            return None
        try:
            for prize in data['Prizes']:
                try:
                    cur = self.mydb.cursor()
                except Exception as e:
                    self.logger.info("No connection to db setting network status = False" +str(e))
                    self.network = False
                    return False
                sql = """UPDATE Prizes SET PrizeType=%s,Name=%s,Name_arab=%s,Stock_cnt = %s, delivered = %s,  delivery_point = %s, delivery_point_arab = %s  WHERE id = %s"""
                val = (prize["PrizeType"],prize['Name'],prize['Name_arab'],prize['Stock_cnt'],prize['delivered'], prize["delivery_point"],prize["delivery_point_arab"], prize["id"])
                cur.execute(sql, val)
                self.mydb.commit()
        except Exception as e:
            #self.logger.error("Json dataread error: " , str(e))
            self.network = False
            return None
        
    def Upload_LocalJsonTodb(self):
        data = self.ReadFile()
        if data is None:
            self.logger.error("Data input is none!")
            return None
        try:
            for prize in data:
                cur = self.mydb.cursor()
                sql = """INSERT INTO Prizes (ID,ClientName, PrizeType, Name, Description,Stock_cnt, delivered, PrizeTypeDescription, delivery_point") VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                val = (0,self.pcname, prize["PrizeType"],prize['Name'],prize['Description'],prize['Stock_cnt'],prize['delivered'],prize['PrizeTypeDescription'], prize['delivery_point'])
                cur.execute(sql, val)
            self.mydb.commit()
        except:
            self.network = False
            return None
            

    
    def ReadFile(self):
        data = None
        try:
            jsonFile = open(self.filename, "r", encoding='utf-8-sig') # Open the JSON file for reading
            data = json.load(jsonFile) # Read the JSON into the buffer
            
        except Exception as e:
            print('Json read error: ' , str(e))
        finally:   
            jsonFile.close() # Close the JSON file
        return data        


    def printerrorlog(self, e):
        self.log.error("Error o exception:" +str(e))
        self.log.error('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))   
  
     
        
         
if __name__ == '__main__':
    db = dbif(logging)
    db.getRandomPrice(1)
    db.updatestamp()
    db.Update_Values_LocalJsonTodb()
    db.Download_to_local_json()
      