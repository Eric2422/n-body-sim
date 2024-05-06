import sys

import numpy as np

from files import Files
from particle import Particle


class Simulation():
    def __init__(self, particles: list, delta_time: float = 1.0) -> None:
        """
        Create one simulation.

        Parameters
        ----------
        particles : list
            A list of particles that are interacting with each other
        delta_time : float, optional
            The amount of time between each tick in seconds, by default 1.0
        """
        self.particles = particles
        self.delta_time = delta_time

    def tick(self):
        """Run one tick of the simulation(i.e. the time specified by delta_time).
        """
        for i in range(len(particles)):
            for j in range(len):
                pass

        for particle in self.particles:
            particle.velocity += particle.acceleration
            particle.position += particle.velocity


if __name__ == '__main__':
    # Check if the user supplied a config file
    if len(sys.argv) < 2:
        print('Please enter the name of the config file.')
        sys.exit()

    # Read the config file data and create particles based on that data
    file_data = Files.read_config_file(sys.argv[1])
    particles = [
        Particle(
            np.array((line[0], line[1], line[2])), 
            line[3],
            line[4]
        )
        for line in file_data
    ]

    simulation = Simulation(particles)