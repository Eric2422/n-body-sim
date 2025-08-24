from enum import auto, Enum, unique

import numpy as np
from numpy import typing as npt
import scipy
import scipy.integrate
import typing

import vectors


@unique
class WireMaterial(Enum):
    """An enum class of various common metals.

    Parameters
    ----------
    Enum : Enum
        A metal to be added to the enum.
    """
    COPPER = auto()
    SILVER = auto()
    GOLD = auto()
    ALUMINUM = auto()


MATERIAL_DENSITIES = {
    WireMaterial.COPPER: 8.96e3,
    WireMaterial.SILVER: 10.5e3,
    WireMaterial.GOLD: 19.3e3,
    WireMaterial.ALUMINUM: 2.70e3
}
"""
All data is at 20 degrees Celsius.
Densities are in kilograms per cubic meter (kg/m^3)
and are taken from the Royal Society of Chemistry(RSC): 
 - https://www.rsc.org/periodic-table/element/29/copper
 - https://www.rsc.org/periodic-table/element/47/silver 
 - https://www.rsc.org/periodic-table/element/79/gold
 - https://www.rsc.org/periodic-table/element/13/aluminium 
"""

MATERIAL_RESISTIVITIES = {
    WireMaterial.COPPER: 1.724e-8,
    WireMaterial.SILVER: 1.59e-8,
    WireMaterial.GOLD: 2.24e-8,
    WireMaterial.ALUMINUM: 2.65e-8
}
"""
All resistivities are taken from the Engineering Toolbox: 
https://www.engineeringtoolbox.com/resistivity-conductivity-d_418.html. 
The values are in ohm-meters(Ω⋅m)
"""


