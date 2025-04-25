from __future__ import annotations

import numpy as np
import scipy.constants

import vectors


class PointParticle:
    """A point particle with a specified position, charge, and mass.
    """

    current_id = 0
    """Used to assign an identifier to each particle."""

    def __init__(
        self,
        position: vectors.PositionVector = np.array([0, 0, 0]),
        velocity: vectors.VelocityVector = np.array([0, 0, 0]),
        acceleration: vectors.AccelerationVector = np.array([0, 0, 0]),
        mass: np.float64 = 1.0,
        charge: np.float64 = 0.0,
        fixed: bool = False
    ) -> None:
        """Initialize a single point particle with a position, charge, and mass.

        Parameters
        ----------
        position : vectors.PositionVector
            The initial position of the particle.
            X is left/right, Y is forward/backward, Z is up/down.
            Specified in meters(m). 
        velocity : vectors.VelocityVector
            The initial velocity of the particle.
            X is left/right, Y is forward/backward, Z is up/down.
            Specified in meters per second(m/s). 
        acceleration : AccelerationVector
            The initial acceleration of the particle.
            X is left/right, Y is forward/backward, Z is up/down.
            Specified in meters per second squared(m/s^2). 
        mass : np.float64, optional
            The mass of the charged particle in kilograms, by default 1.0
        charge : np.float64, optional
            The charge of the particle in coulombs, by default 0.0
        fixed : bool, optional
            Whether this particle's position is constant, by default False
        """
        # Represented by arrays of (X, Y, Z).
        self.position = position.astype(np.float64)
        self.velocity = velocity
        self.acceleration = acceleration

        self.mass = mass
        self.charge = charge

        self.fixed = fixed

        self.id = PointParticle.current_id
        PointParticle.current_id += 1

    def add_force(self, force: vectors.ForceVector) -> None:
        """Update the particle's acceleration by adding a force.

        Parameters
        ----------
        force : np.float64
            The force that is being applied to the particle
        """
        if not self.fixed:
            self.acceleration += force / self.mass

    def set_force(self, force: vectors.ForceVector) -> None:
        self.acceleration = force / self.mass

    def clear_force(self) -> None:
        """Set the force acting upon the particle to 0.
        """
        self.acceleration *= 0

    def apply_lorentz_force_law(self, electric_field: vectors.FieldVector, magnetic_field: vectors.FieldVector) -> None:
        """Calculate and apply the effects of an electromagnetic field on upon this particle.

        Parameters
        ----------
        electric_field : np.ndarray
            A 3D vector measured in N/C representing the electric field acting upon this particle.
        magnetic_field : np.ndarray
            A 3D vector measured in teslas representing the magnetic field acting upon this particle.
        """
        self.apply_electric_field(electric_field)
        self.apply_magnetic_field(magnetic_field)

    def get_gravitational_field(self, point: vectors.PositionVector) -> vectors.FieldVector:
        """Calculate the gravitational field created by this particle at `point`. 

        Parameters
        ----------
        point : np.ndarray
            A 3D vector representing the coordinates of the point that this particle is exerting a gravitational field upon.

        Returns
        -------
        np.ndarray
            A vector of the gravitational field generated at `point`.
        """
        vector_between_points = self.position - point
        distance = np.linalg.norm(vector_between_points)
        unit_vector = vector_between_points / distance

        return unit_vector * scipy.constants.G * self.mass / distance ** 2

    def apply_gravitational_field(self, gravitational_field: vectors.FieldVector) -> None:
        """Calculate and apply the effects of a gravitational field upon this particle.

        Parameters
        ----------
        gravitational_field : np.ndarray
            A 3D vector measured in N/kg representing the gravitational field acting upon this particle.
        """
        self.add_force(self.mass * gravitational_field)

    def get_electric_field(self, point: vectors.PositionVector) -> vectors.FieldVector:
        """Calculate the electric field at `point` due to this particle.

        Parameters
        ----------
        point : np.ndarray
            A 3D vector representing a coordinate.

        Returns
        -------
        np.ndarray
            The vector of the electric field that this particle creates at the point
        """
        vector_between_particles = point - self.position
        distance = np.linalg.norm(vector_between_particles)
        unit_vector = vector_between_particles / distance

        # The Coulomb constant
        k = 1 / (4 * scipy.constants.pi * scipy.constants.epsilon_0)

        # The electric force between the particles
        electric_field = (k * self.charge) / (distance ** 2)

        return -electric_field * unit_vector

    def apply_electric_field(self, electric_field: vectors.FieldVector) -> None:
        """Calculate and apply the effects of a electric field upon this particle.

        Parameters
        ----------
        electric_field : np.ndarray
            A 3D vector measured in N/C representing the electric field acting upon this particle.
        """
        self.add_force(self.charge * electric_field)

    def get_magnetic_field(self, point: vectors.PositionVector) -> vectors.FieldVector:
        """Calculate the magnetic field exerted by by this particle at `point`. 

        Parameters
        ----------
        point : np.ndarray
            The point at which to calculate the magnetic field

        Returns
        -------
        np.ndarray
            The vector of the magnetic field exerted by this particle at `point`.

        Notes
        -----
        It uses the "Biot-Savart Law for point charges," technically a misnomer,
        which only approximates magnetic fields for particles with a velocity << c.
        """
        # The vector between the positions of the particles
        r = point - self.position
        # The unit vector of `r`
        r_hat = r / np.linalg.norm(r)

        magnetic_field = (scipy.constants.mu_0 * self.charge * np.cross(self.velocity, r_hat)
                          / (4 * np.pi * np.linalg.norm(r) ** 2))

        return magnetic_field

    def apply_magnetic_field(self, magnetic_field: vectors.FieldVector) -> None:
        """Calculate and apply the effects of a magnetic field upon this particle.

        Parameters
        ----------
        magnetic_field : np.ndarray
            A 3D vector measured in teslas representing the magnetic field acting upon this particle.
        """
        self.add_force(
            self.charge * np.cross(self.velocity, magnetic_field)
        )

    def __str__(self) -> str:
        position = f'({", ".join((str(dimension) for dimension in self.position))})'
        velocity = f'<{", ".join((str(dimension) for dimension in self.velocity))}>'
        acceleration = f'<{", ".join((str(dimension) for dimension in self.acceleration))}>'

        return f'Particle {self.id}: m={self.mass}, Q={self.charge}, r={position}, v={velocity}, a={acceleration}'
