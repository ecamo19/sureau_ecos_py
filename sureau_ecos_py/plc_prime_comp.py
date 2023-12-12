# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/10_8_plc_prime_comp.ipynb.

# %% auto 0
__all__ = ['plc_prime_comp']

# %% ../nbs/10_8_plc_prime_comp.ipynb 3
import numpy as np
from .plc_comp import plc_comp

# %% ../nbs/10_8_plc_prime_comp.ipynb 4
def plc_prime_comp(plc:float, # Computed using the `plc_comp` function
                   slope:float, # Unknown parameter
                   ) -> float:

    "This function computes PLC Prime from PLC current value"

    return -slope/25 * plc/100 * (1 - plc/100)

