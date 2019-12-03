import logging
import json
import subprocess
import sys
import os
import shutil
import urllib.request
from datetime import datetime
from threading import Timer
from time import time, sleep
from datetime import datetime,timedelta
from sched import scheduler
import os,io
import chromeviewer
sys.path.append('../Modules')
import tools.Internettools

br = None
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
        """ Safely restart  """
        import os
        import sys
        import psutil
        import logging

        try:
            print("Restarting App")
            br.stopbrowser()
            os.system("taskkill /im chromedriver.exe /F")
            p = psutil.Process(os.getpid())
            for handler in p.open_files() + p.connections():
                try:
                    os.close(handler.fd)
                except Exception as e:
                    print(e)
        except Exception as e:
            logging.error(e)

        python = sys.executable
        os.execl(python, python, *sys.argv) 
def internet_on():
    return tools.Internettools.PingDinoCoinWeb()


def RunTask(sc, br, rt): 
    print ("Doing stuff...")
    if internet_on():
        print("Network OK")
        print ("Updateweb")
        UpdateWeb()    
        print ("Refresh Browser")
        if internet_on():
            br.refreshbrowser()
        sc.enter(rt, 1, RunTask, (sc,br,rt,))
    else:
        print("Network DOWN!")
        sc.enter(rt, 1, RunTask, (sc,br,rt,))

   # do your stuff

       
def DinoView():
    version = __version__
    x=datetime.today()
    print(x)
    y = x.replace(day=x.day, hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    delta_t=y-x       
    secs=delta_t.total_seconds()
    #secs =10
    #t = Timer(secs, restart)
    #t.start()
    print("App.Version: "+ version)
    if not os.path.isfile(httptrackpath):
        raise Exception('Cant find httptrack.exe in: '+httptrackpath)
    if not os.path.exists(FilePath+"web"):
        try:
            os.makedirs(FilePath+"web")
        except Exception as e: 
            print('make dirs error: ' + FilePath+"web", e)
    
    
    refreshtime = appsettings.get("refreshtime",120)
    br = ShowBrowser(appsettings)
    s.enter(1, 1, RunTask, (s,br,refreshtime,))
    s.run()


def ShowBrowser(appsettings):
    screen = appsettings.get("WebUrl","testdisplay")
    winpos = appsettings.get("winpos","4000,0")
    url = r"file:///C:/ProgramData/DinoCoin/DinoView/web/www.dinocoin.frihauge.dk/foyer/testdisplay/index.html"
    url = r"file://"+FilePath+"web/"+ webhost +"/foyer/" + screen +"/index.html"
    print ("URL: for view " + url)
    #global br
    br = chromeviewer.cv(url,winpos)
    br.stopbrowser()
    br.startbrowser()
    
    return br
    

    
def UpdateWeb():
    try:
        shutil.rmtree(FilePath+"web_tmp")
    except:
        pass
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    #flags =  """-qiC1%Ps2u1%s%uN0%I0p3DdK0H0%kf2A25000%f#f -F "Mozilla/4.5 (compatible; HTTrack 3.0x; Windows 98)" -%F "<!-- Mirrored from %s%s by HTTrack Website Copier/3.x [XR&CO'2014], %s -->" -%l "en, *" http://www.dinocoin.frihauge.dk/foyer/dinocoin1/ -O1 "C:\fri\dc" +*.png +*.gif +*.jpg +*.jpeg +*.css +*.js -ad.doubleclick.net/* -mime:application/foobar"""
    flags =  """-qiC1%Ps2u1%s%uN0%I0p3DdK0H0%kf2A25000%f#f -F "Mozilla/4.5 (compatible; HTTrack 3.0x; Windows 98)" -%F "<!-- Mirrored from %s%s by HTTrack Website Copier/3.x [XR&CO'2014], %s -->" -%l "en, *"""
    flags2 =  '+*.png +*.gif +*.jpg +*.jpeg +*.css +*.js -ad.doubleclick.net/* -mime:application/foobar'
    
    client = appsettings.get("WebUrl","testdisplay") 
    weburl = r"http://www.dinocoin.frihauge.dk/foyer/"+ client
    pinfo = subprocess.call([httptrackpath,flags,"--update", weburl,"-O1", FilePath+"web_tmp" ,flags2], startupinfo=si)
    if internet_on():
        copytree(FilePath+"web_tmp", FilePath+"web")
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

def copytree(src, dst, symlinks=False, ignore=None):
    try:
        shutil.rmtree(dst)
    except:
        pass
    finally:
        shutil.copytree(src, dst, symlinks=False, ignore=None, copy_function=shutil.copy, ignore_dangling_symlinks=False)
        
if __name__ == '__main__':
    while True:
        try:
            appsettings = ReadSetupFile()
            UpdateWeb() 
            DinoView()
        except Exception as e:
            logging.error("main exception:" +str(e))
            logging.error("Trying to kill chromedriver")
            os.system("taskkill /im chromedriver.exe /F")
            logging.error("Trying to kill chrome.exe")
            os.system("taskkill /im chrome.exe /F")
            pass
        else:
            break
    