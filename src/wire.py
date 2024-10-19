from enum import auto, Enum, unique

import numpy as np
import scipy
import scipy.integrate

from particle import PointParticle


@unique
class WireMaterial(Enum):
    COPPER = auto()
    SILVER = auto()
    GOLD = auto()
    ALUMINUM = auto()


'''
All data is at 20 degrees Celsius.
Densities are in kilgrams per cubic meter (kg/m^3)
and are taken from the Royal Society of Chemistry(RSC): 
 - https://www.rsc.org/periodic-table/element/29/copper
 - https://www.rsc.org/periodic-table/element/47/silver 
 - https://www.rsc.org/periodic-table/element/79/gold
 - https://www.rsc.org/periodic-table/element/13/aluminium 
'''
MATERIAL_DENSITIES = {
    WireMaterial.COPPER: 8.96e3,
    WireMaterial.SILVER: 10.5e3,
    WireMaterial.GOLD: 19.3e3,
    WireMaterial.ALUMINUM: 2.70e3
}


'''
All restivities are taken from the Engineering Toolbox: 
https://www.engineeringtoolbox.com/resistivity-conductivity-d_418.html. 
The values are in ohm-meters(Ω⋅m)
'''
MATERIAL_RESISTIVITIES = {
    WireMaterial.COPPER: 1.724e-8,
    WireMaterial.SILVER: 1.59e-8,
    WireMaterial.GOLD: 2.24e-8,
    WireMaterial.ALUMINUM: 2.65e-8
}


