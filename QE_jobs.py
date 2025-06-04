import os
import subprocess
import yaml

from ase.build import bulk
from ase.io import read, write


def load_pseudopotentials_dict(pseudopotentials_path):
    """
    Loads the dictionary of pseudopotentials from a specified path.

    Parameters:
    pseudopotentials_path (str): The path to the directory containing the pseudopotentials.yml file.

    Returns:
    dict: A dictionary where keys are element symbols and values are corresponding pseudopotential filenames.
    """
    os.environ['ESPRESSO_PSEUDO'] = pseudopotentials_path

    with open(os.path.join(pseudopotentials_path, "pseudopotentials.yml"), "r") as file:
        pseudopotentials_dict = yaml.safe_load(file)
    return pseudopotentials_dict


def run_quantum_espresso(input_file, output_file, pseudopotentials_path):
    """
    Executes a Quantum ESPRESSO calculation using the given input and output files.
    If the calculation fails (i.e., returncode != 0), the job will be retried once.
    If the second attempt also fails, a RuntimeError is raised.

    Parameters:
        input_file (str): The Quantum ESPRESSO input file (e.g., 'output.pwi').
        output_file (str): The file where the Quantum ESPRESSO output will be written (e.g., 'output.pwo').
        pseudopotentials_path (str): The path to the directory containing pseudopotentials.
    """
    os.environ['ESPRESSO_PSEUDO'] = pseudopotentials_path
    command = ["mpirun", "-np", "1", "pw.x", "-in", input_file]

    for attempt in range(2):
        with open(output_file, 'w') as file:
            job = subprocess.run(command, stdout=file, stderr=subprocess.STDOUT)
        if job.returncode == 0:
            break
        else:
            if attempt == 0:
                print("Execution failed, retrying...")
            else:
                raise RuntimeError(f"Quantum ESPRESSO failed with returncode = {job.returncode}")


def create_relax_pwi(element, lattice_param, cubic, kpts, output_filename,
                     pseudopotentials_path, pseudopotentials_dict):
    """
    Creates a Quantum ESPRESSO input file ('output.pwi') for a crystal structure relaxation.

    Parameters:
    element (str): The chemical symbol of the element to create the bulk structure.
    lattice_param (float): The lattice parameter for the bulk structure.
    cubic (bool): Flag to determine if the structure should be cubic.
    kpts (tuple): A tuple representing the k-points grid (e.g., (3, 3, 3)).
    pseudopotentials_path (str): The path to the directory containing pseudopotentials.
    pseudopotentials_dict (dict): Dictionary of element-symbol to pseudopotential filename mappings.
    """
    os.environ['ESPRESSO_PSEUDO'] = pseudopotentials_path
    pseudopotential_file = pseudopotentials_dict[element]
    pseudopotentials = {element: pseudopotential_file}
    structure = bulk(element, a=lattice_param, cubic=cubic)
    input_data_relax = {
        'calculation': 'vc-relax',
        'cell_dofree': 'ibrav',
    }

    write(
        output_filename,
        structure,
        kpts=kpts,
        input_data=input_data_relax,
        pseudopotentials=pseudopotentials,
        tstress=True,
        tprnfor=True
    )


def write_input_file(element, file_pattern, output_filename, kpts, pseudopotentials_path,
                     pseudopotentials_dict):
    """
    Writes the input file for strain calculation or other type of calculation.

    Parameters:
    element (str): The chemical symbol of the structure's element.
    file_pattern (str): File pattern for reading the strained structure files (not used in this template).
    output_filename (str): Path to the output file for PWscf input strain ('output.pwi').
    kpts (tuple): A tuple representing the k-points grid.
    pseudopotentials_path (str): The path to the directory containing pseudopotentials.
    pseudopotentials_dict (dict): Dictionary of element-symbol to pseudopotential filename mappings.
    """
    os.environ['ESPRESSO_PSEUDO'] = pseudopotentials_path
    pseudopotential_file = pseudopotentials_dict[element]
    pseudopotentials = {element: pseudopotential_file}
    input_data_static = {'calculation': 'scf'}
    structure_strain = read(file_pattern)

    write(
        output_filename,
        structure_strain,
        kpts=kpts,
        input_data=input_data_static,
        pseudopotentials=pseudopotentials,
        tstress=True,
        tprnfor=True
    )


def read_structure_xyz(xyz_file):
    """
    Reads a structure from a .xyz file and extracts the element, lattice parameters and whether it's cubic.

    Parameters:
    xyz_file (str): The path to the .xyz file containing the structure information.

    Returns:
    Atoms object: The first structure read from the .xyz file.
    """
    atoms = read(xyz_file, index=0)

    return atoms


if __name__ == '__main__':
    with open("rendered_wano.yml", "r") as file:
        params = yaml.safe_load(file)

    kpts = tuple(map(int, params['kpts'].split(',')))

    structure_file = "structure.xyz"
    atoms = read_structure_xyz(structure_file)

    lattice_param = atoms.cell.lengths()[0]
    cubic = True if len(set(atoms.cell.lengths())) == 1 else False
    element = atoms.get_chemical_symbols()[0]

    script_dir = os.path.dirname(os.path.abspath(__file__))
    pseudopotentials_path = os.path.join(script_dir, 'pseudopotentials')
    pseudopotentials_dict = load_pseudopotentials_dict(pseudopotentials_path)

    calculation_mode = params.get('Type of job')

    if calculation_mode == 'Relaxation':
        create_relax_pwi(
            element=element,
            lattice_param=lattice_param,
            cubic=cubic,
            output_filename='output.pwi',
            kpts=kpts,
            pseudopotentials_path=pseudopotentials_path,
            pseudopotentials_dict=pseudopotentials_dict
        )
        input_file = 'output.pwi'
    elif calculation_mode == 'Calculation energy':
        write_input_file(
            element=element,
            kpts=kpts,
            file_pattern='structure_strain.traj',
            output_filename='output.pwi',
            pseudopotentials_path=pseudopotentials_path,
            pseudopotentials_dict=pseudopotentials_dict
        )
        input_file = 'output.pwi'
    else:
        raise ValueError("Unsupported mode specified in 'rendered_wano.yml'.")

    output_file = "output.pwo"
    run_quantum_espresso(input_file, output_file, pseudopotentials_path)
