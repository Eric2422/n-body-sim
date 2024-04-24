import sys

from particle import Particle
from position import Position
from files import Files


class Simulation():
    def __init__(self) -> None:
        pass
    


# Check if the user supplied a config file
if len(sys.argv) < 2:
    print('Please enter the name of the config file.')
    sys.exit()

file_data = Files.read_config_file(sys.argv[1])