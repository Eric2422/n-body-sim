import numpy as np

from wires import Wire
import vectors

points = np.array(
    (
        (-1e3, 0, 0),
        (1e3, 0, 0)
    )
)

wire = Wire(points, np.float64(1.0))
constant_electric_field = np.array((100, 0.0, 0.0))
particles = ()


def electric_field(r: vectors.PositionVector) -> vectors.FieldVector:
    l = np.linalg.norm(r - points[0])

    return np.array(sum([particle.get_electric_field(
        wire.get_wire_point(l)) for particle in particles]) + constant_electric_field, dtype=np.float64)


print(wire.get_current(electric_field))
print()
print(wire.get_magnetic_field(
    np.array((0.0, 0.0, 0.001)), electric_field))
