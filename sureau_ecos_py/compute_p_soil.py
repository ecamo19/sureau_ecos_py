# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/09_5_compute_p_soil.ipynb.

# %% auto 0
__all__ = ['compute_p_soil']

# %% ../nbs/09_5_compute_p_soil.ipynb 3
def compute_p_soil(rew: float, # Unknown parameter definition
                   alpha_vg: float, # Unknown parameter definition
                   n_vg: float # Unknown parameter definition
                   ) -> float:

    m = 1 - (1 / n_vg)

    # diviser par 10000 pour passer de cm à MPa
    return -1 * ((((1 / rew) ** (1 / m)) - 1) ** (1 / n_vg)) / alpha_vg / 10000
