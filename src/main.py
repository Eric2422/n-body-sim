import sys

import numpy as np
import pandas as pd

from barnes_hut import BarnesHutNode
from files import FileHandler
from particle import PointParticle
from plot import Plot
import numerical_integration
import vectors


class Simulation():
    """Represents one simulation with particles and fields.

    Contains the theta; time_step() size; constant, uniform gravitational field; constant, uniform electrical field; 
    constant, uniform magnetic field; and particles used in the simulation.

    Keeps track of the previous positions of all the partices.
    """

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
        theta : float, optional
            The Barnes-Hut approximation parameter, by default 0.5
        time_step_size : float, optional
            The time increment of the simulation in seconds (s), by default 1.0
        gravitational_field : vectors.FieldVector, optional
            A constant, uniform gravitational field, by default np.zeros(3, dtype=float)
        electric_field : vectors.FieldVector, optional
            A constant, uniform electric field, by default np.zeros(3, dtype=float)
        magnetic_field : vectors.FieldVector, optional
            A constant, uniform magnetic field, by default np.zeros(3, dtype=float)
        particles : list[PointParticle], optional
            A list of particles that are interacting with each other, by default []
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

    def log_particle_position(self, particle: PointParticle) -> None:
        """Save the position of a particle to the particle positions log.

        Parameters
        ----------
        particle : PositionParticle
            A particle to save the position of.
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

    def get_particle_positions_string(self) -> str:
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

    def time_step(self) -> None:
        """Run one time_step() of the simulation."""
        # Generate the root node of the octree
        barnes_hut_root = BarnesHutNode(particles=self.particles)

        # Update particle positions and velocities before calculating the forces.
        for particle in particles:
            self.log_particle_position(particle)

            

            # Simpson's rule.
            mid_velocity = particle.acceleration * (1 / 2) * self.time_step_size
            final_velocity = particle.acceleration * self.time_step_size
            delta_velocity = (self.time_step_size / 6) * (particle.velocity + 4 * mid_velocity + final_velocity)

            # Assume acceleration is constant.
            # Δx = vt + (1/2) at^2
            particle.position += particle.velocity * self.time_step_size + \
                (1 / 2) * particle.acceleration * self.time_step_size ** 2

            particle.velocity += particle.acceleration * self.time_step_size

        # Calculate the forces exerted on the particles and apply the corresponding acceleration.
        for particle in self.particles:
            net_force = np.zeros(3, dtype=float)

            # Use the Barnes-Hut algorithm to approximate the net force exerted on this particle.
            net_force += particle.get_force_experienced(
                barnes_hut_root.get_gravitational_field_exerted(
                    particle.position
                ),
                barnes_hut_root.get_electric_field_exerted(particle.position),
                barnes_hut_root.get_magnetic_field_exerted(particle.position)
            )

            # Add the constant fields
            net_force += particle.get_force_experienced(
                self.electric_field,
                self.magnetic_field,
                self.gravitational_field
            )

            # Update the particle's acceleration based on the force.
            particle.apply_force(net_force)

        self.current_time_step += 1

    def run(self, num_time_steps: int | float = 1, file_handler: FileHandler | None = None, print_progress: bool = False) -> None:
        """Run the simulation for a given number of time_step()s. 

        Parameters
        ----------
        num_time_steps : int | float, optional
            The number of time steps that the simulation runs by, by default 1
        file_handler : FileHandler, optional
            A `FileHandler` object to pass data into as the simulation runs.
            Writes the data into a file, so the data does not need to be looped through again afterward.
            By default None
        print_progress : bool, optional
            Whether to print a progress report on how much of the simulation has been completed, by default False
        """
        # Stores the file output
        output_string = ''

        if file_handler is not None:
            # Clear the output
            file_handler.clear_output_file()

            # Print fields
            output_string += f'g=<{", ".join((str(dimension) for dimension in self.gravitational_field))}>\n'
            output_string += f'E=<{", ".join((str(dimension) for dimension in self.electric_field))}>\n'
            output_string += f'B=<{", ".join((str(dimension) for dimension in self.magnetic_field))}>\n'
            output_string += '\n'

            # Log initial particle states
            output_string += self.get_particle_positions_string()

        if print_progress:
            progress = 0.0
            print(f'Progress: {progress}%', end='\r')

        # Run the necessary number of time_step()s
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
                output_string += self.get_particle_positions_string()

        # Log final state.
        for particle in particles:
            self.log_particle_position(particle)

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
            acceleration=np.array(particle['acceleration']),
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
        num_time_steps=file_data['num time_step()s'],
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
