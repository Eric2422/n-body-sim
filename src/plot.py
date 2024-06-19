import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np

from particle import Particle


class Plot():
    def __init__(self, data: np.array, tick_size: float = 1.0) -> None:
        """Create a 3D NumPy plot

        Parameters
        ----------
        data : np.array
            The data to be plotted. 
            A 2D array of floats. 
            Each row is a particle and each column is a position at a given point in time.
        tick_size : float, optional
            The amount of time between each frame, by default 1.0
        """
        self.figure = plt.figure()
        self.ax = self.figure.add_subplot(111, projection='3d')

        x, y, z = (np.linspace(0, 10), np.linspace(0, 10), np.linspace(0, 10))
        self.line, = self.ax.plot(x, y, z, 'b-')

        print(f'Data: {data}')
        lines = [self.ax.plot(datum[0, 0:1], datum[1, 0:1], datum[2, 0:1]) for datum in data]

        plot_animation = animation.FuncAnimation(self.figure, self.update, fargs=(data, lines), interval=tick_size/1000)

    def update(self, num, positions, lines):
        for line, position in zip(lines, positions):
            # `set_data()` does not work on 3D data
            line.set_data(positions[0:2, :num])
            line.set_3d_properties(positions[2,:num])