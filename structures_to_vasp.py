import sys
from glob import glob

from pymatgen.core import Structure
from pymatgen.io.vasp.sets import MPScanRelaxSet


USER_INCAR_SETTINGS = {
    "ISMEAR": 0,
    "SIGMA": 0.05,
    "ISYM": 0,
    "METAGGA": "SCAN",
    "LDAU": True,
    "LDAUTYPE": 2,
    "LDAUL": {"Ca": -1, "Ce": 3, "Ti": 2, "Mn": 2, "O": -1},
    "LDAUU": {"Ca": 0, "Ce": 2, "Ti": 2.5, "Mn": 2.7, "O": 0},
    "LDAUJ": {"Ca": 0, "Ce": 0, "Ti": 0, "Mn": 0, "O": 0},
    "LDAUPRINT": 1,
    "LMAXMIX": 6,
    "NELMIN": 6,
    "LPLANE": True,
    "NCORE": 8,
    "LSCALU": False,
    "NSIM": 4,
}


RUNSCRIPT = """#!/bin/bash
#SBATCH --job-name={job_name}
#SBATCH --output=log
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=64
#SBATCH --mem-per-cpu=3G
#SBATCH --partition=dragon2
#SBATCH --exclusive

ulimit -s unlimited

srun -n 64 /software/vasp.6.4.1/bin/vasp_std
"""


def write_runscript(path, job_name):
    with open(path + "/runscript", "w") as f:
        f.write(RUNSCRIPT.format(job_name=job_name))


def main():
    # get endmember-configuration directories
    directories = sorted(glob("end_member_*"))
    for directory in directories:
        structure_files = sorted(glob(directory + "/*.vasp"))
        if len(structure_files) == 0:
            print(f"Warning: no structure files found in {directory}")
            continue
        for structure_file in structure_files:
            structure = Structure.from_file(structure_file)

            # apply small random perturbations to the ion positions
            structure.perturb(distance=0.01, min_distance=0.01)

            # create VASP input files
            MPScanRelaxSet(structure, user_incar_settings=USER_INCAR_SETTINGS).write_input(structure_file[:-5])

            # write runscript
            i_endmember = directory.split("_")[2]
            i_configuration = directory.split("_")[4]
            i_poscar = structure_file.split("_")[-1][:-5]
            job_name = f"{i_endmember}_{i_configuration}_{i_poscar}"
            write_runscript(structure_file[:-5], job_name)


if __name__ == "__main__":
    main()
