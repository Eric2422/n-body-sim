import typing

import numpy as np

import vectors


class NumericalIntegration:
    """A class of static methods to calculate initival value problems (IVPs) using numerical analysis.
    """
    @staticmethod
    def eulers():
        pass

    @staticmethod
    def runge_kutta():
        pass

    @staticmethod
    def leapfrog(
        acceleration: typing.Callable[[vectors.PositionVector], vectors.ForceVector],
        time: float,
        initial_values: np.ndarray = np.zeros(3)
    ):
        pass
