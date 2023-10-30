import numpy as np

class OutsideEnvironment(): 
    def __init__(self, meanT: float, halfrangeT: float):
        self.meanT = meanT
        self.halfrangeT = halfrangeT 

        # meanT = 8, halfrangeT = 4 for winter temps 4-12C
        # meanT = 19, halfrangeT = 5 for summer temps 14-24C
        
    def outsideTemp(self) -> float: 
        global time_points
        return self.halfrangeT * np.sin((np.pi/12)*(time_points - 9))+self.meanT

    
    def getCurrentOutsideTemperature(self, currentTime: float) -> float: 
        global currentTime
        return self.halfrangeT * np.sin((np.pi/12)*(currentTime - 9))+self.meanT
