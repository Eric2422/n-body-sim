import json
import os
import pathlib
import sys
import typing

import jsonschema
import referencing


class FileHandler:
    """Handles the creation, reading, and writing of files."""

    INPUT_DIR = pathlib.Path('./input')
    """Represents the directory that contains the input files."""
    SCHEMA_DIR = pathlib.Path('./schemas')
    """Represents the directory that contains the schema files used for JSON formatting."""
    OUTPUT_DIR = pathlib.Path('./output')
    """Represents the directory that contains the output files."""

    @typing.override
    def __init__(
        self,
        schema_file: str = 'main.json',
        input_file: str = 'sample.json'
    ) -> None:
        """Initiate a file handler for reading and creating files.

        Parameters
        ----------
        schema_file : str, default = 'schema.json'
            The name of the JSON schema file used for the input files.

            Found in the `./input` directory but does not contain the directory.
            Best to keep it to the default unless you want to write an entire JSON schema.

        input_file : str, default = 'sample.csv'
            The file path of the input file, including file extension.

            Accepts both with and without the directory.
            The output file will have the same name
            but with the ".txt" file extension instead.
        """
        self.input_file_path = pathlib.Path(
            input_file if os.path.dirname(input_file) == 'input'
            else self.INPUT_DIR / input_file
        )

        # The output file has the same name as input_file
        # but with the '.txt' extension.
        self.output_file_path = pathlib.Path(
            FileHandler.OUTPUT_DIR /
            (pathlib.Path(input_file).stem + '.txt')
        )
        """Stores the path of the output file."""

        self.output_io_wrapper = None
        """Stores the `TextIOWrapper` that handles writing to the output file."""

        # Open the schema file and read it.
        with open(FileHandler.SCHEMA_DIR / schema_file) as file:
            self.schema = json.load(file)

    def open_output_file(self) -> bool:
        """Open a `TextIOWrapper` for `self.output_file_path`.
        Should be closed by :func:`clear_output_file()` after done writing to it.

        Returns
        -------
        bool
            Whether the operation succeeds.
        """
        try:
            self.output_io_wrapper = self.output_file_path.open('a')
            return True

        except OSError:
            return False

    def append_to_output_file(self, output_string: str = '\n') -> bool:
        """Append the given string into the output file.
        If the `self.output_file_path` has already been opened,
        then the string will be append to it without closing.

        Elsewise, it will open `self.output_file_path`, append to it,
        then close it.

        Parameters
        ----------
        output_string : str, default = '\n'
            The string to be appended to the given file.
        """
        try:
            # If the output file has already been used, use it.
            if self.output_io_wrapper == None:
                with self.output_file_path.open('a') as file:
                    file.write(output_string)

            else:
                self.output_io_wrapper.write(output_string)

            return True

        except OSError:
            return False

    def clear_output_file(self) -> bool:
        """Clear the output file.

        Returns
        -------
        bool
            Whether the operation succeeds. If :py:``
        """
        try:
            # If the output file has already been used, use it.
            if self.output_io_wrapper is None:
                self.output_file_path.write_text('')

            else:
                self.output_io_wrapper.truncate(0)

            return True

        except OSError:
            return False

    def close_output_file(self) -> bool:
        """Close the output file.

        Returns
        -------
        bool
            Whether the operation succeeds. 
            Fails if the output file is not open in the first place.
        """
        try:
            # Check if the TextIOWrapper exists.
            # If not, the operation fails.
            if self.output_io_wrapper == None:
                raise OSError()

            else:
                self.output_io_wrapper.close()
                return True

        except OSError:
            return False

    def read_input_file(self) -> dict:
        """Read the input JSON file, extract the data, and return it as a `dict`.

        Returns
        -------
        dict
            A `dict` containing information about the initial state of the simulation.
            Stores a `list` of the particles.

        Raises
        ------
        `FileNotFoundError`
            When the input file can not be found.
        """
        # Try to open the input file.
        try:
            with open(self.input_file_path) as file:
                return json.load(file)

        except OSError or FileNotFoundError:
            print('Please enter a valid input file.')
            sys.exit()

    def retrieve_schema_file(self, uri: str) -> referencing.Resource:
        """Retrieve a `referencing.Resource` from the given URI,
        representing a JSON as a Python object.

        Parameters
        ----------
        uri : str
            The URI of the JSON file to read.
            The file will automatically be assumed to under :py:const:`self.SCHEMA_DIR`.

        Returns
        -------
        referencing.Resource
            The `Resource` created from the contents of the JSON file.
        """
        pathlib.Path = self.SCHEMA_DIR / uri
        contents = json.loads(pathlib.Path.read_text())

        return referencing.Resource.from_contents(contents)

    def validate_input_dict(
        self,
        input_dict: dict,
        schema: dict | None = None
    ) -> None:
        """Determine whether or not the given `dict` is valid by the schema.

        Parameters
        ----------
        input_dict : dict
            The `dict` that is being validated.
        schema : dict` | `None, optional
            The JSON schema or schema property to validate the other JSON `dict` with,
            by `self.json_schema`.

        Raises
        ------
        `ValidationError`
            If the given input `dict` does not conform to the JSON schema.
        """
        # If no schema is passed in,
        # default to `self.json_schema`
        schema_dict = self.schema if schema is None else schema

        # Create registry that retrieves all necessary files.
        registry = referencing.Registry(retrieve=self.retrieve_schema_file)

        # Validate the input dict using the schema and registry
        validator = jsonschema.Draft202012Validator(
            schema=schema_dict, registry=registry
        )
        validator.validate(input_dict)

    def write_input_file(self, input_dict: dict) -> None:
        """Write a schema-valid Python dictionary into a input JSON file.

        The file must be in the `input/` directory.
        The `input_dict` must conform to the JSON schema in `self.schema_file`.

        If the file does not exist, a new file will be created.
        If the file *does* exist, any pre-existing content will be overwritten.
        The file will have the same name as `self.input_file`.

        Parameters
        ----------
        input_dict : dict
            An object to write into the file as a JSON.
        """
        self.validate_input_dict(input_dict)

        # Write the object as a JSON into the input file
        json.dump(
            input_dict,
            self.input_file_path.open('w+'),
            indent=4
        )

    def create_json_template(self, schema: dict | None = None) -> typing.Any:
        """Recursively loop through the provided schema
        and generate a schema-valid dictionary of default values.

        Parameters
        ----------
        schema : dict, optional
            The JSON schema or schema property to generate a `dict` with,
            by default `self.schema`.

        Returns
        -------
        dict
            A `dict` of default values that conforms to the schema.
        """
        # If no schema is passed in,
        # default to `self.json_schema`
        schema_dict = self.schema if schema is None else schema

        # If the schema contains a subschema,
        # open and read it
        if '$ref' in schema_dict:
            with open(FileHandler.SCHEMA_DIR / schema_dict['$ref']) as file:
                ref_schema = json.load(
                    file
                )
            return self.create_json_template(ref_schema)

        if 'default' in schema_dict:
            return schema_dict['default']

        # Else, generate a value of the appropriate type
        match schema_dict['type']:
            case 'object':

                # Recurse through the properties of the object
                return {
                    property: self.create_json_template(
                        schema_dict['properties'][property]
                    )
                    for property in schema_dict['properties']
                }

            case 'array':
                # Create the array element to be copied
                array_element = self.create_json_template(schema_dict['items'])

                # Add the minimum number of elements necessary.
                if 'minItems' in schema_dict:
                    return [
                        array_element for i in range(schema_dict['minItems'])
                    ]

                else:
                    return [array_element]

            case 'string':
                return ''

            case 'number':
                if 'minimum' in schema_dict:
                    return schema_dict['minimum']

                if 'exclusiveMinimum' in schema_dict:
                    return schema_dict['exclusiveMinimum'] + 1.0

                return 0.0

            case 'integer':
                if 'minimum' in schema_dict:
                    return schema_dict['minimum']

                if 'exclusiveMinimum' in schema_dict:
                    return schema_dict['exclusiveMinimum'] + 1

                return 0

            case 'boolean':
                return False

            case _:
                return None


# Generate a default blank template input file.
if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise ValueError(
            "Please pass in the name of the input file to write to."
        )

    # Create a file handler using the given JSON schema
    file_handler = FileHandler(input_file=sys.argv[1])

    template_dict = file_handler.create_json_template()
    file_handler.write_input_file(template_dict)