class Wire():
    """A straight, rigid, thin, circular, current-carrying wire with a specified position and length.
        Has uniform density and resistivity.
    """

    def __init__(
        self,
        points: npt.NDArray[np.float64],
        mass: float = 1.0,
        resistance: float = 1.0,
    ) -> None:
        """Initiate a straight current-carrying wire.

        Parameters
        ----------
        points : npt.NDArray[float]
            A 2D array of the points that the wire connects.
        mass : float
            The total mass of the wire in kilograms(kg). Greater than 0, by default 1.0
        resistance : float
            The resistance of the wire in ohms(Ω). Greater than 0, by default 1.0
        """
        self.points = points
        # The velocity of the center of mass
        # 3D vector
        self.velocity = np.zeros(shape=(3))
        # The acceleration of the center of mass
        # 3D vector
        self.acceleration = np.zeros(shape=(3))

        # Torque is a 3D vector consisting of pitch, yaw, and roll.
        # TODO: Type may change.
        self.torque = np.zeros(shape=(3))

        self.mass = mass
        self.resistance = resistance

    def get_unit_vector(self) -> vectors.UnitVector:
        """Get the unit vector in the direction of the wire from the first to last point.

        Returns
        -------
        vectors.UnitVector
            A 3D vector representing the unit vector in the direction of the wire. 
        """
        wire_vector = self.points[1] - self.points[0]
        return wire_vector / np.linalg.norm(wire_vector)

    def get_wire_point(self, distance: float) -> vectors.PositionVector:
        """Returns a point along the wire given a distance from the first point.

        Parameters
        ----------
        distance : float
            The distance from the start of the wire. 

        Returns
        -------
        vectors.PositionVector
            A 3D vector representing a point along the wire. 
        """
        return self.points[0] + self.get_unit_vector() * distance

    def get_closest_point(self, point: vectors.PositionVector) -> vectors.PositionVector:
        """Given any point, find the wire point closest to it.

        Parameters
        ----------
        point : vectors.PositionVector
            Any point from which to find the closest wire point.

        Returns
        -------
        vectors.PositionVector
            The wire point that is closest to the given point.
        """
        # Get the vector from `point` to one end of the wire
        vector = point - self.points[0]
        return self.points[0] + (np.dot(vector, self.get_unit_vector()))

    def get_center_of_mass(self) -> vectors.PositionVector:
        """Get the position of the center of mass of this wire.

        Since the wire is of uniform linear density, the center of mass is in the middle.

        Returns
        -------
        vectors.PositionVector
            A 3D vector representing the position of the center of mass.
        """
        return (self.points[0] + self.points[1]) / 2.0

    def get_length(self) -> float:
        """Calculate the total length of the wire.

        Returns
        -------
        float
            A scalar value representing the total length of this wire. 
        """
        # Sum the distance between each point
        length = 0
        for i in range(0, len(self.points) - 1):
            length += np.linalg.norm(self.points[i+1] - self.points[i])

        return float(length)

    def get_electromotive_force(
            self,
            electric_field: typing.Callable[[
                vectors.PositionVector], vectors.FieldVector]
    ) -> float:
        """Calculate the electromotive force(emf) generated across the wire.

        Parameters
        ----------
        electric_field : typing.Callable[vectors.PositionVector], vectors.FieldVector]
            A function that returns the electric field at any given point.

        Returns
        -------
        float
            The electromotive force across this wire, measured in volts(V).
        """
        # Negative integral of the electric field across the wire.
        return -scipy.integrate.quad(
            lambda l: np.dot(
                electric_field(self.get_wire_point(l)),
                self.get_unit_vector()
            ),
            0,
            self.get_length()
        )[0]

    def get_current(self, electric_field: typing.Callable[[vectors.PositionVector], vectors.FieldVector]) -> float:
        """Calculate the current flowing through this wire.

        Parameters
        ----------
        electric_field : typing.Callable[[vectors.PositionVector], vectors.FieldVector]]
            A function that returns the electric field at any given point.

        Returns
        -------
        float
            The current flowing through this wire, measured in amps(A).
        """
        return self.get_electromotive_force(electric_field) / self.resistance

    def get_magnetic_field(
            self,
            field_point: vectors.PositionVector,
            electric_field: typing.Callable[[
                vectors.PositionVector], vectors.FieldVector]
    ) -> vectors.FieldVector:
        """Calculate the magnetic field generated by this wire at a point.

        Parameters
        ----------
        vectors.PositionVector
            A 3D vector of float representing a point to calculate the magnetic field at.
        electric_field : typing.Callable[[vectors.PositionVector], vectors.FieldVector]
            A function that returns the electric field at any given point.

        Returns
        -------
        vectors.FieldVector
            A 3D vector representing the strength of the magnetic field at the point in teslas(T). 

        Notes
        -----
        The calculation is based on the Biot-Savart law.
        Technically, the Biot-Savart law is only fully accurate for a steady current and electric field.
        However, it is a close-enough approximation if the current does not change too rapidly.
        """
        def r(l: float) -> vectors.PositionVector:
            """Calculate r, the 3D vector between the magnetic field point and the point of integration.

            Parameters
            ----------
            l : float
                The distance along this wire from `start_point` in meters.

            Returns
            -------
            vectors.PositionVector
                A 3D vector from the point of integration to `field_point`.
            """
            return field_point - self.get_wire_point(l)

        biot_savart_constant = scipy.constants.mu_0 / (4 * scipy.constants.pi)
        return biot_savart_constant \
            * self.get_current(electric_field) \
            * scipy.integrate.quad_vec(
                lambda l: np.cross(
                    self.get_unit_vector(),
                    r(l) / np.linalg.norm(r(l)) ** 3
                ),
                0,
                self.get_length()
            )[0]

    def apply_force(self, force: vectors.ForceVector) -> None:
        """Apply a net force to this wire. 

        Parameters
        ----------
        force : vectors.ForceVector
            The force that is applied upon this wire.
        """
        self.acceleration += force / self.mass

    def apply_torque(self, torque) -> None:
        self.torque += torque

    def apply_magnetic_field(
            self,
            magnetic_field: typing.Callable[[vectors.PositionVector], vectors.FieldVector],
            electric_field: typing.Callable[[
                vectors.PositionVector], vectors.FieldVector]
    ) -> None:
        """Apply a magnetic force to the wire based on a magnetic field.

        Parameters
        ----------
        magnetic_field : typing.Callable[[vectors.PositionVector], vectors.FieldVector]
            A function that returns the magnetic field at any given point.
        electric_field : typing.Callable[[ vectors.PositionVector], vectors.FieldVector]
            A function that returns the electric field at any given point.
        """
        self.apply_force(
            scipy.integrate.quad_vec(
                lambda l: np.cross(
                    magnetic_field(l),
                    self.get_unit_vector()
                ),
                self.points[0],
                self.points[1]
            )
        )

        self.apply_torque(
            scipy.integrate.quad_vec(
                lambda l: np.cross(
                    magnetic_field(l) * self.get_current(electric_field),
                    l - self.get_center_of_mass()
                ),
                self.points[0],
                self.points[1]
            )
        )
