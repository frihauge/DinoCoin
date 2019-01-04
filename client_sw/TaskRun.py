import logging
from PrizeModule import Prize as Pr
from AdamModule import adam



class TaskRun():
    
    
    def __init__(self, log):
        self.Version = 1.0
        self.logger = log
        self.Description = "Module TaskRun"
        self.logger.info("Connecting iomodule ip 192.168.50.15")
        self.iomodule = adam.adam6000("192.168.50.15")
        succes = self.iomodule.connect()
        self.iomodule.writepoutputport(0,True)
     
  
    def run(self):
        stat = self.iomodule.readinputno(0)
        if (stat > 0 ):
            self.logger.log(logging.INFO,"Generateprize()")
        if stat == -1:
            self.logger.log(logging.INFO,"Pinging port 0 stat:"+ str(stat))
                    
            