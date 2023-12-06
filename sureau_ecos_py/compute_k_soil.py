# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/09_3_compute_k_soil.ipynb.

# %% auto 0
__all__ = ['compute_k_soil']

# %% ../nbs/09_3_compute_k_soil.ipynb 3
import collections

# %% ../nbs/09_3_compute_k_soil.ipynb 4
def compute_k_soil(
    rew: float,
    i_vg: float,
    n_vg: float,
    k_sat_vg: float,
    b_gc: float,  # Calculated using the `compute_b_gc` function
):
    # Create empty dict for storing params
    k_soil_parameters = collections.defaultdict(list)

    m = 1 - (1 / n_vg)

    k_soil = k_sat_vg * rew ** (i_vg) * (1 - (1 - rew ** (1 / m)) ** m) ** 2

    k_soil_gc = 1000 * b_gc * k_soil

    k_soil_parameters["k_soil"] = k_soil
    k_soil_parameters["k_soil_gc"] = k_soil_gc

    return k_soil_parameters
