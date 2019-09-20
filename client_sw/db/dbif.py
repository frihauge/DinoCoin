#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
@author: EFRI
Frihauge IT
"""
import logging
import random
import mysql.connector
from mysql.connector import pooling
import os
import time
import datetime
import json
import io

class db_mysql():
    def __init__(self, log, root):
        self.root = root
        self.logger = log
        self.mydb=None
        self.connection_pool = None
        self.pcname = os.environ['COMPUTERNAME']
        self.FilePath = 'C:\\ProgramData\\DinoCoin\\DinoPrint\\'
       
        self.filename =self.FilePath+ self.pcname + '_prize.json'
        
        self.mysqlconnected = False
        self.network = False
        self.createlocalfile()
        if self.connect():
            self.CreateTables()
            self.Download_to_local_json()

                   
    def connect(self):
        try:
            if self.connection_pool is not None:
                self.mydb = self.connection_pool.get_connection()
            #self.mydb = mysql.connector.connect(host="mysql4.gigahost.dk",user="frihaugedk",passwd="Thisisnot4u", database="frihaugedk_dc2019",connect_timeout=5)
            else:
                self.connectpooling()
                if self.connection_pool is not None:
                    self.mydb = self.connection_pool.get_connection()
                else:
                    self.logger.info("No database connection: ")
                    self.network = False
                    return False                
    
        except Exception as e:
            self.connection_pool = None
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
    def connectpooling(self):
        try:
            self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="pynative_pool",
                                                                          pool_size=5,
                                                                          pool_reset_session=True,
                                                                          host='mysql4.gigahost.dk',
                                                                          database='frihaugedk_dc2019',
                                                                          user='frihaugedk',
                                                                          password='Thisisnot4u',
                                                                          connect_timeout=5)
        
            print ("Printing connection pool properties ")
            print("Connection Pool Name - ", self.connection_pool.pool_name)
            print("Connection Pool Size - ", self.connection_pool.pool_size)
        
            # Get connection object from a pool
            self.mydb = self.connection_pool.get_connection()
        
        
            if self.mydb.is_connected():
               db_Info = self.mydb.get_server_info()
               print("Connected to MySQL database using connection pool ... MySQL Server version on ",db_Info)
        
               cursor = self.mydb.cursor()
               cursor.execute("select database();")
               record = cursor.fetchone()
               print ("Your connected to - ", record)
               return
        except Exception as e :
            print ("Error while connecting to MySQL using Connection pool ", e)

    
    
    def CreateTables(self):
        try:
            cur = self.mydb.cursor()

            cur.execute("CREATE TABLE IF NOT EXISTS Clients (id int(11) NOT NULL AUTO_INCREMENT,clientname varchar(45),PC_Alias varchar(45),Version varchar(45),LastOnline TIMESTAMP, PRIMARY KEY (id), UNIQUE (clientname))")
            cur.execute("CREATE TABLE IF NOT EXISTS Settings (id int(11) NOT NULL AUTO_INCREMENT,clientname varchar(45),Parameter varchar(45),Value varchar(128), PRIMARY KEY (id),UNIQUE (clientname, Parameter))")
            cur.execute("CREATE TABLE IF NOT EXISTS won_prizes (id int(11) NOT NULL AUTO_INCREMENT, client_id INT, prize_id INT,time TIMESTAMP, PRIMARY KEY (id))")

            sql = "INSERT IGNORE INTO Clients (clientname, Version) VALUES (%s,%s) on duplicate key update Version = %s"
            cur.execute(sql, (self.pcname, self.root.version, self.root.version))
            cur.execute("CREATE TABLE IF NOT EXISTS PrizeTypes (id int(11) NOT NULL AUTO_INCREMENT, PrizeType INT,PrizeTypeName varchar(45), PRIMARY KEY (id))")
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
    
    def DoesTablesExist(self):
        cur = self.mydb.cursor()
        cur.execute("SHOW TABLES")
        rv = cur.fetchall()
        for x in rv:
            print(x)
            
    def CheckifDatainPrizes(self):
        cur = self.mydb.cursor()
        sql = ("SELECT count(*) FROM `Prizes` WHERE `ClientName` = %s")
        val = (self.pcname,)
        cur.execute(sql, val)
        rv = cur.fetchall()
        for x in rv:
            print(x)
        
                
    def CreatePrizetableExist(self):
        cur = self.mydb.cursor()
        self.logger.info("Create PrizeTable") 
        sql =   ("""CREATE TABLE IF NOT EXISTS Prizes(
                                id int(11) NOT NULL AUTO_INCREMENT,
                                ClientName varchar(45),
                                PrizeType INT,
                                Name varchar(45),
                                Description varchar(45),
                                Stock_cnt INT,
                                delivered INT,
                                PrizeTypeDescription varchar(45),
                                delivery_point varchar(45),
                                FOREIGN KEY(ClientName) REFERENCES Clients(clientname), PRIMARY KEY (id))""")

        cur.execute(sql)
        self.mydb.commit()
        
        
    def updatetimestamp(self):
        if self.network:
            try:
                cur = self.mydb.cursor()
                ts = time.time()
                self.timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                sql = "UPDATE Clients SET LastOnline = %s WHERE  clientname = %s"
                cur.execute(sql, (self.timestamp, self.pcname))
                self.mydb.commit()
            except Exception as e:
                if not self.connect():
                    self.network = False
                    return False
     
  
     
        
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
        sql = """SELECT id,  PrizeType, Name, Description, Stock_cnt, delivered, PrizeTypeDescription, delivery_point FROM `Prizes` WHERE `ClientName` = %s"""
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
    
    def insert_prizewon(self,pdata):
        ts = time.time()
        self.timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        try:
            for prize in pdata:
                try:
                    cur = self.mydb.cursor()
                except Exception as e:
                    self.logger.info("No connection to db" +str(e))
                    self.network = False
                    return False
                sql = ("""INSERT IGNORE INTO won_prizes (client_id, prize_id, time) VALUES (%s,%s,%s)""")
                val = (pdata["id"],prize['id'],self.timestamp)
                cur.execute(sql, val)
                self.mydb.commit()
        except Exception as e:
            self.logger.error("Json dataread error: " , str(e))
            
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
                sql = """UPDATE Prizes SET PrizeType=%s,Name=%s,Stock_cnt = %s, delivered = %s, Description =%s, delivery_point = %s WHERE id = %s"""
                val = (prize["PrizeType"],prize['Name'],prize['Stock_cnt'],prize['delivered'],prize['Description'], prize["delivery_point"], prize["id"])
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


    def SaveWonData(self,prize_data):
        if self.network:
            self.insert_prizewon(prize_data)    
            
    def SaveFile(self,data):
        ## Save our changes to JSON file
        filedict = {"Prizes": [], "Networkstatus": []}
        filedict['Prizes']= data 
        filedict['Networkstatus']= self.network
        jsonFile = open(self.filename, "w+", encoding='utf-8')
        jsonFile.write(json.dumps(filedict, indent=4, ensure_ascii=False))
        jsonFile.close()
        if self.network:
            self.Update_Values_LocalJsonTodb()      
        
           
class dbif():

    def __init__(self, log, root):
        self.root = root
        self.Version = 1.0
        self.Description = "Interface for database"
        self.data = None
        self.store_wonlog = False
        self.logger = log
        #self.logger.info("Connecting Google")
        #self.g = gf.googlefile(self.logger)
        self.logger.info("Connecting DataBase")
        self.db_mysql = db_mysql(self.logger, self.root)

    def SaveFile(self,data):
        self.db_mysql.SaveFile(data)

    def getRandomPrice(self, prizeType): # 1 or 2
        self.logger.info("Downloading local prize file")
        self.db_mysql.Download_to_local_json(reconnecttry=False)
            
        availbleprize = []
        availbleStockcnt = []
        
        data = self.db_mysql.ReadFile()
        if data is None:
            self.logger.error("Data from Database drive is none!")
            return None
        prizeypecnt = 0
        if 'Prizes' not in data:
            return "No prize in data"
        for da in data['Prizes']:
            if da['PrizeType'] == prizeType and da['Stock_cnt'] > 0:
                availbleprize.append(da)
        totalprizes = len(availbleprize)
        if totalprizes == 0: # No more stuck
            self.logger.error("No more availble prizes with prizetype:"+ str(prizeType))
            return "Ingen Præmie","Ingen steder"
        sum = 0
        for i in availbleprize:
            sum = sum + int(i['Stock_cnt'])

        percentlist = []
        for i in availbleprize:
            percentlist.append(int(i['Stock_cnt'])/sum)
        p = random.choices(availbleprize, percentlist, k=1)[0]
        try:
            for idx in data['Prizes']:
                if idx['id']==p['id']:
                    idx['Stock_cnt']-=1
                    if idx['delivered'] is None:
                        idx['delivered'] = 0
                    idx['delivered']+=1
                    winnerLabel = idx['Name']
                    if idx['delivery_point'] == None:
                        idx['delivery_point'] = ""
                    deliverypoint = idx['delivery_point']
                    break
        except Exception as e:
            self.logger.error("Something wrong with prize :"+ str(p) +"Error: " +str(e))       
                   
            # Update data 

        # self.g.SaveFile(data)
        self.SaveFile(data['Prizes'])
        if self.store_wonlog:
            self.db_mysql.SaveWonData(p)
        return winnerLabel, deliverypoint
        
    def download_file(self,reconnecttry):
      self.db_mysql.Download_to_local_json(reconnecttry)  
      
        
         
if __name__ == '__main__':
    db = dbif(logging)
    db.getRandomPrice(1)
    db.updatestamp()
    db.Update_Values_LocalJsonTodb()
    db.Download_to_local_json()
      