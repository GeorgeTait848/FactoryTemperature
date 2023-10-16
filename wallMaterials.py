from enum import Enum


class ThermalConductivity(Enum): 
    CONCRETE = 0.8
    STEEL = 50.2


class Cuboid(): 
    def __init__(self, l: float, w: float, h: float):
        self.l = l
        self.w = w
        self.h = h

    def getSurfaceArea(self) -> float: 
        return 0 #change to get actual value 

    def getVolume(self) -> float: 
        return self.l * self.w * self.h

    def getSurfaceAreaToVolumeRatio(self) -> float:
        return self.getSurfaceArea()/self.getVolume