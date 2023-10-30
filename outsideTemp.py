import numpy as np
import matplotlib.pyplot as plt

class OutsideEnvironment(): 
    def __init__(self, meanT: float, halfrangeT: float):
        self.meanT = meanT
        self.halfrangeT = halfrangeT 

        # meanT = 8, halfrangeT = 4 for winter temps 4-12C
        # meanT = 19, halfrangeT = 5 for summer temps 14-24C
        
    def getCurrentOutsideTemperature(self, currentTime: float) -> float: 
        return self.halfrangeT * np.sin((np.pi/12)*(currentTime - 9))+self.meanT


def main():
    t = [i for i in range(25)]
    env = OutsideEnvironment(281, 4)

    temps = [env.getCurrentOutsideTemperature(time) - 273 for time in t]
    plt.plot(t,temps)
    plt.show()



if __name__ == "__main__":
    main()