import numpy as np

from particle import PointParticle
import vectors


class BarnesHutCell():
    def __init__(
            self,
            x_bounds: np.ndarray[np.float64],
            y_bounds: np.ndarray[np.float64],
            z_bounds: np.ndarray[np.float64],
            particles: list[PointParticle] = []
    ):
        self.x_bounds = x_bounds
        self.y_bounds = y_bounds
        self.z_bounds = z_bounds
        
        self.mass = 0
        self.center_of_mass = np.empty(3)

        # If there is more than one particle
        if len(particles) > 1:
            pass
    
        # If this is an external node(i.e. it has only 0 or 1 particles)
        else:
            for particle in particles:
                pass

        self.child_cells = self.create_child_cells()

    def create_child_cells(self):
        width = self.x_bounds[1] - self.x_bounds[0]

        child_cells = []

        if len(self.particles) <= 1:
            return child_cells

        for x in range(2):
            for y in range(2):
                for z in range(2):
                    lower_x = self.x_bounds[0] + (x * width)
                    lower_y = self.y_bounds[0] + (y * width)
                    lower_z = self.z_bounds[0] + (z * width)

                    child_cells.append(
                        BarnesHutCell(
                            np.array((lower_x, lower_x + width)),
                            np.array((lower_y, lower_y + width)),
                            np.array((lower_z, lower_z + width))
                        )
                    )

        return child_cells

    def get_total_mass(self):
        total_mass = 0

        # If there are child cells, loop through them to sum the moments and masses.
        if len(self.child_cells) > 0:
            for child_cell in self.child_cells:
                total_mass += child_cell.get_total_mass()

        # If there are no child cells, loop through the particles of this cell.
        else:
            for particle in self.particles:
                total_mass += particle.mass

        return total_mass

    def get_center_of_mass(self) -> vectors.PositionVector:
        """Return the center of mass of this Barnes-Hut cell.

        Returns
        -------
        vectors.PositionVector
            A 3D NumPy array that represents a location.
        """
        moments = np.zeros(shape=(3))
        total_mass = 0

        # If there are child cells, loop through them to sum the moments and masses.
        if len(self.child_cells) > 0:
            for child_cell in self.child_cells:
                child_cell_mass = child_cell.get_total_mass()
                moments += (child_cell_mass * child_cell.get_center_of_mass())
                total_mass += child_cell_mass

        # If there are no child cells, loop through the particles of this cell.
        else:
            for particle in self.particles:
                moments += (particle.mass * particle.position)
                total_mass += particle.mass

        # If mass is not zero, return the center of mass.
        # Else return the centroid
        return moments / total_mass if total_mass != 0 else np.array(((np.mean(self.x_bounds), np.mean(self.y_bounds), np.mean(self.z_bounds))))

    def get_gravitationl_field(self, position: vectors.PositionVector) -> vectors.FieldVector:
        pass

    def __str__(self):
        return f'''X: [{self.x_bounds[0]}, {self.x_bounds[1]}], Y: [{self.y_bounds[0]}, {self.y_bounds[1]}], Z: [{self.z_bounds[0]}, {self.z_bounds[1]}]
Center of Mass: {self.get_center_of_mass()}
{len(self.child_cells)} child cell(s), {len(self.particles)} particle(s)'''
