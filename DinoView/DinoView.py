import logging
import json
import subprocess
import sys
from time import time, sleep
from sched import scheduler
import os,io

if sys.platform.startswith('linux'):
    from systems.linux import System
elif sys.platform.startswith('darwin'):
    from systems.mac import System
elif sys.platform.startswith('win32'):
    from systems.win import System
else:
    raise SystemExit('Sorry, multibrowse is not supported for your platform ({}).'.format(sys.platform))
system = System()
s = scheduler(time, sleep)

FilePath = 'C:\\ProgramData\\DinoCoin\\DinoView\\'
httptrackpath = r"C:\Program Files\WinHTTrack\httrack.exe"
defaultweburl = "http://www.dinocoin.frihauge.dk/foyer/default/"  
__status__  = "production"
# The following module attributes are no longer updated.

__date__    = "26032019"
__version__ = "1.0_" +__date__

def RunTask(sc): 
    print ("Doing stuff...")
    UpdateWeb()
    url = r"file:///C:/ProgramData/DinoCoin/DinoView/web/www.dinocoin.frihauge.dk/foyer/testdisplay/index.html"
   
   # system.close_existing_browsers()
    system.open_browser(url, 1)
    system.clean_up()  

    # do your stuff
    s.enter(10, 1, RunTask, (sc,))
       
def DinoView():
    version = __version__
    appsettings = ReadSetupFile()
    #DownLoadWeb(appsettings)
    s.enter(1, 1, RunTask, (s,))
    s.run()
    
def DownLoadWeb(appsettings):
    weburl = appsettings.get("WebUrl",defaultweburl) 
    subprocess.call([httptrackpath, weburl, "-O", FilePath+"web"])
def UpdateWeb():
    pinfo = subprocess.call([httptrackpath,"--update","-O", FilePath+"web" ])
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
        DinoView()
    except Exception as e:
        logging.error("main exception:" +str(e))
        
    