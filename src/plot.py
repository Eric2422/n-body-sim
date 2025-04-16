import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from files import FileHandler

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

        # Set dimenions of plot.
        # Scalar margin
        margin = 1.25
        min_x = np.min(data_frame['x'].values)
        max_x = np.max(data_frame['x'].values)
        plt.xlim(left=min_x * margin, right=max_x * margin)

        min_y = np.min(data_frame['y'].values)
        max_y = np.max(data_frame['y'].values)
        plt.ylim(bottom=min_y * margin, top=max_y * margin)

        min_z = np.min(data_frame['z'].values)
        max_z = np.max(data_frame['z'].values)
        ax.set_zlim(min_z * margin, max_z * margin)

        # The animation runs at real speed.
        self.plot_animation = animation.FuncAnimation(
            fig,
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

        # Stop the function from going out of bounds
        if end_index > len(self.data_frame):
            return self.plot,

        data = self.data_frame.loc[start_index: end_index]

        self.plot.set_data(data.x, data.y)
        self.plot.set_3d_properties(data.z)

        return self.plot,

    def show(self) -> None:
        """Display this plot and run the animation. """
        plt.show()

    def save_plot_to_file(self, file_handler) -> None:
        print(f'./{FileHandler.OUTPUT_DIR}/{file_handler.output_file.stem}.mp4')
        self.plot_animation.save(f'{FileHandler.OUTPUT_DIR}/{file_handler.output_file.stem}.mp4')
