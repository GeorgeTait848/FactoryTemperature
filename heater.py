class Heater(): 

    def __init__(self, heatOutputRate: float, switchedOn: bool = False):
        self.heatOutputRate = heatOutputRate
        self.switchedOn = switchedOn

    def getHeatOutput(self, interval: float) -> float:
        if self.switchedOn: 
            return self.heatOutputRate*interval
        return 0

    def switchOn(self): 
        self.switchedOn = True
    
    def switchOff(self): 
        self.switchedOn = False

    def __bool__(self): 
        return self.switchedOn