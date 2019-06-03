import logging
import requests
import json
import os,io
import sys
import tkinter as tk
from tkinter import *                
from tkinter import font  as tkfont 
from PIL import Image, ImageTk
#sys.path.insert(0,r'c:\workspace\project\Dinocoin\SW\DinoCoin\client_sw\AdamModule')
import adam
from MobilePay import MobilePayImpl
logname = "DinoPay.log"
logging.basicConfig(filename=logname,
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)

logging.info("Running DinoPay")

class AppMain(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        root = tk.Tk._root(self)
        root.overrideredirect(True)
        root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, PayWithMobilePay, StartPayment):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")

    def show_frame(self, page_name, amount=None):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()

    def InitPayment(self, page_name,amount=None):
        ## STart new payment
        mp.PaymentStart(mp.getNewOrderId(),amount)
        frame = self.frames[page_name]
        frame.tkraise()

class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        mp = MobilePayImpl.mpif()
        label = tk.Label(self, text="Pay With MobilePay", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        
        load = Image.open("img/BT_PayMP.png")
        render = ImageTk.PhotoImage(load)
           # labels can be text or images
        img = tk.Label(self, image=render)
        img.image = render
        #img.place(x=0, y=0)
        
        btPayWithMobilePay = tk.Button(self,image=render ,text="32121321",relief='raised',
                            command=lambda: controller.show_frame("PayWithMobilePay"))
        
        btPayWithMobilePay.pack(pady=300)


class PayWithMobilePay(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Valg belob", font=controller.title_font)
        label.pack(side="top", fill="y", pady=10)
        fr=Frame(self)
        fr.pack(fill=Y, side=TOP, pady= 200)
        button_100 = tk.Button(fr, text="100 Kr",
                           command=lambda: controller.InitPayment("StartPayment",100))
        button_200 = tk.Button(fr, text="200 Kr",
                           command=lambda: controller.InitPayment("StartPayment",200))
        button_300 = tk.Button(fr, text="300 Kr",
                           command=lambda: controller.InitPayment("StartPayment",300))
        button_100.pack(side=tk.LEFT, padx=10)
        button_200.pack(side=tk.LEFT, padx=10)
        button_300.pack(side=tk.LEFT, padx=10)
        


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
        appsettings = ReadSetupFile()
        mp = MobilePayImpl.mpif()
        app = AppMain()
        app.mainloop()

        mp.reqResp()
        #except Exception as e:
        # logging.error("main exception:" +str(e))