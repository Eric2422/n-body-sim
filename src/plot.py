"""Module for plotting the results of simulations. See :class:`Plot`
for more details.
"""


import typing

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import matplotlib.lines
import numpy as np
import pandas as pd


class Plot:
    """A Matplotlib plot of the movement of particles over time. The plot
    will be run in real-time (i.e., each second of the simulation will be
    displayed as a second of animation).

    Parameters
    ----------
    data_frame : :class:`~pandas.DataFrame`
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


    Attributes
    ----------
    DATA_FRAME : :class:`~pandas.DataFrame`
        The data frame that the plot will read and display as an animation.
    PLOT : :class:`~matplotlib.lines.Line2D`
        The plot created internally.
    FPS : int
        The number of frames per second that the animation runs at.
    PLOT_ANIMATION : :class:`~matplotlib.lines.Line2D`
        The animation of :const:`PLOT`.
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

        self.DATA_FRAME = data_frame

        # Plot initial data points, one for each particle.
        initial_data = data_frame[data_frame['t'] == 0]
        self.PLOT, = ax.plot(
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

        self.FPS = round(1 / time_step_size)

        # The animation runs at real speed.
        self.PLOT_ANIMATION = animation.FuncAnimation(
            fig,
            self.update,
            # Convert from seconds to milliseconds.
            interval=time_step_size / 1000,
            blit=True,
            cache_frame_data=False
        )

    def update(self, num: int) -> tuple[matplotlib.lines.Line2D]:
        """Update the plot points of the scatter. Passed into the ``func``
        parameter of:class:`~animation.FuncAnimation`. See there for more
        details.

        Parameters
        ----------
        num : int
            The number of intervals that have elapsed.

        Returns
        -------
        tuple[:class:`~matplotlib.lines.Line2D`]
            A tuple containing the artists used to update the plot.
        """
        # The particles are flattened into a single data frame,
        # so the end index will be two after the start index.
        start_index = num * len(self.DATA_FRAME[self.DATA_FRAME['t'] == 0])
        end_index = start_index + 2

        # Stop the function from going out of bounds.
        if end_index > len(self.DATA_FRAME):
            return self.PLOT,

        data = self.DATA_FRAME.loc[start_index: end_index]

        self.PLOT.set_data(data.x, data.y)
        self.PLOT.set_3d_properties(data.z)  # type: ignore

        return self.PLOT,

    def show(self) -> None:
        """Display this plot and run the animation."""
        plt.show()

    def save_to_file(self, filename: str) -> None:
        """Save the plot as a GIF file with the given name. The filename
        will be resolved using :const:`~files.FileHandler.OUTPUT_DIR`,
        i.e., the GIF will be saved under the same directory as the text
        files.

        Parameters
        ----------
        filename : str
            The filename that the GIF will be saved to. It does not matter
            if it includes a file extension or what file extension is
            used. Any file extension will be removed and replaced with
            ``.gif``.
        """
        ff_writer = animation.FFMpegWriter(fps=self.FPS)
        self.PLOT_ANIMATION.save(filename, writer=ff_writer)
