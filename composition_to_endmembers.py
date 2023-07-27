import pandas as pd

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
        N_Bs = [(target_total_metal_charge - oxidation_state_A) / oxidation_state_B, 1]
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
    ems = main({"A": {"Ca": [2], "Ce": [3, 4]}, "B": {"Ti": [3, 4], "Mn": [2, 3, 4]}})

    # convert to pandas dataframe
    df_A = pd.DataFrame([x["A"] for x in ems])
    df_B = pd.DataFrame([x["B"] for x in ems])
    df_O = pd.DataFrame([x["O"] for x in ems])
    df_end_member = pd.DataFrame([x["end_member"] for x in ems], columns=["end_member"])
    df_configuration = pd.DataFrame([x["configuration"] for x in ems], columns=["configuration"])

    # rename columns
    df_A = df_A.rename(columns={"element": "element_A", "oxidation_state": "oxidation_state_A", "N": "N_A"})
    df_B = df_B.rename(columns={"element": "element_B", "oxidation_state": "oxidation_state_B", "N": "N_B"})
    df_O = df_O.rename(columns={"element": "element_O", "oxidation_state": "oxidation_state_O", "N": "N_O"})
    df = pd.concat([df_A, df_B, df_O, df_end_member, df_configuration], axis=1)

    # write to csv
    df.to_csv("end_members.csv", index=False)
