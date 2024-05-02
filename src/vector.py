import math

import numpy as np

class Vector:
    def __init__(self, magnitude: float = 0, horizontal_direction: float = 0, vertical_direction: float = 0) -> None:
        """
        Instantiate a vector with a magnitude and direction

        Parameters
        ----------
        magnitude : float, optional
            The magnitude of the vector, by default 0
        direction : float, optional
            The direction of the vector in radians, by default 0
        """
        self.magnitude = magnitude
        self.direction = (horizontal_direction, vertical_direction)


    def get_components(self) -> np.array:
        """
        Calculate the components of this vector.

        Returns
        -------
        np.array
            _description_
        """
        x_component = self.magnitude * math.cos(self.direction)

        