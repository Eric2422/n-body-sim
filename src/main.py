import sys

import numpy as np
import pandas as pd

from files import FileHandler
from particle import PointParticle
from plot import Plot
from wires import Wire


class Simulation():
    def __init__(self, particles: list[PointParticle], num_ticks: int, tick_size: float = 1.0) -> None:
        """Initiate one simulation.

        Parameters
        ----------
        particles : list
            A list of particles that are interacting with each other.
        num_ticks: int
            The duration of the simulation, measured in ticks.
        tick_size : float, optional
            The time increment of the simulation in seconds, by default 1.0
        """
        self.particles = particles
        # A log of all the particles' positions over the course of the simulation
        self.particle_positions = np.empty((len(self.particles), num_ticks, 3))

        # Constant, universal fields
        self.electric_field = np.zeros(3)
        self.magnetic_field = np.zeros(3)
        self.gravitational_field = np.zeros(3)

        self.num_ticks = num_ticks
        self.current_tick = 0
        self.tick_size = tick_size

    def apply_force_from_particle(self, particle1: PointParticle, particle2: PointParticle) -> None:
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

    def tick(self) -> None:
        """Run one tick of the simulation.
        """
        # Calculate the electrostatic force that the particles exert on each other
        # Update the particle's acceleration and and velocity, but not the position
        for particle1 in self.particles:
            # Calculate the forces from the other particles
            for particle2 in self.particles:
                self.apply_force_from_particle(particle1, particle2)

            # Add the constant fields
            particle1.apply_lorentz_force_law(
                self.electric_field, self.magnetic_field
            )
            particle1.apply_gravitational_field(self.gravitational_field)

            # Update the particle's velocity
            particle1.velocity += particle1.acceleration * self.tick_size

        # Update particle positions after calculating the forces, so it doesn't affect force calculations
        for index, particle in zip(range(len(self.particles)), self.particles):
            self.particle_positions[index][self.current_tick] = particle.position
            particle.position += particle.velocity * self.tick_size

        self.current_tick += 1

    def run(self, ticks_to_run: int = None, file_handler: FileHandler = None, plot: Plot = None) -> None:
        """Run the simulation for a given number of ticks. 

        Parameters
        ----------
        ticks_to_run : int, optional
            The number of ticks that the simulation runs by, by default `self.num_ticks`
        file_handler : FileHandler, optional
            A file handler to pass into 
        """
        if ticks_to_run == None:
            ticks_to_run = self.num_ticks

        file_handler.clear_output_file()

        # If a file handler is passed, output the results to a file
        output_string = ''
        for i in range(ticks_to_run):
            self.tick()

            if file_handler is not None:
                output_string += f'Time: {self.current_tick *
                                          self.tick_size} s\n'

                for particle in self.particles:
                    output_string += particle.__str__() + '\n'

                output_string += '\n'

        file_handler.append_to_output_file(output_string)


if __name__ == '__main__':
    # Check if the user supplied a config file
    if len(sys.argv) < 2:
        raise ValueError('Please enter the name of the config file.')

    wire_points = np.array(((0, 0, 0), (1, 1, 1)))
    wire = Wire(wire_points, 1)

    # Read the config file data and create particles based on that data
    file_handler = FileHandler(config_file=sys.argv[1])
    file_data = file_handler.read_config_file()

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

    simulation = Simulation(
        particles,
        num_ticks=file_data['num ticks'],
        tick_size=file_data['tick size']
    )
    simulation.run(file_handler=file_handler)

    print(
        simulation.particle_positions[:, :, 0]
    )
    data_frame = df = pd.DataFrame({
        "time": np.linspace(0, int(file_data['num ticks']), int(file_data['tick size'])),
        "x": simulation.particle_positions[:, :, 0], 
        "y": simulation.particle_positions[:, :, 1], 
        "z": simulation.particle_positions[:, :, 2]
    })
    print(data=df[df['time']==0])

    plot = Plot(simulation.particle_positions, tick_size=simulation.tick_size)
    plot.show()
