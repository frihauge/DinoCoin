import logging
import requests
import json
import os,io
import sys
import tkinter as tk
from sched import scheduler
from time import time, sleep
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
s = scheduler(time, sleep)




def restart():
    print("#Restart")
    python = sys.executable
    os.execl(python, python, * sys.argv)

def RunTask(sc,rt,iomodule): 
    print ("Check adam for coins ok ")
    # do your stuff
    iomodule.readinputbit(num)
    s.enter(rt, 1, RunTask, (sc,rt,))

class AppMain(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        small = 200
        self.title_font = tkfont.Font(family='Helvetica', size=36, weight="bold", slant="italic")
        self.background = 'light gray'
        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        root = tk.Tk._root(self)
        root.overrideredirect(True)
        root.call('encoding', 'system', 'utf-8')

        root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth()-small, root.winfo_screenheight()-small))

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        container.config(background = self.background)
        self.setupadammodule()   
        self.setup_mp() 
        # self.setupcoinoktimer()
        self.frames = {}
        for F in (StartPage, PayWithMobilePay, StartPayment):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")
            frame.configure(background='light gray')
        self.show_frame("StartPage")

    def show_frame(self, page_name, amount=None):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()

    def InitPayment(self, page_name, amount=None):
        ## STart new payment
        mp.PaymentStart(mp.getNewOrderId(), amount)
        frame = self.frames[page_name]
        frame.tkraise()
        
    def setupadammodule(self):
        set =  appsettings.get('Adam', {'Adam':[{'host':"192.168.1.200"}]})
        adamhost = set[0]['host']
        logging.info("Connecting iomodule ip " + str(adamhost))
        self.iomodule = adam.adam6000(logging, str(adamhost))
        
    def readveningemptystatus(self):
        set =  appsettings.get('Adam', {'Adam':[{'emptyflag':"2"}]})
        emptyflagport = set[0]['emptyflag']
        self.iomodule.readinputbit(int(emptyflagport))
        logging.info("Connecting iomodule ip " + str(adamhost))
        
    def setupcoinoktimer(self):
        iscoinsleftok = appsettings.get("setupcoinoktimer",120)
        s.enter(1, 1, RunTask, (s,iscoinsleftok, self.iomodule,))
        s.run()
    def setup_mp(self):
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
        button_50.pack(side=tk.LEFT, padx=50)
        button_100.pack(side=tk.LEFT, padx=50)
        button_200.pack(side=tk.LEFT, padx=10)
        
class VendingEmpty(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="VendingEmpty", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        button = tk.Button(self, text="Go to the start page",
                           command=lambda: controller.show_frame("StartPage"))
        button.pack()

class StartPayment(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Confirm Payment", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        button = tk.Button(self, text="Go to the start page",
                           command=lambda: controller.show_frame("StartPage"))
        button.pack()

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
            db_file.write(json.dumps({'Adam':[{'host':"192.168.1.200"}]}))
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
