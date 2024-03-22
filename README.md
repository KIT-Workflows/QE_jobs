# QE_jobs

**Version:** 0.0.1

**Author:** J. Schaarschmidt

## Description

This script is utilized to perform Quantum ESPRESSO (QE) calculations for two main types of jobs: relaxation of crystal structures and energy calculation.

## Inputs

- `rendered_wano.yml`: A YAML configuration file specifying the type of job (`Relaxation` or `Calculation energy`), parameters for the simulation, and the path to the structure file.

- `structure.xyz`: The essential input file for detailing the crystal structure. It needs to specify the type of elements, lattice parameters, the crystal type, and other relevant data for the calculation.

Depending on the type of job selected, different output files and processes are initiated:

## Outputs

For **Relaxation**:

- `output.pwi`: The Quantum ESPRESSO input file created for the relaxation process, encompassing computational parameters, structural details, and instructions for the relaxation calculation.
- `output.pwo`: The resulting file from Quantum ESPRESSO after the relaxation job, containing details about the final structure, energy, forces, and other computed properties.

For **Energy Calculation**:

- `structure_strain.traj`: (Optional) A file pattern to read strained structures if needed for the computation.
- `output.pwi`: Similar to the relaxation process, this serves as the input file for Quantum ESPRESSO but tailored for energy calculation.
- `output.pwo`: The resulting file containing the outcome of the energy calculation, including total energy, electron density, and other pertinent results.

## Dependencies

The successful operation of this workflow necessitates the following components:

- **ASE (Atomic Simulation Environment):** A Python toolset for manipulating atoms, executing simulations, and analyzing outcomes. It serves to manage crystal structures and mold Quantum ESPRESSO input files.
- **pwtools:** Part of the Quantum ESPRESSO package, helpful for the input and output processing of simulations.
- **Quantum Espresso:** The core software executing the computations for material modeling based on density-functional theory.