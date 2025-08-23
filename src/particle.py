from __future__ import annotations

import numpy as np
import scipy.constants

import typing
import vectors


class PointParticle:
    """A point particle with a specified position, charge, and mass."""

    current_id = 0
    """Used to assign an identifier to each particle."""

    def __init__(
        self,
        position: vectors.PositionVector = np.array([0.0, 0.0, 0.0]),
        velocity: vectors.VelocityVector = np.array([0.0, 0.0, 0.0]),
        acceleration: vectors.AccelerationVector = np.array([0.0, 0.0, 0.0]),
        fixed: bool = False,
        mass: float = 1.0,
        charge: float = 0.0
    ) -> None:
        """Initialize a single point particle with a position, charge, and mass.

        Parameters
        ----------
        position : vectors.PositionVector, optional
            The initial position of the particle in 3D space, by default np.array([0.0, 0.0, 0.0])
            x is left/right, y is forward/backward, z is up/down.
            Specified in meters(m).
        velocity : vectors.VelocityVector, optional
            The initial velocity of the particle in 3D space, by default np.array([0.0, 0.0, 0.0])
            x is left/right, y is forward/backward, z is up/down.
            Specified in meters per second(m/s).
        acceleration : vectors.AccelerationVector, optional
            The initial acceleration of the particle in 3D space, by default np.array([0.0, 0.0, 0.0])
            x is left/right, y is forward/backward, z is up/down.
            Specified in meters per second squared(m/s^2).
        fixed : bool, optional
            Whether this particle's position is constant, by default False
        mass : float | float, optional
            The mass of the charged particle in kilograms(kg), by default 1.0
        charge : float | float, optional
            The charge of the particle in coulombs(C), by default 0.0
        """
        # Represented by arrays of (x, y, z).
        self.position = position
        self.velocity = velocity
        self.acceleration = acceleration

        self.mass = np.float64(mass)
        self.charge = np.float64(charge)

        self.fixed = fixed
        """Whether this particle's position is constant."""

        self.id = PointParticle.current_id
        PointParticle.current_id += 1

    def set_force(self, force: vectors.ForceVector = np.zeros(3)) -> None:
        """Set the force of this particle based on the given force.

        Parameters
        ----------
        force : vectors.ForceVector, optional
            The force applied upon this particle, by default np.zeros(3)
        """
        self.acceleration = force / self.mass

    def get_gravitational_field_exerted(self, point: vectors.PositionVector) -> vectors.FieldVector:
        """Calculate the gravitational field created by this particle at `point`. 

        Parameters
        ----------
        point : vectors.PositionVector
            A 3D vector representing the coordinates of the point that this particle is exerting a gravitational field upon.

        Returns
        -------
        vectors.FieldVector
            A vector of the gravitational field generated at `point`.
        """
        r = point - self.position
        # If the points are overlapping, there is no force.
        if np.all(r == 0):
            return r

        distance = np.linalg.norm(r)

        return np.array(-r * scipy.constants.G * self.mass / (distance ** 3))

    def get_gravitational_force_experienced(self, gravitational_field: vectors.FieldVector) -> vectors.ForceVector:
        """Get the gravitational force acting upon this particle by the given gravitational field. 

        Parameters
        ----------
        gravitational_field : vectors.FieldVector
            A NumPy array of shape (1, 3) representing a 3D vector of the gravitational field acting upon this particle.

        Returns
        -------
        vectors.ForceVector
            A NumPy array of shape (1, 3) representing a 3D vector of the gravitational force 
            acting upon this particle as a result of the gravitational field.
        """
        return np.array(self.mass * gravitational_field)

    def get_electric_field_exerted(self, point: vectors.PositionVector) -> vectors.FieldVector:
        """Calculate the electric field at `point` due to this particle.

        Parameters
        ----------
        point : vectors.PositionVector
            A 3D vector representing a coordinate.

        Returns
        -------
        vectors.FieldVector
            The vector of the electric field that this particle creates at the point
        """
        r = point - self.position
        # If the points are overlapping, there is no force.
        if np.all(r == 0):
            return r

        distance = np.linalg.norm(r)

        # The Coulomb constant
        k = 1 / (4 * scipy.constants.pi * scipy.constants.epsilon_0)

        return np.array(- r * (k * self.charge) / (distance ** 3))

    def get_electrostatic_force_experienced(self, electric_field: vectors.FieldVector) -> vectors.ForceVector:
        """Get the electrostatic force acting upon this particle by the given electric field. 

        Parameters
        ----------
        electric_field : vectors.FieldVector
            A NumPy array of shape (1, 3) representing a 3D vector of the gravitational field acting upon this particle.

        Returns
        -------
        vectors.ForceVector
            A NumPy array of shape (1, 3) representing a 3D vector of the electrostatic force 
            exerted upon this particle by the electric field.
        """
        return self.charge * electric_field

    def get_magnetic_field_exerted(self, point: vectors.PositionVector) -> vectors.FieldVector:
        """Calculate the magnetic field exerted by by this particle at `point`. 

        Parameters
        ----------
        point : vectors.PositionVector
            The point at which to calculate the magnetic field.

        Returns
        -------
        vectors.FieldVector
            The vector of the magnetic field exerted by this particle at `point`.

        Notes
        -----
        It uses the "Biot-Savart Law for point charges," technically a misnomer,
        which only approximates magnetic fields for particles with a velocity << c.
        """
        r = point - self.position
        # If the points are overlapping, there is no force.
        if np.all(r == 0):
            return r

        distance = np.linalg.norm(r)

        return (scipy.constants.mu_0 * self.charge * np.cross(self.velocity, r)
                / (4 * np.pi * distance ** 3))

    def get_magnetic_force_experienced(self, magnetic_field: vectors.FieldVector) -> vectors.ForceVector:
        """Get the magnetic force acting upon this particle by the given electric field. 

        Parameters
        ----------
        magnetic_field : vectors.FieldVector
            A NumPy array of shape (1, 3) representing a 3D vector of the gravitational field acting upon this particle.

        Returns
        -------
        vectors.ForceVector
            A NumPy array of shape (1, 3) representing a 3D vector of the electrostatic force 
            exerted upon this particle by the magnetic field.
        """
        return self.charge * np.cross(self.velocity, magnetic_field)

    def get_force_experienced(
        self,
        gravitational_field: vectors.FieldVector,
        electric_field: vectors.FieldVector,
        magnetic_field: vectors.FieldVector
    ) -> vectors.ForceVector:
        return (
            self.get_gravitational_force_experienced(gravitational_field)
            + self.get_electrostatic_force_experienced(electric_field)
            + self.get_magnetic_force_experienced(magnetic_field)
        )

    def apply_fields(
        self,
        gravitational_field: vectors.FieldVector,
        electric_field: vectors.FieldVector,
        magnetic_field: vectors.FieldVector
    ) -> None:
        """Calculate and apply the effects of an electromagnetic field on upon this particle.

        Parameters
        ----------
        gravitational_field: vectors.FieldVector
            A 3D vector measured in newtons per kilogram(N/kg) representing the electric field acting upon this particle.
        electric_field :vectors.FieldVector
            A 3D vector measured in newtons per coulomb(N/C) representing the electric field acting upon this particle.
        magnetic_field :vectors.FieldVector
            A 3D vector measured in teslas(T) representing the magnetic field acting upon this particle.
        """
        self.set_force(
            self.get_gravitational_force_experienced(gravitational_field)
            + self.get_electrostatic_force_experienced(electric_field)
            + self.get_magnetic_force_experienced(magnetic_field)
        )

    def __str__(self) -> str:
        position_string = f'({", ".join((str(dimension) for dimension in self.position))})'
        velocity_string = f'<{", ".join((str(dimension) for dimension in self.velocity))}>'
        acceleration_string = f'<{", ".join((str(dimension) for dimension in self.acceleration))}>'

        return f'Point Particle {self.id}{'(fixed)' if self.fixed else ''}: r={position_string}, v={velocity_string}, a={acceleration_string}, m={self.mass}, Q={self.charge}'