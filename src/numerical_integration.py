import typing

import numpy as np
import numpy.typing as npt

import vectors


class NumericalIntegration:
    """A class of static methods to calculate time-dependent initial value problems (IVPs) using numerical analysis.
    """
    @staticmethod
    def eulers(
        derivative: typing.Callable[[float, npt.NDArray[np.float64]], npt.NDArray[np.float64]],
        initial_values: npt.NDArray[np.float64] = np.zeros(3),
        initial_time: float = 0.0,
        time_step_size: float = 1,
        num_time_steps: int = 1
    ) -> npt.NDArray[np.float64]:
        # Prevent an invalid time steps size.
        if time_step_size == 0:
            raise ValueError("Euler's method requires a non-zero time step size.")

        # Prevent an invalid number of time steps.
        if num_time_steps <= 0:
            raise ValueError("Euler's method requires at least one time step.")

        # Set up initial conditions.
        time = initial_time
        values = initial_values

        # Perform Euler's method the necessary number of times.
        for i in range(num_time_steps):
            # Avoid NumPy dimension errors.
            try:
                # Allow for going backward in time.
                values += derivative(time, values) * abs(time_step_size)

            except ValueError:
                raise ValueError(f'The derivative {getattr(callable, '__name__', 'Unknown')} returned an array'
                                 f'that is dimensionally incompatible with the initial values.')

            time += time_step_size

        return values

    @staticmethod
    def runge_kutta():
        pass

    @staticmethod
    def leapfrog(
        acceleration: typing.Callable[[vectors.PositionVector], vectors.AccelerationVector],
        initial_values: np.ndarray = np.zeros(3),
        time: float = 1
    ):
        pass
