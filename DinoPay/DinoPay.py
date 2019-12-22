#!/usr/bin/env python
# -*- coding: latin-1 -*-
import logging
from logging.handlers import RotatingFileHandler
import unicodedata
import json
import os,io
import sys
import tkinter as tk
from sched import scheduler
import time
from datetime import datetime
import urllib.request
from threading import Thread
from tkinter import *                
from tkinter import font  as tkfont 
from PIL import Image, ImageTk
from datetime import datetime,timedelta
from threading import Timer
import threading
import queue
from _codecs import decode
#from pywinauto.win32defines import BACKGROUND_BLUE
sys.path.append('../Modules')
from AdamModule import adam
from MobilePay import MobilePayImpl
from db import dbpayif
import tools.Internettools
logname = "DinoPay.log"
AppName ="DinoPay"

AppVersion  =datetime.now().strftime("%Y%m%d_%H%M%S")
FilePath = 'C:\\ProgramData\\DinoCoin\\DinoPay\\'

log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')

logFile = logname

my_handler = RotatingFileHandler(logFile, mode='a', maxBytes=5*1024*1024, 
                                 backupCount=2, encoding=None, delay=0)
my_handler.setFormatter(log_formatter)
my_handler.setLevel(logging.INFO)

app_log = logging.getLogger('root')
app_log.setLevel(logging.INFO)
app_log.addHandler(my_handler)

appsettings = 0
s = scheduler(time, time.sleep)




def restart():
        """ Safely restart  """
        import os
        import sys
        import psutil
        import logging

        try:
            print("Restarting App")
            p = psutil.Process(os.getpid())
            for handler in p.open_files() + p.connections():
                os.close(handler.fd)
        except Exception as e:
            logging.error(e)

        python = sys.executable
        os.execl(python, python, *sys.argv) 


    
