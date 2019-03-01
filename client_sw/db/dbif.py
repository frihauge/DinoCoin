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
import time
import datetime
import json
import io
VersionNumber = "Ver 0.5 BETA"
from . import googlefile as gf

class db_mysql():
    def __init__(self, log):
        self.logger = log
        self.mydb=None
        self.pcname = os.environ['COMPUTERNAME']
        self.filename = self.pcname + '_prize.json'
        self.mysqlconnected = False
        self.network = False
        self.createlocalfile()
        if self.connect():
            self.Download_to_local_json()
       
    def connect(self):
        try:
            self.mydb = mysql.connector.connect(host="mysql4.gigahost.dk",user="frihaugedk",passwd="Thisisnot4u", database="frihaugedk_dc2019")
        except Exception as e:
            self.logger.error("Can't connect to db: " +str(e))
            self.network = False
            return False
        self.mysqlconnected = self.mydb.is_connected()
        if not self.mysqlconnected:
            self.network = False
            return False
        self.logger.info("-----------Network Connected------------")
        self.network = True
        cur = self.mydb.cursor()

        
        #cur.execute("DROP TABLE Prizes")
       # cur.execute("DROP TABLE PrizeTypes")
        #cur.execute("DROP TABLE Clients")

        #cur.execute("DROP TABLE Clients")

