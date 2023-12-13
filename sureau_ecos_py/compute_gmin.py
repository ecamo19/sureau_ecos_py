# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/10_10_compute_gmin.ipynb.

# %% auto 0
__all__ = ['compute_gmin']

# %% ../nbs/10_10_compute_gmin.ipynb 3
import numpy as np

# %% ../nbs/10_10_compute_gmin.ipynb 4
# Osmotic potential
def compute_gmin(leaf_temp:float, # Temperature of the leaf (degC)
                 gmin_20:float, # leaf conductance at 20 degC
                 t_phase:float,  # Temperature for phase transition of gmin
                 q10_1:float, # Q10 values for gmin= f(T) below T_phase
                 q10_2:float, # Q10 values for gcuti = f(T) above T_phase
                 gmin_temp_off = False, # # Unknown parameter definition
                 ) -> float:

        "Calculate minimum conductance (gmin) following Cochard et al. (2019)"

        print('original R code have a ambiguous gmin_temp_off specification')
        if gmin_temp_off is False:

            if leaf_temp <= t_phase:
                gmin = gmin_20 * q10_1**((leaf_temp - 20)/10)
                return gmin

            elif leaf_temp > t_phase:
                gmin = gmin_20 * q10_1**((t_phase - 20) / 10) * q10_2**((leaf_temp - t_phase) / 10)
                return gmin

        else:
            gmin = gmin_20
            return gmin

