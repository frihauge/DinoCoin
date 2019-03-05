import logging
import json
import tkinter as tk
from GUI import  MainGui


   
def DinoPrint():
    global VersionNumber
    root = tk.Tk()
    root.iconbitmap(r'DinoPrint.ico')
    app =MainGui.App(root)
    app.root.mainloop()
    
    
     

if __name__ == '__main__':
    try:
        DinoPrint()
    except Exception as e:
        logging.log("main exception:" +str(e))
        
    