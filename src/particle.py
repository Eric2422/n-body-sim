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
            The mass of the charged particle in kilograms, by default 1.0
        """
        # Represented by arrays of (X, Y, Z).
        self.position = position
        self.velocity = np.array((0, 0, 0))
        self.acceleration = np.array((0, 0, 0))

        self.charge = charge
        self.mass = mass

    def coulumbs_law(self, particle: Particle) -> np.array:
        """
        Calculate the force between this particle and another particle using Coulumb's law.

        Parameters
        ----------
        particle : Particle
            The other charged particle that is interacting with this one.

        Returns
        -------
        np.array
            The force vector between this charge and another one.
        """
        distance = math.dist(self.position, particle.position)

        k = 1 / (4 * constants.pi * constants.epsilon_0)

        force_magnitude = (k * self.charge * particle.charge) / (distance ** 2)

        x_distance = particle.position[0] - self.position[0]
        y_distance = particle.position[1] - self.position[1]
        z_distance = particle.position[2] - self.position[2]

        horizontal_angle = math.atan2()

        return 
    
    def __str__(self) -> str:
        return f'Particle with {self.charge} C and {self.mass} kg at {self.position}'