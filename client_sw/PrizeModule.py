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
            
			
			
	def getRandomPrice(prizeType): # 1 or 2
    conn, _ = getConnection()

    c = conn.cursor()

    c.execute("SELECT id, supply, label FROM supply WHERE type = ?", (prizeType, ))
    data = c.fetchall()
    
    totalSupply = 0
    for row in data:
        totalSupply += row[1]
    
    if totalSupply == 0: # No more stuck
        return None
    
    n = random.randint(0, totalSupply - 1)
    winnerId = -1
    winnerLabel = ""
    
    for row in data:
        if n >= row[1]: # not this type
            n -= row[1]
        else:
            winnerId = row[0]
            winnerLabel = row[2]
            break
    
    if winnerId == -1: # should never happen
        return None

    c.execute("UPDATE supply SET supply = supply - 1, distributed = distributed + 1, distributed_total = distributed_total + 1 WHERE id = ?", (winnerId, ))

    c.close()
    conn.commit()
    conn.close()

    return winnerLabel