import numpy as np
# import scipy.integrate as integrate
import math
import matplotlib.pyplot as plt
from heater import Heater
from wallMaterials import ThermalConductivity, Cuboid
from outsideTemp import OutsideEnvironment
from trapezoidal import trapezoidal 
from typing import Optional, Protocol
import utils
AIR_SPECIFIC_HEAT_CAPACITY = 1.2 # kJ m^-3 K^-1


class TemperatureSimulatable(Protocol): 
    def getTempTimeDerivative(self, currentTime: float) -> float:
        ...
    
    def updateTemp(self, currentTime: float, dt: float): 
        ...
    
    def simulateTemp(self, timeSamples: list[float], toggleHeaterAt: Optional[list[float]])-> list[float]:
        ...

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


    def getTempTimeDerivative(self, currentTime: float) -> float: 

        P_in = self.heater.heatOutputRate if self.heater.switchedOn else 0
        heatCapacity = AIR_SPECIFIC_HEAT_CAPACITY*self.surface_walls.getVolume()
        surfaceArea = self.surface_walls.getSurfaceArea()
        outsideTemp = self.outdoors.getCurrentOutsideTemperature(currentTime)
        conductivity = self.conductivity.value

        result = P_in/heatCapacity - conductivity*surfaceArea*(self.ind_temp - outsideTemp)/(self.wallThickness*heatCapacity)
        return result


    def updateTemp(self, currentTime: float, dt: float):
        dT = trapezoidal(f=self.getTempTimeDerivative, x=currentTime, dx=dt)
        self.ind_temp += dT

    def determineIfToggleHeater(self, toggleHeaterAt: Optional[list[float]], 
                currentTime: float, currentToggleIndex: int) -> bool: 
        if toggleHeaterAt is None: 
            return False
        
        if currentToggleIndex == len(toggleHeaterAt): 
            return False

        return currentTime >= toggleHeaterAt[currentToggleIndex]

    def simulateTemp(self, timeSamples: list[float], toggleHeaterAt: Optional[list[float]])-> list[float]: 

        temperatures = []
        currentlyHeated = self.heated
        currentToggleIndex = 0

        for i in range(len(timeSamples)-1): 
            currentTime = timeSamples[i]
            dt = timeSamples[i+1]-timeSamples[i]
            temperatures.append(self.ind_temp)

            if self.determineIfToggleHeater(toggleHeaterAt,currentTime, currentToggleIndex): 
                self.heated = False if currentlyHeated else True
                currentlyHeated = self.heated
                currentToggleIndex +=1

            self.updateTemp(currentTime, dt)
        
        
        return temperatures


class NDFactory: 

    '''Computes non-dimensionalised heat equation for the above factory model.'''

    def __init__(self, ndTemp: float, mu: float,
                epsilon: float, env_mean_temp: float,
                env_temp_half_width: float, heated: bool) -> None:
        self.T = ndTemp
        self.mu = mu
        self.epsilon = epsilon
        self.T_0 = env_mean_temp
        self.T_1 = env_temp_half_width
        self.heated = heated



    def getTempTimeDerivative(self, currentTime: float) -> float: 

        mu = self.mu if self.heated else 0
        return mu - self.epsilon*(self.T - 1 - self.T_1*math.sin(currentTime)/self.T_0)

    def updateTemp(self, currentTime: float, dt: float) -> float: 
        dT = trapezoidal(self.getTempTimeDerivative, currentTime, dt)
        self.T += dT
        return dT

    def determineIfToggleHeater(self, toggleHeaterAt: Optional[list[float]], 
                currentTime: float, currentToggleIndex: int) -> bool: 
        if toggleHeaterAt is None: 
            return False
        
        if currentToggleIndex == len(toggleHeaterAt): 
            return False

        return currentTime >= toggleHeaterAt[currentToggleIndex]

    def simulateTemp(self, timeSamples: list[float], toggleHeaterAt: Optional[list[float]] = None, returnDerivs: bool = False) -> list[float] or tuple[list[float]]:

        currentlyHeated = self.heated
        currentToggleIndex = 0
        temperatures = [0.0 for _ in range(len(timeSamples)-1)]
        derivs = [0.0 for _ in range(len(timeSamples)-1)]

        for i in range(len(timeSamples)-1): 
            currentTime = timeSamples[i]
            dt = timeSamples[i+1]-timeSamples[i]
            temperatures[i] = self.T

            if self.determineIfToggleHeater(toggleHeaterAt,currentTime, currentToggleIndex): 
                self.heated = False if currentlyHeated else True
                currentlyHeated = self.heated
                currentToggleIndex +=1

            dT = self.updateTemp(currentTime, dt)
            derivs[i] = dT
        
        
        if returnDerivs: 
            return temperatures, derivs

        return temperatures
        
        

