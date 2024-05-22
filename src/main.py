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

    def tick(self):
        """Run one tick of the simulation(i.e. the time specified by delta_time).
        """
        # Loop through all the particles
        # for particle1 in self.particles:
        #     force = 0
            
        #     # Calculate the force of the other particles on this particle
        #     for particle2 in self.particles:
        #         force += particle1.coulombs_law(particle2) if particle1 != particle2 else 0
            
        #     # Apply the force by calculating the acceleration on the particle
        #     particle1.acceleration = force / particle1.mass

        #     particle1.velocity += particle1.acceleration
        #     particle1.position += particle1.velocity
        num_particles = len(self.particles)
        for i in range(num_particles):
            particle1 = self.particles[i]

            for j in range(i, num_particles):
                particle2 = self.particles[j]
                force = particle1.coulombs_law(particle2)

                particle1.acceleration += force / particle1.mass
                particle2.acceleration -= force / particle2.mass

            particle1.velocity += particle1.acceleration
            particle1.position += particle1.velocity
            

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