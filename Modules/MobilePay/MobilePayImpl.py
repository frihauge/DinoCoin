import logging
import json
import hmac
import hashlib
import base64
from datetime import datetime
import requests
import pytz


class mpif():

    def __init__(self, key=None, MerchantId="POSDKDC307", LocationId=None, url=None, Name=None):
        self.logger = logging.getLogger('DinoGui')
        self.url = 'https://sandprod-pos2.mobilepay.dk/API/V08/RegisterPoS'
        self.MerchantId = MerchantId
        # self.locationname = "Gartnervej 4"
        self.PosId = ""
        self.PoSUnitId = None
        self.key = key
        self.url = url
        self.Name = Name
        self.LocationId = LocationId
        self.Checkedin = False

        if Name is None:
            self.Name = "Gartnervej 4"
        if LocationId is None:
            self.LocationId = "00001"
        if key is None:
            self.key = "344A350B-0D2D-4D7D-B556-BC4E2673C882"
        if url is None:
            self.url = "https://sandprod-pos2.mobilepay.dk/API/V08/"

    def ping_mp(self):
        success,_ = self.GetUniquePosId()
        return success
    
    def calchmac(self, method, contentbody, utctime):
        com_url = self.url + method
        clearstr = str.format("{} {} {}", com_url, contentbody, utctime)
        hcryp = hmac.new(bytes(self.key, 'UTF-8'), bytes(clearstr, 'UTF-8'), hashlib.sha256)
        hmacstr = base64.b64encode(hcryp.digest()).decode()
        return hmacstr

    def calcPayLoadHmac(self, payload):
        MerchantSub = self.MerchantId[3:9]
        utfBytes = bytes(MerchantSub, 'ISO-8859-1')
        key = (hashlib.sha256(utfBytes).digest())
        # inbytes = bytes(payload, 'ISO-8859-1')
        hcryp = hmac.new(key, bytes(payload, 'ISO-8859-1'), hashlib.sha256)
        hmacstr = base64.b64encode(hcryp.digest()).decode()
        return hmacstr

    def GetHamacPayload(self, orderid, Amount, BulkRef):
        # self.PosId= "a123456-b123-c123-d123-e12345678901"
        # self.MerchantId= "POSDK99999"
        # self.LocationId= "88888"
        BulkRef = "MP Bulk Reference"
        alias = self.MerchantId + self.LocationId
        payload = str.format("{0}#{1}#{2}#{3}#{4}#", alias, self.PosId, orderid, Amount, BulkRef)
        # payload = "POSDK9999988888#a123456-b123-c123-d123-e12345678901#123A124321#43.33#MP Bulk Reference#"
        payloadhmac = self.calcPayLoadHmac(payload)
        return payloadhmac

    def reqResp(self, method, contentdata, console_log=True):
        # #parsing response
        try:
            tNow = datetime.utcnow()
            utcnow = int(tNow.timestamp())
            data_json = json.dumps(contentdata, separators=(",", ":"))
            hmcode = self.calchmac(method, data_json, utcnow)
            auth = str.format("{} {}", hmcode, utcnow)
            header = {'Content-Type': 'application/json', 'Authorization': auth}
            r = requests.post(url=self.url + method, data=data_json, headers=header)
            return self.responsehandler(r, method,console_log)
        except Exception as e:
            print("No Internet: " + str(e))
            return False, 0

    def StartUpReg(self):
        success, PosId = self.RegisterPoS()
        if success:
            plist = self.GetPosList()
            PosIds = plist.get('Poses', None)
            if PosIds is not None:
                for i in PosIds:
                    payments = i.get('Payment', None)
                    if payments is not None:
                        # Status = payments.get('Status', None)
                        # OrderId = payments.get('OrderId', None)
                        # Amount = payments.get('Amount', 0)
                        # self.PaymentRefund(OrderId, Amount)
                        self.PaymentCancel()
        else:
            # Get a new posid
            self.PosId = None
            success, PosId = self.RegisterPoS()
        return success, PosId

    def RegisterPoS(self):
        print("RegisterPoS")
        try:
            data = {"MerchantId": self.MerchantId, "LocationId": self.LocationId, "PosId": self.PosId, "Name": self.Name}
            success, response = self.reqResp('RegisterPoS', data)
            if success:
                self.PosId = self.findparaminresponse(response, 'PoSId')
                print (self.PosId)
        except Exception as e:
            print("Registerpos exception: " + str(e))
            return False, 0
        return success, self.PosId

    def UnRegisterPoS(self, PosId=None):
        if PosId is not None:
            uregPosId = PosId
        else:
            uregPosId = self.PosId
        data = {"MerchantId": self.MerchantId, "LocationId": self.LocationId, "PosId": uregPosId, "Name": self.Name}
        success, response = self.reqResp('UnRegisterPoS', data)
        return success

    def AssignPoSUnitIdToPos(self, PoSUnitId):
        self.PoSUnitId = PoSUnitId
        if self.PoSUnitId is None or self.PoSUnitId == "":
            return False
        data = {"MerchantId": self.MerchantId, "LocationId":self.LocationId, "PosId": self.PosId, "PoSUnitId": self.PoSUnitId}
        success, response = self.reqResp('AssignPoSUnitIdToPos', data)
        return success

    def UnAssignPoSUnitIdToPos(self):
        if self.PoSUnitId is None or self.PoSUnitId == "":
            return False
        data = {"MerchantId": self.MerchantId, "LocationId": self.LocationId, "PosId": self.PosId, "PoSUnitId": self.PoSUnitId}
        success, response = self.reqResp('UnAssignPoSUnitIdToPoS', data)
        return success

    def GetCurrentPayment(self):
        if self.PoSUnitId is None or self.PoSUnitId == "":
            return False
        data = {"MerchantId": self.MerchantId, "LocationId": self.LocationId, "PosId": self.PosId}
        success, response = self.reqResp('GetCurrentPayment', data)
        return success

    def GetPosList(self):
        data = {"MerchantId": self.MerchantId, "LocationId": self.LocationId}
        success, response = self.reqResp('GetPosList', data)
        return response
    
    def GetUniquePosId(self):
        data = {"MerchantId": self.MerchantId, "LocationId": self.LocationId}
        success, response = self.reqResp('GetUniquePosId', data, console_log=False)
        return success,response

    
    def PaymentCancel(self):
        data = {"MerchantId": self.MerchantId, "LocationId": self.LocationId, "PosId": self.PosId}
        success, _ = self.reqResp('PaymentCancel', data)
        return success

    def PaymentRefund(self, orderid, AmountPay):
        Amount = str.format("{:.2f}", AmountPay)
        BulkRef = "MP Bulk Reference"
        data = {"MerchantId": self.MerchantId, "LocationId": self.LocationId, "PoSId": self.PosId, "OrderId": orderid, "Amount": Amount, "BulkRef": BulkRef}
        success, _ = self.reqResp('PaymentRefund', data)
        return success

    def PaymentStart(self, orderid, AmountPay):
        self.Checkedin = False

        Amount = str.format("{:.2f}", AmountPay)
        BulkRef = "MP Bulk Reference"
        HmacVal = self.GetHamacPayload(orderid, Amount, BulkRef)
        data = {"MerchantId": self.MerchantId, "LocationId": self.LocationId, "PoSId": self.PosId, "OrderId": orderid, "Amount": Amount, "BulkRef": BulkRef, "Action": "Start", "CustomerTokenCalc": 0, "HMAC": HmacVal}
        success, response = self.reqResp('PaymentStart', data)
        return success, response

    def GetPaymentStatus(self, orderid):
        data = {"MerchantId": self.MerchantId, "LocationId": self.LocationId, "PoSId": self.PosId, "Orderid": orderid}
        success, response = self.reqResp('GetPaymentStatus', data, console_log=False)
        if success and response['PaymentStatus'] == 20:
            self.Checkedin = True
        return success, response

    def getNewOrderId(self):
        tz = pytz.timezone('Europe/Berlin')
        now = datetime.now(tz)
        orderid = (hex(int(now.timestamp())))
        orderid = orderid[2:]
        return orderid

    def findparaminresponse(self, resp, param):
        if param in resp:
            return resp[param]
        else:
            return None

    def responsehandler(self, response, method, console_log=True):
        success = False
        if console_log:
            print("Exe: " + str(method))
            print(response.status_code, response.reason)
            print(response)
        data = response.json()
        if response.status_code == 200:
            success = True
        return success, data
    