class FactorySimulation: 

    def __init__(self, initialTemp: float, mu: float, epsilon: float, 
                env_mean_temp: float, env_temp_half_width: float, 
                toggleHeaterAt: Optional[list[float]] = None, 
                dt: float = 0.001):
        
        self.heatedFactory = NDFactory(initialTemp, mu, epsilon, env_mean_temp, env_temp_half_width, heated=True)
        self.toggledHeatingFactory = NDFactory(initialTemp, mu, epsilon, env_mean_temp, env_temp_half_width, heated=True)
        self.nonHeatedFactory = NDFactory(initialTemp, mu, epsilon, env_mean_temp, env_temp_half_width, False)

        self.toggleHeaterAt = toggleHeaterAt
        self.dt = dt

    def timeSamples(self, until: float): 
        return np.arange(0,until + self.dt, self.dt)

    def getEnvironmentTemps(self, until: float): 
        timeSamples = self.timeSamples(until)[0:-1]
        envTemps = self.heatedFactory.T_0 + self.heatedFactory.T_1*np.sin(timeSamples)
        return envTemps

    def select(self, id: int): 
        if id < 0 or id > 2: 
            raise Exception("""
            id must be a value between 0 and 2. 
            0: Get simulation data for heated case.
            1: Get simulation data for toggled heating case.
            2: Get simulation data for non-heated case.""")

        if id == 0: 
            return self.heatedFactory
         
        if id == 1: 
            return self.toggledHeatingFactory
        
        return self.nonHeatedFactory

    def getTemperatureSimulationData(self, id: int, until: float) -> NDFactory: 

        factory = self.select(id)
        
        timeSamples = self.timeSamples(until)

        if id == 0 or id == 2: 

            return factory.simulateTemp(timeSamples)

        return factory.simulateTemp(timeSamples, self.toggleHeaterAt)
        
    

    def getTemperatureTimeDerivs(self, id: int, until: float):

        factory = self.select(id)

        temp = NDFactory(factory.T, factory.mu, factory.epsilon, factory.T_0, factory.T_1, factory.heated)
        timeSamples = self.timeSamples(until)
        
        _, derivs = temp.simulateTemp(timeSamples, returnDerivs=True)
        return derivs

    def getSteadyStateIndex(self, id: int, until: float, iteration: int=0): 
        if iteration == 5: 
            raise Exception("Could not find steady state time, try again for longer simulation time")

        
        derivs = self.getTemperatureTimeDerivs(id, until)

        return utils.indexOfSignChangeIn(derivs)
        


    def getSteadyStateTime(self, id: int, until: float, iteration: int=0): 

        timeSamples = self.timeSamples(until)
        indexOfSteadyState = self.getSteadyStateIndex(id, until, iteration)
        if indexOfSteadyState == -1: 
            return self.getSteadyStateTime(id, until + 8*math.pi, iteration=iteration+1)

        return timeSamples[indexOfSteadyState]

    def plotTempsMultipleMu(self, ids: list[int], until: float, muVals: list[float]):

        xLabel = "t"
        yLabel = "T"

        labels = {0: "Heated", 
        1: "Toggled Heating", 
        2: "Non-Heated"}

        colours = {0: "black", 1: "green", 2: "red"}

        title = "Dimensionless Factory Temperature Simulation for \u03bc={}".format(self.heatedFactory.mu) 
        fig, axs = plt.subplots(2,2)
        plt.suptitle(title)
        

        timeSamples = self.timeSamples(until)
    
        for i in range(2): 
            for j in range(2): 

                sim = FactorySimulation(self.heatedFactory.T, self.heatedFactory.mu, muVals[i*2 + j], self.heatedFactory.T_0, self.heatedFactory.T_1)
                axs[i,j].plot(timeSamples[0:-1], sim.getEnvironmentTemps(until), color="blue", label="Env")
                axs[i,j].set_xlabel(xLabel, fontdict={"size": 12})
                axs[i,j].set_ylabel(yLabel, fontdict={"size": 12})
                axs[i,j].set_title("\u03bd = {}".format(muVals[i*2 + j]))
                axs[i,j].grid(visible=True)
                for id in ids: 
                    currLabel = labels[id]
                    data = sim.getTemperatureSimulationData(id, until)
                    currColour = colours[id]
                    axs[i,j].plot(timeSamples[0:-1], data, color=currColour, label=currLabel)
                axs[i,j].legend()
        
        
        plt.show()


    def plotTemps(self, ids: list[int], until: float):
        xLabel = "t  []"
        yLabel = "T  []"

        labels = {0: "Heated", 
        1: "Toggled Heating", 
        2: "Non-Heated"}

        colours = {0: "black", 1: "green", 2: "red"}

        title = "Dimensionless Factory Temperature Simulation for \u03bc={}, \u03bd = {}".format(self.heatedFactory.mu, self.heatedFactory.epsilon) 
        plt.title(title)
        
        timeSamples = self.timeSamples(until)

        plt.plot(timeSamples[0:-1], self.getEnvironmentTemps(until), color="blue", label="Env")
        plt.xlabel(xLabel, fontdict={"size": 12})
        plt.ylabel(yLabel, fontdict={"size": 12})

        for id in ids: 
            currLabel = labels[id]
            data = self.getTemperatureSimulationData(id, until)
            currColour = colours[id]
            plt.plot(timeSamples[0:-1], data, color=currColour, label=currLabel)

        plt.legend()
        plt.grid(visible=True)
        plt.show()
        

    def plotSteadyStateTimes(self, mu: list[float], nu: list[float]): 

        initialTempDiff = round(self.heatedFactory.T -self.heatedFactory.T_0, 2)
        plt.title("Steady state dimensionless time vs \u03bc for (T_i-T_0) = {}".format(initialTempDiff))
        plt.ylabel("Steady state time", fontdict={"size": 15})
        plt.xlabel("\u03bc", fontdict={"size": 15})


        l = len(mu)
        for n in nu: 
            nRounded = round(n, 2)
            print("Calculating steady state time for \u03bd = {}".format(nRounded))
            x = [0.0 for _ in range(l)]
            y = [0.0 for _ in range(l)]

            for i in range(l): 
                sim = FactorySimulation(self.heatedFactory.T, mu[i], n, self.heatedFactory.T_0, self.heatedFactory.T_1)
                x[i] = mu[i]
                y[i] = sim.getSteadyStateTime(0, 15)

            plt.plot(x,y, label="\u03bd = {}".format(nRounded))
            print("Plot added for \u03bd = {}".format(nRounded))
        plt.grid(True)
        plt.legend()
        plt.show()

    def getDataAfterSteadyStateTime(self, id: int, until: float): 
        ssInd = self.getSteadyStateIndex(id, until)
        temps = self.getTemperatureSimulationData(id, until)
        times = self.timeSamples(until)
        derivs = self.getTemperatureTimeDerivs(id, until)

        return times[ssInd:-1], temps[ssInd:-1], derivs[ssInd:-1]

    def getEnvPeakTimesAndTempsInSteadyState(self, id: int, until: float): 
        envTemps = self.getEnvironmentTemps(until)
        ssTime = self.getSteadyStateTime(id, until)
        i = 0
        t = math.pi*(i + 1.0/2)
        pt = []
        pT = []
        while t <= ssTime: 
            i += 1
            t = math.pi*(i + 1.0/2)
        
        while t <= until: 
            ind = math.floor(t/self.dt)
            pt.append(t)
            pT.append(envTemps[ind])
            i +=1
            t = math.pi*(i + 1.0/2)
        
        return pt[1:-1], pT[1:-1]

    def getTimesAndTemperaturesOfSteadyStatePeaks(self, id: int, until: float) -> tuple[list[float], list[float]]:

        times, temps, derivs = self.getDataAfterSteadyStateTime(id, until)
    
        signChangeTimes = []
        signChangeTemps = []
        signChangeIndex = utils.indexOfSignChangeIn(derivs)

        while signChangeIndex != -1: 
            
            signChangeTimes.append(times[signChangeIndex])
            times = times[signChangeIndex:-1]

            signChangeTemps.append(temps[signChangeIndex])
            temps = temps[signChangeIndex:-1]
            
            derivs = derivs[signChangeIndex:-1]
            signChangeIndex = utils.indexOfSignChangeIn(derivs)

        return signChangeTimes[1:-1], signChangeTemps[1:-1]

            

    def getSteadyStatePhaseAndTempDiffs(self, id: int, until: float): 
        envPeakt, envPeakT = self.getEnvPeakTimesAndTempsInSteadyState(id, until)
        indPeakt, indPeakT = self.getTimesAndTemperaturesOfSteadyStatePeaks(id, until)
        l = min(len(envPeakt), len(indPeakt))
        
        phaseDiffs = [0 for _ in envPeakt]
        tempDiffs = [0 for _ in envPeakt]

        for i in range(l): 

            phaseDiffs[i] = abs(envPeakt[i] - indPeakt[i])
            tempDiffs[i] = abs(envPeakT[i] - indPeakT[i])
        
        return np.mean(phaseDiffs), np.mean(tempDiffs)
            

    def plotSteadyStatePhaseDiffs(self, id: int, until: float, nuVals: list[float]):

        sims = [FactorySimulation(self.heatedFactory.T, self.heatedFactory.mu, nu, self.heatedFactory.T_0, self.heatedFactory.T_1) for nu in nuVals]

        lnNu = np.log(nuVals)
        lnPhaseDiffs = [np.log(sim.getSteadyStatePhaseAndTempDiffs(id, until)[0]) for sim in sims]
        plt.title("Steady State Phase Difference vs ln(\u03bd)", fontdict={"size": 15})
        plt.xlabel("ln(\u03bd)", fontdict={"size": 30})
        plt.ylabel("ln(\u03c6)", fontdict={"size": 30})
        plt.plot(lnNu, lnPhaseDiffs, color="black")
        plt.grid(visible=True)
        plt.show()

    def plotSteadyStateTempDiffs(self, id: int, until: float, nuVals: list[float]): 
        sims = [FactorySimulation(self.heatedFactory.T, self.heatedFactory.mu, nu, self.heatedFactory.T_0, self.heatedFactory.T_1) for nu in nuVals]

        muOverNu = [self.heatedFactory.mu/nu for nu in nuVals]
        tempDiffs = [sim.getSteadyStatePhaseAndTempDiffs(id, until)[1] for sim in sims]
        plt.title("Steady State Peak Temperature Difference vs \u03bc/\u03bd", fontdict={"size": 15})
        plt.xlabel("\u03bc/\u03bd", fontdict={"size": 30})
        plt.ylabel("Peak Temperature Difference", fontdict={"size": 15})
        plt.plot(muOverNu, tempDiffs, color="black")
        plt.grid(visible=True)
        plt.show()



def main():
    print("Hello World \n")

    timeOfSim = 60
    toggleHeaterAt = np.arange(start=0, stop=timeOfSim, step=4.0)
    sim = FactorySimulation(initialTemp=1.5, mu=1, epsilon=1, env_mean_temp=1, env_temp_half_width=0.1, toggleHeaterAt=toggleHeaterAt)

    
    # sim.plotTempsMultipleMu([0, 2], timeOfSim, [0.5, 1, 2, 4])
    # sim.plotTemps([0,2], timeOfSim)
    # mu = [0.2*(i+1) for i in range(30)]
    nuForPhase = [0.1*(i+1) for i in range(19)] + [2.5 + 2*i for i in range(40)]
    nuForTemp = [0.1*(i+1) for i in range(100)]
    # sim.plotSteadyStatePhaseDiffs(0, timeOfSim, nuForPhase)
    sim.plotSteadyStateTempDiffs(0, timeOfSim, nuForTemp)
    

    # sim = FactorySimulation(5.0, 0, 0, 1.0, 0.1)
    # sim.plotSteadyStateTimes(mu, nu)


   



if __name__ == "__main__":
    main()