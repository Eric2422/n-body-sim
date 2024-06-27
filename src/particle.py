from __future__ import annotations
import math

import numpy as np
import scipy.constants


class Particle:
    """Represent a single charged particle with a specified position, charge, and mass
    """

    def __init__(self, position: np.array, charge: float = 0.0, mass: float = 1.0) -> None:
        """Initialize a single particle with a position, charge, and mass.

        Parameters
        ----------
        position : np.array
            The position that the particle is at.
            X is left/right, Y is forward/backward, Z is up/down.
            Specified in meters. 
        charge : float, optional
            The charge of the particle in coulombs, by default 0.0
        mass : float, optional
            The mass of the charged particle in kilograms, by default 1.0
        """
        # Represented by arrays of (X, Y, Z).
        self.position = position
        self.velocity = np.array((0.0, 0.0, 0.0))
        self.acceleration = np.array((0.0, 0.0, 0.0))

        self.charge = charge
        self.mass = mass

    def apply_force(self, force: float):
        """
        Update the particle's acceleration by adding a force.

        Parameters
        ----------
        force : float
            The force that is being applied to the particle
        """
        self.acceleration += force / self.mass

    def coulombs_law(self, particle: Particle) -> np.array:
        """Calculate the force exerted on this particle by another particle.

        Parameters
        ----------
        particle : Particle
            The other charged particle that is interacting with this one.

        Returns
        -------
        np.array
            The force vector exerted on this charge by another one.
        """
        distance = math.dist(list(self.position), list(particle.position))

        k = 1 / (4 * scipy.constants.pi * scipy.constants.epsilon_0)

        # The magnitude of the electric force.
        force_magnitude = (k * self.charge * particle.charge) / (distance ** 2)

        vector_between_particles = particle.position - self.position

        # Break the electric force into X, Y, and Z components
        force_vector = np.array(
            [-force_magnitude * (coordinate / distance)
             for coordinate in vector_between_particles]
        )

        return force_vector

    def biot_savart_law(self, particle: Particle) -> np.array:
        """Calculate the magnetic force exerted on this particle by another particle. 
        It uses the "Biot-Savart Law for point charges," technically a misnomer,
        which only approximates magnetic fields for particles with a velocity << c.

        Parameters
        ----------
        particle : Particle
            Another particle which is exerting a magnetic field on this particle

        Returns
        -------
        np.array
            A vector the magnetic force that this particle experiences due to `particle`
        """
        # The vector between the positions of the particles
        r = particle.position - self.position
        r_hat = r / np.linalg.norm(r)

        magnetic_field = (scipy.constants.mu_0 * particle.charge * np.cross(particle.velocity * r_hat) 
                          / (4 * np.pi * r ** 2))
        
        print(f'B field: {magnetic_field}')

        magnetic_force = self.charge * np.cross(self.velocity, magnetic_field)

        return magnetic_force

    def __str__(self) -> str:
        coordinates = f'({", ".join([str(num) for num in self.position])})'
        return f'Particle with {self.charge} C and {self.mass} kg at {coordinates}'
