
"""Module to simplify and manage file creation, reading, and writing.

If run as ``__main__``, will creeate a blank input file based on the
default values in the schemas.
"""


import io
import json
import os
import pathlib
import sys
import typing

import jsonschema
import referencing


class FileHandler:
    """Class of attributes and methods to create, read, and write to
    files.

    Parameters
    ----------
    schema_file : str, default='schema.json'
        The name of the JSON schema file used for the input files.

        Found in :const:`INPUT_DIR` but does not contain the
        directory. Best to keep it to the default unless you want to
        write an entire JSON schema.
    input_file : str, default='sample.csv'
        The file path of the input file, including file extension.

        Accepts both with and without the directory.
        The output file will have the same name
        but with the ".txt" file extension instead.

    Attributes
    ----------
    INPUT_DIR : :class:`pathlib.Path`
        Represents the directory that contains the input files.
    SCHEMA_DIR : :class:`pathlib.Path`
        Represents the directory that contains the schema files used for
        JSON formatting.
    OUTPUT_DIR : :class:`pathlib.Path`
        Represents the directory that contains the output files.
    INPUT_FILE_PATH : str
        A string that stores the path of the input file.
    INPUT_DATA : Any
    OUTPUT_FILE_PATH : str
        A string that stores the path of the output file.

    Raises
    ------
    OSError
        If `schema_file` can not be read or its formatting is incorrect.
    """
    INPUT_DIR = pathlib.Path('./input')
    SCHEMA_DIR = pathlib.Path('./schemas')
    OUTPUT_DIR = pathlib.Path('./output')

    @typing.override
    def __init__(
        self,
        schema_file: str = 'main.json',
        input_file_path: str = 'sample.json'
    ) -> None:

        self.INPUT_FILE_PATH = pathlib.Path(
            input_file_path if os.path.dirname(input_file_path) == 'input'
            else self.INPUT_DIR / input_file_path
        )

        # If the file path does not include the input/, add it.
        # Then read the data.
        with open(self.INPUT_FILE_PATH) as file:
            self.INPUT_DATA = json.load(file)

        # The output file has the same name as input_file
        # but with the '.txt' extension.
        self.OUTPUT_FILE_PATH = pathlib.Path(
            FileHandler.OUTPUT_DIR /
            (pathlib.Path(input_file_path).stem + '.txt')
        )

        self.__output_io_wrapper: io.TextIOWrapper | None = None

        # Open the schema file and read it.
        with open(FileHandler.SCHEMA_DIR / schema_file) as file:
            self.SCHEMA = json.load(file)

    def open_output_file(self) -> None:
        """Open an :class:`io.TextIOWrapper` for :const:`OUTPUT_FILE_PATH`.
        Should be closed by :meth:`clear_output_file()` after done writing
        to it.

        Raises
        ------
        OSError
            If :const:`OUTPUT_FILE_PATH` does not point to an accessible file.
        """
        self.__output_io_wrapper = self.OUTPUT_FILE_PATH.open('a')

    def append_to_output_file(self, output_string: str = '\n') -> None:
        """Append the given string into the output file. If
        :const:`OUTPUT_FILE_PATH` has already been opened, then the string
        will be appended to it without closing.

        Elsewise, it will open :const:`OUTPUT_FILE_PATH`, append to it,
        and then close it.

        Parameters
        ----------
        output_string : str, default = '\\n'
            The string to be appended to the given file.

        Raises
        ------
        OSError
            If the output file is not writeable.
        """
        # If the output file has already been used, use it.
        if self.__output_io_wrapper == None:
            with self.OUTPUT_FILE_PATH.open('a') as file:
                file.write(output_string)

        else:
            self.__output_io_wrapper.write(output_string)

    def clear_output_file(self) -> None:
        """Clear the output file.

        Raises
        ------
        OSError
            If the output file is not writeable.
        """
        # If the output file has already been used, use it.
        if self.__output_io_wrapper is None:
            self.OUTPUT_FILE_PATH.write_text('')

        else:
            self.__output_io_wrapper.truncate(0)

    def close_output_file(self) -> None:
        """Close the :attr:`__output_io_wrapper`. If it is not open,
        nothing happens.
        """
        # Check if the TextIOWrapper exists.
        # If not, the operation fails.
        if self.__output_io_wrapper != None:
            self.__output_io_wrapper.close()

    def retrieve_schema_file(self, uri: str) -> referencing.Resource:
        """Retrieve the contents of a given JSON file as a Python object.

        Parameters
        ----------
        uri : str
            The URI of the JSON file to read. The file will be assumed to
            be under :const:`SCHEMA_DIR`.

        Returns
        -------
        referencing.Resource
            The contents of the JSON file as a Python object.
        """
        pathlib.Path = self.SCHEMA_DIR / uri
        contents = json.loads(pathlib.Path.read_text())

        return referencing.Resource.from_contents(contents)

    def validate_input_dict(
        self,
        input_dict: dict,
        schema: dict | None = None
    ) -> bool:
        """Determine whether or not the given :class:`dict` is valid by the schema.

        Parameters
        ----------
        input_dict : :class:`dict`
            The :class:`dict` that is being validated.
        schema : dict, optional
            The JSON schema or schema property to validate the other JSON
            :class:`dict` with. If ``None``, defaults to :const:`SCHEMA`.

        Returns
        -------
            Whether the given dictionary conforms to :const:`SCHEMA`.
        """
        # If no schema is passed in, default to self.json_schema.
        schema_dict = self.SCHEMA if schema is None else schema

        # Create registry that retrieves all necessary files.
        registry = referencing.Registry(retrieve=self.retrieve_schema_file)

        # Validate the input dict using the schema and registry.
        validator = jsonschema.Draft202012Validator(
            schema=schema_dict, registry=registry
        )

        try:
            validator.validate(input_dict)
            return True

        except jsonschema.ValidationError:
            return False

    def write_input_file(self, input_dict: dict) -> None:
        """Write a schema-valid Python dictionary into a input JSON file.

        The file must be in :const:`INPUT_DIR`. The `input_dict` must
        conform to the JSON schemas in :const:`SCHEMA_DIR`.

        If the file does not exist, a new file will be created.
        If the file *does* exist, any pre-existing content will be
        overwritten. The file will have the same name as
        :const:`INPUT_FILE_PATH`.

        Parameters
        ----------
        input_dict : :class:`dict`
            An object to write into the file as a JSON.
        """
        self.validate_input_dict(input_dict)

        # Write the object as a JSON into the input file
        with self.INPUT_FILE_PATH.open('w+') as file:
            json.dump(
                input_dict,
                file,
                indent=4
            )

    def create_json_template(self, schema: dict | None = None) -> typing.Any:
        """Recursively loop through the provided schema
        and generate a schema-valid dictionary of default values.

        Parameters
        ----------
        schema : dict, optional
            The JSON schema or schema property to generate a :class:`dict` with.
            If ``None``, the value of ``schema`` will be
            assumed.

        Returns
        -------
        :class:`dict`
            A :class:`dict` of default values that conforms to the schema.
        """
        # If no schema is passed in, default to self.json_schema.
        schema_dict = self.SCHEMA if schema is None else schema

        # If the schema contains a subschema, open and read it.
        if '$ref' in schema_dict:
            with open(FileHandler.SCHEMA_DIR / schema_dict['$ref']) as file:
                ref_schema = json.load(
                    file
                )
            return self.create_json_template(ref_schema)

        if 'default' in schema_dict:
            return schema_dict['default']

        # Else, generate a value of the appropriate type.
        match schema_dict['type']:
            case 'object':

                # Recurse through the properties of the object.
                return {
                    property: self.create_json_template(
                        schema_dict['properties'][property]
                    )
                    for property in schema_dict['properties']
                }

            case 'array':
                # Create the array element to be copied.
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
    file_handler = FileHandler(input_file_path=sys.argv[1])

    template_dict = file_handler.create_json_template()
    file_handler.write_input_file(template_dict)
