import csv
import sys

import numpy as np


class Files:
    @staticmethod
    def read_config_file(file_name: str = 'sample.csv') -> np.array:
        """Read a given CSV file, extract the data, and return it.

        Parameters
        ----------
        file_name : str, optional
            The name of the input file, which is a CSV file.
            Does not contain the directory(i.e. ./config/)
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
        config_dir = './config/'

        # Check if the file exists
        try:
            with open(config_dir + file_name, newline='') as config_file:
                # Return the CSV values as a 2D array of floats
                return np.genfromtxt(config_file, delimiter=',', dtype=float)

        except OSError or FileNotFoundError:
            print('Please enter a valid config file.')
            sys.exit()

    @staticmethod
    def output_to_file(file_name: str = 'sample.csv', output_string: str = 'sample.csv') -> None:
        """Append the given string into the output file.

        Parameters
        ----------
        file_name : str, optional
            The name of the file to write to, 
            excluding the directory(i.e. ./output/), by default 'sample.csv'
        output_string: str, optional
            The string to be appended to the given file, by default 'sample.csv'
        """
        output_dir = './output/'

        try:
            with open(output_dir + file_name, 'a') as csv_file:
                csv_writer = csv.writer(csv_file, delimiter=', ')
        
        except OSError:
            print('The output file could not be opened.')