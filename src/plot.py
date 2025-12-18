import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


class Plot():
    def __init__(
        self,
        data_frame: pd.DataFrame,
        time_step_size: float = 1.0
    ) -> None:
        """Create a 3D NumPy plot.

        Parameters
        ----------
        data_frame : pd.DataFrame
            A data frame with four columns: t, x, y, z
            Contains the time and position of particles.
        time_step_size : float, optional
            The amount of time between each frame, by default 1.0
        """
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        self.data_frame = data_frame

        self.num_particles = len(data_frame[data_frame['t'] == 0])

        initial_data = data_frame[data_frame['t'] == 0]
        # Plot points, one for each particle.
        self.plot, = ax.plot(
            initial_data.x,
            initial_data.y,
            initial_data.z,
            linestyle="",
            marker="o"
        )

        # Set dimensions of plot.
        # Scalar margin
        MARGIN = 1.25
        min_x = np.min(np.array(data_frame['x'].values))
        max_x = np.max(np.array(data_frame['x'].values))
        width = max_x - min_x
        ax.set_xlim(
            left=min_x - (width * MARGIN),
            right=max_x + (width * MARGIN)
        )
        ax.set_xlabel('meters (m)')

        min_y = np.min(np.array(data_frame['y'].values))
        max_y = np.max(np.array(data_frame['y'].values))
        length = max_y - min_y
        ax.set_ylim(
            bottom=min_y - (length * MARGIN),
            top=max_y + (length * MARGIN)
        )
        ax.set_ylabel('meters (m)')

        min_z = np.min(np.array(data_frame['z'].values))
        max_z = np.max(np.array(data_frame['z'].values))
        height = max_z - min_z
        ax.set_zlim(  # type: ignore
            min_z - (height * MARGIN),
            max_z + (height * MARGIN)
        )
        ax.set_zlabel('meters (m)')  # type: ignore

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
