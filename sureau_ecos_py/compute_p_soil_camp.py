# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/09_6_compute_p_soil_camp.ipynb.

# %% auto 0
__all__ = ['compute_p_soil_camp']

# %% ../nbs/09_6_compute_p_soil_camp.ipynb 3
def compute_p_soil_camp(sws: float, # Unknown parameter definition
                        tsc: float, # Unknown parameter definition
                        b_camp: float, # Unknown parameter definition
                        psie: float # Unknown parameter definition
                        )-> float:
    return -1 * (psie * ((sws / tsc) ** -b_camp))
