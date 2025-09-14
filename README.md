# *n*-Body Simulator

A physics simulation for simulating the movement of point particles.
It also simulates the effects of electromagnetic and gravitational fields.
All numbers are in SI units.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
  - [Schemas](#schemas)
  - [Input Files](#input-files)
  - [Running the Simulation](#running-the-simulation)
  - [Output Files](#output-files)
- [Acknowledgements](#acknowledgements)
  - [Barnes-Hut Algorithm](#barnes-hut-algorithm)

## Installation

If you have not installed Python already, [download it](https://www.python.org/downloads/).

Go to your command line of choice and enter:

```shell
git clone https://github.com/Eric2422/n-body-sim.git
pip install -r requirements
```

## Usage

### Schemas

The [`./schemas`](./schemas/) directory contains the JSON schemas used to validate and generate input files.

> [!Caution]
> It is recommended that you do not edit the schemas.
> Doing so may prevent the program from properly running.

### Input Files

The input files set up the simulation and are located in [`input/`](./input/).
Each input file is a JSON file validated using the schema in [`main.json`](./schemas/main.json).

Running `python src/files.py <input file name>` will create a JSON object filled with default values.

### Running the Simulation

To run the simulation, type `python src/main.py input/<input file name>`.
The file name should contain the file extension(i.e. `.json`).

### Output Files

The output files, located in [`output/`](./output/), store records of the state of the particles over time.
The output file will have the same base name as the input file but will have a file extension of `.txt` instead.

## Acknowledgements

### Barnes-Hut Algorithm
