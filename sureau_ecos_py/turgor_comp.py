# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/10_2_turgor_comp.ipynb.

# %% auto 0
__all__ = ['turgor_comp']

# %% ../nbs/10_2_turgor_comp.ipynb 3
import numpy as np


# %% ../nbs/10_2_turgor_comp.ipynb 4
def turgor_comp(pi_ft:float, # Osmotic potential at full turgor (MPa)
            e_symp:float, # Modulus of elastoicoty of the Symplasm (MPa/%)
            r_stemp:float # Unknown parameter
            ) -> float:
    "Turgor pressure"
    return -pi_ft - e_symp * r_stemp

