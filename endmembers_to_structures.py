import os

import pandas as pd
from pymatgen.analysis.defects.generators import VacancyGenerator
from pymatgen.core import Structure


def generate_vacancies(structure, rm_species):
    vacancy_generator = VacancyGenerator()
    vacancies = [x.defect_structure for x in vacancy_generator.generate(structure, [rm_species])]
    return vacancies


def main():
    df = pd.read_csv("end_members.csv")
    old_structure = Structure.from_file("CaTiO3.vasp")
    for i in range(len(df)):
        new_structure = old_structure.copy()

        # Replace the species in the structure
        new_structure.replace_species({"Ca": df["element_A"][i], "Ti": df["element_B"][i]})

        # Make directory for the end member configuration
        directory = f"end_member_{df['end_member'][i]}_configuration_{df['configuration'][i]}"
        if not os.path.exists(directory):
            os.mkdir(directory)

        if df["N_A"][i] == 1 and df["N_B"][i] == 1 and df["N_O"][i] == 3:
            new_structure.to(filename=f"{directory}/POSCAR.vasp", fmt="poscar")

        elif df["N_O"][i] == 2.5:
            first_vacancies = generate_vacancies(new_structure, rm_species="O")
            second_vacancies = []
            for first_vacancy in first_vacancies:
                second_vacancies.extend(generate_vacancies(first_vacancy, rm_species="O"))
            for j, vacancy_structure in enumerate(second_vacancies):
                vacancy_structure.to(filename=f"{directory}/POSCAR_{j}.vasp", fmt="poscar")

        elif df["N_O"][i] == 2:
            first_vacancies = generate_vacancies(new_structure, rm_species="O")
            second_vacancies = []
            for first_vacancy in first_vacancies:
                second_vacancies.extend(generate_vacancies(first_vacancy, rm_species="O"))
            third_vacancies = []
            for second_vacancy in second_vacancies:
                third_vacancies.extend(generate_vacancies(second_vacancy, rm_species="O"))
            fourth_vacancies = []
            for third_vacancy in third_vacancies:
                fourth_vacancies.extend(generate_vacancies(third_vacancy, rm_species="O"))
            with open(f"{directory}/README", "w") as f:
                f.write("Number of vacancies: " + str(len(fourth_vacancies)) + "\n")
                f.write("How can we reduce the number of vacancies? \n")

        elif df["N_A"][i] == 1 and df["N_B"][i] == 0.75:
            vacancies = generate_vacancies(new_structure, rm_species=df["element_B"][i])
            for j, vacancy_structure in enumerate(vacancies):
                vacancy_structure.to(filename=f"{directory}/POSCAR_{j}.vasp", fmt="poscar")

        elif df["N_A"][i] == 2 / 3 and df["N_B"][i] == 1:
            with open(f"{directory}/README", "w") as f:
                f.write("It's hard to achieve 2/3 occupation on the A- and B-sites in an orthorhombic cell. How can we "
                        "deal with this? Try to find an experimental structure?\n")
            break


if __name__ == "__main__":
    main()
