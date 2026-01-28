Usage
=====

Schemas
-------

The ``schemas/`` directory contains the JSON schemas used to validate
and generate input files.

.. CAUTION::
    It is recommended that you do not edit the schemas.
    Doing so may prevent the program from properly running.

Input Files
-----------

The input files set up the simulation and are located in ``input/``.
Each input file is a JSON file validated using the schema in ``main.json``.

The ``num_time_steps`` property of the input file dictates how many time steps the
simulator runs. If it is set to 0, only the initial state will be given.

Running ``python src/files.py <input filename>`` will create a JSON object filled
with default values as specified in the schemas.

Output Files
------------

The output files, located in ``output/``, store records of the particle
states over time. The output file will have the same base name as the input file
but will have a file extension of ``.txt`` instead.

Running the Simulation
----------------------

To run the simulation, type ``python src/main.py input/<input filename>``.
The filename should contain the file extension (i.e., ``.json``).