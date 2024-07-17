from __future__ import annotations
import math

import numpy as np
import scipy.constants


class PointParticle:
    """Represent a point particle with a specified position, charge, and mass.
    """

    def __init__(self, position: np.array, charge: np.float64 = 0.0, mass: np.float64 = 1.0, fixed: bool = False) -> None:
        """Initialize a single point particle with a position, charge, and mass.

        Parameters
        ----------
        position : np.array
            The position that the particle is at.
            X is left/right, Y is forward/backward, Z is up/down.
            Specified in meters. 
        charge : np.float64, optional
            The charge of the particle in coulombs, by default 0.0
        mass : np.float64, optional
            The mass of the charged particle in kilograms, by default 1.0
        fixed : bool, optional
            Whether this particle's position is constant, by default False
        """
        # Represented by arrays of (X, Y, Z).
        self.position = position.astype(np.float64)
        self.velocity = np.array((0.0, 0.0, 0.0))
        self.acceleration = np.array((0.0, 0.0, 0.0))

        self.charge = charge
        self.mass = mass

        self.fixed = fixed

    def apply_force(self, force: np.float64) -> None:
        """Update the particle's acceleration by adding a force.

        Parameters
        ----------
        force : np.float64
            The force that is being applied to the particle
        """
        if not self.fixed:
            self.acceleration += force / self.mass

    def gravity(self, particle: PointParticle) -> np.array:
        """Calculate the gravitational field created by this particle at a position. 

        Parameters
        ----------
        position : np.array
            The position that the particle is exerting a gravitational field is exerting.
            A 3D vector of type np.float64. 

        Returns
        -------
        np.array
            A vector of the gravitational force exerted on this particle.
        """
        vector_between_points = particle.position - self.position
        distance = np.linalg.norm(vector_between_points)
        unit_vector = vector_between_points / distance

        force_magnitude = scipy.constants.G * self.mass * particle.mass / distance ** 2
        gravitational_force = force_magnitude * unit_vector

        return gravitational_force

    def electric_field(self, point: np.array) -> np.array:
        """Calculate the electric field at a point due to this particle.

        Parameters
        ----------
        point : np.array
            A 3D vector representing a coordinate.
        
        Returns
        -------
        np.array
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

    def magnetic_field(self, point: np.array) -> np.array:
        """Calculate the magnetic field exerted by by this particle at a point. 
        It uses the "Biot-Savart Law for point charges," technically a misnomer,
        which only approximates magnetic fields for particles with a velocity << c.

        Parameters
        ----------
        point : np.array
            The point at which to calculate the magnetic field

        Returns
        -------
        np.array
            The vector of the magnetic field exerted by this particle at the position.
        """
        # The vector between the positions of the particles
        r = point - self.position
        # The unit vector of `r`
        r_hat = r / np.linalg.norm(r)

        magnetic_field = (scipy.constants.mu_0 * self.charge * np.cross(self.velocity, r_hat)
                          / (4 * np.pi * np.linalg.norm(r) ** 2))

        return magnetic_field

    def __str__(self) -> str:
        coordinates = f'({" m, ".join([str(num) for num in self.position])} m)'
        return f'Particle with {self.charge} C and {self.mass} kg at {coordinates}'
