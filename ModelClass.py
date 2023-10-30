import numpy as np
# import scipy.integrate as integrate
import math
import matplotlib.pyplot as plt
from heater import Heater
from wallMaterials import ThermalConductivity, Cuboid
from outsideTemp import OutsideEnvironment
from trapezoidal import trapezoidal 


AIR_SPECIFIC_HEAT_CAPACITY = 1.2 # kJ m^-3 K^-1


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

        P_in = self.heater.heatOutputRate if self.heater.switchedOn else 0
        heatCapacity = AIR_SPECIFIC_HEAT_CAPACITY*self.surface_walls.getVolume()
        surfaceArea = self.surface_walls.getSurfaceArea()
        outsideTemp = self.outdoors.getCurrentOutsideTemperature(currentTime)
        conductivity = self.conductivity.value

        result = P_in/heatCapacity - conductivity*surfaceArea*(self.ind_temp - outsideTemp)/(self.wallThickness*heatCapacity)
        return result


    def updateTemperature(self, currentTime: float, dt: float):
        dT = trapezoidal(f=self.nonDimensionalisedTemperatureDerivative, x=currentTime, dx=dt)
        self.ind_temp += dT

    def simulateTemperature(self, timeSamples: list[float])-> list[float]: 
        temperatures = []

        for i in range(len(timeSamples)-1): 
            currentTime = timeSamples[i]
            dt = timeSamples[i+1]-timeSamples[i]
            temperatures.append(self.ind_temp)
            self.updateTemperature(currentTime, dt)
        
        
        return temperatures




def main():
    print("Hello World \n")
    start = 0
    end = 24
    step = 0.001
    time_points = [start + i * step for i in range(int((end - start) / step) + 1)] #measure temp over 24hrs
    outsideEnv = OutsideEnvironment(281,4)
    
    heatedFactory = Factory(283.0, Cuboid(50,100,20), ThermalConductivity.CONCRETE, Heater(3e5, switchedOn=True), outsideEnv, 0.05)
    nonHeatedFactory = Factory(283.0, Cuboid(50,100,20), ThermalConductivity.CONCRETE, Heater(3e5), outsideEnv, 0.05)
    heatedTemps = heatedFactory.simulateTemperature(time_points)
    nonHeatedTemps = nonHeatedFactory.simulateTemperature(time_points)

    outsideTemps = [outsideEnv.getCurrentOutsideTemperature(t) for t in time_points[0:-1]]
    plt.plot(time_points[0:-1], heatedTemps, label='Indoor Temperature w heating')
    plt.plot(time_points[0:-1], nonHeatedTemps, label="Indoor Temperature w/o heating")
    plt.plot(time_points[0:-1], outsideTemps, label='Outdoor Temperature')
    plt.legend()
    plt.show()
   



if __name__ == "__main__":
    main()