import sys

import numpy as np

from files import FileHandler
from particle import PointParticle
from plot import Plot
from wire import Wire


class Simulation():
    def __init__(self, particles: list, num_ticks: int, tick_size: float = 1.0) -> None:
        """Initiate one simulation.

        Parameters
        ----------
        particles : list
            A list of particles that are interacting with each other
        num_ticks: int
            The number of ticks that the simulation runs for
        tick_size : float, optional
            The amount of time between each tick in seconds, by default 1.0
        """
        self.particles = particles
        # Keep a log of all the particles' positions over the course of the simulation
        self.particle_positions = np.empty((len(self.particles), num_ticks, 3))

        # Constant, universal fields
        self.electric_field = np.zeros(3)
        self.magnetic_field = np.zeros(3)
        self.gravitational_field = np.zeros(3)

        self.num_ticks = num_ticks
        self.current_tick = 0
        self.tick_size = tick_size

    def apply_force_from_particle(self, particle1: PointParticle, particle2: PointParticle):
        """Calculate and apply the force form `particle2` on `particle1`.

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
                    particle2.calculate_electric_field(particle1.position),
                    particle2.calculate_magnetic_field(particle1.position)
                )
                
                particle1.apply_gravitational_field(
                    particle2.calculate_gravitational_field(
                        particle1.position)
                )

    def tick(self) -> None:
        """Run one tick of the simulation(i.e. the time specified by `tick_size`).
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

        # Update position after calculating the force, so it doesn't affect the force calculations
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
        """
        if ticks_to_run == None:
            ticks_to_run = self.num_ticks

        # If a file handler is passed, output the results to a file
        for i in range(ticks_to_run):
            self.tick()

            if file_handler is not None:
                file_handler.append_to_file(
                    f'Time: {self.current_tick * self.tick_size} s')

                for particle in self.particles:
                    file_handler.append_to_file(particle.__str__())

                file_handler.append_to_file()


if __name__ == '__main__':
    # Check if the user supplied a config file
    if len(sys.argv) < 2:
        raise ValueError('Please enter the name of the config file.')

    # Read the config file data and create particles based on that data
    file_handler = FileHandler(sys.argv[1])
    file_data = file_handler.read_config_file()

    particles = [
        PointParticle(
            np.array((line[0], line[1], line[2])),
            line[3],
            line[4]
        )
        for line in file_data
    ]

    simulation = Simulation(particles, num_ticks=100, tick_size=0.1)
    simulation.run(file_handler=file_handler)

    plot = Plot(simulation.particle_positions, tick_size=simulation.tick_size)
    plot.show()
