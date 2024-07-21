import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np


class Plot():
    def __init__(self, data: np.ndarray, tick_size: np.float64 = 1.0) -> None:
        """Create a 3D NumPy plot

        Parameters
        ----------
        data : np.ndarray
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

        self.plot_animation = animation.FuncAnimation(
            self.figure, self.update, fargs=(data, lines), interval=tick_size/1000)

    def update(self, num: int, data, lines) -> None:
        """Update the plot points of the plot. 

        Parameters
        ----------
        num : int
            The number of intervals that have elapsed.
        positions : np.ndarray
            The data of the 
        lines : list
            A list containing the lines of the plot. 
        """
        for line, datum in zip(lines, data):
            line.set_data_3d(datum[:num, :].T)

    def show(self) -> None:
        """Display this plot and run the animation
        """
        plt.show()