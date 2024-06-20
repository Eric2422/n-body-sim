import sys

from matplotlib import pyplot as plt
import numpy as np

from files import Files
from particle import Particle
from plot import Plot

class Simulation():
    def __init__(self, particles: list, tick_size: float = 1.0) -> None:
        """Initiate one simulation.

        Parameters
        ----------
        particles : list
            A list of particles that are interacting with each other
        delta_time : float, optional
            The amount of time between each tick in seconds, by default 1.0
        """
        self.particles = particles
        self.tick_size = tick_size

        self.particle_positions = np.array([[] for particle in self.particles])

    def calculate_electromagnetic_force(self, particle1: Particle) -> np.array:
        """Calculate the electrostatitc force exerted on given particle in `self.particles`.

        Parameters
        ----------
        particle1 : Particle
            The particle to calculate the electrostatic force exerted on. 

        Returns
        -------
        np.array
            The net force vector exerted on `particle1`
        """
        net_force = 0

        # Find the net force on the given particle
        for particle2 in self.particles:
            if particle1 != particle2:
                net_force += particle1.coulombs_law(particle2)

        return net_force

    def tick(self) -> None:
        """Run one tick of the simulation(i.e. the time specified by `tick_size`).
        """
        # Calculate the electrostatic force that the particles exert on each other
        # Update the particle's acceleration and and velocity, but not the position
        for particle in self.particles:
            net_force = self.calculate_electromagnetic_force(particle)
            particle.apply_force(net_force)
            particle.velocity += particle.acceleration * self.tick_size

        # Update position after calculating the force, so it doesn't affect the force
        for particle in self.particles:
            particle.position += particle.velocity * self.tick_size


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

    simulation = Simulation(particles, tick_size=0.1)
    plot = Plot()

    for i in range(100):
        simulation.tick()

        for particle in simulation.particles:
            print(particle)

        print()