import logging
import json
import subprocess
import sys
from datetime import datetime
from threading import Timer
from time import time, sleep
from sched import scheduler
import os,io
import chromeviewer

logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
rootLogger = logging.getLogger()

fileHandler = logging.FileHandler("{0}/{1}.log".format('.\\', 'DinoView'))
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)


s = scheduler(time, sleep)

webhost = "www.dinocoin.frihauge.dk"
FilePath = 'C:/ProgramData/DinoCoin/DinoView/'
httptrackpath = r"C:\Program Files\WinHTTrack\httrack.exe"
defaultweburl = r"http://www.dinocoin.frihauge.dk/foyer/testdisplay" 
__status__  = "production"
# The following module attributes are no longer updated.

__date__    = "28042019"
__version__ = "1.1_" +__date__

def restart():
    print("#Restart")
    python = sys.executable
    os.execl(python, python, * sys.argv)


def RunTask(sc, br, rt): 
    print ("Doing stuff...")
    UpdateWeb()
    br.refreshbrowser()
   # do your stuff
    s.enter(rt, 1, RunTask, (sc,br,rt,))
       
def DinoView():
    version = __version__
    print("App.Version: "+ version)
    if not os.path.isfile(httptrackpath):
        raise Exception('Cant find httptrack.exe in: '+httptrackpath)
    refreshtime = appsettings.get("refreshtime",120)
    br = ShowBrowser(appsettings)
    s.enter(1, 1, RunTask, (s,br,refreshtime,))
    s.run()


def ShowBrowser(appsettings):
    screen = appsettings.get("WebUrl","testdisplay")
    winpos = appsettings.get("winpos","3000,0")
    url = r"file:///C:/ProgramData/DinoCoin/DinoView/web/www.dinocoin.frihauge.dk/foyer/testdisplay/index.html"
    url = r"file://"+FilePath+"/web/"+ webhost +"/foyer/" + screen +"/index.html"
    print ("URL: for view " + url)
    #DownLoadWeb(appsettings)
    br = chromeviewer.cv(url,winpos)
    br.startbrowser()
    return br
    

    
    
def DownLoadWeb(appsettings):
    client = appsettings.get("WebUrl","testdisplay") 
    weburl = r"http://www.dinocoin.frihauge.dk/foyer/"+ client
    subprocess.call([httptrackpath, weburl, "-O", FilePath+"web"])
    
def UpdateWeb():
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    client = appsettings.get("WebUrl","testdisplay") 
    weburl = r"http://www.dinocoin.frihauge.dk/foyer/"+ client
    pinfo = subprocess.call([httptrackpath,"--update",weburl,"-O", FilePath+"web" ], startupinfo=si)
    print(pinfo)
 
    
def ReadSetupFile():
    mainsetupfile =FilePath+ 'DinoViewSetup.json'
    
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
    try:
        appsettings = ReadSetupFile()
        x=datetime.today()
        y = x.replace(day=x.day, hour=1, minute=0, second=0, microsecond=0) + timedelta(days=1)
        delta_t=y-x       
        secs=delta_t.total_seconds()
        t = Timer(secs, restart)
        t.start()
        DinoView()
    except Exception as e:
        logging.error("main exception:" +str(e))
        
    