# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/09_6_compute_p_soil_camp.ipynb.

# %% auto 0
__all__ = ['compute_p_soil_camp']

# %% ../nbs/09_6_compute_p_soil_camp.ipynb 3
def compute_p_soil_camp(sws: float, tsc: float, b_camp: float, psie: float):
    return -1 * (psie * ((sws / tsc) ** -b_camp))
