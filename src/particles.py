"""Module of particles and pseudo-particles (i.e., collections of
particles treated as a single particle).
"""


import typing

import numpy as np
import numpy.typing as npt
import scipy.constants

import vectors


class PointParticle:
    """A point particle in 3D space with a velocity, acceleration, charge,
    and mass.

    Parameters
    ----------
    position : :type:`vectors.PositionVector`, default=np.array([0.0, 0.0, 0.0]).
        The initial position of the particle in meters (m).
    velocity : :type:`vectors.VelocityVector`, default=np.array([0.0, 0.0, 0.0]).
        The initial velocity of the particle in meters per second (m/s).
    acceleration : :type:`vectors.AccelerationVector`, default=np.array([0.0, 0.0, 0.0])
        The initial acceleration of the particle in meters per second
        squared (m/s^2).
    mass : float, default=1.0
        The mass of the charged particle in kilograms (kg).
    charge : float, default=0.0
        The charge of the particle in coulombs (C).

    Attributes
    ----------
    current_id : int
        The ID number that will be assigned to :attr:`ID` of the next
        object instantiated, increasing by one (1) everytime.
    position : :type:`vectors.PositionVector`
        The current position of the particle in meters (m).
    velocity : :type:`vectors.VelocityVector`
        The current velocity of the particle in meters per second (m/s).
    acceleration : :type:`vectors.AccelerationVector`
        The current acceleration of the particle in meters per second
        squared (m/s^2).
    MASS : float
        The mass of the particle in kilograms (kg), which should never
        change.
    CHARGE : float
        The charge of the particle in coulombs (C), which should never
        change.
    ID : int
        The unique ID identifying the particle, which should never change.
    """

    current_id = 0

    @typing.override
    def __init__(
        self,
        position: vectors.PositionVector = np.array([0.0, 0.0, 0.0]),
        velocity: vectors.VelocityVector = np.array([0.0, 0.0, 0.0]),
        acceleration: vectors.AccelerationVector = np.array([0.0, 0.0, 0.0]),
        mass: float = 1.0,
        charge: float = 0.0
    ) -> None:
        """Automatically increment :attr:`current_id` by 1."""
        # Represented by arrays of (x, y, z).
        self.position = position
        self.velocity = velocity
        self.acceleration = acceleration

        self.MASS = mass
        self.CHARGE = charge

        self.ID = PointParticle.current_id
        PointParticle.current_id += 1

    def apply_force(self, force: vectors.ForceVector = np.zeros(3)) -> None:
        """Set the acceleration of this particle based on the given force.

        Parameters
        ----------
        force : :type:`vectors.ForceVector`, default=np.zeros(3)
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
        point : :type:`vectors.PositionVector`
            The coordinates of the point that this particle is exerting a
            gravitational field upon, in meters (m).

        Returns
        -------
        :type:`vectors.FieldVector`
            The gravitational field generated at ``point`` in newtons per
            kilogram (N/kg).
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
        gravitational_field : :type:`vectors.FieldVector`
            The gravitational field acting upon this particle,
            in newtons per kilogram (N/kg).

        Returns
        -------
        :type:`vectors.ForceVector`
            The force acting upon this particle as a result of the
            gravitational field, in newtons (N).
        """
        return self.MASS * gravitational_field

    def get_electric_field_exerted(
        self,
        point: vectors.PositionVector
    ) -> vectors.FieldVector:
        """Calculate the electric field at a given point due to this
        particle.

        Parameters
        ----------
        point : :type:`vectors.PositionVector`
            The point to calculate the electric field at in meters (m).

        Returns
        -------
        :type:`vectors.FieldVector`
            The electric field that this particle creates at the given
            point in newtons per coulomb (N/C).
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
        """Calculate the force acting upon this particle by the given
        electric field.

        Parameters
        ----------
        electric_field : :type:`vectors.FieldVector`
            The electric field acting upon this particle in newtons per
            coulomb (N/C).

        Returns
        -------
        :type:`vectors.ForceVector`
            The force exerted upon this particle by the electric field in
            newtons (N).
        """
        return self.CHARGE * electric_field

    def get_magnetic_field_exerted(
        self,
        point: vectors.PositionVector
    ) -> vectors.FieldVector:
        """Calculate the magnetic field exerted by by this particle at a
        given point.

        Parameters
        ----------
        point : :type:`vectors.PositionVector`
            The point at which to calculate the magnetic field in meters
            (m).

        Returns
        -------
        :type:`vectors.FieldVector`
            The magnetic field exerted by this particle at the given point
            in teslas (T).

        Notes
        -----
        It uses the "Biot-Savart Law for point charges", technically a
        misnomer, which only approximates magnetic fields for particles
        with a velocity << c.
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
        magnetic_field : :type:`vectors.FieldVector`
            The magnetic field acting upon this particle in teslas (T).
        velocity : :type:`vectors.FieldVector`, optional
            The velocity to use for the magnetic force calculations.
            If ``None``, defaults to :attr:`velocity`.

        Returns
        -------
        :type:`vectors.ForceVector`
            The force exerted upon this particle by the magnetic field in
            newtons (N).
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
        gravitational_field : :type:`vectors.FieldVector`, default=np.array((0, 0, 0))
            The gravitational field acting upon this particle.
        electric_field : :type:`vectors.FieldVector`, default=np.array((0, 0, 0))
            The electric field acting upon this particle.
        magnetic_field : :type:`vectors.FieldVector`, default=np.array((0, 0, 0))
            The magnetic field acting upon this particle.
        velocity : type:`vectors.VelocityVector`, optional.
            The velocity to use for the magnetic force calculations,
            which may differ from :attr:`velocity`. If ``None``, default
            to :attr:`velocity`.

        Returns
        -------
        :type:`vectors.ForceVector`
            The net force exerted upon this particle as a result of
            gravitational, electric, and magnetic fields.
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
        """Calculate and apply the forces from gravitational and
        electromagnetic fields on upon this particle.

        Parameters
        ----------
        gravitational_field : :type:`vectors.FieldVector`
            The gravitational field acting upon this particle in newtons
            per kilogram (N/kg).
        electric_field : :type:`vectors.FieldVector`
            The electric field acting upon this particle in newtons per
            coulomb (N/C).
        magnetic_field : :type:`vectors.FieldVector`
            The magnetic field acting upon this particle in teslas (T).
        """
        self.apply_force(
            self.get_gravitational_force_experienced(gravitational_field)
            + self.get_electrostatic_force_experienced(electric_field)
            + self.get_magnetic_force_experienced(magnetic_field)
        )

    @typing.override
    def __eq__(self, value: object) -> bool:
        """Return whether an :class:`object` is equal to this
        :class:`PointParticle`. They are equal if and only if the
        :class:`object` is also a :class:`PointParticle` with the same
        :const:`ID`.

        Parameters
        ----------
        value : :class:`object`
            The :class:`object` to compare against this
            :class:`PointParticle` for equality.

        Returns
        -------
        bool
            Whether ``value`` is also a :class:`PointParticle` with the
            same :const:`ID`.
        """
        return isinstance(value, PointParticle) and self.ID == value.ID

    @typing.override
    def __str__(self) -> str:
        """Return a string containing information about this particle's
        current state.

        Returns
        -------
        str
            Return a string containing information about this particle's
            current state.
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
        """Return a string containing all the arguments needed to
        instantiate another identical particle (aside from
        :const:`PointParticle.id`).

        Returns
        -------
        str
            A string containing all the arguments needed to instantiate
            another identical particle (aside from
            :const:`PointParticle.id`).
        """
        cls = self.__class__.__name__
        return (
            f'{cls}({self.position}, {self.velocity}, {self.acceleration}, '
            f'{self.MASS}, {self.CHARGE})'
        )


class BarnesHutNode:
    """A single node of a Barnes-Hut octree, which contains eight child
    nodes. For brevity's sake, the mechanics of the Barnes-Hut algorithm
    will not be explained here. See the `Wikipedia article`_ or this
    `Arbor article`_ for a full explanation.
    .. _Wikipedia article: https://en.wikipedia.org/wiki/Barnes-Hut_simulation
    .. _Arbor article: https://arborjs.org/docs/barnes-hut

    Assumes a center of charge rather than using a multipole expansion.

    Parameters
    ----------
    particles : list[PointParticle], default=[]
        List of particles that are contained within this Barnes-Hut node.
    x_bounds : npt.NDArray[np.float64], optional
        A 2-element NumPy array that contains the lower and upper x
        bounds in that order. If ``None``, the bounds will be
        automatically calculated to be the smallest possible that
        would contain all the particles.
    y_bounds : npt.NDArray[np.float64], optional
        A 2-element NumPy array that contains the lower and upper y
        bounds in that order. If ``None``, the bounds will be
        automatically calculated to be the smallest possible that
        would contain all the particles.
    z_bounds : npt.NDArray[np.float64], optional
        A 2-element NumPy array that contains the lower and upper z
        bounds in that order. If ``None``, the bounds will be
        automatically calculated to be the smallest possible that
        would contain all the particles.

    References
    ----------
    """

    @staticmethod
    def cube_bounds(
        x_bounds: npt.NDArray[np.float64],
        y_bounds: npt.NDArray[np.float64],
        z_bounds: npt.NDArray[np.float64]
    ) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64], float]:
        """Make the given bounds cube (i.e., all with the same size), but
        preserve the centroid. The smaller two dimensions will increased
        to the same size as the largest dimension.

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
            The newly cubed bounds, the centroid, and the new size of the
            cube bounds (i.e., the previous maximum dimension),
            respectively.
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
        """A two-element array containing the lower and upper x bounds of
        this node."""

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
        """A two-element array containing the lower and upper y bounds of
        this node."""

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
        """A two-element array containing the lower and upper z bounds of
        this node."""

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
        """Total mass of all particles in this node, measured in 
        kilograms (kg)."""
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
        """Total charge of all particles in this node, measured in
        coulombs (C)."""
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
            A list of child Barnes-Hut nodes, each representing an octant
            of this node.
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
        particle : :class:`PointParticle`
            The particle to check.

        Returns
        -------
        bool
            ``True`` if the particle is within the bounds of this node.

            ``False`` otherwise.
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
        """Calculate the approximate gravitational field exerted by this
        node at a given point.

        Parameters
        ----------
        point : :type:`vectors.PositionVector`
            The position to calculate the gravitational field at measured
            in meters (m).

        theta : float, default=0.0
            The value of theta, the Barnes-Hut approximation parameter
            being used.

            Given the distance between the point and the center of mass,
            it used to determine whether to return an approximate or
            exact value for the gravitational field. When 0.0, no
            approximation will occur.

        particle_id : int, default=-1
            The ID of the particle to exclude from the force calculation.

            When the value is -1, no particles will be excluded from the
            force calculation.

        Returns
        -------
        :type:`vectors.FieldVector`
            The gravitational field produced by this node measured in
            newtons per kg (N/kg).
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
        point : :type:`vectors.PositionVector`
            The position to calculate the electric field at.
            Measured in meters (m).
        theta : float, default=0.0
            The value of theta, the Barnes-Hut approximation parameter
            being used. Given the distance between the point and the
            center of charge, it used to determine whether to return an
            approximate or exact value for the gravitational field.
            When 0.0, no approximation will occur.

        particle_id : int, default=-1
            The ID of the particle to exclude from the force calculation.

            When -1, no particles will be excluded from the force
            calculation.

        Returns
        -------
        :type:`vectors.FieldVector`
            The electric field vector produced by this node measured in
            newtons per coulomb (N/C).
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
        """Calculate the approximate magnetic field exerted by this node
        at a given point.

        Parameters
        ----------
        point : :type:`vectors.PositionVector`
            The point at which to calculate the magnetic field.
            Measured in meters (m).
        theta : float, default=0.0
            The value of theta, the Barnes-Hut approximation parameter
            being used.

            Given the distance between the point and the center of charge,
            it used to determine whether to return an approximate or exact
            value for the magnetic field. When 0.0, no approximation will
            occur.
        particle_id : int, default=-1
            The ID of the particle to exclude from the force calculation.

            When  -1, no particles will be excluded
            from the force calculation.

        Returns
        -------
        :type:`vectors.FieldVector`
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
            If this node has no child nodes, it is a leaf node and its
            height is 0.
        """
        return (
            0 if len(self.CHILD_NODES) == 0
            else 1 + max(child.get_height() for child in self.CHILD_NODES)
        )

    @typing.override
    def __str__(self):
        """Return information about the centroid, total mass, center of
        mass, total charge, center of charge, velocity of center of
        charge, particles, and child nodes.
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
