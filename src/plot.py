"""Module for plotting the results of simulations. See :class:`Plot`
for more details.
"""


import typing

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


class Plot:
    """A Matplotlib plot of the movement of particles over time. The plot
    will be run in real-time (i.e., each second of the simulation will be
    displayed as a second of animation).

    Parameters
    ----------
    data_frame : :class:`pandas.DataFrame`
        A data frame with four columns: t, x, y, and z.
        Contains the time and position of particles.
    time_step_size : float, default=1.0
        The amount of time between each frame.
    margin : float, default=1.25
        The amount of extra space in each dimension as a factor of its
        size.

        For example, if the x dimension has a range of [-1.0, 1.0], a
        margin of 1.25 means that plot will have an x range of 
        [-1.5, 1.5].
    min : float, default=1.0
        The minimum size of each dimension.
    """

    @typing.override
    def __init__(
        self,
        data_frame: pd.DataFrame,
        time_step_size: float = 1.0,
        margin: float = 1.25,
        min: float = 1.0
    ) -> None:
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        self.data_frame = data_frame

        self.num_particles = len(data_frame[data_frame['t'] == 0])

        # Plot initial data points, one for each particle.
        initial_data = data_frame[data_frame['t'] == 0]
        self.plot, = ax.plot(
            initial_data.x,
            initial_data.y,
            initial_data.z,
            linestyle="",
            marker="o"
        )

        # Scalar margin
        margin = 1.25

        # Set x limits.
        min_x = np.min(np.array(data_frame['x'].values))
        max_x = np.max(np.array(data_frame['x'].values))
        plot_width = max((max_x - min_x) * margin, min)
        ax.set_xlim(
            min_x - plot_width,
            max_x + plot_width
        )
        ax.set_xlabel('x (m)')

        # Set y limits.
        min_y = np.min(np.array(data_frame['y'].values))
        max_y = np.max(np.array(data_frame['y'].values))
        plot_width = max((max_y - min_y) * margin, min)
        ax.set_ylim(
            min_y - plot_width,
            max_y + plot_width
        )
        ax.set_ylabel('y (m)')

        # Set z limits.
        min_z = np.min(np.array(data_frame['z'].values))
        max_z = np.max(np.array(data_frame['z'].values))
        plot_height = max((max_z - min_z) * margin, min)
        ax.set_zlim(  # type: ignore
            min_z - plot_height,
            max_z + plot_height
        )
        ax.set_zlabel('z (m)')  # type: ignore

        self.fps = round(1 / time_step_size)

        # The animation runs at real speed.
        self.plot_animation = animation.FuncAnimation(
            fig,
            self.update,
            # Convert from seconds to milliseconds.
            interval=time_step_size / 1000,
            blit=True,
            cache_frame_data=False
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

        # Stop the function from going out of bounds
        if end_index > len(self.data_frame):
            return self.plot,

        data = self.data_frame.loc[start_index: end_index]

        self.plot.set_data(data.x, data.y)
        self.plot.set_3d_properties(data.z)  # type: ignore

        return self.plot,

    def show(self) -> None:
        """Display this plot and run the animation."""
        plt.show()

    def save_plot_to_file(self, filename: str) -> None:
        """Save the plot as a GIF file.

        Parameters
        ----------
        filename : str
            The name that the file will be saved with.
        """
        FFwriter = animation.FFMpegWriter(fps=self.fps)
        self.plot_animation.save(filename, writer=FFwriter)
