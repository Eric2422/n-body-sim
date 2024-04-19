import math
from scipy import constants

from position import Position

class Particle:
    """
    Represent a single charged particle with a specified position, charge, and mass
    """
    
    def __init__(self, position: Position, charge: float = 0.0, mass: float = 1) -> None:
        """
        Initialize a single particle with a position, charge, and mass.

        Parameters
        ----------
        position : Position
            The position that the particle is at
            Specified in meters. 
        charge : float, optional
            The charge of the particle in coulombs, by default 0.0
        mass : float, optional
            The mass of the charged paritcle in kilograms, by default 1
        """
        self.position = position
        self.charge = charge
        self.mass = mass

    def coulumbs_law(self, particle) -> float:
        """
        Calculate the force between this particle and another particle using Coulumb's law.

        Parameters
        ----------
        particle : Particle
            The other charged particle that is interacting with this one.

        Returns
        -------
        float
            The force between this charge and another
        """
        distance = self.position.get_distance(particle.position)
        k = 4 * constants.pi * constants.epsilon_0

        return (self.charge * particle.charge) / (k * distance ** 2)