import logging
import json
import hmac
import hashlib
import base64
import datetime 

        
class mpif():
    def __init__(self):
        self.logger = logging
        self.url = 'https://sandprod-pos2.mobilepay.dk/API/V08/RegisterPoS'
        self.headers={'content-type':'application/json','Authorization': 'zSQQxEXEqS1ETbxyAFmq8vDRTkWfg3LQ29bsCx2Bqm4= 1557255784'}
        self.MerchantId = "POSDK64549"
        self.LocationId = "66001"
        self.PosId = ""
        self.Name = "Skattekisten"
        self.key = "344A350B-0D2D-4D7D-B556-BC4E2673C882"
        self.url = "https://sandprod-pos2.mobilepay.dk/API/V08/"
        utctime = "1557241609"
        contentbody = """{"POSId":"a123456-b123-c123-d123-e12345678901","LocationId":"88888","MerchantId":"POSDK99999"}"""
        self.reqResp()
        
    def calchmac(self, method, contentbody, utctime):
          com_url = self.url + method  
          clearstr = str.format("{} {} {}",com_url,contentbody,utctime)
          hcryp = hmac.new( bytes(self.key,'UTF-8'), bytes(clearstr,'UTF-8'), hashlib.sha256 )
          hmacstr = base64.b64encode(hcryp.digest()).decode()      
          return hmacstr 

            
        
    def reqResp(self):
    ##parsing response
        utcnow = datetime.datetime.utcnow()
        ts = int(utcnow.timestamp())
        data={"MerchantId": self.MerchantId, "LocationId":self.LocationId, "PosId": self.PosId, "name": self.Name}
        msg = json.dumps(data,separators=(",", ":"))
        hmcode = self.calchmac("RegisterPoS", msg, "1557241609")
        r = requests.get(url = self.url, data=data)
        print(r.status_code, r.reason)
        print(r)

    def RegisterPoS(self):
        print("")
       


if __name__ == '__main__':
    try:
       m = mpif() 
    except Exception as e:
        logging.error("main exception:" +str(e))
