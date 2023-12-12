# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/10_1_rs_comp.ipynb.

# %% auto 0
__all__ = ['rs_comp']

# %% ../nbs/10_1_rs_comp.ipynb 3
import numpy as np


# %% ../nbs/10_1_rs_comp.ipynb 4
def rs_comp(pi_ft:float, # Osmotic potential at full turgor (MPa)
            e_symp:float, # Modulus of elastoicoty of the Symplasm (MPa/%)
            p_min:float # Unknown parameter
            ) -> float:
    "Compute Rs from pmin (resolution from Bartlet et al 2012 EcolLett and email Herve Cochard 19/06/2015)"
    return max((-1 * (p_min + pi_ft - e_symp) - np.sqrt((p_min + pi_ft - e_symp)**2 + 4 * (p_min * e_symp))) / (2 * e_symp), 1 - pi_ft / p_min)

