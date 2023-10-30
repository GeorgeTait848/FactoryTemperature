import numpy as np
import scipy.integrate as integrate
import math
import matplotlib.pyplot as plt
from heater import Heater
from wallMaterials import ThermalConductivity, Cuboid
from outsideTemp import OutsideEnvironment

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

        P_in = self.heater.heatOutputRate
        heatCapacity = AIR_SPECIFIC_HEAT_CAPACITY*self.surface_walls.getVolume()
        surfaceArea = self.surface_walls.getSurfaceArea()
        outsideTemp = self.outdoors.getCurrentOutsideTemperature(currentTime)
        conductivity = self.conductivity.value

        return P_in/heatCapacity - conductivity*surfaceArea/(self.wallThickness*heatCapacity)*(self.ind_temp - outsideTemp)

    def updateTemperature(self, currentTime: float, dt: float):

        dimensionlessTempDerivative = np.array(self.nonDimensionalisedTemperatureDerivative(currentTime))
        
        newTemp = integrate.trapezoid(dimensionlessTempDerivative,currentTime, dx=dt)

        self.ind_temp = newTemp[0]

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
    step = 0.1
    time_points = [start + i * step for i in range(int((end - start) / step) + 1)] #measure temp over 24hrs
    outsideEnv = OutsideEnvironment(8,4)
    factory = Factory(0.0, Cuboid(50,100,20), ThermalConductivity.STEEL, Heater(3e5), outsideEnv, 0.05)

    temps = factory.simulateTemperature(time_points)

    plt.plot(time_points[0:-1], temps)
   



if __name__ == "__main__":
    main()