def refundfrom(ordernummer,belob):
    m = mpif()
    
    m.url = 'https://mobilepaypos2.danskebank.dk/API/V08/'
    m.key ='36619E65-9C01-4B94-92CD-2B22A041CEFC'
    m.MerchantId = 'POSDK64549'
    m.PosId  = 'ad4b491f-036e-40f0-9d53-276c34de98fb'
        #m.AssignPoSUnitIdToPos("100000625947428")
    m.LocationId ='00001'
    m.Name ='Broen shopping'
    m.RegisterPoS()
    res = m.GetPaymentStatus("5dfd1b17")
    print(res)
    m.PaymentRefund(ordernummer, belob)
    print(res)
   
 
            
if __name__ == '__main__':
    try:
        #refundfrom("5dfd1b17",20.00)
        
        m = mpif()
        #live
     
        #m.getNewOrderId()
        m.RegisterPoS()
        m.AssignPoSUnitIdToPos("100000625947428")
        m.UnAssignPoSUnitIdToPos()
        m.PaymentStart("123A124311", 0.11)
        m.PaymentStart("123A124310", 0.11)
        PayDoneStatus = False
        while (not PayDoneStatus):
            res = m.GetPaymentStatus("123A124310")
            PayDoneStatus = res['PaymentStatus'] != 30
        stat = m.PaymentRefund("123A124310", 0.11)
        print (stat)
        polist = m.GetPosList()
        print("PosList " + str(polist['Poses']))
        for i in polist['Poses']:
            m.UnRegisterPoS(i['PosId'])
    except Exception as e:
        logging.error("main exception:" + str(e))
