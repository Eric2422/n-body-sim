# *n*-Body Simulator

A physics simulator for the interactions of point particles in constant, uniform
gravitational and electromagnetic fields. All numbers are in SI base units.

## Table of Contents

- [Installation](#installation)
- [Sphinx](#sphinx)
- [Usage](#usage)
  - [Schemas](#schemas)
  - [Input Files](#input-files)
  - [Output Files](#output-files)
  - [Running the Simulation](#running-the-simulation)
- [References](#references)

## Installation

1. If you have not installed Python already, [download it](https://www.python.org/downloads/).

2. Enter into your terminal:

```shell
git clone https://github.com/Eric2422/n-body-sim.git
cd n-body-sim/
pip install -r requirements.txt
```

## Sphinx

This project suppports Sphinx documentation. Currently there is no dedicated website
for the documentation, but you can build the documentation yourself.

After intalling, type into your terminal:

```shell
cd docs/
sphinx-build -M html source/ build/
```

The resulting HTML files should now appear in [`docs/build/](docs/build/).

Sometimes Sphinx will generate warnings about duplicate objects or documents not
being included. If that happens, ignore it and and build again. If errors are still
occurring, please [create a new issue](https://github.com/Eric2422/n-body-sim/issues/new).

After the Sphinx documentation is built, open [`docs/build/html/index.html`](docs/build/html/index.html)
in your browser of choice.

## Usage

### Schemas

The [`schemas/`](schemas/) directory contains the JSON schemas used to validate
and generate input files.

> [!Caution]
> It is recommended that you do not edit the schemas.
> Doing so may prevent the program from properly running.

### Input Files

The input files set up the simulation and are located in [`input/`](./input/).
Each input file is a JSON file validated using the schema in [`main.json`](./schemas/main.json).

The `num_time_steps` property of the input file dictates how many time steps the
simulator runs. If it is set to 0, only the initial state will be given.

Running `python src/files.py <input file name>` will create a JSON object filled
with default values as specified in the [schemas](./schemas/).

### Output Files

The output files, located in [`output/`](./output/), store records of the particle
states over time. The output file will have the same base name as the input file
but will have a file extension of `.txt` instead.

### Running the Simulation

To run the simulation, type `python src/main.py input/<input file name>`.
The file name should contain the file extension (i.e., `.json`).

## References

Ventimiglia, T., & Wayne, K. (2011, January 15). *The Barnes-Hut Algorithm*. ArborJS.
<https://arborjs.org/docs/barnes-hut>.
