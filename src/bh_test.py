import numpy as np
import sys

from barnes_hut import BarnesHutCell
import files
from particle import PointParticle

# Check if the user supplied a input file
if len(sys.argv) < 2:
    raise ValueError('Please enter the name of the input file.')

# Read the input file data and create particles based on that data
file_handler = files.FileHandler(input_file=sys.argv[1])
file_data = file_handler.read_input_file()

# Create a list of particles as described by the file data.
particles = [
    PointParticle(
        position=np.array(particle['position']),
        velocity=np.array(particle['velocity']),
        acceleration=np.array(particle['acceleration']),
        mass=particle['mass'],
        charge=particle['charge']
    )
    for particle in file_data['particles']
]

barnes_hut_cell = BarnesHutCell(
    particles=particles
)

testParticle = PointParticle(position=np.array((2, 2, 2)), mass=1, charge=1)

print(barnes_hut_cell)
print(testParticle.get_force_experienced(
    barnes_hut_cell.get_gravitational_field_exerted(testParticle.position),
    barnes_hut_cell.get_electric_field_exerted(testParticle.position),
    barnes_hut_cell.get_magnetic_field_exerted(testParticle.position)
))