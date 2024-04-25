import sys

import numpy as np

from files import Files
from particle import Particle
from position import Position


class Simulation():
    def __init__(self, particles) -> None:
        pass


if __name__ == '__main__':
    # Check if the user supplied a config file
    if len(sys.argv) < 2:
        print('Please enter the name of the config file.')
        sys.exit()

    file_data = Files.read_config_file(sys.argv[1])
    particles = [
        Particle(
            Position(line[0], line[1], line[2]), 
            line[3],
            line[4]         
        )
        for line in file_data
    ]

    