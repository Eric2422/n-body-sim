import numpy as np
import scipy

from particle import PointParticle
import vectors


class BarnesHutCell():
    def __init__(
        self,
        x_bounds: np.ndarray[np.float64],
        y_bounds: np.ndarray[np.float64],
        z_bounds: np.ndarray[np.float64],
        particles: list[PointParticle] = [],
    ):
        """Constructs a Barnes-Hut cell and recursively create its child nodes.

        Will catch out of bounds particles.

        Parameters
        ----------
        x_bounds : np.ndarray[np.float64]
            A 2-element NumPy array that contains the lower and upper X bounds, in that order
        y_bounds : np.ndarray[np.float64]
            A 2-element NumPy array that contains the lower and upper Y bounds, in that order
        z_bounds : np.ndarray[np.float64]
            A 2-element NumPy array that contains the lower and upper Z bounds, in that order
        particles : list[PointParticle], optional
            List of particles that are contained within this Barnes-Hut cell.
        """
        self.x_bounds = x_bounds
        self.y_bounds = y_bounds
        self.z_bounds = z_bounds

        # Remove out of bounds particles
        for particle in particles:
            if not self.contains_particle(particle):
                particles.remove(particle)

        self.total_mass = 0

        total_moment = np.zeros(3)

        # If this cell is an internal node(i.e. it has more than 1 particle)
        if len(particles) > 1:
            self.child_cells = self.create_child_cells(particles)

            for child_cell in self.child_cells:
                self.total_mass += child_cell.total_mass
                total_moment += child_cell.total_mass * child_cell.center_of_mass

        # If this is an external node(i.e. it has only 0 or 1 particles)
        else:
            self.child_cells = []

            for particle in particles:
                self.total_mass += particle.mass
                total_moment += particle.mass * particle.position

        # Divide the total moment by center of mass to obtain the center of mass
        # If mass is 0, return the centroid
        self.center_of_mass = total_moment / self.total_mass if self.total_mass != 0 else np.array((
            np.mean(x_bounds), np.mean(y_bounds), np.mean(z_bounds)))

    def contains_particle(self, particle: PointParticle) -> bool:
        return (particle.position[0] >= self.x_bounds[0] and particle.position[0] <= self.x_bounds[1]
                and particle.position[1] >= self.y_bounds[0] and particle.position[1] <= self.y_bounds[1]
                and particle.position[2] >= self.z_bounds[0] and particle.position[2] <= self.z_bounds[1])

    def create_child_cells(self, particles):
        centroid = np.array((
            np.mean(self.x_bounds),
            np.mean(self.y_bounds),
            np.mean(self.z_bounds)
        ))

        # Width of child cells
        child_width = self.x_bounds[1] - self.x_bounds[0] / 2

        # List of all the child BH cells
        child_cells = []

        # Stores the particles in each octant
        # Indexed by x(left-right), y(back-front), z(bottom-top)
        octant_particles_list = (
            (([], []),
             ([], [])),
            (([], []),
             ([], []))
        )

        # Loop through each particle and categorize them into an octant
        for particle in particles:
            # Right-front-top
            if particle.position[0] >= centroid[0] and particle.position[1] >= centroid[1] and particle.position[2] >= centroid[2]:
                octant_particles_list[1][1][1].append(particle)

            # Left-front-top
            elif particle.position[0] <= centroid[0] and particle.position[1] >= centroid[1] and particle.position[2] >= centroid[2]:
                octant_particles_list[0][1][1].append(particle)

            # Right-back-top
            elif particle.position[0] >= centroid[0] and particle.position[1] <= centroid[1] and particle.position[2] >= centroid[2]:
                octant_particles_list[1][0][1].append(particle)

            # Left-back-top
            elif particle.position[0] <= centroid[0] and particle.position[1] <= centroid[1] and particle.position[2] >= centroid[2]:
                octant_particles_list[0][0][1].append(particle)

            # Right-front-bottom
            elif particle.position[0] >= centroid[0] and particle.position[1] >= centroid[1] and particle.position[2] <= centroid[2]:
                octant_particles_list[1][1][0].append(particle)

            # Left-front-bottom
            elif particle.position[0] <= centroid[0] and particle.position[1] >= centroid[1] and particle.position[2] <= centroid[2]:
                octant_particles_list[0][1][0].append(particle)

            # Right-back-bottom
            elif particle.position[0] >= centroid[0] and particle.position[1] <= centroid[1] and particle.position[2] <= centroid[2]:
                octant_particles_list[1][0][0].append(particle)

            # Left-back-bottom
            elif particle.position[0] <= centroid[0] and particle.position[1] <= centroid[1] and particle.position[2] <= centroid[2]:
                octant_particles_list[0][0][0].append(particle)

        # Loop eight times to create the octants
        for i in range(2):
            for j in range(2):
                for k in range(2):
                    lower_x = self.x_bounds[0] + (i * child_width)
                    lower_y = self.y_bounds[0] + (j * child_width)
                    lower_z = self.z_bounds[0] + (k * child_width)

                    child_cells.append(
                        BarnesHutCell(
                            x_bounds=np.array(
                                (lower_x, lower_x + child_width)),
                            y_bounds=np.array(
                                (lower_y, lower_y + child_width)),
                            z_bounds=np.array(
                                (lower_z, lower_z + child_width)),
                            particles=octant_particles_list[i][j][k],
                        )
                    )

        return child_cells

    def get_gravitationl_field(self, point: vectors.PositionVector) -> vectors.FieldVector:
        """Calculate the approximate gravitational field exerted by this cell at a certain point.

        Parameters
        ----------
        point : vectors.PositionVector
            A 3D NumPy array representing a 3D position vector. Measured in meters(m).

        Returns
        -------
        vectors.FieldVector
            A 3D NumPy array representing a 3D field vector. Measured in newtons per kg (N / kg).
        """
        vector_between_points = point - self.center_of_mass
        distance = np.linalg.norm(vector_between_points)
        unit_vector = vector_between_points / distance

        return unit_vector * scipy.constants.G * self.total_mass / distance ** 2

    def get_electrical_field(self, point: vectors.PositionVector) -> vectors.FieldVector:
        pass

    def get_magnetic_field(self, point: vectors.PositionVector) -> vectors.FieldVector:
        pass

    def get_depth(self):
        if len(self.child_cells) == 0:
            return 2

        return max(child.get_depth() for child in self.child_cells)

    def __str__(self):
        string = f'''X: [{self.x_bounds[0]}, {self.x_bounds[1]}], Y: [{self.y_bounds[1]}, {self.y_bounds[1]}], Z: [{self.z_bounds[0]}, {self.z_bounds[1]}]
Center of Mass: {self.center_of_mass}
{len(self.child_cells)} child cell(s):'''

        for child_node in self.child_cells:
            string += f'\n\t{child_node.__str__().replace('\n', '\n\t')}\n'

        return string
