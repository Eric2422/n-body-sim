import json
import pathlib
import sys

import numpy as np
import jsonschema
import referencing
import referencing.exceptions


class FileHandler:
    CONFIG_DIR = './config'
    SCHEMA_DIR = pathlib.Path('./schemas')
    OUTPUT_DIR = pathlib.Path('./output')

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
        self.output_file = FileHandler.OUTPUT_DIR / f'{file_name.split(".")[0]}.txt'

        # Open the schema file and read
        self.schema_dict = json.load(
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

    def retrieve_schema_file(self, uri: str):
        """Retrieve a 

        Parameters
        ----------
        uri : str
            _description_

        Returns
        -------
        _type_
            _description_
        """
        path = self.SCHEMA_DIR / pathlib.Path(uri)
        print(f'path: {path}')
        contents = json.loads(path.read_text())
        return referencing.Resource.from_contents(contents)

    def validate_config_dict(self, config_dict: dict) -> bool:
        """Determine whether or not the given Python dict is valid by the schema.

        Parameters
        ----------
        config_dict : dict
            The dict that is being validated.

        Returns
        -------
        bool
            Whether the dict is valid. 
        """
        # self.retrieve_schema_file('main.json')
        print(config_dict)

        registry = referencing.Registry(retrieve=self.retrieve_schema_file)
        
        validator = jsonschema.Draft202012Validator(self.schema_dict, registry=registry)
        validator.validate(config_dict)

    def write_config_file(self, file_name: str = "config=.json", config_dict: dict = None) -> None:
        """Write a Python dictionary into a schema-valid config JSON file .

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
        if not self.validate_config_dict(config_dict):
            print()

        # Write the object as a JSON into the config file
        # json.dump(config_dict, f'./config/{file_name}')

    def create_json_template(self, schema: dict = None) -> dict:
        """Recursively loop through the provided schema and generate a schema-valid dictionary of blank values.

        Parameters
        ----------
        schema : dict, optional
            The JSON schema or schema property to generate a dictionary with, by default `self.json_schema`.

        Returns
        -------
        dict
            A dictionary of blank values that conforms to the schema.
        """
        # If no schema is passed in,
        # default to `self.json_schema`
        if schema is None:
            schema = self.schema_dict

        # If the schema contains a subschema,
        # open and read it
        if '$ref' in schema:
            ref_schema = json.load(
                open(FileHandler.SCHEMA_DIR / schema['$ref'])
            )
            return self.create_json_template(ref_schema)

        # Else, generate a value of the appropriate type
        match schema['type']:
            case 'object':

                # Recurse through the properties of the object
                return {property: self.create_json_template(schema['properties'][property])
                        for property in schema['properties']
                        }

            case 'array':
                # Create the array element to be copied
                array_element = self.create_json_template(schema['items'])

                # Add the mininum number of elements necessary.
                if 'minItems' in schema:
                    return [array_element for i in range(schema['minItems'])]

                else:
                    return [array_element]

            case 'string':
                return ''

            case 'number':
                if 'mininum' in schema:
                    return schema['mininum']

                elif 'exclusiveMininum' in schema:
                    return schema['exclusiveMininum'] + 1.0

                return 0.0

            case 'integer':
                if 'mininum' in schema:
                    return schema['mininum']

                elif 'exclusiveMininum' in schema:
                    return schema['exclusiveMininum'] + 1

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

    blank_dict = file_handler.create_json_template()
    # print(blank_dict)
    file_handler.write_config_file(config_dict=blank_dict)
