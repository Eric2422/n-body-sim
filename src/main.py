"""Module to create and instantiate simulations.
Can be run as ``__main__``.
"""


import sys
import typing

import numpy as np
import pandas as pd

import files
import particles
import plot
import vectors


class Simulation:
    """One simulation of a given initial conditions of particles and
    fields.

    Contains the theta; time step size; constant, uniform gravitational
    field; constant, uniform electrical field; constant, uniform magnetic
    field; and particles used in the simulation.

    Keeps track of the previous positions of all the partices.

    Parameters
    ----------
    theta : float, default=0.5
        The Barnes-Hut approximation parameter.
    time_step_size : float, default=1.0
        The time increment of the simulation in seconds (s).
    gravitational_field : :type:`vectors.FieldVector`, default=np.zeros(3, dtype=float)
        A constant, uniform gravitational field.
    electric_field : :type:`vectors.FieldVector`, default=np.zeros(3, dtype=float)
        A constant, uniform electric field.
    magnetic_field : :type:`vectors.FieldVector`, default=np.zeros(3, dtype=float)
        A constant, uniform magnetic field.
    particles_list : list[:type:`particles.PointParticle], default=[]
        A :class:`list` of particles that are interacting with each other
        in the simulation.

    Attributes
    ----------
    particles_list : list[PointParticle]
        A :class:`list` of particles that are interacting with each other
        in the simulation.
    particles_data : :class:`pd.DataFrame`
        A record of all the particles' states over the course of the simulation.
    gravitational_field : :class:`fields.FieldVector`
        A constant, uniform gravitational field.
    electric_field : :class:`fields.FieldVector`
        A constant, uniform electric field.
    magnetic_field : :class:`fields.FieldVector`
        A constant, uniform magnetic field.
    current_time_step : int
        The number of time steps that have passed since the beginning of
        the simulation.
    time_step_size : float
        The time increment of the simulation in seconds (s).
    theta : float
        The Barnes-Hut approximation parameter.
    """

    @typing.override
    def __init__(
        self,
        theta: float = 0.5,
        time_step_size: float = 1.0,
        gravitational_field: vectors.FieldVector = np.zeros(3, dtype=float),
        electric_field: vectors.FieldVector = np.zeros(3, dtype=float),
        magnetic_field: vectors.FieldVector = np.zeros(3, dtype=float),
        particles_list: list[particles.PointParticle] = []
    ) -> None:
        self.particles_list = particles_list

        self.particles_data = pd.DataFrame({
            't': np.empty(0, dtype=float),
            'x': np.empty(0, dtype=float),
            'y': np.empty(0, dtype=float),
            'z': np.empty(0, dtype=float)
        })

        # Constant, universal fields.
        self.gravitational_field = gravitational_field
        self.electric_field = electric_field
        self.magnetic_field = magnetic_field

        self.current_time_step = 0
        self.time_step_size = time_step_size

        self.theta = theta

    def record_particle_data(self, particle: particles.PointParticle) -> None:
        """Save the state of a particle to the particles data.

        Parameters
        ----------
        particle : :class:`particles.PointParticle`
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

        for particle in self.particles_list:
            output_string += particle.__str__() + '\n'

        output_string += '\n'

        return output_string

    def calculate_particle_force(
        self,
        particle: particles.PointParticle,
        barnes_hut_root: particles.BarnesHutNode,
        position: vectors.PositionVector | None = None,
        velocity: vectors.VelocityVector | None = None
    ) -> vectors.ForceVector:
        """Calculate the force exerted on a particle by the fields and
        other particles.

        Parameters
        ----------
        particle : :class:`particles.PointParticle`
            The particle to calculate the force upon.
        barnes_hut_root : BarnesHutNode
            The Barnes-Hut tree that contains all the particles.
        position : :type:`vectors.PositionVector`, optional
            A hypothetical position of the particle to calculate with,
            possibly different from its current position.
            If ``None``, defaults to
            :attr:`particle.position <particles.PointParticle.position>`.
        velocity : :type:`vectors.VelocityVector`, optional
            A hypothetical velocity of the particle to calculate with,
            possibly different from its current position.
            If ``None``, defaults to
            :attr:`particle.velocity <particles.PointParticle.velocity>`.

        Returns
        -------
        :type:`vectors.ForceVector`
            The force exerted on a particle by the fields and other
            particles.
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
        barnes_hut_root = particles.BarnesHutNode(self.particles_list)

        # Stores the new positions and velocities.
        new_data = np.zeros((len(particles_list), 2, 3))

        # Update particle positions and velocities before calculating the forces.
        for i in range(len(particles_list)):
            particle = particles_list[i]

            # Update particle acceleration.
            particle.acceleration = self.calculate_particle_force(
                particle, barnes_hut_root
            ) / particle.MASS

            # Record data after updating acceleration.
            self.record_particle_data(particle)

            # Use the classic Runge-Kutta method to to approximate velocity and position.
            rk4_accelerations = np.zeros((4, 3))
            rk4_velocities = np.zeros((4, 3))

            rk4_accelerations[0] = particle.acceleration
            rk4_velocities[0] = particle.velocity

            rk4_accelerations[1] = self.calculate_particle_force(
                particle, barnes_hut_root
            ) / particle.MASS
            rk4_velocities[1] = (particle.velocity
                                 + rk4_accelerations[0] * self.time_step_size / 2)
            position = (particle.position
                        + rk4_velocities[0] * self.time_step_size / 2
                        + 1/2 * rk4_accelerations[0] *
                        (self.time_step_size / 2) ** 2
                        )

            rk4_accelerations[2] = self.calculate_particle_force(
                particle, barnes_hut_root, position, rk4_velocities[1]
            ) / particle.MASS
            rk4_velocities[2] = (particle.velocity
                                 + rk4_accelerations[1] * self.time_step_size / 2)
            position = (particle.position
                        + rk4_velocities[1] * self.time_step_size / 2
                        + 1/2 * rk4_accelerations[1]
                        * (self.time_step_size / 2) ** 2
                        )

            rk4_accelerations[3] = self.calculate_particle_force(
                particle, barnes_hut_root, position, rk4_velocities[2]
            ) / particle.MASS
            rk4_velocities[3] = (particle.velocity
                                 + rk4_accelerations[2] * self.time_step_size)
            position = (particle.position
                        + rk4_velocities[2] * self.time_step_size
                        + 1/2 * rk4_accelerations[2] * self.time_step_size ** 2
                        )

            # Calculate the new velocity and position.
            new_data[i, 0] = (
                particle.position
                + self.time_step_size / 6
                * (
                    rk4_velocities[0]
                    + 2 * rk4_velocities[1]
                    + 2 * rk4_velocities[2]
                    + rk4_velocities[3]
                )
            )
            new_data[i, 1] = (
                particle.velocity
                + self.time_step_size / 6
                * (
                    rk4_accelerations[0]
                    + 2 * rk4_accelerations[1]
                    + 2 * rk4_accelerations[2]
                    + rk4_accelerations[3]
                )
            )

        # Update the particle's position and velocity.
        for i in range(len(particles_list)):
            particle = particles_list[i]

            # Update position, velocity, and acceleration.
            particle.position = new_data[i, 0]
            particle.velocity = new_data[i, 1]

        self.current_time_step += 1

    def run(
        self,
        num_time_steps: int = 1,
        file_handler: files.FileHandler | None = None,
        print_progress: bool = False
    ) -> None:
        """Run the simulation for a given number of time steps.

        Parameters
        ----------
        num_time_steps : int, default=1
            The number of time steps that the simulation runs by.
        file_handler : :class:`files.FileHandler`, optional
            A :class:`files.FileHandler` object,
            which writes data into a text file as the simulation runs.
            If ``None``, do not write any data into a file.
        print_progress : bool, default=False
            Whether to print a progress report on how much of the simulation
            has been completed.
        """
        # Stores the file output.
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
                    # Print the current progress
                    # and then return to the beginning of the line.
                    print(f'Progress: {round(progress * 100, 1)}%', end='\r')

        except Exception as exception:
            # If an error occurs in the middle for unknown reasons, close the output file.
            if file_handler is not None:
                file_handler.close_output_file()

            raise exception

        else:
            # Record final state of the particles.
            for particle in particles_list:
                # Generate the root node of the octree.
                barnes_hut_root = particles.BarnesHutNode(self.particles_list)

                # Update the particle's final acceleration.
                particle.acceleration = self.calculate_particle_force(
                    particle, barnes_hut_root) / particle.MASS

                # Record data for the final time.
                self.record_particle_data(particle)

            if file_handler is not None:
                # Write final particle states.
                file_handler.append_to_output_file(self.get_particles_string())
                file_handler.close_output_file()

        # If printing progress reports,
        # add an extra line to account for the carriage returns.
        if print_progress:
            print()


