import os
from glob import glob


def main():
    for directory in sorted(glob("end_*/*/")):
        os.chdir(directory)
        os.system("sbatch runscript")
        os.chdir("../..")


if __name__ == "__main__":
    main()
