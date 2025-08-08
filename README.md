# *n*-Body Simulator

A physics simulation for simulating the movement of point particles.
It also simulates the effects of electromagnetic and gravitational fields.
All numbers are in SI units.

## Setting Up the Simulation

### Schemas

The [`./schemas`](./schemas/) directory contains the JSON schemas used to validate and generate configuration files.

> [!Caution]
> It is recommended that you do not edit the schemas.
> Doing so may prevent the program from properly running.

### Configuration Files

The configuration files are used to set up the simulation and are located in [`config/`](./config/).
Each configuration file is a JSON file validated using the [`main.json` schema](./schemas/main.json).
Running `python src/files.py {configuration file name}` will create a JSON object full of blank values.

## Running the Simulation

To run the simulation, type `python src/main.py config/{configuration file name}`.
The file name should contain the file extension(i.e. `.json`).

## Output Files

The output files, located in [`output/`](./output/), store records of the state of the particles over time.
The output file will have the same base name as the configuration file but will have a file extension of `.txt` instead.
A sample output file named [`sample.txt`](./output/sample.txt) is provided.

## Citations

### Barnes-Hut algorithm

### Metal resistivities

- [https://www.engineeringtoolbox.com/resistivity-conductivity-d_418.html](https://www.engineeringtoolbox.com/resistivity-conductivity-d_418.html)

### Metal densities

- [https://www.rsc.org/periodic-table/element/29/copper](https://www.rsc.org/periodic-table/element/29/copper)
- [https://www.rsc.org/periodic-table/element/47/silver](https://www.rsc.org/periodic-table/element/47/silver)
- [https://www.rsc.org/periodic-table/element/79/gold](https://www.rsc.org/periodic-table/element/79/gold)
- [https://www.rsc.org/periodic-table/element/13/aluminium](https://www.rsc.org/periodic-table/element/13/aluminium)
