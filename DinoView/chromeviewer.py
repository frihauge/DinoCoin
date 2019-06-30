import logging
import psutil
import win32process
import win32process as process
import win32gui
import win32con
from selenium import webdriver
from selenium.webdriver.support import ui
from selenium.webdriver.chrome.options import Options

class cv():
    
    def __init__(self,url,windowpos="4000,0"):
        self.url = url
        self.Version = 1.0
        self.Description = "Module handlng chromebrowser"
        self.chrome_options = Options()
        self.windowposition = windowpos
        self.driver = None
        self.setOptions()

    def setOptions(self):
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--start-maximized")
        self.chrome_options.add_argument("--window-position="+ self.windowposition)
        self.chrome_options.add_argument("--disable-web-security")
        self.chrome_options.add_argument("--disable-infobars")
        self.chrome_options.add_argument("--ignore-certificate-errors")
        self.chrome_options.add_argument('--disable-gpu')
        # self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument("--kiosk")
        self.chrome_options.add_argument("--disable-password-manager-reauthentication")
            
    def startbrowser(self):
        try:
            self.driver = webdriver.Chrome(options=self.chrome_options)
            self.winHnd = self.driver.window_handles[0];
            self.driver.get(self.url)
            p = psutil.Process(self.driver.service.process.pid).children()[0].pid
            hnd = get_hwnds(p)[0]
            win32gui.SetWindowPos(hnd, win32con.HWND_TOPMOST, 0,0,0,0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        except Exception as e:
            logging.error("main exception:" +str(e)) 
    
    def refreshbrowser(self):
        self.driver.switch_to.window(self.driver.current_window_handle)
        self.driver.refresh();
        
    
def get_hwnds(pid):
    """return a list of window handlers based on it process id"""
    def callback(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
            _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
            if found_pid == pid:
                hwnds.append(hwnd)
        return True
    hwnds = []
    win32gui.EnumWindows(callback, hwnds)
    return hwnds 
   