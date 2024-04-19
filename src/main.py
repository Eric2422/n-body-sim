from scipy import constants

from particle import Particle
from position import Position

electron = Particle(Position(0, 0, 0), -1, constants.electron_mass)
proton = Particle(Position(0, 1, 0), 1, constants.proton_mass)

print(f'{electron.coulumbs_law(proton)} N')