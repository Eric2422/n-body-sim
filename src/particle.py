from __future__ import annotations

import math
import numpy as np
from scipy import constants

class Particle:
    """
    Represent a single charged particle with a specified position, charge, and mass
    """
    
    def __init__(self, position: np.array, charge: float = 0.0, mass: float = 1.0) -> None:
        """
        Initialize a single particle with a position, charge, and mass.

        Parameters
        ----------
        position : np.array
            The position that the particle is at.
            X is left/right, Y is forward/backward, Z is up/down.
            Specified in meters. 
        charge : float, optional
            The charge of the particle in coulombs, by default 0.0
        mass : float, optional
            The mass of the charged paritcle in kilograms, by default 1
        """
        # Represented by arrays of (x, y, z).
        self.position = position
        self.velocity = np.array((0, 0, 0))
        self.acceleration = np.array((0, 0, 0))

        self.charge = charge
        self.mass = mass

    def get_distance(self, particle: Particle) -> float:
        """
        Calculate the distance between this particle and another particle in meters.

        Parameters
        ----------
        particle : Particle, optional
            The other particle to measure the distance to.

        Returns
        -------
        A float representing the distance to the other particle
        """
        x_distance = self.position[0] - particle.position[0]
        y_distance = self.position[1] - particle.position[1]
        z_distance = self.position[2] - particle.position[2]

        # Use Pythagorean's theorem to calculate the distance
        return math.sqrt(
            x_distance ** 2 
            + y_distance ** 2 
            + z_distance ** 2
        )

    def coulumbs_law(self, particle: Particle) -> np.array:
        """
        Calculate the force components between this particle and another particle using Coulumb's law.

        Parameters
        ----------
        particle : Particle
            The other charged particle that is interacting with this one.

        Returns
        -------
        np.array
            The force componenets between this charge and another one.
            Represented in the format (x, y, z)
        """
        distance = self.get_distance(particle)
        k = 1 / (4 * constants.pi * constants.epsilon_0)

        # The magnitute of the force
        force_magnitude = (k * self.charge * particle.charge) / (distance ** 2)

        # Decompose it into X, Y, and Z components
        angle = math.acos

        return 
    
    def __str__(self) -> str:
        return f'Particle with {self.charge} C and {self.mass} kg at {self.position}'