import typing

import numpy as np
import scipy.constants

import vectors


class PointParticle:
    """A point particle with a specified position, charge, and mass."""

    current_id = 0
    """Used to assign an identifier to each particle.
    Increments every time a new particle is created."""

    @typing.override
    def __init__(
        self,
        position: vectors.PositionVector = np.array([0.0, 0.0, 0.0]),
        velocity: vectors.VelocityVector = np.array([0.0, 0.0, 0.0]),
        acceleration: vectors.AccelerationVector = np.array([0.0, 0.0, 0.0]),
        mass: float = 1.0,
        charge: float = 0.0
    ) -> None:
        """Initialize a single point particle with a position, charge, and mass.

        Parameters
        ----------
        position : vectors.PositionVector, optional
            The initial position of the particle in meters (m).
            x is left/right, y is forward/backward, z is up/down.

            By default `np.array([0.0, 0.0, 0.0])`.
        velocity : vectors.VelocityVector, optional
            The initial velocity of the particle in meters per second (m/s).
            x is left/right, y is forward/backward, z is up/down.

            By default `np.array([0.0, 0.0, 0.0])`.
        acceleration : vectors.AccelerationVector, optional
            The initial acceleration of the particle in meters per second squared (m/s^2).
            x is left/right, y is forward/backward, z is up/down.

            By default `np.array([0.0, 0.0, 0.0])`
        mass : float, default=1.0
            The mass of the charged particle in kilograms (kg).
        charge : float, default=0.0
            The charge of the particle in coulombs (C).
        """
        # Represented by arrays of (x, y, z).
        self.position = position
        """The current position of this particle in meters (m)."""
        self.velocity = velocity
        """The current velocity of this particle in meters per second (m/s)."""
        self.acceleration = acceleration
        """The current acceleration of this particle in meters per second squared (m/s^2)."""

        self.MASS = mass
        """The mass of this particle in kilograms (kg), which should never change."""
        self.CHARGE = charge
        """The charge of this particle in coulombs (C), which should never change."""

        self.ID = PointParticle.current_id
        """The unique ID identifying this particle, which should never change."""
        PointParticle.current_id += 1

    def apply_force(self, force: vectors.ForceVector = np.zeros(3)) -> None:
        """Set the acceleration of this particle based on the given force.

        Parameters
        ----------
        force : vectors.ForceVector, default=np.zeros(3)
            The force applied upon this particle in newtons (N).
        """
        self.acceleration = force / self.MASS

    def get_gravitational_field_exerted(
        self,
        point: vectors.PositionVector
    ) -> vectors.FieldVector:
        """Calculate the gravitational field created by this particle at a
        given point.

        Parameters
        ----------
        point : vectors.PositionVector
            The coordinates of the point that this particle is exerting a
            gravitational field upon, in meters (m).

        Returns
        -------
        vectors.FieldVector
            The gravitational field generated at `point` in newtons per kilogram (N/kg).
        """
        r = point - self.position
        distance = np.linalg.norm(r)

        # If the points are overlapping, there is no force.
        if distance == 0:
            return np.zeros(3, dtype=float)

        return -r * scipy.constants.G * self.MASS / distance ** 3

    def get_gravitational_force_experienced(
        self,
        gravitational_field: vectors.FieldVector
    ) -> vectors.ForceVector:
        """Calculate the gravitational force acting upon this particle
        by the given gravitational field.

        Parameters
        ----------
        gravitational_field : vectors.FieldVector
            The gravitational field acting upon this particle,
            in newtons per kilogram (N/kg).

        Returns
        -------
        vectors.ForceVector
            The force acting upon this particle as a result of the
            gravitational field, in newtons (N).
        """
        return self.MASS * gravitational_field

    def get_electric_field_exerted(
        self,
        point: vectors.PositionVector
    ) -> vectors.FieldVector:
        """Calculate the electric field at a given point due to this particle.

        Parameters
        ----------
        point : vectors.PositionVector
            The point to calculate electric field at
            in meters (m).

        Returns
        -------
        vectors.FieldVector
            The electric field that this particle creates at the given point
            in newtons per coulomb (N/C).
        """
        r = point - self.position
        distance = np.linalg.norm(r)

        # If the points are overlapping, there is no force.
        if distance == 0:
            return np.zeros(3, dtype=float)

        # The Coulomb constant
        k = 1 / (4 * np.pi * scipy.constants.epsilon_0)

        return -r * k * self.CHARGE / distance ** 3

    def get_electrostatic_force_experienced(
        self,
        electric_field: vectors.FieldVector
    ) -> vectors.ForceVector:
        """Calculate the force acting upon this particle by the
        given electric field.

        Parameters
        ----------
        electric_field : vectors.FieldVector
            The electric field acting upon this particle in newtons per coulomb (N/C).

        Returns
        -------
        vectors.ForceVector
            The force exerted upon this particle by the electric field in newtons (N).
        """
        return self.CHARGE * electric_field

    def get_magnetic_field_exerted(
        self,
        point: vectors.PositionVector
    ) -> vectors.FieldVector:
        """Calculate the magnetic field exerted by by this particle at a given point.

        Parameters
        ----------
        point : vectors.PositionVector
            The point at which to calculate the magnetic field,
            in meters (m).

        Returns
        -------
        vectors.FieldVector
            The magnetic field exerted by this particle at the given point,
            in teslas (T).

        Notes
        -----
        It uses the "Biot-Savart Law for point charges", technically a misnomer,
        which only approximates magnetic fields for particles with a velocity << c.
        """
        r = point - self.position
        distance = np.linalg.norm(r)

        # If the points are overlapping, there is no force.
        if distance == 0:
            return np.zeros(3, dtype=float)

        return (
            scipy.constants.mu_0 * self.CHARGE * np.cross(self.velocity, r)
            / (4 * np.pi * distance ** 3)
        )

    def get_magnetic_force_experienced(
        self,
        magnetic_field: vectors.FieldVector,
        velocity: vectors.FieldVector | None = None
    ) -> vectors.ForceVector:
        """Calculate the magnetic force acting upon this particle by the
        given electric field.

        Parameters
        ----------
        magnetic_field : vectors.FieldVector
            The magnetic field acting upon this particle in teslas (T).
        velocity : vectors.FieldVector` | `None
            The velocity to use for the magnetic force calculations,
            by default `self.velocity`.

        Returns
        -------
        vectors.ForceVector
            The force exerted upon this particle by the magnetic field in newtons (N).
        """
        return (
            self.CHARGE
            * np.cross(
                self.velocity if velocity is None else velocity,
                magnetic_field
            ).astype(float)
        )

    def get_force_experienced(
        self,
        gravitational_field: vectors.FieldVector = np.array((0, 0, 0)),
        electric_field: vectors.FieldVector = np.array((0, 0, 0)),
        magnetic_field: vectors.FieldVector = np.array((0, 0, 0)),
        velocity: vectors.FieldVector | None = None
    ) -> vectors.ForceVector:
        """Calculate the net force exerted on this particle as a result of
        gravitational, electric, and magnetic fields.

        Parameters
        ----------
        gravitational_field : vectors.FieldVector, default=`np.array((0, 0, 0))`
            The gravitational field acting upon this particle.
        electric_field : vectors.FieldVector, default=`np.array((0, 0, 0))`
            The electric field acting upon this particle.
        magnetic_field : vectors.FieldVector, default=`np.array((0, 0, 0))`
            The magnetic field acting upon this particle.
        velocity : vectors.FieldVector` | `None
            The velocity to use for the magnetic force calculations,
            by default `self.velocity`.

        Returns
        -------
        vectors.ForceVector
            The net force exerted upon this particle as a result
            of gravitational, electric, and magnetic fields.
        """
        return (
            self.get_gravitational_force_experienced(gravitational_field)
            + self.get_electrostatic_force_experienced(electric_field)
            + self.get_magnetic_force_experienced(magnetic_field, velocity)
        )

    def apply_fields(
        self,
        gravitational_field: vectors.FieldVector,
        electric_field: vectors.FieldVector,
        magnetic_field: vectors.FieldVector
    ) -> None:
        """Calculate and apply the forces from gravitational and electromagnetic
        fields on upon this particle.

        Parameters
        ----------
        gravitational_field : vectors.FieldVector
            The gravitational field acting upon this particle in N/kg.
        electric_field : vectors.FieldVector
            The electric field acting upon this particle in N/C.
        magnetic_field : vectors.FieldVector
            The magnetic field acting upon this particle in T.
        """
        self.apply_force(
            self.get_gravitational_force_experienced(gravitational_field)
            + self.get_electrostatic_force_experienced(electric_field)
            + self.get_magnetic_force_experienced(magnetic_field)
        )

    @typing.override
    def __eq__(self, value: object) -> bool:
        """Return whether an `object` is equal to this `PointParticle`.
        They are equal if and only if the `object` is also a `PointParticle` with the same `ID`.

        Parameters
        ----------
        value : object
            The `object` to compare against this `PointParticle` for equality.

        Returns
        -------
        bool
            Whether `value` is also a `PointParticle` with the same `ID`.
        """
        return isinstance(value, PointParticle) and self.ID == value.ID

    @typing.override
    def __str__(self) -> str:
        """Return a string containing information about this particle's current state.

        Returns
        -------
        str
            Return a string containing information about this particle's current state.
        """
        position_string = (
            f'({", ".join((str(dimension) for dimension in self.position))})'
        )
        velocity_string = (
            f'<{", ".join((str(dimension) for dimension in self.velocity))}>'
        )
        acceleration_string = (
            f'<{", ".join((str(dimension) for dimension in self.acceleration))}>'
        )

        return (
            f'Point Particle: r={position_string}, v={velocity_string}, '
            f'a={acceleration_string}, m={self.MASS}, q={self.CHARGE}'
        )

    @typing.override
    def __repr__(self) -> str:
        """Return a string containing all the arguments needed to instantiate
        another identical particle (aside from :const:`PointParticle.id`).

        Returns
        -------
        str
            A string containing all the arguments needed to instantiate
            another identical particle (aside from :const:`PointParticle.id`).
        """
        cls = self.__class__.__name__
        return (
            f'{cls}({self.position}, {self.velocity}, {self.acceleration}, '
            f'{self.MASS}, {self.CHARGE})'
        )