if __name__ == '__main__':
    # Check if the user supplied a input file.
    if len(sys.argv) < 2:
        raise ValueError('Please enter the name of the input file.')

    # Read the input file data and create particles based on it.

    # Attempt to read the input file.
    try:
        file_handler = files.FileHandler(input_filepath=sys.argv[1])

    except OSError:
        raise OSError(
            'The input file does not exist or does not contain a properly '
            'formatted JSON. Please correct it.'
        )

    # Check if the input file conforms to the schema.
    if not file_handler.validate_input_dict(file_handler.INPUT_DATA):
        raise ValueError(
            'The input file contains a properly formatted JSON, '
            'but it does not conform to the JSON schema. Please correct it.'
        )

    # Create a list of particles as described by the file data.
    particles_list = [
        particles.PointParticle(
            position=np.array(particle['position']),
            velocity=np.array(particle['velocity']),
            mass=particle['mass'],
            charge=particle['charge']
        )
        for particle in file_handler.INPUT_DATA['particles']
    ]

    # Create and run the simulation.
    simulation = Simulation(
        theta=file_handler.INPUT_DATA['theta'],
        time_step_size=file_handler.INPUT_DATA['time step size'],
        gravitational_field=np.array(
            file_handler.INPUT_DATA['gravitational field']),
        electric_field=np.array(file_handler.INPUT_DATA['electric field']),
        magnetic_field=np.array(file_handler.INPUT_DATA['magnetic field']),
        particles_list=particles_list
    )
    simulation.run(
        num_time_steps=file_handler.INPUT_DATA['num time steps'],
        file_handler=file_handler,
        print_progress=True
    )

    # Plot the simulation.
    plot = plot.Plot(
        data_frame=simulation.particles_data,
        time_step_size=simulation.time_step_size
    )

    # plot.save_plot_to_file()
    plot.show()
