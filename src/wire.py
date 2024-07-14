import numpy as np


class Wire():
    """A straight current-carrying wire with a specified position, length, and resistance.
    """
    def __init__(self, end1: np.array, end2: np.array, resistance: np.float64) -> None:
        """Initiate a an electric wire

        Parameters
        ----------
        end1 : np.array
            The coordinates of one end of the wire
        end2 : np.array
            The coordinates of the other end of the wire
        current : np.float64
            The current running through the wire in amperes
        resistance : np.float64
            The total resistance of the wire
        """
        self.end1 = end1
        self.end2 = end2
        self.resistance = resistance