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
from . import receiptrenderer

class custom():
    
    def __init__(self, log):
        self.Version = 1.0
        self.Description = "Setup Custom printer"
        self.logger = log
        self.printer_name = 'CUSTOM VKP80 II'
        self.hPrinter = win32print.OpenPrinter (self.printer_name)
        if self.hPrinter == None:
            print('No printer installed')
     

    def printlabel(self,prizeLabel):
        filename = 'receipt.pdf'
        r = receiptrenderer.ReceiptRenderer(widthBuffer=20, offsetLeft=8)
        r.render(filename, prizeLabel, ''.join(random.choice('0123456789') for _ in range(10)), ''.join(random.choice(string.ascii_uppercase + '0123456789') for _ in range(10)))
        time.sleep(.1)
        test = win32api.ShellExecute (
            0,
            "print",
            filename,
            #
            # If this is None, the default printer will
            # be used anyway.
            #
            '/d:"%s"' % printer_name,
            ".",
            0
            )
if __name__ == '__main__':
    co = custom(None)
    co.printlabel("prizeLabel")
    