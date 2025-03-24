import numpy as np

from wires import Wire

points = np.array(
    (
        (-1e3, 0, 0),
        (1e3, 0, 0)
    )
)

wire = Wire(points, 1.0)
constatnt_electric_field = np.array((100, 0.0, 0.0))
particles = ()


def electric_field(l: np.float64):
    return sum([particle.get_electric_field(
        wire.get_wire_point(l)) for particle in particles]) + constatnt_electric_field


print(wire.get_current(electric_field))
print()
print(wire.get_magnetic_field(
    np.array((0.0, 0.0, 0.001)), electric_field))
