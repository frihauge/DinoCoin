import logging
import requests
import json
import MobilePayImpl




if __name__ == '__main__':
    try:
        mp = mpif()
        mp.reqResp()
    except Exception as e:
        logging.error("main exception:" +str(e))
        
    