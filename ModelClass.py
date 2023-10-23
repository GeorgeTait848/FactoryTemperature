import numpy as np
import scipy as sp
import math
from heater import Heater
from wallMaterials import ThermalConductivity, Cuboid
from outsideTemp import OutsideEnvironment

AIR_SPECIFIC_HEAT_CAPACITY = 1.2 # kJ m^-3 K^-1

start = 0
end = 24
step = 0.1
time_points = [start + i * step for i in range(int((end - start) / step) + 1)] #measure temp over 24hrs

class Factory:

    def __init__(self, ind_temp: float, surface_walls: Cuboid, 
                conductivity: ThermalConductivity, 
                heater: Heater, 
                outsideEnv: OutsideEnvironment,
                wallThickness: float):

        self.ind_temp = ind_temp
        self.surface_walls = surface_walls
        self.conductivity = conductivity
        self.heater = heater
        self.wallThickness = wallThickness
        self.outdoors = outsideEnv


    def nonDimensionalisedTemperatureDerivative(self, currentTime: float) -> float: 

        P_in = self.heater.heatOutputRate
        heatCapacity = AIR_SPECIFIC_HEAT_CAPACITY*self.surface_walls.getVolume()
        surfaceArea = self.surface_walls.getSurfaceArea()
        outsideTemp = self.outdoors.getCurrentOutsideTemperature(currentTime)

        return P_in/heatCapacity - self.conductivity*surfaceArea/(self.wallThickness*heatCapacity)*(self.ind_temp - outsideTemp)


        
        
    
    


