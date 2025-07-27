import numpy as np
import numpy.typing as npt
import scipy

from particle import PointParticle
import vectors


class BarnesHutCell():
    """Represents one node of a Barnes-Hut octree.
    """

    def __init__(
        self,
        x_bounds: npt.NDArray[np.float64] | None = None,
        y_bounds: npt.NDArray[np.float64] | None = None,
        z_bounds: npt.NDArray[np.float64] | None = None,
        particles: list[PointParticle] = [],
    ):
        """Constructs a Barnes-Hut cell and recursively create its child nodes.

        Will catch out of bounds particles.
        If `x_bounds`, `y_bounds`, or `z_bounds` are left `None`, ]
        they will be automatically inferred based on the positions of the particles in the list.

        Parameters
        ----------
        x_bounds : npt.NDArray[np.float64], optional
            A 2-element NumPy array that contains the lower and upper X bounds in that order, by default None
        y_bounds : npt.NDArray[np.float64], optional
            A 2-element NumPy array that contains the lower and upper X bounds in that order, by default None
        z_bounds : npt.NDArray[np.float64], optional
            A 2-element NumPy array that contains the lower and upper X bounds in that order, by default None
        particles : list[PointParticle], optional
            List of particles that are contained within this Barnes-Hut cell.
        """
        self.x_bounds = np.array((
            min(particles,
                key=lambda ele: ele.position[0]).position[0],
            max(particles,
                key=lambda ele: ele.position[0]).position[0]
        )) if x_bounds is None else x_bounds

        self.y_bounds = np.array((
            min(particles,
                key=lambda ele: ele.position[1]).position[1],
            max(particles,
                key=lambda ele: ele.position[1]).position[1]
        )) if y_bounds is None else y_bounds

        self.z_bounds = np.array((
            min(particles,
                key=lambda ele: ele.position[2]).position[2],
            max(particles,
                key=lambda ele: ele.position[2]).position[2]
        )) if z_bounds is None else z_bounds

        self.width: np.float64 = self.x_bounds[1] - self.x_bounds[0]

        # Remove out of bounds particles
        for particle in particles:
            print('Oh NoEs, A pArTiClE wAs oUt Of BoUnDs!')
            if not self.within_cell_bounds(particle):
                particles.remove(particle)

        self.particles = particles

        self.total_mass: np.float64 = np.float64(0.0)
        mass_moment = np.zeros(3)

        self.total_charge = 0
        charge_moment = np.zeros(3)

        # Completely made-up name.
        # q * v = q * d / t = q / t * d = I * d
        # Thus, moment of current
        current_moment = np.zeros(3)

        # If this cell is an internal node(i.e. it has more than 1 particle)
        if len(particles) > 1:
            self.child_cells = self.create_child_cells()

            for child_cell in self.child_cells:
                self.total_mass += child_cell.total_mass
                mass_moment += child_cell.total_mass * child_cell.center_of_mass

                self.total_charge += child_cell.total_charge
                charge_moment += child_cell.total_charge * child_cell.center_of_mass
                current_moment += child_cell.total_charge * child_cell.center_of_charge_velocity

        # If this is an external node(i.e. it has only 0 or 1 particles)
        else:
            self.child_cells = []

            for particle in particles:
                self.total_mass += particle.mass
                mass_moment += particle.mass * particle.position

                self.total_charge
                charge_moment += particle.charge * particle.position
                current_moment += particle.charge * particle.velocity

        centroid = np.array((
            np.mean(self.x_bounds), np.mean(self.y_bounds), np.mean(self.z_bounds)))

        # Divide the mass moment by center of mass to obtain the center of mass
        # If mass is 0, return the centroid
        self.center_of_mass = mass_moment / \
            self.total_mass if self.total_mass != 0 else centroid

        # Divide the charge moment by center of charge to obtain the center of charge
        # If charge is 0, return the centroid
        self.center_of_charge = charge_moment / \
            self.total_charge if self.total_charge != 0 else centroid

        self.center_of_charge_velocity = current_moment / \
            self.total_charge if self.total_charge != 0 else centroid

    def within_cell_bounds(self, particle: PointParticle) -> bool:
        """Returns whether a given particle is within the bounds of this Barnes-Hut cell.

        Parameters
        ----------
        particle : PointParticle
            The particle to check.

        Returns
        -------
        bool
            True if the particle is within the bounds of this cell, False otherwise.
        """
        return (particle.position[0] >= self.x_bounds[0] and particle.position[0] <= self.x_bounds[1]
                and particle.position[1] >= self.y_bounds[0] and particle.position[1] <= self.y_bounds[1]
                and particle.position[2] >= self.z_bounds[0] and particle.position[2] <= self.z_bounds[1])

    def create_child_cells(self) -> list['BarnesHutCell']:
        """Recursively creates child cells for this Barnes-Hut cell.

        Returns
        -------
        list['BarnesHutCell']   
            A list of child Barnes-Hut cells, each representing an octant of this cell.
        """
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
        for particle in self.particles:
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

    def get_gravitational_field_exerted(self, point: vectors.PositionVector, theta: np.float64 = np.float64(0.0)) -> vectors.FieldVector:
        """Calculate the approximate gravitational field exerted by this cell at a certain point.

        Parameters
        ----------
        point : vectors.PositionVector
            A 3D NumPy array representing a 3D position vector. Measured in meters(m).
        theta : np.float64, optional
            The value of theta, the Barnes-Hut approximation parameter being used.
            Given the distance between the point and the center of mass, 
            it used to determine whether to return an approximate or exact value for the gravitational field.
            When theta is 0.0, no approximation will occur.
            By default, 0.0

        Returns
        -------
        vectors.FieldVector
            A 3D NumPy array representing a 3D gravitational field vector. Measured in newtons per kg(N/kg).
        """
        r = point - self.center_of_mass
        distance = np.linalg.norm(r)
        r_hat = r / distance if distance != 0 else np.zeros(3)

        force = np.zeros(3)
        if self.width < theta * distance:
            return r_hat * scipy.constants.G * self.total_mass / distance ** 2

        # If this cell has child cells,
        elif len(self.child_cells) > 0:
            for child_cell in self.child_cells:
                force += child_cell.get_gravitational_field_exerted(
                    point=point)

        else:
            for particle in self.particles:
                force += particle.get_gravitational_field_exerted(point=point)

        return force

    def get_electric_field_exerted(self, point: vectors.PositionVector, theta: np.float64 = np.float64(0.0)) -> vectors.FieldVector:
        """Calculate the approximate electric field exerted by this cell at a certain point.

        Parameters
        ----------
        point : vectors.PositionVector
            A 3D NumPy array representing a 3D position vector. Measured in meters(m).
        theta : np.float64, optional
            The value of theta, the Barnes-Hut approximation parameter being used.
            Given the distance between the point and the center of charge, 
            it used to determine whether to return an approximate or exact value for the gravitational field.
            When theta is 0.0, no approximation will occur.
            By default, 0.0

        Returns
        -------
        vectors.FieldVector
            A 3D NumPy array representing a 3D electric field vector. Measured in newtons per coulomb(N/C).
        """
        r = point - self.center_of_charge
        distance = np.linalg.norm(r)
        r_hat = r / distance if distance != 0 else np.zeros(3)

        # The Coulomb constant
        k = 1 / (4 * scipy.constants.pi * scipy.constants.epsilon_0)

        force = np.zeros(3)
        if self.width < theta * distance:
            # The electrostatic force between the particles
            electric_field = (k * self.total_charge) / (distance ** 2)

            return -electric_field * r_hat

        # If this cell has child cells,
        elif len(self.child_cells) > 0:
            for child_cell in self.child_cells:
                force += child_cell.get_electric_field_exerted(point=point)

        else:
            for particle in self.particles:
                force += particle.get_electric_field_exerted(point=point)

        return force

    def get_magnetic_field_exerted(self, point: vectors.PositionVector, theta: np.float64 = np.float64(0.0)) -> vectors.FieldVector:
        """Calculate the approximate magnetic field exerted by this cell at a certain point.

        Parameters
        ----------
        point : vectors.PositionVector
            A 3D NumPy array representing a 3D position vector. Measured in meters(m).
        theta : np.float64, optional
            The value of theta, the Barnes-Hut approximation parameter being used.
            Given the distance between the point and the center of charge, 
            it used to determine whether to return an approximate or exact value for the magnetic field.
            When theta is 0.0, no approximation will occur.
            By default, 0.0

        Returns
        -------
        vectors.FieldVector
            A 3D NumPy array representing a 3D magnetic field vector. Measured in teslas(T). 
        """
        # The vector between the positions of the particles
        r = point - self.center_of_charge
        # The distance between the particle and center of charge
        distance = np.linalg.norm(r)
        # The unit vector of `r`
        r_hat = r / distance

        force = np.zeros(3)
        if self.width < theta * distance:
            return (scipy.constants.mu_0 * self.total_charge * np.cross(self.center_of_charge_velocity, r_hat)
                    / (4 * np.pi * np.linalg.norm(r) ** 2))

        # If this cell has child cells,
        elif len(self.child_cells) > 0:
            for child_cell in self.child_cells:
                force += child_cell.get_magnetic_field_exerted(point=point)

        else:
            for particle in self.particles:
                force += particle.get_magnetic_field_exerted(point=point)

        return force

    def get_depth(self) -> int:
        """Get the depth of the branch/tree under this Barnes-Hut cell.

        Returns
        -------
        int 
            The depth of the branch/tree under this Barnes-Hut cell.
        If this cell has no child cells, it is a leaf node and the depth is 1.
        """
        if len(self.child_cells) == 0:
            return 1

        return max(child.get_depth() for child in self.child_cells)

    def __str__(self):
        string = f'''X: [{self.x_bounds[0]}, {self.x_bounds[1]}], Y: [{self.y_bounds[1]}, {self.y_bounds[1]}], Z: [{self.z_bounds[0]}, {self.z_bounds[1]}]
Total mass: {self.total_mass}
Total charge: {self.total_charge}
Center of Mass: {self.center_of_mass}
{len(self.child_cells)} child cell(s):'''

        for child_node in self.child_cells:
            string += f'\n\t{child_node.__str__().replace('\n', '\n\t')}\n'

        return string
