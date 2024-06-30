from __future__ import annotations
import math

import numpy as np
import scipy.constants


class Particle:
    """Represent a single charged particle with a specified position, charge, and mass
    """

    def __init__(self, position: np.array, charge: float = 0.0, mass: float = 1.0, fixed: bool = False) -> None:
        """Initialize a single particle with a position, charge, and mass.

        Parameters
        ----------
        position : np.array
            The position that the particle is at.
            X is left/right, Y is forward/backward, Z is up/down.
            Specified in meters. 
        charge : float, optional
            The charge of the particle in coulombs, by default 0.0
        mass : float, optional
            The mass of the charged particle in kilograms, by default 1.0
        fixed : bool, optional
            Whether this particle can move, by default False
        """
        # Represented by arrays of (X, Y, Z).
        self.position = position
        self.velocity = np.array((0.0, 0.0, 0.0))
        self.acceleration = np.array((0.0, 0.0, 0.0))

        self.charge = charge
        self.mass = mass

        self.fixed = fixed

    def apply_force(self, force: float):
        """
        Update the particle's acceleration by adding a force.

        Parameters
        ----------
        force : float
            The force that is being applied to the particle
        """
        if not self.fixed:
            self.acceleration += force / self.mass

    def coulombs_law(self, particle: Particle) -> np.array:
        """Calculate the force exerted on this particle by another particle.

        Parameters
        ----------
        particle : Particle
            The other charged particle that is interacting with this one.

        Returns
        -------
        np.array
            The force vector exerted on this charge by another one.
        """
        vector_between_particles = particle.position - self.position
        distance = np.linalg.norm(vector_between_particles)
        unit_vector = vector_between_particles / distance

        # The Coulomb constant
        k = 1 / (4 * scipy.constants.pi * scipy.constants.epsilon_0)

        # The electric force between the particles
        electric_force = (k * self.charge * particle.charge) / (distance ** 2)

        return -electric_force * unit_vector

    def biot_savart_law(self, particle: Particle) -> np.array:
        """Calculate the magnetic force exerted on this particle by another particle. 
        It uses the "Biot-Savart Law for point charges," technically a misnomer,
        which only approximates magnetic fields for particles with a velocity << c.

        Parameters
        ----------
        particle : Particle
            Another particle which is exerting a magnetic field on this particle

        Returns
        -------
        np.array
            A vector the magnetic force that this particle experiences due to `particle`
        """
        # The vector between the positions of the particles
        r = particle.position - self.position
        # The unit vector of `r`
        r_hat = r / np.linalg.norm(r)

        magnetic_field = (scipy.constants.mu_0 * particle.charge * np.cross(particle.velocity, r_hat)
                          / (4 * np.pi * r ** 2))
        magnetic_force = self.charge * np.cross(self.velocity, magnetic_field)

        return magnetic_force

    def gravity(self, particle: Particle) -> np.array:
        distance = particle.position - self.position
        unit_vector = distance / np.linalg.norm(distance)

        force = scipy.constants.G * self.mass * particle.mass / distance ** 2

        return force * unit_vector

    def __str__(self) -> str:
        coordinates = f'({", ".join([str(num) for num in self.position])})'
        return f'Particle with {self.charge} C and {self.mass} kg at {coordinates}'
