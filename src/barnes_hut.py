import typing

import numpy as np
import numpy.typing as npt
import scipy

from particle import PointParticle
import vectors


class BarnesHutNode():
    """Represents one node of a Barnes-Hut octree.
    """

    @classmethod
    def cube_bounds(
        cls,
        x_bounds: npt.NDArray[np.float64],
        y_bounds: npt.NDArray[np.float64],
        z_bounds: npt.NDArray[np.float64]
    ) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64], float]:
        """Make the given bounds cube (i.e., all with the same length),
        preserving the centroid.

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
            The newly cubed bounds, the centroid, and the size of any dimension.
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

        # Size of the largest dimension.
        size = max(width, length, height)

        # If the bounds are already cube, just stop here and return it as it is.
        if width == length and length == height:
            return np.array((x_bounds, y_bounds, z_bounds)), centroid, size

        # Reset the other two dimensions to match the size of the largest dimension.
        half_size = size / 2
        new_bounds = np.array(
            [(centroid[i] - half_size, centroid[i] + half_size)
             for i in range(3)],
            dtype=float
        )

        return new_bounds, centroid, size

    @typing.override
    def __init__(
        self,
        particles: list[PointParticle] = [],
        x_bounds: npt.NDArray[np.float64] | None = None,
        y_bounds: npt.NDArray[np.float64] | None = None,
        z_bounds: npt.NDArray[np.float64] | None = None
    ):
        """Construct a Barnes-Hut node and recursively create its child nodes.

        Will catch out of bounds particles.
        If `x_bounds`, `y_bounds`, or `z_bounds` are `None`,
        they will be automatically inferred based on the positions of the particles in the list.

        Parameters
        ----------
        particles : list[PointParticle], default=[]
            List of particles that are contained within this Barnes-Hut node.
        x_bounds : npt.NDArray[np.float64], optional
            A 2-element NumPy array that contains the lower and upper x bounds in that order.
            If the argument is `None`, the bounds will be automatically calculated
            to be the smallest possible that would contain all the particles.
        y_bounds : npt.NDArray[np.float64], optional
            A 2-element NumPy array that contains the lower and upper y bounds in that order.
            If the argument is `None`, the bounds will be automatically calculated
            to be the smallest possible that would contain all the particles.
        z_bounds : npt.NDArray[np.float64], optional
            A 2-element NumPy array that contains the lower and upper z bounds in that order.
            If the argument is `None`, the bounds will be automatically calculated
            to be the smallest possible that would contain all the particles.
        """
        # If `x_bounds` is not given,
        # set it based on the minimum and maximum x positions of the particles.
        # Else, set it to the given x bounds.
        self.X_BOUNDS = (
            np.array((
                min(particles, key=lambda ele: ele.position[0]).position[0],
                max(particles, key=lambda ele: ele.position[0]).position[0]
            )) if x_bounds is None
            else x_bounds
        )
        """A two-element array containing the lower and upper x-bounds of this node."""

        # If `y_bounds` is not given,
        # set it based on the minimum and maximum y positions of the particles.
        # Else, set it to the given y bounds.
        self.Y_BOUNDS = (
            np.array((
                min(particles, key=lambda ele: ele.position[1]).position[1],
                max(particles, key=lambda ele: ele.position[1]).position[1]
            )) if y_bounds is None
            else y_bounds
        )
        """A two-element array containing the lower and upper y-bounds of this node."""

        # If `y_bounds` is not given,
        # set it based on the minimum and maximum y positions of the particles.
        # Else, set it to the given z bounds.
        self.Z_BOUNDS = (
            np.array((
                min(particles, key=lambda ele: ele.position[2]).position[2],
                max(particles, key=lambda ele: ele.position[2]).position[2]
            )) if z_bounds is None
            else z_bounds
        )
        """A two-element array containing the lower and upper z-bounds of this node."""

        # The centroid of the Barnes Hut node
        centroid: npt.NDArray[np.float64]

        self.SIZE: float
        """The distance from one side of the node to the other."""

        # Make the bounds cubical if they are not.
        bounds, centroid, self.SIZE = BarnesHutNode.cube_bounds(
            self.X_BOUNDS,
            self.Y_BOUNDS,
            self.Z_BOUNDS
        )

        self.X_BOUNDS, self.Y_BOUNDS, self.Z_BOUNDS = bounds

        self.PARTICLES = [
            particle for particle in particles if self.particle_within_bounds(particle)]
        """A list of all particle included in this node."""

        self.TOTAL_MASS = sum(particle.MASS for particle in self.PARTICLES)
        """Total mass of all particles in this node, measured in kilograms (kg)."""
        mass_moment = sum(
            particle.MASS * particle.position for particle in self.PARTICLES)

        # Divide the mass moment by center of mass to obtain the center of mass.
        # If mass is 0, return the centroid.
        self.CENTER_OF_MASS = (
            mass_moment / self.TOTAL_MASS if self.TOTAL_MASS != 0
            else centroid
        )
        """The center of mass of this cell."""

        self.TOTAL_CHARGE = sum(
            particle.CHARGE for particle in self.PARTICLES
        )
        """Total charge of all particles in this node, measured in coulombs (C)."""
        charge_moment = sum(
            particle.CHARGE * particle.position for particle in self.PARTICLES
        )

        # Divide the charge moment by center of charge to obtain the center of charge.
        # If charge is 0, return the centroid.
        self.CENTER_OF_CHARGE = (
            charge_moment / self.TOTAL_CHARGE if self.TOTAL_CHARGE != 0
            else np.zeros(3, dtype=float)
        )

        # Completely made-up name.
        # q * v = q * d / t = q / t * d = I * d
        # Thus, moment of current.
        current_moment = sum(
            particle.CHARGE * particle.velocity for particle in self.PARTICLES
        )

        self.CENTER_OF_CHARGE_VELOCITY = (
            current_moment / self.TOTAL_CHARGE if self.TOTAL_CHARGE != 0
            else np.zeros(3, dtype=float)
        )

        # Create child nodes if this node is an internal node
        # (i.e., it has more than 1 particle).
        # Create no children if this is an external node
        # (i.e., it has only 0 or 1 particles).
        self.CHILD_NODES = (
            self.create_child_nodes() if len(self.PARTICLES) > 1 and self.SIZE > 0
            else ()
        )

    def create_child_nodes(self) -> tuple[BarnesHutNode]:
        """Recursively create child nodes for this Barnes-Hut node.

        Returns
        -------
        tuple[BarnesHutNode]
            A list of child Barnes-Hut nodes, each representing an octant of this node.
        """
        # Size of child nodes.
        child_size = self.SIZE / 2

        # List of all the child nodes.
        children = []

        # Split each dimension in half.
        x_linspace = np.linspace(
            self.X_BOUNDS[0], self.X_BOUNDS[1], num=2, endpoint=False
        )
        y_linspace = np.linspace(
            self.Y_BOUNDS[0], self.Y_BOUNDS[1], num=2, endpoint=False
        )
        z_linspace = np.linspace(
            self.Z_BOUNDS[0], self.Z_BOUNDS[1], num=2, endpoint=False
        )

        # Loop eight times to create the octants.
        for lower_x in x_linspace:
            for lower_y in y_linspace:
                for lower_z in z_linspace:
                    child = BarnesHutNode(
                        x_bounds=np.array((lower_x, lower_x + child_size)),
                        y_bounds=np.array((lower_y, lower_y + child_size)),
                        z_bounds=np.array((lower_z, lower_z + child_size)),
                        particles=self.PARTICLES.copy(),
                    )
                    children.append(child)

        return tuple(children)

    def particle_within_bounds(self, particle: PointParticle) -> bool:
        """Return whether a given particle is within the bounds of this
        Barnes-Hut node.

        Parameters
        ----------
        particle : PointParticle
            The particle to check.

        Returns
        -------
        bool
            `True` if the particle is within the bounds of this node.

            `False` otherwise.
        """
        return (
            particle.position[0] >= self.X_BOUNDS[0]
            and particle.position[0] <= self.X_BOUNDS[1]
            and particle.position[1] >= self.Y_BOUNDS[0]
            and particle.position[1] <= self.Y_BOUNDS[1]
            and particle.position[2] >= self.Z_BOUNDS[0]
            and particle.position[2] <= self.Z_BOUNDS[1]
        )

    def get_gravitational_field_exerted(
        self,
        point: vectors.PositionVector,
        theta: float = 0.0,
        particle_id: int = -1
    ) -> vectors.FieldVector:
        """Calculate the approximate gravitational field exerted by this node
        at a given point.

        Parameters
        ----------
        point : vectors.PositionVector
            The position to calculate the gravitational field at,
            measured in meters (m).

        theta : float, default=0.0
            The value of theta, the Barnes-Hut approximation parameter being used.

            Given the distance between the point and the center of mass,
            it used to determine whether to return an approximate or exact value
            for the gravitational field.
            When theta is 0.0, no approximation will occur.

        particle_id : int, default=-1
            The ID of the particle to exclude from the force calculation.

            When the value is -1, no particles will be excluded
            from the force calculation.

        Returns
        -------
        vectors.FieldVector
            The gravitational field produced by this node, 
            measured in newtons per kg (N/kg).
        """
        # Calculate the displacement vector between the two points.
        r = point - self.CENTER_OF_MASS
        distance = np.linalg.norm(r)

        # Prevent divide by 0 error.
        if distance == 0:
            return np.zeros(3, dtype=float)

        force = np.zeros(3)

        # If the point is sufficiently far away, approximate the force.
        if self.SIZE < theta * distance:
            return -r * scipy.constants.G * self.TOTAL_MASS / distance ** 3

        # If the point is not sufficiently far away,
        # and this node is internal, add the force from each node.
        if len(self.CHILD_NODES) > 0:
            for child_node in self.CHILD_NODES:
                force += child_node.get_gravitational_field_exerted(
                    point, theta, particle_id)

        # If this the point is not sufficiently far away,
        # and this node is external, add the force from each particle.
        else:
            for particle in self.PARTICLES:
                if particle.ID != particle_id:
                    force += particle.get_gravitational_field_exerted(point)

        return force

    def get_electric_field_exerted(
        self,
        point: vectors.PositionVector,
        theta: float = 0.0,
        particle_id: int = -1
    ) -> vectors.FieldVector:
        """Calculate the approximate electric field exerted by this node
        at a given point.

        Parameters
        ----------
        point : vectors.PositionVector
            The position to calculate the electric field at.
            Measured in meters (m).
        theta : float, default=0.0
            The value of theta, the Barnes-Hut approximation parameter being used.
            Given the distance between the point and the center of charge,
            it used to determine whether to return an approximate or exact value
            for the gravitational field.

            When theta is 0.0, no approximation will occur.

        particle_id : int, default=-1
            The ID of the particle to exclude from the force calculation.

            When the value is -1, no particles will be excluded
            from the force calculation.

        Returns
        -------
        vectors.FieldVector
            The electric field vector produced by this node,
            measured in newtons per coulomb (N/C).
        """
        # Calculate the displacement vector between the two points.
        r = point - self.CENTER_OF_CHARGE
        distance = np.linalg.norm(r)

        # If the distance is 0, return a 0 array to avoid divide by 0.
        if distance == 0:
            return np.zeros(3, dtype=float)

        force = np.zeros(3)

        # The Coulomb constant.
        k = 1 / (4 * np.pi * scipy.constants.epsilon_0)

        # If the point is sufficiently far away, approximate the force.
        if self.SIZE < theta * distance:
            # The electrostatic force between the particles.
            return -r * k * self.TOTAL_CHARGE / distance ** 3

        # If the point is not sufficiently far away,
        # and this node is internal, add the force from each node.
        if len(self.CHILD_NODES) > 0:
            for child_node in self.CHILD_NODES:
                force += child_node.get_electric_field_exerted(
                    point, theta, particle_id)

        # If this the point is not sufficiently far away,
        # and this node is external, add the force from each particle.
        else:
            for particle in self.PARTICLES:
                if particle.ID != particle_id:
                    force += particle.get_electric_field_exerted(point)

        return force

    def get_magnetic_field_exerted(
        self,
        point: vectors.PositionVector,
        theta: float = 0.0,
        particle_id: int = -1
    ) -> vectors.FieldVector:
        """Calculate the approximate magnetic field exerted by this node at a
        given point.

        Parameters
        ----------
        point : vectors.PositionVector
            The point at which to calculate the magnetic field.
            Measured in meters (m).
        theta : float, default=0.0
            The value of theta, the Barnes-Hut approximation parameter being used.


            Given the distance between the point and the center of charge,
            it used to determine whether to return an approximate or exact
            value for the magnetic field.
            When theta is 0.0, no approximation will occur.
        particle_id : int, default=-1
            The ID of the particle to exclude from the force calculation.

            When the value is -1, no particles will be excluded
            from the force calculation.

        Returns
        -------
        vectors.FieldVector
            The magnetic field produced by this node,
            measured in teslas (T).
        """
        # The vector between the positions of the particles.
        r = point - self.CENTER_OF_CHARGE
        # The distance between the particle and center of charge.
        distance = np.linalg.norm(r)

        # If the distance is 0, return 0 vector to avoid divide by 0.
        if distance == 0:
            return np.zeros(3, dtype=float)

        force = np.zeros(3)

        # If the point is sufficiently far away, approximate the force.
        if self.SIZE < theta * distance:
            return (
                scipy.constants.mu_0 * self.TOTAL_CHARGE
                * np.cross(self.CENTER_OF_CHARGE_VELOCITY, r)
                / (4 * np.pi * distance ** 3)
            )

        # If the point is not sufficiently far away,
        # and this node is internal, add the force from each node.
        if len(self.CHILD_NODES) > 0:
            for child_node in self.CHILD_NODES:
                force += child_node.get_magnetic_field_exerted(
                    point, theta, particle_id)

        # If this the point is not sufficiently far away,
        # and this node is external, add the force from each particle.
        else:
            for particle in self.PARTICLES:
                if particle.ID != particle_id:
                    force += particle.get_magnetic_field_exerted(point)

        return force

    def get_height(self) -> int:
        """Return the height of the tree under this Barnes-Hut node.
        The root node (i.e., this node) has a height of 0.

        Returns
        -------
        int
            The height of the subtree under this Barnes-Hut node.
            If this node has no child nodes, it is a leaf node and its height is 0.
        """
        return (
            0 if len(self.CHILD_NODES) == 0
            else 1 + max(child.get_height() for child in self.CHILD_NODES)
        )

    @typing.override
    def __str__(self):
        """Return information about the centroid, total mass, center of mass,
        total charge, center of charge, velocity of center of charge,
        particles, and child nodes.
        """
        string = f'''x: {self.X_BOUNDS}, y: {self.Y_BOUNDS}, z: {self.Z_BOUNDS}
Total mass: {self.TOTAL_MASS}
Center of mass: {self.CENTER_OF_MASS}
Total charge: {self.TOTAL_CHARGE}
Center of charge: {self.CENTER_OF_CHARGE}
Velocity of center of charge: {self.CENTER_OF_CHARGE_VELOCITY}
Particles ({len(self.PARTICLES)}): {self.PARTICLES}
{len(self.CHILD_NODES)} child node(s):'''

        for child_node in self.CHILD_NODES:
            string += f'\n\t{child_node.__str__().replace('\n', '\n\t')}\n'

        return string
