import sys

import numpy as np
import pandas as pd

from files import FileHandler
from particle import PointParticle
from plot import Plot
from wires import Wire


class Simulation():
    def __init__(self, particles: list[PointParticle], total_ticks: int, tick_size: float = 1.0) -> None:
        """Initiate one simulation.

        Parameters
        ----------
        particles : list
            A list of particles that are interacting with each other.
        total_ticks: int
            The duration of the simulation, measured in ticks.
        tick_size : float, optional
            The time increment of the simulation in seconds, by default 1.0
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

        self.total_ticks = total_ticks
        self.current_tick = 0
        self.tick_size = tick_size

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
                particle2.get_electric_field(particle1.position),
                particle2.get_magnetic_field(particle1.position)
            )

            particle1.apply_gravitational_field(
                particle2.get_gravitational_field(
                    particle1.position
                )
            )

            # Lorentz force law
            particle2.apply_lorentz_force_law(
                particle1.get_electric_field(particle2.position),
                particle1.get_magnetic_field(particle2.position)
            )

            particle2.apply_gravitational_field(
                particle1.get_gravitational_field(
                    particle2.position
                )
            )

    def tick(self) -> float:
        """Run one tick of the simulation.

        Returns
        -------
        float
            Returns the progress of the simulator as a decimal, `p`,
            where 0 < `p` <= 1. 
            Progress is measured as how many ticks out of `self.total_ticks` have been completed.
        """
        # Calculate the forces that the particles exert on each other
        # Update the particle's acceleration and, but not the velocity and position
        index = 0

        for i in range(len(self.particles)):
            particle1 = self.particles[i]

            for j in range(i + 1, len(self.particles)):
                # print(f'i, j: {i}, {j}')
                particle2 = self.particles[j]
                self.apply_force_between_particles(particle1, particle2)

            # Add the constant fields
            particle1.apply_lorentz_force_law(
                self.electric_field, self.magnetic_field
            )
            particle1.apply_gravitational_field(self.gravitational_field)

            # print()

        # Update particle positions and velocities after calculating the forces,
        # so it doesn't affect force calculations.
        index = 0
        for particle in particles:
            # Save particle position data
            new_data = pd.DataFrame([{
                't': self.current_tick * self.tick_size,
                'x': np.array((particle.position[0])),
                'y': np.array((particle.position[1])),
                'z': np.array((particle.position[2]))
            }])
            self.particle_positions_log = pd.concat(
                [self.particle_positions_log, new_data], ignore_index=True)

            index += 1

            # Update the particle's velocity
            particle.velocity += particle.acceleration * self.tick_size

            # Update particle positions.
            particle.position += particle.velocity * self.tick_size

        self.current_tick += 1

        return self.current_tick / self.total_ticks

    def run(self, ticks_to_run: int = None, file_handler: FileHandler = None, print_progress=False) -> None:
        """Run the simulation for a given number of ticks. 

        Parameters
        ----------
        ticks_to_run : int, optional
            The number of ticks that the simulation runs by, by default `self.total_ticks`
        file_handler : FileHandler, optional
            A `FileHandler` object to pass data into as the simulation runs.
            Writes the data into a file, 
            so the data does not need to be looped through again afterward.
            By default None
        print_progress : bool, optional
            Whether to print a progress report on how much of the simulation has been completed, by default False
        """

        # By default, run the entire simulation
        if ticks_to_run == None:
            ticks_to_run = self.total_ticks

        file_handler.clear_output_file()

        # Run the necessary number of ticks
        output_string = ''
        for i in range(ticks_to_run):
            progress = self.tick()

            if print_progress:
                # Clear the previous line.
                sys.stdout.write('\033[K')
                # Print the current progress and then return to the beginning of the line.
                print(f'Progess: {round(progress * 100, 1)}%', end='\r')

            # If a `FileHandler` object is passed, output the results to a file.
            if file_handler is not None:
                # Add the current time and particle data to the file
                output_string += f'''Time: {self.current_tick *
                                            self.tick_size} s\n'''
                
                for particle in self.particles:
                    output_string += particle.__str__() + '\n'

                output_string += '\n'

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
    total_ticks = file_data['total ticks']
    tick_size = file_data['tick size']
    simulation = Simulation(
        particles,
        total_ticks=total_ticks,
        tick_size=tick_size
    )
    simulation.run(file_handler=file_handler, print_progress=True)

    # Plot the simulation
    plot = Plot(
        data_frame=simulation.particle_positions_log,
        tick_size=simulation.tick_size
    )
    plot.show()