# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/09_7_compute_theta_at_given_p_soil.ipynb.

# %% auto 0
__all__ = ['compute_theta_at_given_p_soil']

# %% ../nbs/09_7_compute_theta_at_given_p_soil.ipynb 3
def compute_theta_at_given_p_soil(
    psi_target: float, # Unknown parameter definition
    theta_res: float, # Unknown parameter definition
    theta_sat: float, # Unknown parameter definition
    alpha_vg: float, # Unknown parameter definition
    n_vg: float # Unknown parameter definition
) -> float:
    return theta_res + (theta_sat - theta_res) / (
        1 + (alpha_vg * psi_target * 10000) ** n_vg
    ) ** (1 - 1 / n_vg)
