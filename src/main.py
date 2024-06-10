import sys

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

    def calculate_electromagnetic_force(self, particle: Particle):
        pass

    def tick(self):
        """Run one tick of the simulation(i.e. the time specified by delta_time).
        """
        for particle in self.particles:
            net_force = self.calculate_electromagnetic_force(particle)

            
            

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

    force = particles[0].coulombs_law(particles[1])
    print(f'<{force[0]}, {force[1]}, {force[2]}>')

    simulation = Simulation(particles)
    for i in range(10):
        simulation.tick()

        for particle in simulation.particles:
            print(particle)