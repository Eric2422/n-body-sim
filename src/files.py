import csv
import sys

class Files:
    @staticmethod
    def read_config_file(file_name: str = 'sample.csv') -> list:
        """Read a given config file, extract the data, and return it as a 2D list.

        Parameters
        ----------
        file_name : str, optional
            The name of the input file, which is a CSV file.
            Does not contain the directory(i.e. /config/)
            By default 'sample.csv'.

        Returns
        -------
        list
            A 2D list of floats containing data about the particles.
            Each inner list is a particle.

        Raises
        ------
        FileNotFoundError
            When the provided file can not be found.
        """
        config_dir = './config/'

        try:
            with open(config_dir + file_name, newline='') as config_file:
                # Return the CSV values as a 2D list of floats
                return [[float(field) for field in row] for row in csv.reader(config_file, delimiter=',')]

        except FileNotFoundError:
            print('Please enter a valid config file.')
            sys.exit()