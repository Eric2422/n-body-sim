import numpy as np

from barnes_hut import BarnesHutCell
from particle import PointParticle

particles = [
    PointParticle(np.array((0, 0, 0))),
    PointParticle(np.array((0, 100, 0))),
    PointParticle(np.array((100, 100, 0))),
    PointParticle(np.array((100, 0, 0))),
    PointParticle(np.array((0, 0, 100))),
    PointParticle(np.array((0, 100, 100))),
    PointParticle(np.array((100, 100, 100))),
    PointParticle(np.array((100, 0, 100)))
]

barnes_hut_cell = BarnesHutCell(
    np.array((0, 100)),
    np.array((0, 100)),
    np.array((0, 100)),
    parent_particles=particles
)

print(barnes_hut_cell)
