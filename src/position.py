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

    def get_distance(self, position) -> float:
        """
        Calculate the distance between this position and another position in meters.

        Parameters
        ----------
        position : Position
            The other position to measure the distance to.

        Returns
        -------
        A float representing the distance to the other position
        """
        x_distance = position.x - self.x
        y_distance = position.y - self.y
        z_distance = position.z - self.z

        return math.sqrt(x_distance ** 2 
                         + y_distance ** 2 
                         + z_distance ** 2)