class AppMain(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.root = self
        self.mp_stat = None
        self.activepayment = False
        self.iomodulestat = None
        self.paymentdatafile = None
        self.VendingEmpty=False
        self.offlinestat= False
        Appsetting =  appsettings.get('App', {'xpos':0})
        self.debug = Appsetting.get('Debug',False)
        self.amounts_puls = Appsetting.get('amounts_puls',{})
        self.testpayment = False
        
        xpos = Appsetting.get ('xpos',0)
        fullscreen = Appsetting.get ('fullscreen',1)
        
        self.usedb = Appsetting.get ('usedb',True)
        if self.internet_on() and self.usedb :
            self.dbinQueue = queue.Queue()
            self.dboutQueue = queue.Queue()
            self.paymentdb = dbpayif.dbpayifthread(app_log,self.root,self.dbinQueue,self.dboutQueue)
            self.paymentdb.connect()
            self.paymentdb.start()

           
        self.title_font = tkfont.Font(family='ApexSansMediumT', size=36, weight="bold")
        self.background = 'white'
        root = tk.Tk._root(self)
        if fullscreen:
            root.overrideredirect(True)
            root.state('zoomed')
        root.call('encoding', 'system', 'utf-8')
        wininfo =  ("Geo Info Screen high: " + str(root.winfo_screenheight()) + "Screen width: "+str(root.winfo_screenwidth()))
        app_log.info("WinInfo" + str(wininfo))
        print (wininfo)

        localwin = ("{0}x{1}+{2}+0".format(root.winfo_screenwidth(), root.winfo_screenheight(), xpos))
        geo_pos = Appsetting.get ('geo_pos',localwin)
        root.geometry(geo_pos)

        #root.attributes('-fullscreen', True)
        
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        self.container.config(background = self.background)
        self.frames = {}
        for F in (OfflinePage, StartPage, PayWithMobilePay, StartPayment, SwipePayment, PaymentAccepted, PaymentFailed, VendingEmpty):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")
            frame.configure(background=self.background)
        self.setupadammodule()
        self.vs = Timer(5.0, self.VendingStatus) 
        self.offline = Timer(5.0, self.offlineStatus) 
        self.offline.start()
        self.vs.start() 
        self.setup_mp()
        if  self.mp_stat:
            self.show_frame("PayWithMobilePay")
        else:
            self.ft = Timer(0.0, self.FrameTimeOut, ["OfflinePage"])
            self.ft.start() 
        
    def quit(self):
        self.root.destroy      
    


            
    def PaymentStatus(self):
        print("Payment status")
        paied = False
        if self.mp is not None:
            success, response = self.mp.GetPaymentStatus(self.orderid)
            print(response)
            if success:
                paied = response['PaymentStatus'] ==100
                idle = response['PaymentStatus'] ==10
                canceled = response['PaymentStatus'] ==40
                app_log.info("PaymentStatus,Succes  mp response: " + str(response))
            else:
                self.ft = Timer(5.0, self.FrameTimeOut, ["OfflinePage"])
                self.ft.start() 
                return

            
        if self.mp.Checkedin:   
            self.show_frame("SwipePayment")
            self.mp.Checkedin = False   
        if not paied and not idle and not canceled:    
            self.after(1000, self.PaymentStatus)
        elif paied:
            self.pt.cancel()
            self.show_frame("PaymentAccepted")
            self.activepayment = False 
            app_log.info("PaymentAccepted, orderid: " + str(response['OrderId']))
            self.paymentHandle(response)
            self.ft = Timer(5.0, self.FrameTimeOut, ["paied"]) 
            self.ft.start() 
        elif canceled: 
            self.pt.cancel()
            self.ft = Timer(5.0, self.FrameTimeOut, ["PaymentFailed"]) 
            self.ft.start()    
            self.activepayment = False
            self.show_frame("PaymentFailed")
        elif idle:
           # self.setup_mp()
            self.pt.cancel()
            self.ft = Timer(5.0, self.FrameTimeOut, ["PaymentFailed"]) 
            self.ft.start()    
            self.activepayment = False
            self.show_frame("PaymentFailed")
            return      
        else:
            self.pt.cancel()
            self.activepayment = False
            #self.ft = Timer(5.0, self.FrameTimeOut, ["PaymentFailed"]) 
            #self.ft.start()    
            #self.show_frame("PayWithMobilePay")     
        
    def PulseCntGetter(self, amount):
        res = self.amounts_puls.get(str(amount), 0)
        print (res)
        return res 
       
    def paymentHandle(self,paymentstatus):
        stat = False
        if(paymentstatus['PaymentStatus']==100):
            Amount = paymentstatus['Amount']
            pulsecnt = self.PulseCntGetter(int(Amount))
            try:
                print("Pulscnt : " + str(pulsecnt)+", Pulsport : " + str(self.pulseport)+", pulsetime_low : " + str(self.pulsetime_low)+", pulsetime_high : " + str(self.pulsetime_high))
                #stat = self.iomodule.PulsePort(pulsecnt, self.pulseport, self.pulsetime_low, self.pulsetime_high)
                app_log.info("Pulscnt : " + str(pulsecnt)+", Pulsport : " + str(self.pulseport)+", pulsetime_low : " + str(self.pulsetime_low)+", pulsetime_high : " + str(self.pulsetime_high))
                adam.Adam_Set_Cmd.put(("Pulse", pulsecnt))
                #adam.Adam_Set_Cmd.join()  
                item = adam.AdamPulseQueue.get(block=True, timeout=10)
                while not adam.AdamPulseQueue.empty():
                    item = adam.AdamPulseQueue.get(block=True, timeout=2)
                if item is not None:
                    if "Pulse_stat" in  item[0]: 
                        stat = item[1]
                print("Stat: " +str(stat))
                app_log.info("Stat: " +str(stat))
                paymentstatus['Pulsecntstat']= stat
                self.paymentdatafile[paymentstatus['OrderId']].update(paymentstatus)  
                self.storepaymentdata(self.paymentdatafile,self.paymentdatafile[paymentstatus['OrderId']])

     
        
            except Exception as e:
                print ("self.iomodule.PulsePort" + str(e))
                app_log.error("error in self.iomodule.PulsePort ")
                printerrorlog(e)
    
      
    def FrameTimeOut(self, stat):
        if stat == "OfflinePage":
            self.mp_stat, _ = self.mp.StartUpReg()
            if not self.mp_stat:
                self.show_frame("OfflinePage")
                self.ft = Timer(30.0, self.FrameTimeOut,["OfflinePage"]) 
                self.ft.start()
        elif stat == "VendingEmpty" and self.VendingEmpty:
            self.ft = Timer(1.0, self.FrameTimeOut,["VendingEmpty"]) 
            self.ft.start()              
        else:
            self.show_frame("PayWithMobilePay")
       
    def VendingStatus(self):
        if not self.readveningemptystatus() :
            if self.mp is not None:
                if self.activepayment:
                    self.mp.PaymentCancel()
            self.show_frame("VendingEmpty")
            if not self.VendingEmpty: 
                self.VendingEmpty = True
                self.ft = Timer(1.0, self.FrameTimeOut,["VendingEmpty"]) 
                self.ft.start()
          
        else:
            self.VendingEmpty = False
            
        self.vs = Timer(1.0, self.VendingStatus) 
        self.vs.start()
        return True
    
    def offlineStatus(self):
        if not self.internet_on() :
            self.offlinestat = True
            self.show_frame("OfflinePage")  
        else:
            # Online again
            if self.offlinestat:
               self.offlinestat = False 
               self.ft = Timer(1.0, self.FrameTimeOut,["PayWithMobilePay"]) 
               self.ft.start()
            self.checkRefundQueue()
        self.offline = Timer(2.0, self.offlineStatus) 
        self.offline.start()
        return True
    
    def internet_on(self):
            istat = tools.Internettools.PingDinoCoinWeb() 
            if not istat:
                time.sleep(2)
                istat = tools.Internettools.PingDinoCoinWeb() 
            return istat
    
    def checkRefundQueue(self):
        try:
            item = ((None,'REFUND'))
            self.dbinQueue.put(item, block=True, timeout=None)
            self.dbinQueue.join()
            return True       

        except Exception as e: 
            print('Error in write database: ')
            printerrorlog(e)
        
        
    def processrefund(self, data):
        for key, value in data.items():
            refundbefore = data[key].get('RefundAmount',0)
            if not refundbefore:
                        data[key]['Refund']=False
                        success = self.mp.PaymentRefund(value['OrderId'], value['Amount'])
                        if success:
                            data[key]['RefundAmount']=value['Amount']
                            self.storepaymentdata(self.paymentdatafile, data[key])

    def paymenttimeout(self, stat):
        print("Payment Time out!")
         
        if self.mp is not None:
            print("Payment Time out!" + str(self.orderid))
            app_log.info("Payment TimeOut: " + str(self.orderid))
            self.mp.PaymentCancel()
            #mee put in here
            self.PaymentStatus() 
            self.show_frame("PaymentFailed")
            self.ft = Timer(5.0, self.FrameTimeOut, [stat]) 
            self.ft.start()
        
    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()

    def startMobilePayment(self, page_name, amount=None):
  ## STart new payment

        self.VendingEmpty = False
     #   if not self.readveningemptystatus():
     #       if not self.readveningemptystatus():
    #            self.show_frame("VendingEmpty")
     #           print("Vending Empty")
     #           self.VendingEmpty = True
    #            return False
        self.orderid = self.mp.getNewOrderId()
        stat, resp = self.mp.PaymentStart(self.orderid, amount)
        if not stat:
            print ("Error code: " +str(resp))
            if not self.mp.PaymentCancel():
                return False
            if 'StatusCode' not in  resp:
                return False
            if resp['StatusCode'] ==50:
                print ("Payment already in progress: cancled" +str(resp))
                stat, resp = self.mp.PaymentStart(self.orderid, amount)
                if not stat:
                    print ("Error code: " +str(resp))
                    self.mp.PaymentCancel()
                    

        succes, paymentstatus = self.mp.GetPaymentStatus(self.orderid)
        app_log.info("self.mp.GetPaymentStatus() " + str(self.orderid))
        if succes:
            self.activepayment = True
            paymentdata = self.paymentdatafile.get(self.orderid, {self.orderid:{}})
            paymentstatus["Pulsecntstat"]  = False
            paymentstatus["RefundAmount"]  = 0
            paymentstatus["Refund"]  = False
            
            
            paymentdata=paymentstatus
            self.paymentdatafile[self.orderid] = paymentdata
            self.storepaymentdata(self.paymentdatafile,paymentdata) 
            self.pt = Timer(30.0, self.paymenttimeout,["PaymentTimeOut"]) 
            self.pt.start()
            self.after(10, self.PaymentStatus)
 
    def InitPayment(self, page_name, amount=None):
        #self.startMobilePayment(page_name, amount)
        self.show_frame(page_name)
        self.thread = Thread(target = self.startMobilePayment, args = (page_name, amount, ))
        self.thread.start()
        #thread.join()
      
    def StartOver(self):
        self.mp.PaymentCancel()
        self.show_frame("PayWithMobilePay")
    
    
        
                  
    def setupadammodule(self):
        set = appsettings.get('Adam','')
        self.adamhost = set.get('host',"192.168.1.200")
        self.pulseport = set.get('pulseport', 2)
        self.pulsetime_low = set.get('pulseporttime_low_ms',300)
        self.pulsetime_high = set.get('pulseporttime_high_ms',100)
        
        self.VendingstatusPort = set.get('VendingstatusPort',3)
        app_log.info("Connecting iomodule ip " + str(self.adamhost))
        
        self.AdamTask = adam.AdamThreadSendTask(self, app_log, str(self.adamhost))
        self.AdamTask.PulsePortConf(self.pulseport, self.pulsetime_low, self.pulsetime_high)
       # self.AdamTask.setcyclicdata(str(self.VendingstatusPort))
        self.AdamTask.start()
     #   self.iomodule = adam.adam6000(app_log, str(self.adamhost))
     #   self.iomodulestat,_ = self.iomodule.connect()
        app_log.info("Connecting status: " + str(self.iomodulestat))
        return self.iomodulestat
           
    def readveningemptystatus(self):
        statbit = False
        try:
            if self.debug:
                return True
            
            adam.Adam_Set_Cmd.put(("readport", self.VendingstatusPort))
            #adam.Adam_Set_Cmd.join()  
            item = adam.AdamValueQueue.get(block=True, timeout=15)
            while not adam.AdamValueQueue.empty():
                item = adam.AdamValueQueue.get(block=True, timeout=15)
            
                
            #self.iomodule.close()
            #self.iomodulestat,_ = self.iomodule.connect()
            # statbit  = self.iomodule.readinputbit(int(self.VendingstatusPort))
            if item is not None:
                if "IOValue_"+str(self.VendingstatusPort) in  item[0]: 
                    statbit = item[1]
            return statbit
        except Exception as e:
            print ("readveningemptystatus error" + str(e))
            app_log.error("Error readveningemptystatus ")
            return 0
            
        
 
    def setup_mp(self):
        mpsetting =  appsettings.get('Mobilepay', {'url':'https://sandprod-pos2.mobilepay.dk/API/V08/','PoSUnitIdToPos':'100000625947428'})
        url = mpsetting.get ('url','https://sandprod-pos2.mobilepay.dk/API/V08/')
        
        PoSUnitIdToPos =  mpsetting.get('PoSUnitIdToPos','100000625947428')
        LocationId =  mpsetting.get('LocationId','00001')
        Name=  mpsetting.get('LocationName','DinoCoin')
        MerchantId = mpsetting.get('MerchantId','POSDKDC307')
        key = mpsetting.get('key','344A350B-0D2D-4D7D-B556-BC4E2673C882') 
        self.testpayment = mpsetting.get('testpayment',False)
        app_log.info("Connecting Mobile pay ")         
        if self.testpayment:
            self.mp = MobilePayImpl.mpif(key='344A350B-0D2D-4D7D-B556-BC4E2673C882', MerchantId='POSDKDC307', LocationId='00001', url='https://sandprod-pos2.mobilepay.dk/API/V08/', Name='DinoCoin')
        else:
            self.mp = MobilePayImpl.mpif(key=key, MerchantId=MerchantId, LocationId=LocationId, url=url, Name=Name)
        app_log.info("RegisterPOS")
        posid = mpsetting.setdefault('posid',None)
        self.mp.PosId = posid
        self.mp_stat, posid = self.mp.StartUpReg()
        if self.mp_stat:
            mpsetting['posid'] = posid
            appsettings['Mobilepay'] = mpsetting
            WriteSetupFile(appsettings)
            app_log.info("AssignPos" + str(PoSUnitIdToPos))
            self.mp_stat = self.mp.AssignPoSUnitIdToPos(PoSUnitIdToPos)
            self.paymentdatafile = self.ReadPaymentFile()
       
            # self.runrefundonmissed()
        app_log.info(self.mp_stat)

        return self.mp_stat
           
    def runrefundonmissed(self):
        if len(self.paymentdatafile) > 1:
            for key, value in self.paymentdatafile.items():
                if value['Pulsecntstat'] != True:
                    app_log.info("Payment Failed: " +str(value))
                    app_log.info("Refund : " +str(key))
                    refundbefore = self.paymentdatafile[key].get('Refund',False)
                    if not refundbefore:
                        self.paymentdatafile[key]['Refund']=False
                        success = self.mp.PaymentRefund(value['OrderId'], value['Amount'])
                        if success:
                            self.paymentdatafile[key]['Refund']=True
                        self.storepaymentdata(self.paymentdatafile)
        return True       
    
    def storepaymentdata(self,alldata, data_thistransac=None):
        self.WritePaymentFile(alldata)
        if self.usedb and data_thistransac is not None:
            data_thistransac["sysmode"]  = self.testpayment
            self.WritePaymentdb(data_thistransac)    
     
    def WriteRefunddb(self,data):
        try:
            item = (data,'REFUND_PAIED')
            self.dbinQueue.put(item, block=True, timeout=10)
            item = self.dboutQueue.get(block=True, timeout=10)
            print(item)
            #self.dbinQueue.join()
            return True    
        
        except Exception as e: 
            print('Error in write database: ')
            printerrorlog(e)
        
    def WritePaymentdb(self,data):
        try:
            item = (data,'PAY')
            self.dbinQueue.put(item, block=True, timeout=10)
            item = self.dboutQueue.get(block=True, timeout=10)
            print(item)
            #self.dbinQueue.join()
            return True       

        except Exception as e: 
            print('Error in write database: ')
            printerrorlog(e)
    
    def WritePaymentFile(self,data):
        FilePath = 'C:\\ProgramData\\DinoCoin\\DinoPay\\'
        mainsetupfile =FilePath+ 'Payment.json'
        try:
            with io.open(mainsetupfile, 'w') as setfile:
                setfile.write(json.dumps(data))
       
        except Exception as e: 
            print('Error in setup write file: ' + mainsetupfile, e)
            
    def ReadPaymentFile(self):
        FilePath = 'C:\\ProgramData\\DinoCoin\\DinoPay\\'
        mainsetupfile =FilePath+ 'Payment.json'
    
   
        if not os.path.exists(os.path.dirname(mainsetupfile)):
            try:
                os.makedirs(os.path.dirname(mainsetupfile))
            except Exception as e: 
                print('DinoPaySetup make dirs read error: ' + mainsetupfile, e)
            
        if os.path.isfile(mainsetupfile) and os.access(mainsetupfile, os.R_OK):
            print ("Local DinoPaySetup exists and is readable")
        else:
            with io.open(mainsetupfile, 'w') as db_file:
                db_file.write(json.dumps({}))
        data = None
        with io.open(mainsetupfile, 'r') as jsonFile:
            try:
                data = json.load(jsonFile) 
            except Exception as e: 
                print('Error in setup file: ' + mainsetupfile, e)
        return data

class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        mp = MobilePayImpl.mpif()
        label = tk.Label(self, text="Betal med mobile pay", font=controller.title_font,background=controller.background)
        label.pack(side="top", fill="x", pady=5)
        
        load = Image.open("img/BT_PayMP.png")
        render = ImageTk.PhotoImage(load)
      
        #btPayWithMobilePay = tk.Button(self,image=render ,text="32121321",relief='raised',
        #                    command=lambda: controller.show_frame("PayWithMobilePay"))
        #btPayWithMobilePay.image = render
        #btPayWithMobilePay.pack(pady=150)


class PayWithMobilePay(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        ft = tkfont.Font(family='ApexSansMediumT', size=14, weight="bold")
        MPLogo = Image.open("img/MP_Logo1.png")
        MPLogo_render = ImageTk.PhotoImage(MPLogo)
        label = tk.Label(self, image=MPLogo_render,text="",background=controller.background)
        label.pack(side="top", fill="x", pady=0)
        label.image= MPLogo_render
        #bgcolor='grey94'
        bgcolor='grey90'
        fr=Frame(self,bg=bgcolor)
        fr.pack(fill=X,side=TOP, pady= 0)
        fr=Frame(fr,bg=bgcolor)
        fr.pack(side=TOP, pady= 30)
        twenty = Image.open("img/20kr.png")
        twenty_render = ImageTk.PhotoImage(twenty)
   
        twentyfive = Image.open("img/25kr.png")
        twentyfive_render = ImageTk.PhotoImage(twentyfive)
        fifty = Image.open("img/50kr.png")
        fifty_render = ImageTk.PhotoImage(fifty)
        hundred = Image.open("img/100kr.png")
        hundred_render = ImageTk.PhotoImage(hundred)
        twohundred = Image.open("img/200kr.png")
        twohundred_render = ImageTk.PhotoImage(twohundred)
        if self.controller.debug:        
            button_01 = tk.Button(fr, bg=bgcolor,activebackground=bgcolor,text="0.1 Kr",  font=ft, borderwidth=2,
                           command=lambda: controller.InitPayment("StartPayment",0.1))
            button_1 = tk.Button(fr, bg=bgcolor,activebackground=bgcolor,text="1 Kr", font=ft,  borderwidth=2,
                           command=lambda: controller.InitPayment("StartPayment",1))
            button_01.pack(side=tk.LEFT, padx=15)
            button_1.pack(side=tk.LEFT, padx=15)
            
        if '20' in self.controller.amounts_puls:
            button_20 = tk.Button(fr, image=twenty_render, bg=bgcolor, activebackground=bgcolor, text="20 Kr",  borderwidth=0,
                           command=lambda:controller.InitPayment("StartPayment",20))
            button_20.image = twenty_render
            button_20.pack(side=tk.LEFT, padx=15)
        if '25' in self.controller.amounts_puls:
            button_25 = tk.Button(fr, image=twentyfive_render, bg=bgcolor, activebackground=bgcolor, text="25 Kr",  borderwidth=0,
                           command=lambda:controller.InitPayment("StartPayment",25))
            button_25.image = twentyfive_render
            button_25.pack(side=tk.LEFT, padx=15)
            
        if '50' in self.controller.amounts_puls:    
            button_50 = tk.Button(fr, image=fifty_render, bg=bgcolor, activebackground=bgcolor, text="50 Kr",  borderwidth=0,
                           command=lambda:controller.InitPayment("StartPayment",50))

            button_50.image = fifty_render
            button_50.pack(side=tk.LEFT, padx=15)
        if '100' in self.controller.amounts_puls:    
            button_100 = tk.Button(fr, image=hundred_render,bg=bgcolor, activebackground=bgcolor, borderwidth=0, text="100 Kr",
                           command=lambda: controller.InitPayment("StartPayment",100))
            button_100.image = hundred_render
            button_100.pack(side=tk.LEFT, padx=15)
        if '200' in self.controller.amounts_puls:    
           button_200 = tk.Button(fr, image=twohundred_render, bg=bgcolor, activebackground=bgcolor,borderwidth=0, text="200 Kr",
                           command=lambda: controller.InitPayment("StartPayment",200))
           button_200.image = twohundred_render
           button_200.pack(side=tk.LEFT, padx=15)
       
        
        
        
        fr2=Frame(self,bg=controller.background)
        fr2.pack(fill=Y, side=TOP, pady= 0)
       
        str = 'Én polet = 1 kr. Poletter kan ikke veksles til kontanter.'
        label = tk.Label(fr2, text=str, font=ft, background=controller.background)
        label.pack(side="top", fill="y", pady=15)

            
        
class VendingEmpty(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        load = Image.open("img/vendingempty.png")
        render = ImageTk.PhotoImage(load)
        label = tk.Label(self, text="Automat tom",background=controller.background, font=controller.title_font)
        label.pack(side="top", fill="x", pady=5)
        button = tk.Button(self, image=render, text="Go to the start page",borderwidth=0,
                           command=lambda: controller.show_frame("PayWithMobilePay"))
        button.image = render
        button.pack(pady=150)


class SwipePayment(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Godkend betaling i MobilePay", background=controller.background, font=controller.title_font)
        label.pack(side="top", fill="x", pady=15)
        
        load = Image.open("img/Swipe.png")
        render = ImageTk.PhotoImage(load)
        label = tk.Label(self, image=render,text="",background=controller.background)
        #button = tk.Button(self, image=render, text="Go to the start page",background=controller.background,borderwidth=0,
        #                   command=lambda: controller.show_frame("PayWithMobilePay"))
        label.image = render
        label.pack(pady=200)
        
        fr2=Frame(self,bg=controller.background)
        fr2.pack(fill=X, side=tk.BOTTOM, padx= 0,expand=YES)
        ft = tkfont.Font(family='ApexSansMediumT', size=14, weight="bold")
        str = 'Én polet = 1 kr. Poletter kan ikke veksles til kontanter.'
        MPLogo = Image.open("img/MP_Logo2.png")
        MPLogo_render = ImageTk.PhotoImage(MPLogo)
        label = tk.Label(fr2, image=MPLogo_render,text="",background=controller.background)
        label.image= MPLogo_render
        label.pack(side=tk.RIGHT, padx=100,pady=0)
        
       # label = tk.Label(fr2, text=str, font=ft, background=controller.background)
        #label.pack(side=tk.RIGHT, padx=0, pady=0)
class OfflinePage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="MobilePay er offline", background=controller.background, font=controller.title_font)
        label.pack(side="top", fill="x", pady=15)
        fr2=Frame(self,bg=controller.background)
        fr2.pack(fill=X, side=tk.BOTTOM, padx= 0,expand=YES)
        ft = tkfont.Font(family='ApexSansMediumT', size=14, weight="bold")
        
        MPLogo = Image.open("img/MP_Logo2.png")
        MPLogo_render = ImageTk.PhotoImage(MPLogo)
        label = tk.Label(fr2, image=MPLogo_render,text="",background=controller.background)
        label.image= MPLogo_render
        label.pack(side=tk.RIGHT, padx=100,pady=0)

class StartPayment(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Hold telefon mod mobilepay terminal", background=controller.background, font=controller.title_font)
        label.pack(side="top", fill="x", pady=15)
        
        load = Image.open("img/Confirm_Payment.png")
        render = ImageTk.PhotoImage(load)
        label = tk.Label(self, image=render,text="",background=controller.background)
        label.image = render
        label.pack(side="top",pady=25)
        
        load = Image.open("img/tilbage.png")
        render = ImageTk.PhotoImage(load)
        button = tk.Button(self, image=render, activebackground = 'white',text="Go to the start page",background=controller.background,borderwidth=0,
                           command=lambda: controller.StartOver())
        button.image = render
        button.pack(side="top",padx=340,pady=25,anchor=W, expand=NO)
       # button.place(x=100,y=100) 
       
        fr2=Frame(self,bg=controller.background)
        fr2.pack(fill=X, side=tk.BOTTOM, padx= 0,pady= 10,expand=YES)
        ft = tkfont.Font(family='ApexSansMediumT', size=14, weight="bold")
        str = 'Én polet = 1 kr. Poletter kan ikke veksles til kontanter.'
        MPLogo = Image.open("img/MP_Logo2.png")
        MPLogo_render = ImageTk.PhotoImage(MPLogo)
        label = tk.Label(fr2, image=MPLogo_render,text="",background=controller.background)
        label.image= MPLogo_render
        label.pack(side=tk.RIGHT, padx=100,pady=0)
        
        label = tk.Label(fr2, text=str, font=ft, background=controller.background)
        label.pack(side=tk.RIGHT, padx=0, pady=0)


        
class PaymentFailed(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Betaling ikke gennemført", background=controller.background, font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
  
        load = Image.open("img/Payment failed.png")
        render = ImageTk.PhotoImage(load)
        label = tk.Label(self, image=render,text="",background=controller.background)
        label.image = render
        label.pack(pady=100)
        MPLogo = Image.open("img/MP_Logo2.png")
        MPLogo_render = ImageTk.PhotoImage(MPLogo)
        label = tk.Label(self, image=MPLogo_render,text="",background=controller.background)
        label.pack(side=tk.RIGHT, padx=40,pady=0)
        label.image= MPLogo_render

class PaymentAccepted(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Betaling gennemført", background=controller.background,font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        
        
        load = Image.open("img/Payment accepted.png")
        render = ImageTk.PhotoImage(load)
      
        render = ImageTk.PhotoImage(load)
        label = tk.Label(self, image=render,text="",background=controller.background)
        label.image = render
        label.pack(pady=100)
        MPLogo = Image.open("img/MP_Logo2.png")
        MPLogo_render = ImageTk.PhotoImage(MPLogo)
        label = tk.Label(self, image=MPLogo_render,text="",background=controller.background)
        label.pack(side=tk.RIGHT, padx=40,pady=0)
        label.image= MPLogo_render
        
    def showFrame(self,cont):
        rame = self.frames[cont]
        frame.tkraise()
        frame.update()
        frame.event_generate("<<ShowFrame>>")
          
def WriteSetupFile(data):
    FilePath = 'C:\\ProgramData\\DinoCoin\\DinoPay\\'
    mainsetupfile =FilePath+ 'DinoPaySetup.json'
    try:
        with io.open(mainsetupfile, 'w') as setfile:
                setfile.write(json.dumps(data))
    except Exception as e: 
            print('Error in setup write file: ' + mainsetupfile, e)

    
def ReadSetupFile():
    FilePath = 'C:\\ProgramData\\DinoCoin\\DinoPay\\'
    mainsetupfile =FilePath+ 'DinoPaySetup.json'
    
   
    if not os.path.exists(os.path.dirname(mainsetupfile)):
        try:
            os.makedirs(os.path.dirname(mainsetupfile))
        except Exception as e: 
            print('DinoPaySetup make dirs read error: ' + mainsetupfile, e)
            
    if os.path.isfile(mainsetupfile) and os.access(mainsetupfile, os.R_OK):
        print ("Local DinoPaySetup exists and is readable")
    else:
        with io.open(mainsetupfile, 'w') as db_file:
            db_file.write(json.dumps({'Mobilepay':{'url':'https://sandprod-pos2.mobilepay.dk/API/V08/'},'App':{'xpos':2560},'Adam':{'host':"192.168.1.200",'pulseport':3,'pulseporttime_low_ms':100,'pulseporttime_high_ow_ms':300,'VendingstatusPort':1}}))
    data = None
    with io.open(mainsetupfile, 'r') as jsonFile:
        try:
            data = json.load(jsonFile) 
        except Exception as e: 
            print('Error in setup file: ' + mainsetupfile, e)
    return data

def printerrorlog(e):
    app_log.error("Error o exception:" +str(e))
    app_log.error('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))   


if __name__ == '__main__':
    while True:
        try:
            app_log.info("Running DinoPay")
            app_log.info(AppVersion)
            print("Version: "+ AppVersion)
            app_log.info("Reading Setupfile")
            
            appsettings = ReadSetupFile()
            app = AppMain()
            x=datetime.today()
            y = x.replace(day=x.day, hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
            delta_t=y-x       
            secs=delta_t.total_seconds()
        #secs =10
       # t = Timer(secs, restart)
       # t.start()
            app.mainloop()
        
        except Exception as e:
            print("main exception:" +str(e))
            app_log.error("main exception:" +str(e))
            app_log.error('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
            time.sleep(60)
            pass
        else:
            break
            
