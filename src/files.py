import sys

import numpy as np


class Files:
    CONFIG_DIR = '../config/'

    @classmethod
    def read_config_file(cls, file_name: str = 'sample.csv') -> np.array:
        """
        Read a given CSV file, extract the data, and return it.

        Parameters
        ----------
        file_name : str, optional
            The name of the input file, which is a CSV file.
            Does not contain the directory(i.e. /config/)
            By default 'sample.csv'.

        Returns
        -------
        np.array
            A 2D NumPy array of floats containing data about the particles.
            Each inner list is a particle.

        Raises
        ------
        FileNotFoundError
            When the provided file can not be found.
        """
        # Check if the file exists
        try:
            with open(cls.CONFIG_DIR + file_name, newline='') as config_file:
                # Return the CSV values as a 2D array of floats
                return np.genfromtxt(config_file, delimiter=',', dtype=float)

        except FileNotFoundError:
            print('Please enter a valid config file.')
            sys.exit()