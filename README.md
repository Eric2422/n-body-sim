A physics simulation for simulating the movement of point particles.
It also simulates the effects of electromagnetic and gravitational fields.
All numbers are in SI units. 

# Setting Up the Simulation

## Schemas
The [./schemas](./schemas/) directory contains the JSON schemas that are used to validate and generate configuration files.
[Caution]
> It is recommended that you do not change them.
> Doing so may prevent the program from properly running.

## Configuration Files
The configuration files are used to set up the simulation and are located in [config/](./config/).

# Running the Simulation
To run the simulation, type `python src/main.py {config file name}`.
Running main.py from the ./src directory will cause errors.
The file should contain the file extension(i.e. ".csv").

# Output Files
The output files store records the state of the particles over time and
are located in [output/](./output/).
A sample file named [sample.txt](./output/sample.txt) is provided. 