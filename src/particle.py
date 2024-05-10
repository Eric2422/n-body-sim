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
        self.velocity = np.array((0.0, 0.0, 0.0))
        self.acceleration = np.array((0.0, 0.0, 0.0))

        self.charge = charge
        self.mass = mass

    def coulombs_law(self, particle: Particle) -> np.array:
        """
        Calculate the force exerted on this particle by another particle.

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

        k = 1 / (4 * constants.pi * constants.epsilon_0)

        # The magnitude of the electric force. 
        force_magnitude = (k * self.charge * particle.charge) / (distance ** 2)

        vectorBetweenPoints = particle.position - self.position
        vectorMagnitude = np.linalg.norm(distance)

        # Break the electric force into X, Y, and Z components
        force_vector = np.array([-force_magnitude * (coordinate / vectorMagnitude) for coordinate in vectorBetweenPoints])
        
        return force_vector
    
    def __str__(self) -> str:
        return f'Particle with {self.charge} C and {self.mass} kg at {self.position}'