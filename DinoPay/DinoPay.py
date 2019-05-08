import logging
import requests
from python_hmac_auth import HmacAuth
import json



class mpif():
    def __init__(self):
        self.logger = logging
        self.url = 'https://sandprod-pos2.mobilepay.dk/API/V08/RegisterPoS'
        self.headers={'content-type':'application/json','Authorization': 'zSQQxEXEqS1ETbxyAFmq8vDRTkWfg3LQ29bsCx2Bqm4= 1557255784'}
        self.MerchantId = "POSDK64549"
        self.LocationId = "66001"
        self.PosId = ""
        self.Name = "Skattekisten"
        auth=HmacAuth('36619E65-9C01-4B94-92CD-2B22A041CEFC', 'self.url')
        
        
    def reqResp(self):
    ##parsing response
        
        r = requests.get(url = self.url, data={'MerchantId': self.MerchantId, 'LocationId':self.LocationId, 'PosId': self.PosId, 'name': self.Name})
        print(r.status_code, r.reason)
        print(r)
       
if __name__ == '__main__':
    try:
        mp = mpif()
        mp.reqResp()
    except Exception as e:
        logging.error("main exception:" +str(e))
        
    