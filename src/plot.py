import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


class Plot():
    def __init__(self, data_frame: pd.DataFrame, tick_size: np.float64 = 1.0) -> None:
        """Create a 3D NumPy plot.

        Parameters
        ----------
        data_frame : pd.DataFrame
            A data frame with four columns: t, x, y, z
            Contains the time and position of particles.
        tick_size : np.float64, optional
            The amount of time between each frame, by default 1.0
        """
        figure = plt.figure()
        ax = figure.add_subplot(111, projection='3d')

        self.data_frame = data_frame
        print(data_frame)
        print()

        
        self.num_particles = len(data_frame[data_frame['t'] == 0])
        print(self.num_particles)

        # Plot points, one for each particle.
        self.plot, = ax.plot(
            data_frame[data_frame['t'] == 0].x,
            data_frame[data_frame['t'] == 0].y,
            data_frame[data_frame['t'] == 0].z, 
            linestyle="", 
            marker="o"
        )

        ax.margins(1, 1, 1)
        plt.xlim(left=-10, right=10)
        plt.ylim(bottom=-10, top=10)
        ax.set_zlim(-10, 10)

        # The animation runs at real speed.
        self.plot_animation = animation.FuncAnimation(
            figure,
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
        # The particles are flattened into a single data frame,
        # so `start_index` is the index of the first particle,
        # and `end_index` is the index of the last particle
        start_index = num * self.num_particles
        end_index = start_index + 2

        if end_index > len(self.data_frame):
            return self.plot,
        
        data = self.data_frame.loc[start_index : end_index]
        print(f'data: {data}', end ='\n' * 2)

        self.plot.set_data_3d(data.x, data.y, data.z)

        return self.plot,

    def show(self) -> None:
        """Display this plot and run the animation. """
        plt.show()
