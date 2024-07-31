import json
import sys

import numpy as np
import jsonschema


class FileHandler:
    CONFIG_DIR = './config'
    SCHEMA_DIR = './schema'
    OUTPUT_DIR = './output'

    def __init__(self, schema_file: str = 'main.json', file_name: str = 'sample.csv') -> None:
        """Initiate a file handler for reading and creating files. 

        Parameters
        ----------
        schema_file: str, optional
            The name of the JSON schema file used for the config files, by default 'schema.json'
            Found in the `./config` directory but does not contain the directory.
        file_name : str, optional
            The name of the config file with the file extension, by default 'sample.csv'
            The output file will have the same name but with the ".txt" file extension instead.
        """
        self.config_file = f'{FileHandler.CONFIG_DIR}/{file_name}'
        self.output_file = f'{
            FileHandler.OUTPUT_DIR}/{file_name.split(".")[0]}.txt'

        # Open the schema file and read
        self.json_schema = json.load(
            open(f'{FileHandler.SCHEMA_DIR}/{schema_file}')
        )

    def append_to_output_file(self, output_string: str = '') -> None:
        """Append the given string into the output file and create a newline.

        Parameters
        ----------
        file_name : str, optional
            The name of the file to write to, 
            excluding the directory(i.e. `output/`), by default `sample.txt`
        output_string: str, optional
            The string to be appended to the given file, by default ''
        """
        try:
            with open(self.output_file, 'a') as output_file:
                output_file.write(f'{output_string}\n')

        except OSError:
            print('The output file could not be opened.')

    def clear_output_file(self) -> None:
        """Clear the output file.
        """
        try:
            open(self.output_file, 'w').close()

        except OSError:
            print('The output file could not be opened.')

    def read_config_file(self) -> np.ndarray:
        """Read a given CSV file, extract the data, and return it.

        Returns
        -------
        np.ndarray
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

    def write_config_file(self, file_name: str = "config=.json", input_dict: object = None) -> None:
        """Write a schema-valid config JSON file based on a Python dictionary.

        Extended Summary
        ----------------
        The file must be in the `./config` directory.
        If the file does not exist, a new file will be created.
        Any pre-existing content will be overwritten.
        The `input_dict` must conform to the JSON schema in `self.schema_file`.

        Parameters
        ----------
        file_name : str, optional
            The name of the config file to be 
        input_dict : str, optional
            An object to write into the file as a JSON, by default `None`.

        Raises
        ------
        ValidationError
            If the given input object does not conform to the JSON schema.
        """
        if not jsonschema.validate(input_dict, self.json_schema):
            return

        # Write the object as a JSON into the config file
        json.dump(input_dict, f'./config/{file_name}')

    def create_json_template(self, schema: dict = None) -> dict:
        """Recursively loop through the provided schema 
        and generate a dictionary of blank values that conforms to the schema.

        Parameters
        ----------
        schema : dict, optional
            _description_, by default None

        Returns
        -------
        dict
            A dictionary of blank values that conforms to the schema.
        """

        if schema is None:
            schema = self.json_schema

        match schema['type']:
            case 'object':
                return {property: self.create_json_template(schema['properties'][property])
                        for property in schema['properties']
                        }

            case 'array':
                if 'minItems' in schema:
                    return [self.create_json_template(schema['items']) for i in range(schema['minItems'])]

            case 'string':
                return ''

            case 'number':
                return 0

            case 'boolean':
                return False

            case _:
                return None


if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise ValueError(
            "Please pass in the name of the configuration file to write to.")

    # Create a file handler using the given JSON schema
    file_handler = FileHandler()

    print(file_handler.create_json_template())
