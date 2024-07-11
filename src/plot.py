import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np

from particle import Particle


class Plot():
    def __init__(self, data: np.array, tick_size: np.float64 = 1.0) -> None:
        """Create a 3D NumPy plot

        Parameters
        ----------
        data : np.array
            The data to be plotted. 
            A 2D array of floats. 
            Each row is a particle and each column is a position at a given point in time.
        tick_size : np.float64, optional
            The amount of time between each frame, by default 1.0
        """
        self.figure = plt.figure()
        self.ax = self.figure.add_subplot(111, projection='3d')

        lines = [self.ax.plot(datum[0, :1], datum[1, :1], datum[2, :1])[0]
                 for datum in data]
        self.ax.margins(1, 1, 1)

        plot_animation = animation.FuncAnimation(
            self.figure, self.update, fargs=(data, lines), interval=tick_size/1000)
        plt.show()

    def update(self, num, positions, lines):
        for line, position in zip(lines, positions):
            line.set_data_3d(position[:num, :].T)
