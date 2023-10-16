import numpy as np
import scipy as sp
import math
from heater import Heater
from wallMaterials import ThermalConductivity, Cuboid

AIR_SPECIFIC_HEAT_CAPACITY = 1.2 # kJ m^-3 K^-1

start = 0
end = 24
step = 0.1
time_points = [start + i * step for i in range(int((end - start) / step) + 1)] #measure temp over 24hrs

class Factory:

    def __init__(self, ind_temp: float, surface_walls: Cuboid, conductivity: ThermalConductivity, 
                heater: Heater, min_temp_factory: float, max_temp_factory: float):

        self.ind_temp = ind_temp
        self.surface_walls = surface_walls
        self.conductivity = conductivity
        self.heater = heater
        self.min_temp_factory = min_temp_factory
        self.max_temp_factory = max_temp_factory


    def method1(self):
        return



