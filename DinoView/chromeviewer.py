import logging
from selenium import webdriver
from selenium.webdriver.support import ui
from selenium.webdriver.chrome.options import Options

class cv():
    
    def __init__(self,url, monitornum):
        self.url = url
        self.Version = 1.0
        self.Description = "Module handlng chromebrowser"
        self.chrome_options = Options()
        self.monitornum = monitornum
        self.driver = None
        self.setOptions()

    def setOptions(self):
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--start-maximized")
        if self.monitornum == 2:
            self.chrome_options.add_argument("--window-position=2000,0")
        self.chrome_options.add_argument("--disable-web-security")
        self.chrome_options.add_argument("--disable-infobars")
        self.chrome_options.add_argument("--ignore-certificate-errors")
        self.chrome_options.add_argument("--kiosk")
        self.chrome_options.add_argument("--disable-password-manager-reauthentication")
            
    def startbrowser(self):
        try:
            self.driver = webdriver.Chrome(options=self.chrome_options)
            self.winHnd = self.driver.window_handles;
            self.driver.get(self.url)
        except Exception as e:
            logging.error("main exception:" +str(e)) 
    
    def refreshbrowser(self):
        self.driver.refresh();
   