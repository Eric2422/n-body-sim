import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np


class Plot():
    def __init__(self, data: np.ndarray, tick_size: np.float64 = 1.0) -> None:
        """Create a 3D NumPy plot.

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

        # print(f'data: {data[0]}')
        # print()
        # Plot 2D lines, one for each particle.
        x_values = [particle[0][0] for particle in data]
        y_values = [particle[0][1] for particle in data]
        z_values = [particle[0][2] for particle in data]
        scatter = self.ax.scatter(
            x_values,
            y_values,
            z_values
        )

        # print(points)

        # for particle in data:
        #     print(particle)
        #     print()

        self.ax.margins(1, 1, 1)

        # The animation runs at real speed.
        self.plot_animation = animation.FuncAnimation(
            self.figure,
            self.update,
            fargs=(data, scatter),
            interval=tick_size / 1000
        )

    def update(self, num: int, data, scatter) -> None:
        """Update the plot points of the scatter. 

        Parameters
        ----------
        num : int
            The number of intervals that have elapsed.
        data : np.ndarray
            The position of the particles in the simulation.
        scatter : list
            A list containing the points of the plot. 
        """
        # For each point, set the corresponding position data
        for point, datum in zip(scatter, data):
            # print(f'datum[num]: {datum[num]}')
            scatter.set_offsets(datum[num])

    def show(self) -> None:
        """Display this plot and run the animation. """
        plt.show()
