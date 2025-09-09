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
        If `x_bounds`, `y_bounds`, or `z_bounds` are left `None`,
        they will be automatically inferred based on the positions of the particles in the list.

        Parameters
        ----------
        x_bounds : npt.NDArray[np.float64], optional
            A 2-element NumPy array that contains the lower and upper x bounds in that order, by default None
        y_bounds : npt.NDArray[np.float64], optional
            A 2-element NumPy array that contains the lower and upper y bounds in that order, by default None
        z_bounds : npt.NDArray[np.float64], optional
            A 2-element NumPy array that contains the lower and upper z bounds in that order, by default None
        particles : list[PointParticle], optional
            List of particles that are contained within this Barnes-Hut cell, by default []
        """
        # If `x_bounds` is not given, set it based on the minimum and maximum x positions of the particles.
        # Else, set it to the given x bounds.
        self.x_bounds = np.array((
            min(particles,
                key=lambda ele: ele.position[0]).position[0],
            max(particles,
                key=lambda ele: ele.position[0]).position[0]
        )) if x_bounds is None else x_bounds

        # If `y_bounds` is not given, set it based on the minimum and maximum y positions of the particles.
        # Else, set it to the given y bounds.
        self.y_bounds = np.array((
            min(particles,
                key=lambda ele: ele.position[1]).position[1],
            max(particles,
                key=lambda ele: ele.position[1]).position[1]
        )) if y_bounds is None else y_bounds

        # If `y_bounds` is not given, set it based on the minimum and maximum y positions of the particles.
        # Else, set it to the given z bounds.
        self.z_bounds = np.array((
            min(particles,
                key=lambda ele: ele.position[2]).position[2],
            max(particles,
                key=lambda ele: ele.position[2]).position[2]
        )) if z_bounds is None else z_bounds

        self.centroid: npt.NDArray[np.float64]
        """The centroid of the Barnes Hut cell"""

        self.size: float
        """The distance from one side of the cell to the other."""

        # Make the bounds cubical if they are not.
        bounds, self.centroid, self.size = BarnesHutCell.cube_bounds(
            self.x_bounds,
            self.y_bounds,
            self.z_bounds
        )

        self.x_bounds, self.y_bounds, self.z_bounds = bounds

        self.particles = [particle for particle in particles if self.within_cell_bounds(particle)]
        """A list of all particle included in this cell."""

        self.total_mass = sum([particle.mass for particle in self.particles])
        """Total mass of all particles in this cell, measured in kilograms(kg)."""
        mass_moment = sum(
            [particle.mass * particle.position for particle in self.particles])

        # Divide the mass moment by center of mass to obtain the center of mass
        # If mass is 0, return the centroid
        self.center_of_mass = mass_moment / self.total_mass if self.total_mass != 0 \
            else self.centroid

        self.total_charge = sum(
            [particle.charge for particle in self.particles]
        )
        """Total charge of all particles in this cell, measured in coulombs(C)."""
        charge_moment = sum(
            [particle.charge * particle.position for particle in self.particles]
        )

        # Divide the charge moment by center of charge to obtain the center of charge
        # If charge is 0, return the centroid
        self.center_of_charge = charge_moment / self.total_charge if self.total_charge != 0 \
            else np.zeros(3, dtype=float)

        # Completely made-up name.
        # q * v = q * d / t = q / t * d = I * d
        # Thus, moment of current
        current_moment = sum(
            [particle.charge * particle.velocity for particle in self.particles]
        )

        self.center_of_charge_velocity = current_moment / self.total_charge if self.total_charge != 0 \
            else self.centroid

        # Create child cells if this cell is an internal node(i.e. it has more than 1 particle)
        # Create no children if this is an external node(i.e. it has only 0 or 1 particles)
        self.child_cells = self.create_child_cells() if len(self.particles) > 1 else []

    @classmethod
    def cube_bounds(
        cls,
        x_bounds: npt.NDArray[np.float64],
        y_bounds: npt.NDArray[np.float64],
        z_bounds: npt.NDArray[np.float64]
    ) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64], float]:
        """Makes the given bounds cube(i.e. all with the same length), preserving the centroid.

        Parameters
        ----------
        x_bounds : npt.NDArray[np.float64]
            The given x bounds to cube.
        y_bounds : npt.NDArray[np.float64]
            The given y bounds to cube.
        z_bounds : npt.NDArray[np.float64]
            The given z bounds to cube.

        Returns
        -------
        tuple[npt.NDArray[np.float64], npt.NDArray[np.float64], float]
            The newly cubed bounds as a 3D array, the centroid, and the size of any dimension.
        """
        centroid = np.array(
            (
                np.mean(x_bounds),
                np.mean(y_bounds),
                np.mean(z_bounds)
            ),
            dtype=float
        )

        width = x_bounds[1] - x_bounds[0]
        length = y_bounds[1] - y_bounds[0]
        height = z_bounds[1] - z_bounds[0]
        size = max(width, length, height)

        if width == length and length == height:
            return np.array((x_bounds, y_bounds, z_bounds)), centroid, size

        half_size = size / 2
        new_bounds = np.array(
            [(centroid[i] - half_size, centroid[i] + half_size)
             for i in range(3)],
            dtype=float
        )

        return new_bounds, centroid, size

    def create_child_cells(self) -> list['BarnesHutCell']:
        """Recursively creates child cells for this Barnes-Hut cell.

        Returns
        -------
        list['BarnesHutCell']   
            A list of child Barnes-Hut cells, each representing an octant of this cell.
        """
        # Size of child cells
        child_size = self.size / 2

        # List of all the child BH cells
        child_cells = []

        # Loop eight times to create the octants
        for lower_x in np.linspace(self.x_bounds[0], self.x_bounds[1], num=2, endpoint=False):
            for lower_y in np.linspace(self.y_bounds[0], self.y_bounds[1], num=2, endpoint=False):
                for lower_z in np.linspace(self.z_bounds[0], self.z_bounds[1], num=2, endpoint=False):
                    child = BarnesHutCell(
                        x_bounds=np.array(
                            (lower_x, lower_x + child_size)),
                        y_bounds=np.array(
                            (lower_y, lower_y + child_size)),
                        z_bounds=np.array(
                            (lower_z, lower_z + child_size)),
                        particles=self.particles.copy(),
                    )
                    child_cells.append(child)

        return child_cells

    def within_cell_bounds(self, particle: PointParticle) -> bool:
        """Returns whether a given particle is within the bounds of this Barnes-Hut cell.

        Parameters
        ----------
        particle : PointParticle
            The particle to check.

        Returns
        -------
        bool
            `True` if the particle is within the bounds of this cell, `False` otherwise.
        """
        return (
            particle.position[0] >= self.x_bounds[0] and particle.position[0] <= self.x_bounds[1]
            and particle.position[1] >= self.y_bounds[0] and particle.position[1] <= self.y_bounds[1]
            and particle.position[2] >= self.z_bounds[0] and particle.position[2] <= self.z_bounds[1]
        )

    def get_gravitational_field_exerted(self, point: vectors.PositionVector, theta: float = 0.0) -> vectors.FieldVector:
        """Calculate the approximate gravitational field exerted by this cell at a certain point.

        Parameters
        ----------
        point : vectors.PositionVector
            A 3D NumPy array representing a 3D position vector. Measured in meters(m).
        theta : float, optional
            The value of theta, the Barnes-Hut approximation parameter being used, by default 0.0
            Given the distance between the point and the center of mass, 
            it used to determine whether to return an approximate or exact value for the gravitational field.
            When theta is 0.0, no approximation will occur.

        Returns
        -------
        vectors.FieldVector
            A 3D NumPy array representing a 3D gravitational field vector. Measured in newtons per kg(N/kg).
        """
        r = point - self.center_of_mass
        distance = np.linalg.norm(r)
        r_hat = r / distance if distance != 0 else np.zeros(3)

        force = np.zeros(3)
        if self.size < theta * distance:
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

    def get_electric_field_exerted(self, point: vectors.PositionVector, theta: float = 0.0) -> vectors.FieldVector:
        """Calculate the approximate electric field exerted by this cell at a certain point.

        Parameters
        ----------
        point : vectors.PositionVector
            A 3D NumPy array representing a 3D position vector. Measured in meters(m).
        theta : float, optional
            The value of theta, the Barnes-Hut approximation parameter being used, by default 0.0
            Given the distance between the point and the center of charge, 
            it used to determine whether to return an approximate or exact value for the gravitational field.
            When theta is 0.0, no approximation will occur.

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
        if self.size < theta * distance:
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

    def get_magnetic_field_exerted(self, point: vectors.PositionVector, theta: float = 0.0) -> vectors.FieldVector:
        """Calculate the approximate magnetic field exerted by this cell at a certain point.

        Parameters
        ----------
        point : vectors.PositionVector
            A 3D NumPy array representing a 3D position vector. Measured in meters(m).
        theta : float, optional
            The value of theta, the Barnes-Hut approximation parameter being used, by default 0.0
            Given the distance between the point and the center of charge, 
            it used to determine whether to return an approximate or exact value for the magnetic field.
            When theta is 0.0, no approximation will occur.

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
        if self.size < theta * distance:
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
        string = f'''x: {self.x_bounds}, y: {self.y_bounds}, z: {self.z_bounds}
Centroid: {self.centroid}
Total mass: {self.total_mass}
Center of mass: {self.center_of_mass}
Total charge: {self.total_charge}
Center of charge: {self.center_of_charge}
Velocity of center of charge: {self.center_of_charge_velocity}
Number of particles: {len(self.particles)}
Particles: {self.particles}
{len(self.child_cells)} child cell(s):'''

        for child_node in self.child_cells:
            string += f'\n\t{child_node.__str__().replace('\n', '\n\t')}\n'

        return string
