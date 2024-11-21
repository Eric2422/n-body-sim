import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


class Plot():
    def __init__(self, data: list[pd.DataFrame], tick_size: np.float64 = 1.0) -> None:
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

        self.data = data
        print(self.data[:, 0, 0])
        print()

        # Plot scatter points, one for each particle.
        x_values = self.data[:, 0, 0]
        y_values = self.data[:, 0, 1]
        z_values = self.data[:, 0, 2]
        self.scatter = self.ax.scatter(
            x_values,
            y_values,
            z_values
        )

        self.ax.margins(1, 1, 1)

        # The animation runs at real speed.
        self.plot_animation = animation.FuncAnimation(
            self.figure,
            self.update,
            interval=tick_size / 1000,  # Convert from seconds to milliseconds.
            blit=True
        )

    def update(self, num: int):
        """Update the plot points of the scatter. 

        Parameters
        ----------
        num : int
            The number of intervals that have elapsed.
        """
        print(num)
        if num > len(self.data[0] - 2):
            return

        # print(self.data[:, num, 0])
        # print('\n\n')
        x_values = self.data[:, num, 0]
        y_values = self.data[:, num, 1]
        z_values = self.data[:, num, 2]
        self.scatter.set_offsets([x_values, y_values, z_values])

        return self.scatter,

    def show(self) -> None:
        """Display this plot and run the animation. """
        plt.show()
