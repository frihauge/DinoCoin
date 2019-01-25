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
VersionNumber = "Ver 0.3 BETA"
#from . import googlefile as gf

class db_mysql():
    def __init__(self):
        self.mydb=None
        self.pcname = os.environ['COMPUTERNAME']
        self.filename = self.pcname + '_prize.json'
        self.mysqlconnected = False
       
        self.connect()
                
    def connect(self):
        try:
            self.mydb = mysql.connector.connect(host="mysql4.gigahost.dk",user="frihaugedk",passwd="Thisisnot4u", database="frihaugedk_dc2019")
        except Exception as e:
            print("Can't connect to db")
            return False
        self.mysqlconnected = self.mydb.is_connected()
        if not self.mysqlconnected:
            return False
        cur = self.mydb.cursor()

        
        #cur.execute("DROP TABLE Prizes")
       # cur.execute("DROP TABLE PrizeTypes")
        #cur.execute("DROP TABLE Clients")

        #cur.execute("DROP TABLE Clients")

# Select data from table using SQL query.

        cur.execute("CREATE TABLE IF NOT EXISTS Clients (id int(11) NOT NULL AUTO_INCREMENT,clientname varchar(45),Version varchar(45),LastOnline TIMESTAMP, PRIMARY KEY (id), UNIQUE (clientname))")

        sql = "INSERT IGNORE INTO Clients (clientname, Version) VALUES (%s,%s)"
        cur.execute(sql, (self.pcname,VersionNumber))
       
        self.mydb.commit()
        self.updatetimestamp()
        self.CreatePrizetableExist()
        
  
        print(self.mydb)
    
    def DoesTablesExist(self):
        cur = self.mydb.cursor()
        sql = cur.execute("SHOW TABLES")
        for x in mycursor:
            print(x)
            
    def CheckifDatainPrizes(self):
        cur = self.mydb.cursor()
        sql = cur.execute("SELECT count(*) FROM `Prizes`")
        for x in mycursor:
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
        cur = self.mydb.cursor()
        ts = time.time()
        self.timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        sql = "UPDATE Clients SET LastOnline = %s WHERE  clientname = %s"
        cur.execute(sql, (self.timestamp, self.pcname))
        self.mydb.commit()
  
     
        
    def createlocalfile(self):
        if os.path.isfile(self.filename) and os.access(self.filename, os.R_OK):
            print ("Local file exists and is readable")
        else:
            with io.open(self.filename, 'w') as db_file:
                db_file.write(json.dumps({"StationName": self.pcname}))
  
    def Download_to_local_json(self):
        cur = self.mydb.cursor()
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
            
        jsonFile = open(self.filename, "w+", encoding='utf-8')
        jsonFile.write(json.dumps(json_data, indent=4, ensure_ascii=False))
        jsonFile.close()
        return True
      
    def Update_Values_LocalJsonTodb(self):
        data = self.ReadFile()
        if data is None:
            self.logger.error("Data input is none!")
            return None
        for prize in data:
            cur = self.mydb.cursor()
            sql = """UPDATE Prizes SET PrizeType=%s,Name=%s,Stock_cnt = %s, delivered = %s, Description =%s WHERE id = %s"""
            val = (prize["PrizeType"],prize['Name'],prize['Stock_cnt'],prize['delivered'],prize['Description'], prize["id"])
            cur.execute(sql, val)

        self.mydb.commit()
        
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

    def Upload_to_server_json(self):
        if data is None:
            self.logger.error("Data input is none!")
            return None
        for i in data:
            print (data[i])
    
    def ReadFile(self):
        data = None
        try:
            jsonFile = open(self.filename, "r", encoding='utf-8-sig') # Open the JSON file for reading
            data = json.load(jsonFile) # Read the JSON into the buffer
            
        except Exception as e:
            print('Json read error: ' , e)
        finally:   
            jsonFile.close() # Close the JSON file
        return data        

    def SaveFile(self,data):
        ## Save our changes to JSON file
        jsonFile = open(self.filename, "w+", encoding='utf-8')
        jsonFile.write(json.dumps(data, indent=4, ensure_ascii=False))
        jsonFile.close()
        if self.network:
            self.update_file(self.filename,self.file_id)      
        
           
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
        
    def ReadFile(self):
        data = None
        try:
            jsonFile = open(self.filename, "r", encoding='utf-8-sig') # Open the JSON file for reading
            data = json.load(jsonFile) # Read the JSON into the buffer
            
        except Exception as e:
            print('Json read error: ' , e)
        finally:   
            jsonFile.close() # Close the JSON file
        return data     
      
    def SaveFile(self,data):
        ## Save our changes to JSON file
        jsonFile = open(self.filename, "w+", encoding='utf-8')
        jsonFile.write(json.dumps(data, indent=4, ensure_ascii=False))
        jsonFile.close()
        if self.db_mysql.connected():
            self.db_mysql.Upload_to_server_json(data)
        
         
if __name__ == '__main__':
    db = db_mysql()
    db.updatetimestamp()
    db.Update_Values_LocalJsonTodb()
   # db.Download_to_local_json()
      