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
        theta : float, default=0.5
            The Barnes-Hut approximation parameter
        time_step_size : float, default=1.0
            The time increment of the simulation in seconds (s)
        gravitational_field : vectors.FieldVector, default=np.zeros(3, dtype=float)
            A constant, uniform gravitational field.
        electric_field : vectors.FieldVector, default=np.zeros(3, dtype=float)
            A constant, uniform electric field.
        magnetic_field : vectors.FieldVector, default=np.zeros(3, dtype=float)
            A constant, uniform magnetic field.
        particles : list[PointParticle], default=[]
            A `list` of particles that are interacting with each other.
        """
        self.particles = particles

        self.particles_data = pd.DataFrame({
            't': np.empty(0, dtype=float),
            'x': np.empty(0, dtype=float),
            'y': np.empty(0, dtype=float),
            'z': np.empty(0, dtype=float)
        })
        """A record of all the particles' states over the course of the simulation."""

        # Constant, universal fields
        self.electric_field = electric_field
        self.magnetic_field = magnetic_field
        self.gravitational_field = gravitational_field

        self.current_time_step = 0.0
        self.time_step_size = time_step_size

        self.theta = theta
        """The Barnes-Hut approximation parameter."""

    def record_particle_data(self, particle: PointParticle) -> None:
        """Save the state of a particle to the particles data.

        Parameters
        ----------
        particle : PointParticle
            A particle to save the state of.
        """
        # Save particle position data
        new_data = pd.DataFrame([{
            't': self.current_time_step * self.time_step_size,
            'x': np.array((particle.position[0])),
            'y': np.array((particle.position[1])),
            'z': np.array((particle.position[2]))
        }])
        self.particles_data = pd.concat(
            [self.particles_data, new_data], ignore_index=True)

    def get_particles_string(self) -> str:
        """Return a string of the particles' current state.

        Returns
        -------
        str
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
    ) -> vectors.ForceVector:
        """Calculate the force exerted on a particle by the fields and other particles.

        Parameters
        ----------
        particle : PointParticle
            The particle to calculate the force upon.
        barnes_hut_root : BarnesHutNode
            The Barnes-Hut tree that contains all the particles.
        position : vectors.PositionVector | None, optional
            A hypothetical position of the particle to calculate with,
            possibly different from its current position.
            If argument is None, default to `particle.position`
        velocity : vectors.VelocityVector | None, optional
            A hypothetical velocity of the particle to calculate with,
            possibly different from its current position.
            If argument is None, default to `particle.velocity`

        Returns
        -------
        vectors.ForceVector
            The force exerted on a particle by the fields and other particles.
        """
        if (position is None):
            position = particle.position

        return (
            particle.get_force_experienced(
                barnes_hut_root.get_gravitational_field_exerted(
                    position, self.theta, particle.ID
                ),
                barnes_hut_root.get_electric_field_exerted(
                    position, self.theta, particle.ID),
                barnes_hut_root.get_magnetic_field_exerted(
                    position, self.theta, particle.ID),
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
        # Generate the root node of the octree.
        barnes_hut_root = BarnesHutNode(self.particles)

        # Stores the new positions and velocities.
        new_data = np.zeros((len(particles), 2, 3))

        # Update particle positions and velocities before calculating the forces.
        for i in range(len(particles)):
            particle = particles[i]

            particle.acceleration = self.calculate_particle_force(
                particle, barnes_hut_root) / particle.MASS

            # Record data after updating acceleration.
            self.record_particle_data(particle)

            # Use Runge-Kutta method to to approximate velocity and position.
            v1 = particle.velocity
            a1 = particle.acceleration

            a2 = self.calculate_particle_force(
                particle, barnes_hut_root) / particle.MASS
            v2 = particle.velocity + a1 * self.time_step_size / 2
            position = (particle.position
                        + v1 * self.time_step_size / 2
                        + 1/2 * a1 * (self.time_step_size / 2) ** 2)

            a3 = self.calculate_particle_force(
                particle, barnes_hut_root, position, v2) / particle.MASS
            v3 = particle.velocity + a2 * self.time_step_size / 2
            position = (particle.position
                        + v2 * self.time_step_size / 2
                        + 1/2 * a2 * (self.time_step_size / 2) ** 2)

            a4 = self.calculate_particle_force(
                particle, barnes_hut_root, position, v3) / particle.MASS
            v4 = particle.velocity + a3 * self.time_step_size
            position = (particle.position
                        + v3 * self.time_step_size
                        + 1/2 * a3 * self.time_step_size ** 2)

            # Calculate the new velocity and position.
            new_data[i, 0] = (particle.position
                              + self.time_step_size / 6 * (v1 + 2 * v2 * 2 * v3 + v4))
            new_data[i, 1] = (particle.velocity
                              + self.time_step_size / 6 * (a1 + 2 * a2 * 2 * a3 + a4))

        # Update the particle's position and velocity.
        for i in range(len(particles)):
            particle = particles[i]

            # Update position, velocity, and acceleration.
            particle.position = new_data[i, 0]
            particle.velocity = new_data[i, 1]

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
        num_time_steps : int, default=1
            The number of time steps that the simulation runs by.
        file_handler : FileHandler, optional
            A :py:class:`FileHandler` object,
            which writes data into a text file as the simulation runs.
            If the argument is None, do not write any data into a file.
        print_progress : bool, default=False
            Whether to print a progress report on how much of the simulation
            has been completed.
        """
        # Stores the file output
        output_string = ''

        if file_handler is not None:
            # Clear the output and open it for further writing.
            file_handler.clear_output_file()
            file_handler.open_output_file()

            # Write constants to output file.
            output_string += (f'theta={self.theta}')
            output_string += (
                f'g=<{", ".join((str(dimension) for dimension in self.gravitational_field))}>\n')
            output_string += (
                f'E=<{", ".join((str(dimension) for dimension in self.electric_field))}>\n')
            output_string += (
                f'B=<{", ".join((str(dimension) for dimension in self.magnetic_field))}>\n')
            output_string += '\n'
            file_handler.append_to_output_file(output_string)

        if print_progress:
            progress = 0.0
            print(f'Progress: {progress}%', end='\r')

        # If an error occurs in the middle for unknown reasons, close the output file.
        try:
            # Run the necessary number of time steps
            for i in range(int(num_time_steps)):
                # If a FileHandler object is passed in, output the results to a file.
                if file_handler is not None:
                    file_handler.append_to_output_file(
                        self.get_particles_string())

                self.time_step()

                if print_progress:
                    progress = (i + 1) / num_time_steps

                    # Clear the previous line.
                    sys.stdout.write('\033[K')
                    # Print the current progress and then return to the beginning of the line.
                    print(f'Progress: {round(progress * 100, 1)}%', end='\r')

        except:
            if file_handler is not None:
                file_handler.close_output_file()

        # Record final state of the particles.
        for particle in particles:
            # Generate the root node of the octree.
            barnes_hut_root = BarnesHutNode(self.particles)

            # Update the particle's final acceleration.
            particle.acceleration = self.calculate_particle_force(
                particle, barnes_hut_root) / particle.MASS

            # Record data for the final time.
            self.record_particle_data(particle)

        if file_handler is not None:
            # Write final particle states.
            file_handler.append_to_output_file(self.get_particles_string())
            file_handler.close_output_file()

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
        data_frame=simulation.particles_data,
        time_step_size=simulation.time_step_size
    )

    # plot.save_plot_to_file()
    plot.show()