class Wire():
    """A straight current-carrying wire with a specified position, length, and resistance."""

    def __init__(self, points: np.ndarray[np.float64],
                 mass: np.float64 = 1.0,
                 resistance: np.float64 = 1.0,
                 material: WireMaterial = None,
                 cross_sectional_area: np.float64 = -1.0
                 ) -> None:
        """Initiate a straight current-carrying wire.

        `resistance` and `mass` are meant to be mutually exclusive with `material` and `cross_sectional_area`.
        If all are specified, `resistance` and `mass` take precedence.

        Parameters
        ----------
        points : np.ndarray[np.float64]
            A 2D array of the points that the wire connects.
        mass : np.float64
            The total mass of the wire in kilograms(kg). Greater than 0, by default 1.0.
        resistance : np.float64
            The total resistance of the wire in ohms(Ω). Greater than 0, by default 1.0.
        material : WireMaterial
            The material that the wire is composed of(e.g. copper, silver, and aluminum), by default `None`
        cross_sectional_area : np.float64
            The cross sectional area of the wire in meters squared(m^2), by default -1.0.
        """
        self.points = points
        self.velocity = np.zeros(shape=3)
        self.acceleration = np.zeros(shape=3)

        if material == None and cross_sectional_area == -1.0:
            self.mass = mass
            self.resistance = resistance

        else:
            length = self.get_length()
            self.mass = length * cross_sectional_area * \
                MATERIAL_DENSITIES[material]
            self.resistance = MATERIAL_RESISTIVITIES[material] * \
                length / cross_sectional_area

    def get_unit_vector(self):
        wire_vector = self.points[1] - self.points[0]
        return wire_vector / np.linalg.norm(wire_vector)

    def get_wire_point(self, distance: np.float64) -> np.ndarray[np.float64]:
        """Returns a point along the wire given a distance from the first point.

        Args:
            distance (np.float64): _description_

        Returns:
            np.array[np.float64]: _description_
        """
        return self.points[0] + self.get_unit_vector() * distance

    def integrate_wire_segments(self, func) -> np.float64:
        """Perform a calculation on each segment of the wire and sum them.

        Parameters
        ----------
        func : function
            A function with a calculation to perform on each segment of the wire
        """
        total = 0

        # Loop through each segment of the wire
        for i in range(len(self.points) - 1):
            # The vector of the space between the points
            wire_vector = self.points[i+1] - self.points[i]
            unit_vector = wire_vector / np.linalg.norm(wire_vector)

            total += func()

        return total

    def get_length(self) -> np.float64:
        """Calculate the total length of the wire.

        Returns
        -------
        np.float64
            A scalar value representing the total length of this wire. 
        """
        # Sum the distance between each point
        length = 0
        for i in range(0, len(self.points) - 1):
            length += np.linalg.norm(self.points[i+1] - self.points[i])

        return length
    
    def get_electromotive_force(self, particles: list[PointParticle], electric_field: np.ndarray[np.float64]) -> np.float64:
        """Calculate the electromotive force(emf) generated across the wire.

        Parameters
        ----------
        particle : PointParticle
            The particle that is exerting a electric field across the wire.
        electric_field : np.ndarray[float64]
            A constant electric field that is being applied to the wire. 

        Returns
        -------
            The difference in electric potential between the ends of the wires.
        """
        def sum_electric_fields(field_point: np.ndarray[np.float64]) -> np.ndarray[np.float64]:
            """Calculate the net electric field at a given point.

            Parameters
            ----------
            field_point : np.ndarray
                A 3D vector representing the point to calculate the electric field at.

            Returns
            -------
            np.ndarray
                A 3D vector representing the net electric field in V/m or N/C.
            """
            # Find the electric field due to each particle
            electric_fields = map(
                lambda particle:
                    particle.electric_field(field_point),
                    particles
            )

            return sum(electric_fields) + electric_field

        # Negative integral of the electric field across the wire.
        emf = -scipy.integrate.quad(
            lambda l: np.dot(
                sum_electric_fields(self.get_wire_point(l)),
                self.get_unit_vector()
            ),
            0,
            self.get_length()
        )[0]

        return emf

    def get_current(self, particles: list[PointParticle], electric_field: np.ndarray[np.float64]) -> np.float64:
        """Calculate the current flowing through this wire.

        Returns
        -------
        np.float64
            The current flowing through the wire in amps.
        """
        return self.get_electromotive_force(particles, electric_field) / self.resistance

    def get_magnetic_field(self, field_point: np.ndarray[np.float64], particles: list[PointParticle], electric_field: np.ndarray[np.float64]) -> np.ndarray[np.float64]:
        """Calculate the magnetic field generated by this wire at a point.

        Parameters
        ----------
        field_point : np.ndarray
            A 3D vector of np.float64 representing a point to calculate the magnetic field at.

        Returns
        -------
        np.ndarray
            A 3D vector representing the strength of the magnetic field at the point in teslas. 
        """
        self.b_field = np.zeros(shape=3)

        def r(l: np.float64) -> np.ndarray[np.float64]:
            """Calculate r, the 3D vector between the magnetic field point and the point of integration.

            Parameters
            ----------
            l : np.float64
                The distance along this wire from `start_point` in meters.
            start_point : np.ndarray
                The point that the wire segment starts from.

            Returns
            -------
            np.ndarray
                A 3D vector from the point of integration to `field_point`.
            """
            return field_point - self.get_wire_point(l)
                
        # Biot-Savart law
        biot_savart_constant = scipy.constants.mu_0 / (4 * scipy.constants.pi)
        return biot_savart_constant \
            * self.get_current(particles, electric_field) \
            * scipy.integrate.quad_vec(
                lambda l: np.cross(
                    self.get_unit_vector(),
                    r(l) / np.linalg.norm(r(l)) ** 3
                ),
                0,
                self.get_length()
            )[0]

    def apply_force(self, force):
        pass

    def apply_magnetic_fields(self, particles: list[PointParticle], magnetic_field: np.ndarray[np.float64]) -> None:
        """Applies the force from particles and electric fields upon this wire. 

        Parameters
        ----------
        particles : list[PointParticle]
            The particles that surround this wire. 
        magnetic_field : np.ndarray[np.float64]
            The constant magnetic field that this wire is located in. 
        """
        magnetic_force = scipy.integrate.quad()


if __name__ == '__main__':
    points = np.array(
        (
            (-1e3, 0, 0),
            (1e3, 0, 0)
        )
    )

    wire = Wire(points, 1.0)
    electric_field = np.array((100, 0.0, 0.0))
    particles = ()
    print(wire.get_current(particles, electric_field))
    print()
    print(wire.get_magnetic_field(np.array((0.0, 0.0, 0.001)), particles, electric_field))
