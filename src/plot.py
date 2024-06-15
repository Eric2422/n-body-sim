from matplotlib import pyplot as plt
import numpy as np

class Plot():
    def __init__(self, x, y, z) -> None:
        self.ax = plt.figure().add_subplot(projection='3d')

        self.x = x
        self.y = y
        self.z = z

    def plot(self) -> None:
        self.ax.plot(self.x, self.y, self.z)
        self.ax.legend()

        plt.show()