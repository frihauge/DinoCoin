#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
@author: EFRI
Frihauge IT
"""

import time


class dbif():

    def __init__(self):
        self.Version = 1.0
        self.Description = "Interface for database"
        self.data = None
        self.loadlocal()

    def loadlocal(self):
        with open('MainDinoClient.json', 'r') as f:
            self.data = json.load(f)
            return True

 