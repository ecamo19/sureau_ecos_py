# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/09_8_compute_theta_at_given_p_soil_camp.ipynb.

# %% auto 0
__all__ = ['compute_theta_at_given_p_soil_camp']

# %% ../nbs/09_8_compute_theta_at_given_p_soil_camp.ipynb 3
def compute_theta_at_given_p_soil_camp(
    theta_sat: float, # Unknown parameter definition
    psi_target: float, # Unknown parameter definition
    psie: float, # Unknown parameter definition
    b_camp: float # Unknown parameter definition
) -> float:

    return theta_sat * (psi_target / -psie) ** (1 / -b_camp)
