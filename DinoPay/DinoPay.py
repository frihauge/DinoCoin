import logging
import requests
import json
import os,io
import sys
import tkinter as tk
from sched import scheduler
import time
from tkinter import *                
from tkinter import font  as tkfont 
from PIL import Image, ImageTk
from datetime import datetime
from threading import Timer
from _codecs import decode
from pywinauto.win32defines import BACKGROUND_BLUE
sys.path.append('../Modules')
from AdamModule import adam
from MobilePay import MobilePayImpl
logname = "DinoPay.log"
logging.basicConfig(filename=logname,
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)
appsettings = 0
s = scheduler(time, time.sleep)




def restart():
    print("#Restart")
    python = sys.executable
    os.execl(python, python, * sys.argv)

def RunTask(sc,rt,iomodule): 
    print ("Check adam for coins ok ")
    # do your stuff
    vendingstat = iomodule.readinputbit(num)
    if not vendingstat:
        s.enter(rt, 1, RunTask, (sc,rt,))
        self.show_frame("VendingEmpty")

class AppMain(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        small = 0
        self.title_font = tkfont.Font(family='Helvetica', size=36, weight="bold", slant="italic")
        self.background = 'light gray'
        self.background = "SystemButtonFace"
        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        root = tk.Tk._root(self)
        #root.overrideredirect(True)
        root.state('zoomed')
        root.call('encoding', 'system', 'utf-8')
        
        print ("Geo Info Screen high: " + str(root.winfo_screenheight()) + "Screen width: "+str(root.winfo_screenwidth()))
        root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth()-small+3000, root.winfo_screenheight()-small))
        #root.state('zoomed')

        #root.attributes('-fullscreen', True)
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        container.config(background = self.background)

      
         
        self.setupadammodule()   
        self.setup_mp() 
        # self.setupcoinoktimer()
        self.frames = {}
        for F in (StartPage, PayWithMobilePay, StartPayment,PaymentAccepted, PaymentFailed, VendingEmpty):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")
            frame.configure(background=self.background)
        self.show_frame("StartPage")
        
    def PaymentStatus(self):
        print("Payment status")
        paied = False
        if self.mp is not None:
            success = self.mp.GetPaymentStatus(self.orderid)
            paied = success['PaymentStatus'] ==100
        if not paied:    
            self.after(1000, self.PaymentStatus)
        else:
            self.ft = Timer(5.0, self.FrameTimeOut) 
            self.ft.start()
            self.show_frame("PaymentAccepted") 
            self.paymentHandle(success)  
    def paymentHandle(self,paymentstatus):
        if(paymentstatus['PaymentStatus']==100):
           Amount = paymentstatus['Amount']
           self.iomodule.PulsPort(self.pulsport, self.pulstime)
    def FrameTimeOut(self):
        print("Frame Time out!")
        self.show_frame("StartPage")
                   
    def paymenttimeout(self):
        print("Payment Time out!")
         
        if self.mp is not None:
            print("Payment Time out!" + str(self.orderid))
            logging.info("Payment TimeOut" + str(self.orderid))
            self.mp.PaymentCancel()
            self.ft = Timer(5.0, self.FrameTimeOut) 
            self.ft.start()
        
    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()

    def InitPayment(self, page_name, amount=None):
        ## STart new payment
        if not self.readveningemptystatus():
            self.ft = Timer(5.0, self.FrameTimeOut) 
            self.ft.start()
            return False
        self.orderid = self.mp.getNewOrderId()
        self.mp.PaymentStart(self.orderid, amount)
        frame = self.frames[page_name]
        self.pt = Timer(60.0, self.paymenttimeout) 
        self.pt.start()
        frame.tkraise()
        self.after(10, self.PaymentStatus)

                  
    def setupadammodule(self):
        set = appsettings.get('Adam',{'host':"192.168.1.200",'pulseport':"2",'pulseporttime_ms':"10",'VendingstatusPort':"10"})
        self.adamhost = set.get('host')
        self.pulstime = set.get('pulseport', 2)
        self.pulsport = set.get('pulseporttime_ms',10)
        self.VendingstatusPort = set.get('VendingstatusPort',3)
        logging.info("Connecting iomodule ip " + str(self.adamhost))
        self.iomodule = adam.adam6000(logging, str(self.adamhost))

           
    def readveningemptystatus(self):
        statbit  = self.iomodule.readinputbit(int(self.VendingstatusPort))
        logging.info("Vending stat bit " + str(statbit))
        return statbit
            
        
    def setupcoinoktimer(self):
        iscoinsleftok = appsettings.get("setupcoinoktimer",120)
        s.enter(1, 1, RunTask, (s,iscoinsleftok, self.iomodule,))
        s.run()
 
    def setup_mp(self):
        setting =  appsettings.get('Mobilepay', {'url':'https://sandprod-pos2.mobilepay.dk/API/V08/','PoSUnitIdToPos':'100000625947428'})
        url = setting.get ('url','https://sandprod-pos2.mobilepay.dk/API/V08/')
        PoSUnitIdToPos =  setting.get('PoSUnitIdToPos','100000625947428')

        logging.info("Connecting Mobile pay ")
        self.mp = MobilePayImpl.mpif()
        logging.info("RegisterPOS")
        stat = self.mp.RegisterPoS()
        logging.info(stat)
        logging.info("AssignPos")
        stat = self.mp.AssignPoSUnitIdToPos("100000625947428")
        logging.info(stat)
        
