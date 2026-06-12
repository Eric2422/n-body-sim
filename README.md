# *n*-Body Simulator

A physics simulator for the interactions of charged point particles
in constant, uniform gravitational and electromagnetic fields.
However, this simulator does not account for relativistic or quantum effects.

All values are in SI units.

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

1. If you have not installed Python already,
   [download it](https://www.python.org/downloads/).

2. Enter into your terminal:

```shell
git clone https://github.com/Eric2422/n-body-sim.git
cd n-body-sim/
pip install -r requirements.txt
```

## Sphinx

This project suppports Sphinx documentation.
There is a [documentation page](https://eric2422.github.io/n-body-sim/),
but it is currently broken
(see [Issue #108](https://github.com/Eric2422/n-body-sim/issues/108)),
so you should build the documentation yourself.

After intalling, type into your terminal:

```shell
sphinx-build -M html docs/source/ docs/build/
```

The resulting HTML files should now appear in [`docs/build/`](docs/build/).

After the Sphinx documentation is built,
open [`docs/build/html/index.html`](docs/build/html/index.html)
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
Each input file is a JSON file validated using the schema in
[`main.json`](./schemas/main.json).

The `num_time_steps` property of the input file dictates how many time steps the
simulator runs.
If it is set to 0, only the initial state will be given.

Running `python src/files.py <input filename>` will create a JSON object filled
with default values as specified in the [schemas](./schemas/).

### Output Files

The output files, located in [`output/`](./output/),
store records of the particle states over time.
The output file will have the same base name as the input file
but will have a file extension of `.txt` instead.

### Running the Simulation

To run the simulation, type `python src/main.py input/<input filename>`.
The filename should contain the file extension (i.e., `.json`).

## References

References are given in the files where they are relevant,
which each file maintaining its own numbering, but here is an overall list.
Since it is ambiguous which files come first,
the following list is sorted alphabetically.

GitHub, `gitignore`, <https://github.com/github/gitignore>, (2026).

T. Komiya, *Appendix: Deploying a Sphinx project online*,
<https://www.sphinx-doc.org/en/master/tutorial/deploying.html>,
(2025).

J. Leedham,
*Automatically document all modules recursively with Sphinx autodoc*,
<https://stackoverflow.com/a/62613202>, (2021).

E. Sciple *et al.*, `checkout`, v6.0.2,
<https://github.com/actions/checkout> (GitHub Inc., San Franciso, 2026).

S. Ueda *et al.*, `actions-gh-pages`, v.4.1.0,
<https://github.com/peaceiris/actions-gh-pages> (GitHub Inc., San Franciso,
2026).

T. Ventimiglia and K. Wayne, *The Barnes-Hut Algorithm*,
<https://arborjs.org/docs/barnes-hut>, (2011).

I. Zosimov *et al.*, `setup-python`, v6.2.0,
<https://github.com/actions/setup-python> (GitHub Inc., San Franciso, 2026).
