import numpy as np

from particle import PointParticle
import vectors


class BarnesHutCell():
    def __init__(
            self,
            x_bounds: np.ndarray[np.float64],
            y_bounds: np.ndarray[np.float64],
            z_bounds: np.ndarray[np.float64],
            parent_particles: list = [PointParticle]
    ):
        self.x_bounds = x_bounds
        self.y_bounds = y_bounds
        self.z_bounds = z_bounds

        # Search through parent cell for all particles that are within this child cell
        self.particles = [
            particle for particle in parent_particles
            if particle.position[0] > x_bounds[0] and particle.position[0] < x_bounds[1]
                and particle.position[1] > y_bounds[0] and particle.position[1] < y_bounds[1]
                and particle.position[2] > z_bounds[0] and particle.position[2] < z_bounds[1]
        ]

        if len(self.particles <= 1): 
            self.child_cells = []
        
        else:
            self.child_cells = [
                
            ]

    def create_child_cells(self):
        pass

    def getCenterofMass(self) -> vectors.PositionVector:
        moments = np.zeros(shape=(3))
        total_mass = 0

        for particle in self.children_particles:
            moments += (particle.mass * particle.position)
            total_mass += particle.mass

        return moments / total_mass
