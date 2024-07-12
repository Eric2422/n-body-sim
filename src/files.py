import csv
import sys

import numpy as np


class FileHandler:
    CONFIG_DIR = './config'
    OUTPUT_DIR = './output'

    def __init__(self, file_name='sample') -> None:
        """Initiate a file handler for reading and creating files. 

        Parameters
        ----------
        file_name : str, optional
            The name of the config and output file without the file extension, by default 'sample'
        """
        self.config_file = f'{FileHandler.CONFIG_DIR}/{file_name}.csv'
        self.output_file = f'{FileHandler.OUTPUT_DIR}/{file_name}.txt'

    def append_to_file(self, output_string: str = '') -> None:
        """Append the given string into the output file and create a newline.

        Parameters
        ----------
        file_name : str, optional
            The name of the file to write to, 
            excluding the directory(i.e. `output/`), by default `sample.txt`
        output_string: str, optional
            The string to be appended to the given file, by default ""
        """
        try:
            with open(self.output_file, 'a') as output_file:
                output_file.write(f'{output_string}\n')

        except OSError:
            print('The output file could not be opened.')

    def clear_output_file(self) -> None:
        """Clear the output file
        """
        try:
            open(self.output_file, 'w').close()

        except OSError:
            print('The output file could not be opened.')

    def read_config_file(self) -> np.array:
        """Read a given CSV file, extract the data, and return it.

        Returns
        -------
        np.array
            A 2D NumPy array of floats containing data about the particles.
            Each inner list is a particle.

        Raises
        ------
        FileNotFoundError
            When the config file can not be found.
        """
        # Check if the config file exists
        try:
            with open(self.config_file, newline='') as config_file:
                # Return the CSV values as a 2D array of floats
                return np.genfromtxt(config_file, delimiter=',', dtype=float)

        except OSError or FileNotFoundError:
            print('Please enter a valid config file.')
            sys.exit()
