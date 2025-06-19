import sys

import numpy as np
import pandas as pd

from barnes_hut import BarnesHutCell
from files import FileHandler
from particle import PointParticle
from plot import Plot


class Simulation():
    def __init__(self, particles: list[PointParticle], tick_size: float = 1.0, theta: float = 0.5) -> None:
        """Initiate one simulation.

        Parameters
        ----------
        particles : list
            A list of particles that are interacting with each other.
        tick_size : float, optional
            The time increment of the simulation in seconds, by default 1.0
        theta : float, optional
            The Barnes-Hut approximation parameter, by default 0.5
        """
        self.particles = particles
        # A log of all the particles' positions over the course of the simulation
        self.particle_positions_log = pd.DataFrame({
            't': np.empty(0),
            'x': np.empty(0),
            'y': np.empty(0),
            'z': np.empty(0)
        })

        # Constant, universal fields
        self.electric_field = np.zeros(3)
        self.magnetic_field = np.zeros(3)
        self.gravitational_field = np.zeros(3)

        self.current_tick = 0
        self.tick_size = tick_size

        # The Barnes-Hut approximation parameter
        self.theta = theta

    def create_barnes_hut_nodes(self) -> BarnesHutCell:
        x_bounds = np.array((
            min(self.particles, key=lambda ele: ele.position[0]).position[0],
            max(self.particles, key=lambda ele: ele.position[0]).position[0]
        ))

        y_bounds = np.array((
            min(self.particles, key=lambda ele: ele.position[1]).position[1],
            max(self.particles, key=lambda ele: ele.position[1]).position[1]
        ))

        z_bounds = np.array((
            min(self.particles, key=lambda ele: ele.position[2]).position[2],
            max(self.particles, key=lambda ele: ele.position[2]).position[2]
        ))

        return BarnesHutCell(x_bounds, y_bounds, z_bounds, self.particles)

    def apply_force_between_particles(self, particle1: PointParticle, particle2: PointParticle) -> None:
        """Calculate and apply the force from one particle upon another.

        Parameters
        ----------
        particle1 : PointParticle
            The particle that is being being moved by `particle2`.
        particle2 : PointParticle
            The particle that is exerting a force upon `particle1`.
        """
        # If the particles are not the same
        if particle1 != particle2:
            # Lorentz force law
            particle1.apply_lorentz_force_law(
                particle2.get_electric_field_exerted(particle1.position),
                particle2.get_magnetic_field_exerted(particle1.position)
            )

            particle1.apply_gravitational_field(
                particle2.get_gravitational_field_exerted(
                    particle1.position
                )
            )

            # Lorentz force law
            particle2.apply_lorentz_force_law(
                particle1.get_electric_field_exerted(particle2.position),
                particle1.get_magnetic_field_exerted(particle2.position)
            )

            particle2.apply_gravitational_field(
                particle1.get_gravitational_field_exerted(
                    particle2.position
                )
            )

    def log_particle_positions(self, particle: PointParticle) -> None:
        """Save the data of a particle to the particle positions log.

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
            _description_
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

        # An array of forces for each particle
        forces = np.zeros(shape=(len(self.particles), 3))

        for particle in self.particles:
            particle.clear_force()

        # Calculate the forces that the particles exert on each other
        # Update the particle's acceleration and, but not the velocity and position
        for i in range(len(self.particles)):
            particle1 = self.particles[i]

            for child_node in barnes_hut_root.child_cells:
                if np.linalg.norm(child_node.center_of_mass - particle1.position) < child_node.width * self.theta and child_node not in barnes_hut_root.particles:
                    pass

                forces[i] += particle1.get_gravitational_force_experienced(
                    child_node.get_gravitational_field(particle1.position))

                forces[i] += particle1.get_electric_force_experienced(
                    child_node.get_electric_field(particle1.position)
                )

                forces[i] += particle1.get_magnetic_field_experienced(
                    child_node.get_magnetic_field(particle1.position)
                )

            for j in range(i + 1, len(self.particles)):
                particle2 = self.particles[j]

                self.apply_force_between_particles(particle1, particle2)

            # Add the constant fields
            particle1.apply_fields(
                self.electric_field, self.magnetic_field, self.gravitational_field)

        # Update particle positions and velocities after calculating the forces,
        # so it doesn't affect force calculations.
        for particle in particles:
            self.log_particle_positions(particle)

            # Update the particle's velocity
            particle.velocity += particle.acceleration * self.tick_size

            # Update particle positions.
            particle.position += particle.velocity * self.tick_size

        self.current_tick += 1

    def run(self, num_ticks: int = -1, file_handler: FileHandler | None = None, print_progress=False) -> None:
        """Run the simulation for a given number of ticks.

        Parameters
        ----------
        num_ticks : int, optional
            The number of ticks that the simulation runs by.
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
            self.log_particle_positions(particle=particle)

        # Run the necessary number of ticks
        for i in range(num_ticks + 1):
            self.tick()
            progress = i / num_ticks

            if print_progress:
                # Clear the previous line.
                sys.stdout.write('\033[K')
                # Print the current progress and then return to the beginning of the line.
                print(f'Progess: {round(progress * 100, 1)}%', end='\r')

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
        particles,
        tick_size=tick_size,
        theta=file_data['theta']
    )
    simulation.run(num_ticks=num_ticks,
                   file_handler=file_handler, print_progress=True)

    # Plot the simulation
    plot = Plot(
        data_frame=simulation.particle_positions_log,
        tick_size=np.float64(simulation.tick_size)
    )

    # plot.save_plot_to_file()
    plot.show()
