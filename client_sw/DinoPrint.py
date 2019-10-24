from pywinauto.application import Application
from datetime import datetime,timedelta
from threading import Timer
import logging
import json
import tkinter as tk
import os,io,sys
from GUI import  MainGui

__status__  = "production"
# The following module attributes are no longer updated.

__date__    = "18092019"
__version__ = "1.5_" +__date__

def restart():
        """ Safely restart prism """
        import os
        import sys
        import psutil
        import logging

        try:
            Print("Restarting App")
            p = psutil.Process(os.getpid())
            for handler in p.open_files() + p.connections():
                os.close(handler.fd)
        except Exception as e:
            logging.error(e)

        python = sys.executable
        os.execl(python, python, *sys.argv) 


def DinoPrint():

    x=datetime.today()
    y = x.replace(day=x.day, hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    delta_t=y-x       
    secs=delta_t.total_seconds()
# secs =10
#t = Timer(secs, restart)
#t.start()
    root = tk.Tk()
    root.version = __version__
    root.appsettings = ReadSetupFile()
    root.iconbitmap(r'DinoPrint.ico')
    app =MainGui.App(root)
    app.root.mainloop()

def ReadSetupFile():
    FilePath = 'C:\\ProgramData\\DinoCoin\\DinoPrint\\'
    mainsetupfile =FilePath+ 'MainSetup.json'
    
    if not os.path.exists(os.path.dirname(mainsetupfile)):
        try:
            os.makedirs(os.path.dirname(mainsetupfile))
        except Exception as e: 
            print('MainSetupFile make dirs read error: ' + mainsetupfile, e)
            
    if os.path.isfile(mainsetupfile) and os.access(mainsetupfile, os.R_OK):
        print ("Local mainsetupfile exists and is readable")
    else:
        with io.open(mainsetupfile, 'w') as db_file:
            db_file.write(json.dumps({'Adam':[{'host':"192.168.1.200"}]}))
    data = None
    with io.open(mainsetupfile, 'r') as jsonFile:
        data = json.load(jsonFile) 
    return data       

if __name__ == '__main__':
  
    while True:
        try:
            DinoPrint()
        except Exception as e:
            os.startfile(__file__)
            sys.exit()
            logging.error("main exception:" +str(e))
            pass
        else:
            break
        