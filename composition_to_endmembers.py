import os

from mp_api.client import MPRester
from pymatgen.core import Species, Composition, Structure

alphabet = "abcdefghijklmnopqrstuvwxyz"


def compute_end_members(oxidation_state_A, oxidation_state_B, target_total_metal_charge=6):
    total_metal_charge = oxidation_state_A + oxidation_state_B
    N_As, N_Bs, N_O = [], [], 0

    # stoichiometric or metal deficient
    if total_metal_charge <= target_total_metal_charge:
        N_As = [1]
        N_Bs = [1]
        N_O = total_metal_charge / 2

    # metal excess and metals have different oxidation states
    elif total_metal_charge == 7:
        N_As = [1, (target_total_metal_charge - oxidation_state_B) / oxidation_state_A]
        N_Bs = [1, (target_total_metal_charge - oxidation_state_A) / oxidation_state_B]
        if oxidation_state_A == 3 or oxidation_state_B == 3:
            N_O = 3

    # metal excess and metals have same oxidation state
    else:
        N_As = [
            1,
            (target_total_metal_charge - oxidation_state_B) / oxidation_state_A,
            target_total_metal_charge / total_metal_charge
        ]
        N_Bs = [
            (target_total_metal_charge - oxidation_state_A) / oxidation_state_B,
            1,
            target_total_metal_charge / total_metal_charge
        ]
        N_O = 3

    return N_As, N_Bs, N_O


def main(sites_metals_oxidation_states, target_total_metal_charge=6):
    end_members = []
    i = 1
    for key_A, value_A in sites_metals_oxidation_states["A"].items():
        for key_B, value_B in sites_metals_oxidation_states["B"].items():
            for oxidation_state_A in value_A:
                for oxidation_state_B in value_B:
                    N_As, N_Bs, N_O = compute_end_members(
                        oxidation_state_A, oxidation_state_B, target_total_metal_charge)

                    members = [
                        {
                            "A": {"element": key_A, "oxidation_state": oxidation_state_A, "N": N_A},
                            "B": {"element": key_B, "oxidation_state": oxidation_state_B, "N": N_B},
                            "O": {"element": "O", "oxidation_state": -2, "N": N_O},
                            "end_member": i,
                            "configuration": alphabet[j],
                        }
                        for j, (N_A, N_B) in enumerate(zip(N_As, N_Bs))
                    ]
                    end_members.extend(members)
                    i += 1
    return end_members


if __name__ == "__main__":
    sites_metals_oxidation_states = {
        "A": {"Ca": [2], "Ce": [3, 4]},
        "B": {"Ti": [3, 4], "Mn": [2, 3, 4]}
    }
    end_members = main(sites_metals_oxidation_states)
    for end_member in end_members:
        # get formula
        A = Species(end_member["A"]["element"], end_member["A"]["oxidation_state"])
        B = Species(end_member["B"]["element"], end_member["B"]["oxidation_state"])
        O = Species(end_member["O"]["element"], end_member["O"]["oxidation_state"])
        species = {
            A: end_member["A"]["N"],
            B: end_member["B"]["N"],
            O: end_member["O"]["N"]
        }
        composition = Composition(species)
        formula, factor = composition.get_integer_formula_and_factor()

        # get materials project documents
        get_materials_project_documents = False
        if get_materials_project_documents:
            with MPRester(os.getenv("MATERIALS_PROJECT_API_KEY")) as mpr:
                docs = mpr.summary.search(
                    formula=formula,
                    theoretical=False,
                )

        # get structure for composition
        structure = Structure.from_file("CaTiO3.vasp")
