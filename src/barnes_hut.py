import numpy as np

from particle import PointParticle
import vectors


class BarnesHutCell():
    def __init__(
            self,
            x_bounds: np.ndarray[np.float64],
            y_bounds: np.ndarray[np.float64],
            z_bounds: np.ndarray[np.float64],
            parent_particles: list[PointParticle] = []
    ):
        self.x_bounds = x_bounds
        self.y_bounds = y_bounds
        self.z_bounds = z_bounds

        # Search through parent cell for all particles that are within this child cell
        self.particles = [
            particle for particle in parent_particles
            if particle.position[0] >= x_bounds[0] and particle.position[0] <= x_bounds[1]
                and particle.position[1] >= y_bounds[0] and particle.position[1] <= y_bounds[1]
                and particle.position[2] >= z_bounds[0] and particle.position[2] <= z_bounds[1]
        ]

        self.child_cells = self.create_child_cells()

    def create_child_cells(self):
        width = self.x_bounds[1] - self.x_bounds[0]

        child_cells = []

        if len(self.particles) <= 1:
            return child_cells

        for x in range(2):
            for y in range(2):
                for z in range(2):
                    child_cells.append(
                        BarnesHutCell(
                            np.array((self.x_bounds[0] + (x * width), self.x_bounds[0] + (2 * x * width))),
                            np.array((self.y_bounds[0] + (y * width), self.y_bounds[0] + (2 * y * width))),
                            np.array((self.z_bounds[0] + (z * width), self.z_bounds[0] + (2 * z * width)))
                        )
                    )
        
        return child_cells

    def get_total_mass(self):
        if len(self.child_cells > 1):
            pass

    def get_center_of_mass(self) -> vectors.PositionVector:
        """Return the center of mass of this Barnes-Hut cell.

        Returns
        -------
        vectors.PositionVector
            A 3D NumPy array that represents a location.
        """
        moments = np.zeros(shape=(3))
        total_mass = 0
        
        # If there are child cells, loop through them.
        if len(self.child_cells) > 0:
            for child_cell in self.child_cells:
                print(child_cell)
                child_cell_mass = child_cell.get_total_mass()
                print(child_cell_mass)
                moments += (child_cell_mass * child_cell.get_center_of_mass())
                total_mass += child_cell_mass

        # If there are no child cells, loop through the particles of this cell.
        else:
            for particle in self.particles:
                moments += (particle.mass * particle.position)
                total_mass += particle.mass

        return moments / total_mass

    def __str__(self):
        return f'''X: [{self.x_bounds[0]}, {self.x_bounds[1]}], Y: [{self.y_bounds[0]}, {self.y_bounds[1]}], Z: [{self.z_bounds[0]}, {self.z_bounds[1]}]
Center of Mass: {self.get_center_of_mass()}
{len(self.child_cells)} child cell(s), {len(self.particles)} particle(s)'''