import sys

from particle import Particle
from position import Position

def read_config_file(file_name: str = 'sample.csv') -> list:
    """
    Read a given config file, extract the data, and return it as a 2D list.

    Parameters
    ----------
    file_name : str, optional
        The name of the input file, which is a CSV file.
        Does not contain the directory(i.e. /config/)
        By default 'sample.csv'.

    Returns
    -------
    list
        A 2D list of data about the particles.
        Each inner list is a particle.
        Each element is a float. 

    Raises
    ------
    FileNotFoundError
        
    """
    config_dir = './config/'

    file_data = []

    try:
        with open(config_dir + file_name, 'r') as config_file:
            for line in config_file.readlines():
                file_data.append([float(i) for i in line.split(", ")])

    except FileNotFoundError:
        print('Please enter a valid config file.')
        sys.exit()
    
    return file_data


# Check if the user supplied a config file
if len(sys.argv) < 2:
    print('Please enter the name of the config file.')
    sys.exit()

particles = read_config_file(sys.argv[1])    

for particle in particles:
    pass