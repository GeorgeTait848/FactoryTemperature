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
        #assumes roof is top side, not a regular factory roof. 
        #assumes no heat loss to floor.
        return 2*self.l*self.h + 2*self.w*self.h + self.l*self.w

    def getVolume(self) -> float: 
        return self.l * self.w * self.h

    def getSurfaceAreaToVolumeRatio(self) -> float:
        return self.getSurfaceArea()/self.getVolume