#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
@author: EFRI
Frihauge IT
"""
##from . import receiptrenderer
from subprocess import call
import time
import random, string
import os, sys
import win32print
import win32api
import subprocess
#import receiptrenderer
from . import receiptrenderer

class custom():
    
    def __init__(self, log):
        self.Version = 1.0
        self.Description = "Setup Custom printer"
        self.logger = log
        self.printer_name = 'CUSTOM VKP80 II'
        self.printfilepath = './tmp'
        try:
            self.hPrinter = win32print.OpenPrinter (self.printer_name)
        except:
            print('No printer installed')
        if not os.path.isdir(self.printfilepath): 
            os.mkdir(self.printfilepath)       # line B
         
     



    def printlabel(self,prizeLabel):
        filename = self.printfilepath+'/receipt.pdf'
        try:
            self.logger.info("Render receipt")
            r = receiptrenderer.ReceiptRenderer(widthBuffer=20, offsetLeft=8)
            r.render(filename, prizeLabel, ''.join(random.choice('0123456789') for _ in range(10)), ''.join(random.choice(string.ascii_uppercase + '0123456789') for _ in range(10)))
            time.sleep(.5)
            self.logger.info("Send to printer")
            printfileabs = os.path.abspath(filename)
            self.printusingwrapper()
            return True
            
            if (os.path.isfile(filename)):
                hinstance = win32api.ShellExecute (
                    0,
                    "print",
                    printfileabs,
                #
                # If this is None, the default printer will
                # be used anyway.
                #
                    '/d:"%s"' % self.printer_name,
                    ".",
                    0
                    )
                time.sleep(0)
                #os.system("TASKKILL /F /IM AcroRD32.exe")
#            os.remove(filename)
            else:
                return False

            return hinstance

        except Exception as e:
            print(e)
            
            
    def printusingwrapper(self):
        filename = self.printfilepath+'/receipt.pdf'
        # acrowrap.exe /t "receipt.pdf" "CUSTOM VKP80 II"
        #acrorun = args + os.path.join(os.getcwd(), 'receipt.pdf').replace('\\', '\\\\')
        subprocess.call(["acrowrap.exe","/t" ,filename, "CUSTOM VKP80 II"])
           # subprocess.check_output(ghostscript)

if __name__ == '__main__':
    co = custom(None)
    co.printusingghostscript()
   # co.printlabel("prizeLabel")
    
