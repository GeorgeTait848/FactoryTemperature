import numpy as np
import scipy as sp
import math

start = 0
end = 24
step = 0.1
time_points = [start + i * step for i in range(int((end - start) / step) + 1)] #measure temp over 24hrs

class HeatingAFactory:

    def __init__(self, ind_temp, outd_temp, surface_walls, conductivity, heat_capacity, const_heat_to_temp, air_volume, min_temp_factory, max_temp_factory):
        self.ind_temp = ind_temp
        self.outd_temp = outd_temp
        self.surface_walls = surface_walls
        self.conductivity = conductivity
        self.heat_capacity = heat_capacity              #more constants/ coeff?
        self.const_heat_to_temp = const_heat_to_temp
        self.air_volume = air_volume
        self.min_temp_factory = min_temp_factory
        self.max_temp_factory = max_temp_factory


    def method1(self):
        return

    def heating_rate(self):
        return

    def external_temp(self):
        sin_values = [math.sin(x) for x in time_points]
        ext_temp_list = [ for x in sin_values] # transformations to Kelvin?
        return


