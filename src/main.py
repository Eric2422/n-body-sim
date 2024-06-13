import sys

import matplotlib.pyplot
import numpy as np

from files import Files
from particle import Particle


class Simulation():
    def __init__(self, particles: list, delta_time: float = 1.0) -> None:
        """Initiate one simulation.

        Parameters
        ----------
        particles : list
            A list of particles that are interacting with each other
        delta_time : float, optional
            The amount of time between each tick in seconds, by default 1.0
        """
        self.particles = particles
        self.delta_time = delta_time

    def calculate_electromagnetic_force(self, particle1: Particle) -> np.array:
        net_force = 0

        # Find the net force on the given particle
        for particle2 in self.particles:
            if particle1 != particle2:
                net_force += particle1.coulombs_law(particle2)
        
        return net_force

    def tick(self) -> None:
        """Run one tick of the simulation(i.e. the time specified by delta_time).
        """
        for particle in self.particles:
            net_force = self.calculate_electromagnetic_force(particle)
            particle.apply_force(net_force)
            particle.velocity += particle.acceleration * self.delta_time
        
        for particle in self.particles:
            particle.position += particle.velocity * self.delta_time


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

    simulation = Simulation(particles, delta_time=0.1)
    for i in range(100):
        simulation.tick()

        for particle in simulation.particles:
            print(particle)
        print()