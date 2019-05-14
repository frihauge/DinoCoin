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
        self.MerchantId = "POSDKDC307"
        self.LocationId = "00001"
        self.locationname = "Gartnervej 4"
        self.PosId = ""
        self.PoSUnitId = None
        self.Name = "Gartnervej 4"
        self.key = "344A350B-0D2D-4D7D-B556-BC4E2673C882"
        self.url = "https://sandprod-pos2.mobilepay.dk/API/V08/"
        

        
    def calchmac(self, method, contentbody, utctime):
          com_url = self.url + method  
          clearstr = str.format("{} {} {}",com_url,contentbody,utctime)
          hcryp = hmac.new( bytes(self.key,'UTF-8'), bytes(clearstr,'UTF-8'), hashlib.sha256 )
          hmacstr = base64.b64encode(hcryp.digest()).decode()      
          return hmacstr 

            
        
    def reqResp(self, method, contentdata):
    ##parsing response
        tNow = datetime.datetime.utcnow()
        utcnow = int(tNow.timestamp())
        data_json = json.dumps(contentdata,separators=(",", ":"))
        hmcode = self.calchmac(method, data_json, utcnow)
        auth = str.format("{} {}", hmcode,utcnow)
        header = {'Content-Type': 'application/json','Authorization': auth}
        r = requests.post(url = self.url+method, data=data_json, headers=header)
        return self.responsehandler(r, method)
       


    def RegisterPoS(self):
        data={"MerchantId": self.MerchantId, "LocationId":self.LocationId, "PosId": self.PosId, "Name": self.Name}
        success, response = self.reqResp('RegisterPoS',data)
        self.PosId = self.findparaminresponse(response, 'PoSId')
        return success
  
       
    def UnRegisterPoS(self):
        data={"MerchantId": self.MerchantId, "LocationId":self.LocationId, "PosId": self.PosId, "Name": self.Name}
        success, response = self.reqResp('UnRegisterPoS',data)
        return success
    
    def AssignPoSUnitIdToPos(self):
        if self.PoSUnitId is None or self.PoSUnitId=="":
            return False
        data={"MerchantId": self.MerchantId, "LocationId":self.LocationId, "PosId": self.PosId, "PoSUnitId": self.PoSUnitId}
        success, response = self.reqResp('AssignPoSUnitIdToPos',data)
        return success
    
    def UnAssignPoSUnitIdToPos(self):
        if self.PoSUnitId is None or self.PoSUnitId=="":
            return False
        data={"MerchantId": self.MerchantId, "LocationId":self.LocationId, "PosId": self.PosId, "PoSUnitId": self.PoSUnitId}
        success, response = self.reqResp('UnAssignPoSUnitIdToPoS',data)
        return success
    
    def GetCurrentPayment(self):
        if self.PoSUnitId is None or self.PoSUnitId=="":
            return False
        data={"MerchantId": self.MerchantId, "LocationId":self.LocationId, "PosId": self.PosId}
        success, response = self.reqResp('GetCurrentPayment',data)
        return success
    
    def GetPosList(self):
        data={"MerchantId": self.MerchantId, "LocationId":self.LocationId}
        success, response = self.reqResp('GetPosList',data)
        return success


 
  
       
    def findparaminresponse(self, resp, param):
        if param in resp:
            return resp[param]
        else:
            return None

    def responsehandler(self, response, method):
        success = False
        print(response.status_code, response.reason)
        print(response)
        data = response.json()
        if response.status_code == 200:
            success = True
        return success, data
          


if __name__ == '__main__':
    try:
       m = mpif()
       m.RegisterPoS()
       m.GetPosList()
       m.UnRegisterPoS()
       
    except Exception as e:
        logging.error("main exception:" +str(e))
