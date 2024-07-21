import numpy as np

import scipy.conftest
import scipy.constants
import scipy.integrate

from particle import PointParticle


class Wire():
    """A straight current-carrying wire with a specified position, length, and resistance.
    """

    def __init__(self, end1: np.ndarray, end2: np.ndarray, resistance: np.float64) -> None:
        """Initiate a an electric wire

        Parameters
        ----------
        end1 : np.ndarray
            The coordinates of one end of the wire
        end2 : np.ndarray
            The coordinates of the other end of the wire
        resistance : np.float64
            The total resistance of the wire
        """
        self.end1 = end1
        self.end2 = end2
        self.resistance = resistance

    def calculate_length(self) -> np.float64:
        """Calculate the length of the wire.

        Returns
        -------
        np.float64
            A scalar value representing the length of this wire. 
        """
        return np.linalg.norm(self.end2 - self.end1)

    def calculate_electromotive_force(self, particles: list) -> np.float64:
        """Calculate the electromotive force(emf) across the wire from the particle.

        Parameters
        ----------
        particle : PointParticle
            The particle that is exerting a electric field across the wire.

        Returns
        -------
        The difference in electric potential between the ends of the wires.
        """
        # The vector of the space between the wires
        wire_vector = self.end2 - self.end1
        unit_vector = wire_vector / self.get_length()

        def sum_electric_fields(point: np.ndarray):
            map(lambda x: x.electric_field(point), particles)

        # Find the negative integral of the electric field from one end of the wire to the other
        return -scipy.integrate.quad_vec(
            lambda x: sum_electric_fields(self.end1.point + unit_vector * x),
            0, self.get_length()
        )

    def calculate_current(self) -> np.float64:
        return self.electromotive_force() / self.resistance

    def calculate_magnetic_field(self, point: np.ndarray) -> np.ndarray:
        """_summary_

        Parameters
        ----------
        point : np.ndarray
            _description_

        Returns
        -------
        np.ndarray
            _description_
        """
        def r(l) -> np.ndarray:
            wire_vector = self.end2 - self.end1
            unit_vector = wire_vector / self.get_length()
            return point - (self.end1 + l * unit_vector)

        return scipy.constants.mu_0 * np.cross(
            self.current(),
            scipy.integrate.quad(
                r() / np.linalg.norm(r()) ** 3,
                0,
                self.get_length()
            )
        ) / 4 * scipy.constants.pi
