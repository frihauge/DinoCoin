#!/usr/bin/env python
# -*- coding: latin-1 -*-
import logging
import unicodedata
import json
import os,io
import sys
import tkinter as tk
from sched import scheduler
import time
from tkinter import *                
from tkinter import font  as tkfont 
from PIL import Image, ImageTk
from datetime import datetime,timedelta
from threading import Timer
from _codecs import decode
from pywinauto.win32defines import BACKGROUND_BLUE
sys.path.append('../Modules')
from AdamModule import adam
from MobilePay import MobilePayImpl
logname = "DinoPay.log"
AppName ="DinoPay"
AppVersion  ="1.0"


logging.basicConfig(filename=logname,
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)
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
        self.mp_stat = None
        self.iomodulestat = None
        self.paymentdatafile = None
        Appsetting =  appsettings.get('App', {'xpos':0})
        self.debug = Appsetting.get('Debug',False)
        xpos = Appsetting.get ('xpos',0)
        fullscreen = Appsetting.get ('fullscreen',1)
        self.title_font = tkfont.Font(family='ApexSansMediumT', size=36, weight="bold")
        self.background = 'white'
        root = tk.Tk._root(self)
        if fullscreen:
            root.overrideredirect(True)
            root.state('zoomed')
        root.call('encoding', 'system', 'utf-8')
        wininfo =  ("Geo Info Screen high: " + str(root.winfo_screenheight()) + "Screen width: "+str(root.winfo_screenwidth()))
        logging.info("WinInfo" + str(wininfo))
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
        # self.setupcoinoktimer()
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
        self.setup_mp()
        if self.iomodulestat and self.mp_stat:
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
            else:
                self.ft = Timer(5.0, self.FrameTimeOut, ["OfflinePage"])
                self.ft.start() 
                return
                #self.show_frame("OfflinePage") 
            
        if self.mp.Checkedin:   
            self.show_frame("SwipePayment")
            self.mp.Checkedin = False   
        if not paied and not idle and not canceled:    
            self.after(1000, self.PaymentStatus)
        elif paied:
            self.pt.cancel()
            self.ft = Timer(5.0, self.FrameTimeOut, ["paied"]) 
            self.ft.start()    
            self.show_frame("PaymentAccepted") 
            logging.info("PaymentAccepted, orderid: " + str(response['OrderId']))
            self.paymentHandle(response)
        elif canceled: 
            self.pt.cancel()
            self.ft = Timer(5.0, self.FrameTimeOut, ["PaymentFailed"]) 
            self.ft.start()    
            self.show_frame("PaymentFailed")     
        else:
            self.pt.cancel()
            self.ft = Timer(5.0, self.FrameTimeOut, ["PaymentFailed"]) 
            self.ft.start()    
            self.show_frame("PaymentFailed")     
        
    def PulseCntGetter(self, amount):
        switcher = {
                    50: 1,
                    100: 2,
                    200: 3,
                    }
        res = switcher.get(amount, 0)
        print (res)
        return res 
       
    def paymentHandle(self,paymentstatus):
        if(paymentstatus['PaymentStatus']==100):
           Amount = paymentstatus['Amount']
           pulsecnt = self.PulseCntGetter(int(Amount))
           if self.iomodulestat:
               stat = self.iomodule.PulsePort(pulsecnt, self.pulseport, self.pulsetime_low, self.pulsetime_high)
               paymentstatus['Pulsecntstat']= stat
               self.paymentdatafile[paymentstatus['OrderId']]  = paymentstatus  
               self.WritePaymentFile(self.paymentdatafile)
   
    def FrameTimeOut(self, stat):
        if stat == "OfflinePage":
            self.mp_stat, _ = self.mp.StartUpReg()
            if not self.mp_stat:
                self.show_frame("OfflinePage")
                self.ft = Timer(30.0, self.FrameTimeOut,["OfflinePage"]) 
                self.ft.start()
            else:
                restart()
            
        elif not self.readveningemptystatus():
            self.show_frame("VendingEmpty")
            self.VendingEmpty = True
            self.ft = Timer(30.0, self.FrameTimeOut,["VendingEmpty"]) 
            self.ft.start()
            return False
        else:
            self.show_frame("PayWithMobilePay")
                   
    def paymenttimeout(self, stat):
        print("Payment Time out!")
         
        if self.mp is not None:
            print("Payment Time out!" + str(self.orderid))
            logging.info("Payment TimeOut" + str(self.orderid))
            self.mp.PaymentCancel()
            self.ft = Timer(5.0, self.FrameTimeOut, [stat]) 
            self.ft.start()
        
    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()

    def InitPayment(self, page_name, amount=None):
        ## STart new payment
        
        if not self.readveningemptystatus():
            self.show_frame("VendingEmpty")
            print("Vending Empty")
            self.VendingEmpty = True
            self.ft = Timer(5.0, self.FrameTimeOut,["VendingEmpty"]) 
            self.ft.start()
            return False
        self.orderid = self.mp.getNewOrderId()
        stat, resp = self.mp.PaymentStart(self.orderid, amount)
        if not stat:
            print ("Error code: " +str(resp))
            self.mp.PaymentCancel()
            if resp['StatusCode'] ==50:
                print ("Payment already in progress: cancled" +str(resp))
                stat, resp = self.mp.PaymentStart(self.orderid, amount)
                if not stat:
                    print ("Error code: " +str(resp))
                    self.mp.PaymentCancel()
                    
        frame = self.frames[page_name]
        frame.tkraise()
        time.sleep(0.01)
        succes, paymentstatus = self.mp.GetPaymentStatus(self.orderid)
        paymentdata = self.paymentdatafile.get(self.orderid, {self.orderid:{}})
        paymentstatus["Pulsecntstat"]  = False
        paymentdata=paymentstatus
        self.paymentdatafile[self.orderid] = paymentdata
        self.WritePaymentFile(self.paymentdatafile) 
        self.pt = Timer(30.0, self.paymenttimeout,["PaymentTimeOut"]) 
        self.pt.start()
        self.after(10, self.PaymentStatus)

                  
    def setupadammodule(self):
        set = appsettings.get('Adam','')
        self.adamhost = set.get('host',"192.168.1.200")
        self.pulseport = set.get('pulseport', 2)
        self.pulsetime_low = set.get('pulseporttime_low_ms',300)
        self.pulsetime_high = set.get('pulseporttime_high_ms',100)
        
        self.VendingstatusPort = set.get('VendingstatusPort',3)
        logging.info("Connecting iomodule ip " + str(self.adamhost))
        self.iomodule = adam.adam6000(logging, str(self.adamhost))
        self.iomodulestat,_ = self.iomodule.connect()
        logging.info("Connecting status: " + str(self.iomodulestat))
        return self.iomodulestat
           
    def readveningemptystatus(self):
        try:
            if self.debug:
                return True
            statbit  = self.iomodule.readinputbit(int(self.VendingstatusPort))
            logging.info("Vending stat bit " + str(statbit))
            return statbit
        except:
            return 0
            
        
    def setupcoinoktimer(self):
        iscoinsleftok = appsettings.get("setupcoinoktimer",120)
        s.enter(1, 1, RunTask, (s,iscoinsleftok, self.iomodule,))
        s.run()
 
    def setup_mp(self):
        mpsetting =  appsettings.get('Mobilepay', {'url':'https://sandprod-pos2.mobilepay.dk/API/V08/','PoSUnitIdToPos':'100000625947428'})
        url = mpsetting.get ('url','https://sandprod-pos2.mobilepay.dk/API/V08/')
        PoSUnitIdToPos =  mpsetting.get('PoSUnitIdToPos','100000625947428')
        LocationId =  mpsetting.get('LocationId','00001')
        Name=  mpsetting.get('Name','DinoCoin')
        MerchantId = mpsetting.get('MerchantId','POSDKDC307')
        key = mpsetting.get('key','344A350B-0D2D-4D7D-B556-BC4E2673C882') 
        logging.info("Connecting Mobile pay ")
        self.mp = MobilePayImpl.mpif(key=key, MerchantId=MerchantId, LocationId=LocationId, url=url, Name=Name)
        logging.info("RegisterPOS")
        posid = mpsetting.setdefault('posid',None)
        self.mp.PosId = posid
        self.mp_stat, posid = self.mp.StartUpReg()
        if self.mp_stat:
            mpsetting['posid'] = posid
            appsettings['Mobilepay'] = mpsetting
            WriteSetupFile(appsettings)
            logging.info("AssignPos" + str(PoSUnitIdToPos))
            self.mp_stat = self.mp.AssignPoSUnitIdToPos(PoSUnitIdToPos)
            self.runrefundonmissed()
        logging.info(self.mp_stat)

        return self.mp_stat
           
    def runrefundonmissed(self):
        self.paymentdatafile = self.ReadPaymentFile()
        if len(self.paymentdatafile) > 1:
            for key, value in self.paymentdatafile.items():
                if value['Pulsecntstat'] != True:
                    logging.info("Payment Failed: " +str(value))
                    logging.info("Refund : " +str(key))
                    refundbefore = self.paymentdatafile[key].get('Refund',False)
                    if not refundbefore:
                        self.paymentdatafile[key]['Refund']=True                  
                        self.mp.PaymentRefund(value['OrderId'], value['Amount'])
                        self.WritePaymentFile(self.paymentdatafile)
        return True       
    
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
        bgcolor='grey94'
        fr=Frame(self,bg=bgcolor)
        fr.pack(fill=X,side=TOP, pady= 0)
        fr=Frame(fr,bg=bgcolor)
        fr.pack(fill=Y,side=TOP, pady= 55)
        
        fifty = Image.open("img/50kr.png")
        #fifty.resize((10, 10), Image.ANTIALIAS)
        fifty_render = ImageTk.PhotoImage(fifty)
        hundred = Image.open("img/100kr.png")
        hundred_render = ImageTk.PhotoImage(hundred)
        twohundred = Image.open("img/200kr.png")
        twohundred_render = ImageTk.PhotoImage(twohundred)
        if self.controller.debug:        
            button_01 = tk.Button(fr, bg=bgcolor,text="0.1 Kr",  font=ft, borderwidth=2,
                           command=lambda: controller.InitPayment("StartPayment",0.1))
            button_1 = tk.Button(fr, bg=bgcolor,text="1 Kr", font=ft,  borderwidth=2,
                           command=lambda: controller.InitPayment("StartPayment",1))
            button_01.pack(side=tk.LEFT, padx=15)
            button_1.pack(side=tk.LEFT, padx=15)
            
        button_50 = tk.Button(fr, image=fifty_render, bg=bgcolor,text="50 Kr",  borderwidth=0,
                           command=lambda: controller.InitPayment("StartPayment",50))

        button_50.image = fifty_render
        button_100 = tk.Button(fr, image=hundred_render,bg=bgcolor, borderwidth=0, text="100 Kr",
                           command=lambda: controller.InitPayment("StartPayment",100))
        button_100.image = hundred_render
        button_200 = tk.Button(fr, image=twohundred_render, bg=bgcolor, borderwidth=0, text="200 Kr",
                           command=lambda: controller.InitPayment("StartPayment",200))
        button_200.image = twohundred_render
        
        button_50.pack(side=tk.LEFT, padx=15)
        button_100.pack(side=tk.LEFT, padx=15)
        button_200.pack(side=tk.LEFT, padx=15)
        fr2=Frame(self,bg=controller.background)
        fr2.pack(fill=Y, side=TOP, pady= 20)
       
        str = 'Én polet = 1 kr. Poletter kan ikke veksles til kontanter.'
        label = tk.Label(fr2, text=str, font=ft, background=controller.background)
        label.pack(side="top", fill="y", pady=0)
        
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
        
        label = tk.Label(fr2, text=str, font=ft, background=controller.background)
        label.pack(side=tk.RIGHT, padx=0, pady=0)
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
        label = tk.Label(self, text="Åbn appen og hold telefon mod mobilepay terminal,", background=controller.background, font=controller.title_font)
        label.pack(side="top", fill="x", pady=15)
        
        load = Image.open("img/Confirm_Payment.png")
        render = ImageTk.PhotoImage(load)
        label = tk.Label(self, image=render,text="",background=controller.background)
        label.image = render
        label.pack(pady=80)
        
        load = Image.open("img/back.png")
        render = ImageTk.PhotoImage(load)
        button = tk.Button(self, image=render, text="Go to the start page",bg=controller.background,borderwidth=0,
                           command=lambda: controller.mp.PaymentCancel())
        button.image = render
        button.pack(pady=40)
       
        fr2=Frame(self,bg=controller.background)
        fr2.pack(fill=X, side=tk.BOTTOM, padx= 0,expand=YES)
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
        label.pack(side="top", fill="x", pady=5)
  
        load = Image.open("img/Payment failed.png")
        render = ImageTk.PhotoImage(load)
        label = tk.Label(self, image=render,text="",background=controller.background)
        label.image = render
        label.pack(pady=150)
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
        label.pack(side="top", fill="x", pady=5)
        
        
        load = Image.open("img/Payment accepted.png")
        render = ImageTk.PhotoImage(load)
      
        render = ImageTk.PhotoImage(load)
        label = tk.Label(self, image=render,text="",background=controller.background)
        label.image = render
        label.pack(pady=150)
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
            db_file.write(json.dumps({'Mobilepay':{'url':'https://sandprod-pos2.mobilepay.dk/API/V08/'},'App':{'xpos':2560},'Adam':{'host':"192.168.1.200",'pulseport':2,'pulseporttime_low_ms':100,'pulseporttime_high_ow_ms':300,'VendingstatusPort':1}}))
    data = None
    with io.open(mainsetupfile, 'r') as jsonFile:
        try:
            data = json.load(jsonFile) 
        except Exception as e: 
            print('Error in setup file: ' + mainsetupfile, e)
    return data




if __name__ == '__main__':
   # try:
        logging.info("Running DinoPay")
        logging.info("Reading Setupfile")
        appsettings = ReadSetupFile()
        app = AppMain()
        x=datetime.today()
        y = x.replace(day=x.day, hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        delta_t=y-x       
        secs=delta_t.total_seconds()
        #secs =10
        t = Timer(secs, restart)
        t.start()
        app.mainloop()
