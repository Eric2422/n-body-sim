import math


class Position:
    def __init__(self, x: float = 0, y: float = 0, z: float = 0) -> None:
        """
        Initialize a representation of a point in 3D space

        Parameters
        ----------
        x : float, optional
            The x coordinate of the position measured in meters, by default 0.
        y : float, optional
            The y coordinate of the position measured in meters, by default 0.
        z : float, optional
            The z coordinate of the position measured in meters, by default 0.
        """
        self.x = x
        self.y = y
        self.z = z

    def __str__(self) -> str:
        return f'({self.x}, {self.y}, {self.z})'