# Select data from table using SQL query.

        cur.execute("CREATE TABLE IF NOT EXISTS Clients (id int(11) NOT NULL AUTO_INCREMENT,clientname varchar(45),Version varchar(45),LastOnline TIMESTAMP, PRIMARY KEY (id), UNIQUE (clientname))")

        sql = "INSERT IGNORE INTO Clients (clientname, Version) VALUES (%s,%s)"
        cur.execute(sql, (self.pcname,VersionNumber))
        cur.execute("CREATE TABLE IF NOT EXISTS PrizeTypes (id int(11) NOT NULL AUTO_INCREMENT, PrizeType INT,PrizeTypeName varchar(45), PRIMARY KEY (id))")

        cur.execute("""INSERT IGNORE INTO PrizeTypes (PrizeType, PrizeTypeName) VALUES (1,"Standard_prize")""")
        cur.execute("""INSERT IGNORE INTO PrizeTypes (PrizeType, PrizeTypeName) VALUES (2,"Special_prize")""")
        self.mydb.commit()
        self.updatetimestamp()
        self.CreatePrizetableExist()
        
  
        print(self.mydb)
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
         
        sql =   ("""CREATE TABLE IF NOT EXISTS Prizes(
                                id int(11) NOT NULL AUTO_INCREMENT,
                                ClientName varchar(45),
                                PrizeType INT,
                                Name varchar(45),
                                Description varchar(45),
                                Stock_cnt INT,
                                delivered INT,
                                PrizeTypeDescription varchar(45),
                                FOREIGN KEY(ClientName) REFERENCES Clients(clientname), PRIMARY KEY (id))""")

        cur.execute(sql)
        self.mydb.commit()
        
        
    def updatetimestamp(self):
        if self.mysqlconnected:
            try:
                cur = self.mydb.cursor()
                ts = time.time()
                self.timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                sql = "UPDATE Clients SET LastOnline = %s WHERE  clientname = %s"
                cur.execute(sql, (self.timestamp, self.pcname))
                self.mydb.commit()
            except Exception as e:
                if not self.connect():
                    return False
     
  
     
        
    def createlocalfile(self):
        if os.path.isfile(self.filename) and os.access(self.filename, os.R_OK):
            print ("Local file exists and is readable")
        else:
            with io.open(self.filename, 'w') as db_file:
                db_file.write(json.dumps({"StationName": self.pcname}))
  
    def Download_to_local_json(self):
        if not self.network:
            self.logger.error("Error no connection to db tring to reconnect")
            if not self.connect():
                return False
             
        try:
            cur = self.mydb.cursor()
        except Exception as e:
            self.logger.error("Error no connection to db" +str(e))
            return False
        try:
            self.logger.info("Check if local file need to be uploaded")
            data = self.ReadFile()
            if True: # put ind hvis der skal chekkes localt data:
                if data['Networkstatus'] == "False":
                    self.logger.info("Upload local data before getting server data")
                    Update_Values_LocalJsonTodb()
        except Exception as e:
            self.logger.error("Error checkking for networkstatus in local file" +str(e))
            return False
        
        self.logger.info("Downloading new prizefile")
        sql = """SELECT id,  PrizeType, Name, Description, Stock_cnt, delivered, PrizeTypeDescription FROM `Prizes` WHERE `ClientName` = %s"""
        val = (self.pcname,)
        cur.execute(sql, val)
        row_headers=[x[0] for x in cur.description] #this will extract row headers
        rv = cur.fetchall()
        json_data=[]
        if not len(rv):
            return False
        for result in rv:
            json_data.append(dict(zip(row_headers,result)))
            
        self.SaveFile(json_data)
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
                    self.logger.error("Error no connection to db" +str(e))
                    self.network = False
                    return False
                sql = """UPDATE Prizes SET PrizeType=%s,Name=%s,Stock_cnt = %s, delivered = %s, Description =%s WHERE id = %s"""
                val = (prize["PrizeType"],prize['Name'],prize['Stock_cnt'],prize['delivered'],prize['Description'], prize["id"])
                cur.execute(sql, val)
                self.mydb.commit()
        except Exception as e:
            self.logger.error("Json dataread error: " , str(e))
        
    def Upload_LocalJsonTodb(self):
        data = self.ReadFile()
        if data is None:
            self.logger.error("Data input is none!")
            return None
        for prize in data:
            cur = self.mydb.cursor()
            sql = """INSERT INTO Prizes (ID,ClientName, PrizeType, Name, Description,Stock_cnt, delivered, PrizeTypeDescription) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            val = (0,self.pcname, prize["PrizeType"],prize['Name'],prize['Description'],prize['Stock_cnt'],prize['delivered'],prize['PrizeTypeDescription'])
            cur.execute(sql, val)

        self.mydb.commit()

    
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

    def __init__(self, log):
        self.Version = 1.0
        self.Description = "Interface for database"
        self.data = None
        self.logger = log
        #self.logger.info("Connecting Google")
        #self.g = gf.googlefile(self.logger)
        self.logger.info("Connecting DataBase")
        self.db_mysql = db_mysql(self.logger)

    def SaveFile(self,data):
        self.db_mysql.SaveFile(data)

    def getRandomPrice(self, prizeType): # 1 or 2
        self.logger.info("Downloading local prize file")
        self.db_mysql.Download_to_local_json()
            
        availbleprize = []
        availbleStockcnt = []
        
        data = self.db_mysql.ReadFile()
        if data is None:
            self.logger.error("Data from Database drive is none!")
            return None
        prizeypecnt = 0
        for da in data['Prizes']:
            if da['PrizeType'] == prizeType and da['Stock_cnt'] > 0:
                availbleprize.append(da)
        totalprizes = len(availbleprize)
        if totalprizes == 0: # No more stuck
            self.logger.error("No more availble prizes with prizetype:"+ str(prizeType))
            return "Ingen Præmie"
        sum = 0
        for i in availbleprize:
            sum = sum + int(i['Stock_cnt'])

        percentlist = []
        for i in availbleprize:
            percentlist.append(int(i['Stock_cnt'])/sum)
        p = random.choices(availbleprize, percentlist, k=1)[0]
        for idx in data['Prizes']:
            if idx['id']==p['id']:
                idx['Stock_cnt']-=1
                idx['delivered']+=1
                winnerLabel = idx['Name']
                break
        # Update data 

        # self.g.SaveFile(data)
        self.SaveFile(data['Prizes'])
        return winnerLabel
        
    def download_file(self):
      self.db_mysql.Download_to_local_json()  
      
        
         
if __name__ == '__main__':
    db = dbif(logging)
    db.getRandomPrice(1)
    db.updatestamp()
    db.Update_Values_LocalJsonTodb()
    db.Download_to_local_json()
      