import time
import socket
from customprinter import custom

class Prize():
    
    
    def __init__(self, host):
        self.Version = 1.0
        self.Description = "Module handlng prize"
        self._Prize = {0 : 'StdPrize', 1 : 'GoldPrize'}

    def newprize(self, prizetype):
        if prizetype == self._Prize['StdPrize']:
            prize = GetDBStdPrize()
        if prizetype == self._Prize['GoldPrize']:
            prize = GetDBGoldPrize()