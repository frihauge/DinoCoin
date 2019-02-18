import logging
import json
import tkinter as tk
from GUI import  MainGui


   
def DinoPrint():
   while True:
        try:
            root = tk.Tk()
            root.iconbitmap(r'DinoPrint.ico')
            app =MainGui.App(root)
            app.root.mainloop()
        except Exception as e:
            logging.log("main exception:" +str(e))
            pass
        else:
            break    
    
    
     

if __name__ == '__main__':
    DinoPrint()
    