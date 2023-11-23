# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/03_calculate_radiation_diurnal_pattern.ipynb.

# %% auto 0
__all__ = ['calculate_radiation_diurnal_pattern']

# %% ../nbs/03_calculate_radiation_diurnal_pattern.ipynb 3
from typing import List
from math import pi, cos, sin

# %% ../nbs/03_calculate_radiation_diurnal_pattern.ipynb 4
def calculate_radiation_diurnal_pattern(
    time_of_the_day: List[
        int
    ],  # a numeric value of vector indicating the time of the day (in seconds)
    day_length: int,  # value indicating the duration of the day (in seconds)
):
    "Calculated diurnal pattern of temperature assuming a sinusoidal pattern with T = tmin at sunrise and T = (tmin + tmax)/2 at sunset. From sunset to sunrise follows a linear trend"

    # calculate_radiation_diurnal_pattern ----------------------------------

    # sunrise
    ws = (day_length / 3600.0) * (pi / 24.0)
    w = ws - (time_of_the_day / day_length) * (ws * 2.0)

    prop = ((pi / 24.0) * (cos(w) - cos(ws))) / (sin(ws) - ws * cos(ws))

    return prop / 3600.0