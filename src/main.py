import sys
import typing

import numpy as np
import pandas as pd

from barnes_hut import BarnesHutNode
from files import FileHandler
from particle import PointParticle
from plot import Plot
import vectors


class Simulation():
    """Represents one simulation with particles and fields.

    Contains the theta; time step size; constant, uniform gravitational field;
    constant, uniform electrical field; constant, uniform magnetic field;
    and particles used in the simulation.

    Keeps track of the previous positions of all the partices.
    """

    @typing.override
    def __init__(
        self,
        theta: float = 0.5,
        time_step_size: float = 1.0,
        gravitational_field: vectors.FieldVector = np.zeros(3, dtype=float),
        electric_field: vectors.FieldVector = np.zeros(3, dtype=float),
        magnetic_field: vectors.FieldVector = np.zeros(3, dtype=float),
        particles: list[PointParticle] = []
    ) -> None:
        """Initialize a simulation.

        Parameters
        ----------
        `theta` : `float`, optional
            The Barnes-Hut approximation parameter, by default 0.5
        `time_step_size` : `float`, optional
            The time increment of the simulation in seconds (s), by default 1.0
        `gravitational_field` : `vectors.FieldVector`, optional
            A constant, uniform gravitational field, by default `np.zeros(3, dtype=float)`
        `electric_field` : `vectors.FieldVector`, optional
            A constant, uniform electric field, `by default np.zeros(3, dtype=float)`
        `magnetic_field` :` vectors.FieldVector`, optional
            A constant, uniform magnetic field, `by default np.zeros(3, dtype=float)`
        `particles` : `list[PointParticle]`, optional
            A `list` of particles that are interacting with each other, by default `[]`
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
        self.electric_field = electric_field
        self.magnetic_field = magnetic_field
        self.gravitational_field = gravitational_field

        self.current_time_step = 0.0
        self.time_step_size = time_step_size

        self.theta = theta
        """The Barnes-Hut approximation parameter."""

    def log_particle(self, particle: PointParticle) -> None:
        """Save the state of a particle to the particles log.

        Parameters
        ----------
        `particle` : `PointParticle`
            A particle to save the state of.
        """
        # Save particle position data
        new_data = pd.DataFrame([{
            't': self.current_time_step * self.time_step_size,
            'x': np.array((particle.position[0])),
            'y': np.array((particle.position[1])),
            'z': np.array((particle.position[2]))
        }])
        self.particle_positions_log = pd.concat(
            [self.particle_positions_log, new_data], ignore_index=True)

    def get_particle_string(self) -> str:
        """Return a string of the particles' current state.

        Returns
        -------
        `str`
            A string describing the state of all particles.
        """

        # Add the initial time and particle data to the file
        output_string = f't={self.current_time_step * self.time_step_size}\n'

        for particle in self.particles:
            output_string += particle.__str__() + '\n'

        output_string += '\n'

        return output_string

    def calculate_particle_force(
        self,
        particle: PointParticle,
        barnes_hut_root: BarnesHutNode,
        position: vectors.PositionVector | None = None,
        velocity: vectors.VelocityVector | None = None
    ):
        if (position is None):
            position = particle.position

        return (
            particle.get_force_experienced(
                barnes_hut_root.get_gravitational_field_exerted(
                    position, particle.ID
                ),
                barnes_hut_root.get_electric_field_exerted(
                    position, particle.ID),
                barnes_hut_root.get_magnetic_field_exerted(
                    position, particle.ID),
                velocity
            )
            + particle.get_force_experienced(
                self.gravitational_field,
                self.electric_field,
                self.magnetic_field,
                velocity
            )
        )

    def time_step(self) -> None:
        """Run one time step of the simulation."""
        # Generate the root node of the octree
        barnes_hut_root = BarnesHutNode(self.particles)

        # Stores the new positions and velocities.
        new_data = np.zeros((len(particles), 2, 3))

        # Update particle positions and velocities before calculating the forces.
        for i in range(len(particles)):
            particle = particles[i]

            # Update the particle's acceleration.
            particle.acceleration = self.calculate_particle_force(
                particle, barnes_hut_root) / particle.MASS

            # Log after the current acceleration has been calculated.
            self.log_particle(particle)

            # Use Runge-Kutta method to to approximate velocity and position.
            v1 = particle.velocity
            a1 = particle.acceleration

            print()
            print(f'position: {particle.position}')
            print(f'v1: {v1}')
            print(f'a1: {a1}')

            a2 = self.calculate_particle_force(
                particle, barnes_hut_root) / particle.MASS
            v2 = particle.velocity + a1 * self.time_step_size / 2
            position = (particle.position
                        + v1 * self.time_step_size / 2
                        + 1/2 * a1 * (self.time_step_size / 2) ** 2)

            print(f'position: {position}')
            print(f'v2: {v2}')
            print(f'a2: {a2}')

            a3 = self.calculate_particle_force(
                particle, barnes_hut_root, position, v2) / particle.MASS
            v3 = particle.velocity + a2 * self.time_step_size / 2
            position = (particle.position
                        + v2 * self.time_step_size / 2
                        + 1/2 * a2 * (self.time_step_size / 2) ** 2)

            print(f'position: {position}')
            print(f'v3: {v3}')
            print(f'a3: {a3}')

            a4 = self.calculate_particle_force(
                particle, barnes_hut_root, position, v3) / particle.MASS
            v4 = particle.velocity + a3 * self.time_step_size
            position = (particle.position
                        + v3 * self.time_step_size
                        + 1/2 * a3 * self.time_step_size ** 2)

            print(f'position: {position}')
            print(f'v4: {v4}')
            print(f'a4: {a4}')

            # Calculate the new velocity and position.
            new_data[i, 1] = (self.time_step_size / 6 *
                              (a1 + 2 * a2 * 2 * a3 + a4))
            new_data[i, 0] = (self.time_step_size / 6 *
                              (v1 + 2 * v2 * 2 * v3 + v4))

        # Update the particle's position and velocity.
        for i in range(len(particles)):
            particle = particles[i]
            particle.position = new_data[i, 0]
            particle.velocity = new_data[i, 1]

            # Acceleration has already been updated in the previous loop.

        self.current_time_step += 1

    def run(
        self,
        num_time_steps: int = 1,
        file_handler: FileHandler | None = None,
        print_progress: bool = False
    ) -> None:
        """Run the simulation for a given number of time steps.

        Parameters
        ----------
        `num_time_steps` : `int`, optional
            The number of time steps that the simulation runs by, by default 1
        `file_handler` : `FileHandler`, optional
            A `FileHandler` object to pass data into as the simulation runs.
            Writes the data into a file,
            so the data does not need to be looped through again afterward.
            By default `None`
        `print_progress` : `bool`, optional
            Whether to print a progress report on how much of the simulation
            has been completed, by default `False`
        """
        # Stores the file output
        output_string = ''

        if file_handler is not None:
            # Clear the output
            file_handler.clear_output_file()

            # Print fields
            output_string += (
                f'g=<{", ".join((str(dimension) for dimension in self.gravitational_field))}>\n')
            output_string += (
                f'E=<{", ".join((str(dimension) for dimension in self.electric_field))}>\n')
            output_string += (
                f'B=<{", ".join((str(dimension) for dimension in self.magnetic_field))}>\n')
            output_string += '\n'

            # Log initial particle states
            output_string += self.get_particle_string()

        if print_progress:
            progress = 0.0
            print(f'Progress: {progress}%', end='\r')

        # Run the necessary number of time steps
        for i in range(int(num_time_steps)):
            self.time_step()

            if print_progress:
                progress = (i + 1) / num_time_steps

                # Clear the previous line.
                sys.stdout.write('\033[K')
                # Print the current progress and then return to the beginning of the line.
                print(f'Progress: {round(progress * 100, 1)}%', end='\r')

            # If a `FileHandler` object is passed, output the results to a file.
            if file_handler is not None:
                output_string += self.get_particle_string()

        # Log final state.
        for particle in particles:
            self.log_particle(particle)

        if file_handler is not None:
            file_handler.append_to_output_file(output_string)

        # If printing progress reports, add an extra line to account for the carriage returns.
        if print_progress:
            print()


if __name__ == '__main__':
    # Check if the user supplied a input file
    if len(sys.argv) < 2:
        raise ValueError('Please enter the name of the input file.')

    # Read the input file data and create particles based on that data
    file_handler = FileHandler(input_file=sys.argv[1])
    file_data = file_handler.read_input_file()

    # Create a list of particles as described by the file data.
    particles = [
        PointParticle(
            position=np.array(particle['position']),
            velocity=np.array(particle['velocity']),
            mass=particle['mass'],
            charge=particle['charge']
        )
        for particle in file_data['particles']
    ]

    # Create and run the simulation
    simulation = Simulation(
        theta=file_data['theta'],
        time_step_size=file_data['time step size'],
        gravitational_field=np.array(file_data['gravitational field']),
        electric_field=np.array(file_data['electric field']),
        magnetic_field=np.array(file_data['magnetic field']),
        particles=particles
    )

    simulation.run(
        num_time_steps=file_data['num time steps'],
        file_handler=file_handler,
        print_progress=True
    )

    # Plot the simulation
    plot = Plot(
        data_frame=simulation.particle_positions_log,
        time_step_size=simulation.time_step_size
    )

    # plot.save_plot_to_file()
    plot.show()
