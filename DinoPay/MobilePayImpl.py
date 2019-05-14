import logging
import json
import hmac
import hashlib
import base64
import datetime
import requests


        
class mpif():
    def __init__(self):
        self.logger = logging
        self.url = 'https://sandprod-pos2.mobilepay.dk/API/V08/RegisterPoS'
        self.headers={'content-type':'application/json','Authorization': 'zSQQxEXEqS1ETbxyAFmq8vDRTkWfg3LQ29bsCx2Bqm4= 1557255784'}
        self.MerchantId = "POSDKDC307"
        self.LocationId = "00001"
        self.locationname = "Gartnervej 4"
        self.PosId = ""
        self.Name = "Gartnervej 4"
        self.key = "344A350B-0D2D-4D7D-B556-BC4E2673C882"
        self.url = "https://sandprod-pos2.mobilepay.dk/API/V08/"
        utctime = "1557241609"
        contentbody = """{"POSId":"a123456-b123-c123-d123-e12345678901","LocationId":"88888","MerchantId":"POSDK99999"}"""
        self.RegisterPoS()
        
    def calchmac(self, method, contentbody, utctime):
          com_url = self.url + method  
          clearstr = str.format("{} {} {}",com_url,contentbody,utctime)
          hcryp = hmac.new( bytes(self.key,'UTF-8'), bytes(clearstr,'UTF-8'), hashlib.sha256 )
          hmacstr = base64.b64encode(hcryp.digest()).decode()      
          return hmacstr 

            
        
    def reqResp(self, method):
    ##parsing response
        utcnow = datetime.datetime.utcnow()
        ts = int(utcnow.timestamp())
        data={"MerchantId": self.MerchantId, "LocationId":self.LocationId, "PosId": self.PosId, "Name": self.Name}
        utcnow = "1557770264"
        msg = json.dumps(data,separators=(",", ":"))
        hmcode = self.calchmac(method, msg, utcnow)
        auth = str.format("{} {}", hmcode,utcnow)
        header = {'Content-Type': 'application/json','Authorization': auth}
        r = requests.post(url = self.url, data=data, headers=header)
        print(r.status_code, r.reason)
        print(r)

    def RegisterPoS(self):
        response = self.reqResp('RegisterPoS')
        print(response)
       


if __name__ == '__main__':
    try:
       m = mpif() 
    except Exception as e:
        logging.error("main exception:" +str(e))
