from position import Position

class Particle:
    """
    Represent a single charged particle with a specified charge and mass
    """
    
    def __init__(self, position: Position, charge: float = 0.0, mass: float = 1) -> None:
        """
        Initialize a single particle

        Parameters
        ----------
        position : Position
            The position that the particle is at.
            Specified in 
        charge : float, optional
            The charge of the particle in coulombs, by default 0.0
        mass : float, optional
            The mass of the charged paritcle in kilograms, by default 1
        """
        self.position = position
        self.charge = charge
        self.mass = mass