import typing

import numpy as np
import numpy.typing as npt

import vectors


class NumericalIntegration:
    """Contains static methods to solve time-dependent
    initial value problems (IVPs) using numerical analysis.
    """
    @staticmethod
    def eulers(
        derivative: typing.Callable[
            [float, npt.NDArray[np.float64]],
            npt.NDArray[np.float64]
        ],
        initial_values: npt.NDArray[np.float64] = np.zeros(3),
        initial_time: float = 0.0,
        time_step_size: float = 1,
        num_time_steps: int = 1
    ) -> npt.NDArray[np.float64]:
        """Approximate the solution to the IVP via Euler's method
        using the given time step size and number of time steps.

        Parameters
        ----------
        `derivative` : `typing.Callable[[float, npt.NDArray[np.float64]], npt.NDArray[np.float64]]`
            The derivative to integrate.
            The first argument should be time,
            while the second argument should be the spatial dimensions.
            There should be at least one spatial dimension,
            but there is no upper limit.

            The returned array should have the same dimensions as the input array
            and initial values.
        `initial_values` : `npt.NDArray[np.float64]`, optional
            The initial values used to solve the IVP.
            It should have the same dimensions as the input and output arrays of `derivative`.

            By default `np.zeros(3)`
        `initial_time` : `float`, optional
            THe initial time of the IVP, by default 0.0
        `time_step_size` : `float`, optional
            The time step size used to integrate the IVP, by default 1
        `num_time_steps` : `int`, optional
            The number of time steps to integrate by, by default 1

        Returns
        -------
        `npt.NDArray[np.float64]`
            An array with the same dimensions as the `initial_values` and
            input and output arrays of `derivative`.

            Contains the values of the spatial dimensions after integrating
            for the given number of time steps.

        Raises
        ------
        `ValueError`
            Raised if the time step size is 0,
            the number of time steps is less than 1,
            or the arrays do not match in dimension.
        """
        # Prevent an invalid time steps size.
        if time_step_size == 0:
            raise ValueError(
                "Euler's method requires a non-zero time step size.")

        # Prevent an invalid number of time steps.
        if num_time_steps < 1:
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
    def runge_kutta(
        derivative: typing.Callable[
            [float, npt.NDArray[np.float64]],
            npt.NDArray[np.float64]
        ],
        initial_values: npt.NDArray[np.float64] = np.zeros(3),
        initial_time: float = 0.0,
        time_step_size: float = 1,
        num_time_steps: int = 1
    ):
        pass

    @staticmethod
    def leapfrog(
        acceleration: typing.Callable[
            [float, vectors.PositionVector],
            vectors.AccelerationVector
        ],
        initial_values: np.ndarray = np.zeros(3),
        initial_time: float = 0,
        time_step_size: float = 1,
        num_time_steps: int = 1
    ):
        pass
