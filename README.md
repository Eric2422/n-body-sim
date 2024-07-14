A physics simulation for simulating the movement of point particles.
It also simulates the effects of electromagnetic and gravitational fields.
All numbers are in SI units. 

# Running the Simulation
To run the simulaiton, type `python src/main.py {config file name}`.
The file should contain the file extension(i.e. ".csv")

# Config Files
The config files are used to set up the simulation and are located in [config/](./config/).
Each config file is a CSV.
A sample file named [sample.csv](./config/sample.csv) is provided.
Each line is a point particle in the following format:
> {x}, {y}, {y}, {charge}, {mass}

# Output Files
The output files store records the state of the particles over time and
are located in [output/](./output/).
A sample file named [sample.txt](./output/sample.txt) is provided. 