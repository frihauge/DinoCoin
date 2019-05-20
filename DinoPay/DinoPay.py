import logging
import requests
import json
from .client_sw.AdamModule import Adam
from AdamModule import adam
import MobilePayImpl
logname = "DinoPay.log"
logging.basicConfig(filename=logname,
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)

logging.info("Running DinoPay")





if __name__ == '__main__':
    try:
        mp = mpif()
        mp.reqResp()
    except Exception as e:
        logging.error("main exception:" +str(e))
        
    