class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        mp = MobilePayImpl.mpif()
        label = tk.Label(self, text="Betal med mobile pay", font=controller.title_font,background=controller.background)
        label.pack(side="top", fill="x", pady=10)
        
        load = Image.open("img/BT_PayMP.png")
        render = ImageTk.PhotoImage(load)
      
        btPayWithMobilePay = tk.Button(self,image=render ,text="32121321",relief='raised',
                            command=lambda: controller.show_frame("PayWithMobilePay"))
        btPayWithMobilePay.image = render
        btPayWithMobilePay.pack(pady=300)


class PayWithMobilePay(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        txt ="Valg belob"
        label = tk.Label(self, text=txt, font=controller.title_font, background=controller.background)
        label.pack(side="top", fill="y", pady=20)
        fr=Frame(self)
        fr.pack(fill=Y, side=TOP, pady= 200)
        fifty = Image.open("img/50kr.png")
        fifty.resize((10, 10), Image.ANTIALIAS)
        fifty_render = ImageTk.PhotoImage(fifty)
        hundred = Image.open("img/100kr.png")
        hundred_render = ImageTk.PhotoImage(hundred)
        twohundred = Image.open("img/200kr.png")
        twohundred_render = ImageTk.PhotoImage(twohundred)
                

        button_50 = tk.Button(fr, image=fifty_render, text="50 Kr",
                           command=lambda: controller.InitPayment("StartPayment",50))

        button_50.image = fifty_render
        button_100 = tk.Button(fr, image=hundred_render, text="100 Kr",
                           command=lambda: controller.InitPayment("StartPayment",100))
        button_100.image = hundred_render
        button_200 = tk.Button(fr, image=twohundred_render,text="200 Kr",
                           command=lambda: controller.InitPayment("StartPayment",200))
        button_200.image = twohundred_render
        button_50.pack(side=tk.LEFT, padx=0)
        button_100.pack(side=tk.LEFT, padx=0)
        button_200.pack(side=tk.LEFT, padx=0)
        
class VendingEmpty(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        load = Image.open("img/vendingempty.png")
        render = ImageTk.PhotoImage(load)
        label = tk.Label(self, text="VendingEmpty", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        button = tk.Button(self, image=render, text="Go to the start page",
                           command=lambda: controller.show_frame("StartPage"))
        button.image = render
        button.pack(pady=300)

class StartPayment(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Confirm Payment", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        
        load = Image.open("img/Confirm_Payment.png")
        render = ImageTk.PhotoImage(load)
        button = tk.Button(self, image=render, text="Go to the start page",
                           command=lambda: controller.show_frame("StartPage"))
        button.image = render
        button.pack(pady=300)

class PaymentFailed(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Payment Failed Try again", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        
        
        load = Image.open("img/Payment failed.png")
        render = ImageTk.PhotoImage(load)
      
        failedbt = tk.Button(self,image=render ,text="32121321",relief='raised',
                            command=lambda: controller.show_frame("StartPage"))

        failedbt.image = render
        failedbt.pack(pady=300)
        
class PaymentAccepted(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Payment Accepted", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        
        
        load = Image.open("img/Payment accepted.png")
        render = ImageTk.PhotoImage(load)
      
        failedbt = tk.Button(self,image=render ,text="32121321",relief='raised',
                            command=lambda: controller.show_frame("StartPage"))

        failedbt.image = render
        failedbt.pack(pady=300)
        
    def showFrame(self,cont):
        rame = self.frames[cont]
        frame.tkraise()
        frame.update()
        frame.event_generate("<<ShowFrame>>")
          

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
            db_file.write(json.dumps({'Adam':{'host':"192.168.1.200",'pulseport':"2",'pulseporttime_ms':"10"}}))
    data = None
    with io.open(mainsetupfile, 'r') as jsonFile:
        data = json.load(jsonFile) 
    return data

  


if __name__ == '__main__':
   # try:
        logging.info("Running DinoPay")
        logging.info("Reading Setupfile")
        appsettings = ReadSetupFile()
        app = AppMain()
        x=datetime.today()
        y=x.replace(day=x.day+1, hour=0, minute=0, second=0, microsecond=0)
        delta_t=y-x
        secs=delta_t.seconds+1
        t = Timer(secs, restart)
        t.start()
        app.mainloop()
