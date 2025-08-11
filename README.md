# *n*-Body Simulator

## Table of Contents

- [Setting Up the Simulation](#setting-up-the-simulation)
  - [Schemas](#schemas)
  - [Configuration Files](#configuration-files)
- [Running the Simulation](#running-the-simulation)
- [Output Files](#output-files)
- [Citations](#citations)
  - [Barnes-Hut Algorithm](#barnes-hut-algorithm)
  - [Metal Densities](#metal-densities)
  - [Metal Resistivities](#metal-resistivities)

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

The configuration files set up the simulation and are located in [`config/`](./config/).
Each configuration file is a JSON file validated using the schema in [`main.json`](./schemas/main.json).
Running `python src/files.py <configuration file name>` will create a JSON object filled with default values.

## Running the Simulation

To run the simulation, type `python src/main.py config/<configuration file name>`.
The file name should contain the file extension(i.e. `.json`).

## Output Files

The output files, located in [`output/`](./output/), store records of the state of the particles over time.
The output file will have the same base name as the configuration file but will have a file extension of `.txt` instead.

## Citations

### Barnes-Hut Algorithm

### Metal Densities

- [https://www.rsc.org/periodic-table/element/29/copper](https://www.rsc.org/periodic-table/element/29/copper)
- [https://www.rsc.org/periodic-table/element/47/silver](https://www.rsc.org/periodic-table/element/47/silver)
- [https://www.rsc.org/periodic-table/element/79/gold](https://www.rsc.org/periodic-table/element/79/gold)
- [https://www.rsc.org/periodic-table/element/13/aluminium](https://www.rsc.org/periodic-table/element/13/aluminium)

### Metal Resistivities

- [https://www.engineeringtoolbox.com/resistivity-conductivity-d_418.html](https://www.engineeringtoolbox.com/resistivity-conductivity-d_418.html)
