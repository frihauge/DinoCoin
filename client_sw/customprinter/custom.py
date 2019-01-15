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
from . import receiptrenderer

class custom():
    
    def __init__(self, log):
        self.Version = 1.0
        self.Description = "Setup Custom printer"
        self.logger = log
        self.printer_name = 'CUSTOM VKP80 II'
        self.printfilepath = './tmp'
        self.hPrinter = win32print.OpenPrinter (self.printer_name)
        if self.hPrinter == None:
            print('No printer installed')
        if not os.path.isdir(self.printfilepath): 
            os.mkdir(self.printfilepath)       # line B
         
     



    def printlabel(self,prizeLabel):
        filename = self.printfilepath+'/receipt.pdf'
        r = receiptrenderer.ReceiptRenderer(widthBuffer=20, offsetLeft=8)
        r.render(filename, prizeLabel, ''.join(random.choice('0123456789') for _ in range(10)), ''.join(random.choice(string.ascii_uppercase + '0123456789') for _ in range(10)))
        time.sleep(.1)
        printfileabs = os.path.abspath(filename)
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
            time.sleep(2)
            os.system("TASKKILL /F /IM AcroRD32.exe")
            os.remove(filename)
        else:
            return False
        
        return hinstance
if __name__ == '__main__':
    co = custom(None)
    co.printlabel("prizeLabel")
    