import sys

import numpy as np
import pandas as pd

from barnes_hut import BarnesHutCell
from files import FileHandler
from particle import PointParticle
from plot import Plot
import vectors


class Simulation():
    """Represents one simulation with particles and fields.
    """

    def __init__(
        self,
        theta: float = 0.5,
        tick_size: float = 1.0,
        gravitational_field: vectors.FieldVector = np.zeros(3, dtype=float),
        electric_field: vectors.FieldVector = np.zeros(3, dtype=float),
        magnetic_field: vectors.FieldVector = np.zeros(3, dtype=float),
        particles: list[PointParticle] = []
    ) -> None:
        """Initialize a simulation.

        Parameters
        ----------
        theta : float, optional
            The Barnes-Hut approximation parameter, by default 0.5
        tick_size : float, optional
            The time increment of the simulation in seconds, by default 1.0
        gravitational_field : vectors.FieldVector, optional
            A constant, uniform gravitational field, by default np.zeros(3, dtype=float)
        electric_field : vectors.FieldVector, optional
            A constant, uniform electric field, by default np.zeros(3, dtype=float)
        magnetic_field : vectors.FieldVector, optional
            A constant, uniform magnetic field, by default np.zeros(3, dtype=float)
        particles : list[PointParticle], optional
            A list of particles that are interacting with each other., by default []
        """
        self.particles = particles

        self.particle_positions_log = pd.DataFrame({
            't': np.empty(0, dtype=float),
            'x': np.empty(0, dtype=float),
            'y': np.empty(0, dtype=float),
            'z': np.empty(0, dtype=float)
        })
        """A log of all the particles' positions over the course of the simulation."""

        # Constant, universal fields
        self.gravitational_field = np.array(gravitational_field)
        self.electric_field = np.array(electric_field)
        self.magnetic_field = np.array(magnetic_field)

        self.current_tick = 0
        self.tick_size = tick_size

        self.theta = theta
        """The Barnes-Hut approximation parameter."""

    def create_barnes_hut_nodes(self) -> BarnesHutCell:
        return BarnesHutCell(particles=self.particles)

    def log_particle_position(self, particle: PointParticle) -> None:
        """Save the position of a particle to the particle positions log.

        Parameters
        ----------
        particle : PositionParticle
            A particle to save the position of.
        """
        # Save particle position data
        new_data = pd.DataFrame([{
            't': self.current_tick * self.tick_size,
            'x': np.array((particle.position[0])),
            'y': np.array((particle.position[1])),
            'z': np.array((particle.position[2]))
        }])
        self.particle_positions_log = pd.concat(
            [self.particle_positions_log, new_data], ignore_index=True)

    def get_particle_positions_string(self) -> str:
        """Return a string of the particles' current state.

        Returns
        -------
        str
            A string describing the state of all particles.
        """

        # Add the initial time and particle data to the file
        output_string = f't={self.current_tick * self.tick_size}\n'

        for particle in self.particles:
            output_string += particle.__str__() + '\n'

        output_string += '\n'

        return output_string

    def tick(self) -> None:
        """Run one tick of the simulation."""
        # Get the root node of the octree
        barnes_hut_root = self.create_barnes_hut_nodes()
        print(barnes_hut_root)

        # An array of net force acting upon each particle
        net_forces = np.zeros(shape=(len(self.particles), 3))

        for particle in self.particles:
            particle.set_force()

        # Calculate the forces that the particles exert on each other
        # Update the particle's acceleration and, but not the velocity and position
        for i in range(len(self.particles)):
            particle1 = self.particles[i]

            for child_node in barnes_hut_root.child_cells:
                net_forces[i] += particle1.get_gravitational_force_experienced(
                    child_node.get_gravitational_field_exerted(particle1.position))

                net_forces[i] += particle1.get_electrostatic_force_experienced(
                    child_node.get_electric_field_exerted(particle1.position)
                )

                net_forces[i] += particle1.get_magnetic_force_experienced(
                    child_node.get_magnetic_field_exerted(particle1.position)
                )

            # Add the constant fields
            net_forces[i] += particle1.get_force_experienced(
                self.electric_field, self.magnetic_field, self.gravitational_field
            )

        # Update particle positions and velocities after calculating the forces,
        # so it doesn't affect force calculations.
        for particle in particles:
            self.log_particle_position(particle)

            # Update the particle's velocity
            particle.velocity += particle.acceleration * self.tick_size

            # Update particle positions.
            particle.position += particle.velocity * self.tick_size

        self.current_tick += 1

    def run(self, num_ticks: int = 1, file_handler: FileHandler | None = None, print_progress=False) -> None:
        """Run the simulation for a given number of ticks.

        Parameters
        ----------
        num_ticks : int
            The number of ticks that the simulation runs by, by default 1.
        file_handler : FileHandler, optional
            A `FileHandler` object to pass data into as the simulation runs.
            Writes the data into a file,
            so the data does not need to be looped through again afterward.
            By default None
        print_progress : bool, optional
            Whether to print a progress report on how much of the simulation has been completed, by default False
        """
        output_string = ''
        if file_handler is not None:
            file_handler.clear_output_file()

            # Print fields
            output_string += f'g=<{", ".join((str(dimension) for dimension in self.gravitational_field))}>\n'
            output_string += f'E=<{", ".join((str(dimension) for dimension in self.electric_field))}>\n'
            output_string += f'B=<{", ".join((str(dimension) for dimension in self.magnetic_field))}>\n\n'

            output_string += self.get_particle_positions_string()

        # Record initial particle data
        for particle in particles:
            self.log_particle_position(particle=particle)

        # Run the necessary number of ticks
        for i in range(num_ticks):
            self.tick()
            progress = i / num_ticks if num_ticks == 0 else float(1.0)

            if print_progress:
                # Clear the previous line.
                sys.stdout.write('\033[K')
                # Print the current progress and then return to the beginning of the line.
                print(f'Progress: {round(progress * 100, 1)}%', end='\r')

            # If a `FileHandler` object is passed, output the results to a file.
            if file_handler is not None:
                output_string += self.get_particle_positions_string()

        if file_handler is not None:
            file_handler.append_to_output_file(output_string)

        # If printing progress reports,
        # add an extra line to account for the carriage returns.
        if print_progress:
            print()


if __name__ == '__main__':
    # Check if the user supplied a config file
    if len(sys.argv) < 2:
        raise ValueError('Please enter the name of the config file.')

    # Read the config file data and create particles based on that data
    file_handler = FileHandler(config_file=sys.argv[1])
    file_data = file_handler.read_config_file()

    # Create a list of particles as described by the file data.
    particles = [
        PointParticle(
            position=np.array(particle['position']),
            velocity=np.array(particle['velocity']),
            acceleration=np.array(particle['acceleration']),
            mass=particle['mass'],
            charge=particle['charge']
        )
        for particle in file_data['particles']
    ]

    # Create and run the simulation
    num_ticks = int(file_data['num ticks'])
    tick_size = file_data['tick size']
    simulation = Simulation(
        theta=file_data['theta'],
        tick_size=tick_size,
        gravitational_field=file_data['gravitational field'],
        electric_field=file_data['electric field'],
        magnetic_field=file_data['magnetic field'],
        particles=particles
    )
    simulation.run(
        num_ticks=num_ticks,
        file_handler=file_handler,
        print_progress=True
    )

    # Plot the simulation
    plot = Plot(
        data_frame=simulation.particle_positions_log,
        tick_size=simulation.tick_size
    )

    # plot.save_plot_to_file()
    # plot.show()
