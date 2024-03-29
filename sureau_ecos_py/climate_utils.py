# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_climate_utils.ipynb.

# %% auto 0
__all__ = ['compute_vpd_from_t_rh', 'compute_etp_pt', 'compute_etp_pm', 'calculate_radiation_diurnal_pattern',
           'calculate_temperature_diurnal_pattern', 'calculate_rh_diurnal_pattern', 'ppfd_umol_to_rg_watt',
           'rg_watt_to_ppfd_umol', 'rg_convertions', 'declination']

# %% ../nbs/00_climate_utils.ipynb 3
import numpy as np
from numpy import exp
from typing import List
from math import pi, cos, sin, atan

# %% ../nbs/00_climate_utils.ipynb 4
def compute_vpd_from_t_rh(
    relative_humidity: float,  # Air relative_humidity (%)
    temperature: float,  # Air temperature (degrees Celsius)
    air_pressure: float = 101325,  # Unknown parameter definition Air pressure, used?
) -> float:
    "Compute vapor pressure deficit (VPD) from air relative humidity and air temperature"

    # Constants -----------------------------------------------------------------

    # molar weight dry air (g/mol)
    mass = 28.966

    # molar weight H20 H2O(g/mol) Mh2o not used in this function??
    mass_h2o = 18

    # Perfect gas constant %J/mol/K
    rgz = 8.314472

    # conversion of temperature in K
    temp_kelvin = temperature + 273.15

    # D_air not used in this function??
    d_air = ((air_pressure) / (rgz * (temp_kelvin))) * mass

    # Compute VPD -------------------------------------------------------------
    es = 6.108 * exp(17.27 * temperature / (237.2 + temperature)) * 100

    ea = relative_humidity * es / 100

    vpd = (es - ea) / 1000

    if vpd < 0:
        vpd = 0

    return vpd

# %% ../nbs/00_climate_utils.ipynb 9
def compute_etp_pt(
    tmoy: float,  # Mean temperature over the considered time step (degrees Celsius)
    net_radiation: float,  # Cumulative Net radiation over the considered  time sep  (MJ.m2)
    pt_coeff: float = 1.26,  # An empirical constant accounting for the vapor pressure deficit and resistance values Typically, α is 1.26 for open bodies of water, but has a wide range of values from less than 1 (humid conditions) to almost 2 (arid conditions).
    g: float = 0,  # Unknown parameter definition
) -> float:
    "Calcule Potential evapotranspiration (mm) PET using Pristeley Taylor Formulation"

    # Constants -----------------------------------------------------------------

    # Stefan-Boltzman constant [MJ.K^-4.m^-2.day^-1]
    # sb_constant = 4.903 * 10**9

    # Psychometer constant
    gamma = 0.0666

    # Latent heat of vaporisation
    lamb = 2.45

    # Compute ETP -------------------------------------------------------------

    #  s: slope of the saturation vapour pressure function (AO 1998)
    slope_sta = (
        4098
        * 0.6108
        * exp((17.27 * tmoy) / (tmoy + 237.3))
        / ((tmoy + 237.3) ** 2)
    )
    # s <-       4098 * 0.6108 * exp((17.27 * Tmoy) / (Tmoy + 237.3)) / ((Tmoy + 237.3)^2)

    etp = (
        pt_coeff
        * (slope_sta / (slope_sta + gamma))
        * ((net_radiation - g) / lamb)
    )
    # ETP <- PTcoeff * (s / (s + gamma)) * ((NetRadiation - G) / lambda)

    return etp

# %% ../nbs/00_climate_utils.ipynb 15
def compute_etp_pm(
    tmoy: float,  # Mean temperature over the considered time step (degrees Celsius)
    net_radiation: float,  # Cumulative Net radiation over the considered  time sep (MJ.m2)
    u: float,  #  Wind speed (m.s-1)
    vpd: float,  # Vapor pressure deficit (kpa)
    g: float = 0,  # Unknown parameter definition
) -> float:
    "Compute reference ETP from Penmman formulation"

    # Constants -----------------------------------------------------------------

    # Stefan-Boltzman constant [MJ.K^-4.m^-2.day^-1]
    # sb_constant = 4.903 * 10**9

    # Psychometer constant
    gamma = 0.0666

    # Latent heat of vaporisation
    # lamb = 2.45

    # Compute ETP -------------------------------------------------------------

    #  s: slope of the saturation vapour pressure function (AO 1998)
    # delta = 4098 * 0.6108 * exp((17.27 * Tmoy) / (Tmoy + 237.3)) / ((Tmoy + 237.3)^2)
    delta = (
        4098
        * 0.6108
        * np.exp((17.27 * tmoy) / (tmoy + 237.3))
        / ((tmoy + 237.3) ** 2)
    )

    # ga = 0.34 * max(u, 0.001)

    u2 = u * (4.87 / np.log(67.8 * 10 - 5.42))

    n1 = 0.408 * delta * net_radiation
    n2 = gamma * (37 / (tmoy + 273)) * u2 * vpd
    d = delta + gamma * (1 + 0.34 * u2)

    # Return E
    return (n1 + n2) / (d)

# %% ../nbs/00_climate_utils.ipynb 18
def calculate_radiation_diurnal_pattern(
    time_of_the_day: List[
        int
    ],  # a numeric value of vector indicating the time of the day (in seconds)
    day_length: int,  # value indicating the duration of the day (in seconds)
) -> float:
    "Calculated diurnal pattern of temperature assuming a sinusoidal pattern with T = tmin at sunrise and T = (tmin + tmax)/2 at sunset. From sunset to sunrise follows a linear trend"

    # calculate_radiation_diurnal_pattern ---------------------------------------

    # sunrise
    ws = (day_length / 3600.0) * (pi / 24.0)
    w = ws - (time_of_the_day / day_length) * (ws * 2.0)

    prop = ((pi / 24.0) * (cos(w) - cos(ws))) / (sin(ws) - ws * cos(ws))

    return prop / 3600.0

# %% ../nbs/00_climate_utils.ipynb 21
def calculate_temperature_diurnal_pattern(
    time_of_the_day: List[
        int
    ],  # a numeric value of vector indicating the time of the day (in seconds from sunrise)
    day_length: int,  # value indicating the duration of the day (in seconds)
    tmin: float,  # Unknown parameter definition
    tmax: float,  # Unknown parameter definition
    tmin_prev: float,  # Unknown parameter definition
    tmax_prev: float,  # Unknown parameter definition
    tmin_next: float,  # Unknown parameter definition
) -> float:
    "Calculated diurnal pattern of temperature assuming a sinusoidal pattern with T = tmin at sunrise and T = (tmin+tmax)/2 at sunset. From sunset to sunrise follows a linear trend"

    # calculate_temperature_diurnal_pattern -------------------------------------

    if time_of_the_day < 0.0 or time_of_the_day > day_length:
        tfin = 86400.0 - day_length

        if time_of_the_day < 0.0:
            time_of_the_day = time_of_the_day + 86400.0 - day_length

            # Return Temp
            return 0.5 * (tmax_prev + tmin_prev) * (
                1.0 - (time_of_the_day / tfin)
            ) + tmin * (time_of_the_day / tfin)

        else:
            time_of_the_day = time_of_the_day - day_length

            # Return Temp
            return 0.5 * (tmax + tmin) * (
                1.0 - (time_of_the_day / tfin)
            ) + tmin_next * (time_of_the_day / tfin)

    else:
        ct = cos(1.5 * pi * time_of_the_day / day_length)

    # Return Temp
    return 0.5 * (tmin + tmax - (tmax - tmin) * ct)

# %% ../nbs/00_climate_utils.ipynb 22
def calculate_rh_diurnal_pattern(
    temperature: float,  # Unknown parameter definition
    rhmin: float,  # Unknown parameter definition
    rhmax: float,  # Unknown parameter definition
    tmin: float,  # Unknown parameter definition
    tmax: float,  # Unknown parameter definition
) -> float:
    "Calculate diurnal pattern of relative humidity from temperature"

    # calculate rh diurnal pattern ----------------------------------------------
    return rhmax + ((temperature - tmin) / (tmax - tmin)) * (rhmin - rhmax)

# %% ../nbs/00_climate_utils.ipynb 23
def ppfd_umol_to_rg_watt(
    ppfd: float,  # Photosynthetic photon flux density (umol.m-2.s-1)
    j_to_mol: float = 4.6,  # Conversion factor
    frac_par: float = 0.5,  # Function of solar rdiation that is photosynthetically active radiation (PAR)
) -> float:
    "Convert ppfd (umol) to rg (watt)"

    # calculate Global radiation (rg)(W/m2) -------------------------------------
    rg = ppfd / frac_par / j_to_mol
    return rg

# %% ../nbs/00_climate_utils.ipynb 24
def rg_watt_to_ppfd_umol(
    rg: float,  # Global radiation (W/m2)
    j_to_mol: float = 4.6,  # Conversion factor
    frac_par: float = 0.5,  # Function of solar rdiation that is photosynthetically active radiation (PAR)
) -> float:
    "Convert rg (watt) to ppfd (umol)"

    # calculate Photosynthetic photon flux density (umol.m-2.s-1) ---------------

    return rg * frac_par * j_to_mol

# %% ../nbs/00_climate_utils.ipynb 25
def rg_convertions(
    rg_watts: float = None,  # instantaneous radiation (watt)
    rg_mj: float = None,  # instantaneous radiation (in Mega Jule?)
    nhours: float = None,  # Unknown parameter definition
) -> float:
    "Convert instantaneous radiation in watt to dialy cumulative radiation in MJ (MJ.day-1)"

    if rg_watts is not None and rg_mj is None:
        print("Conversion of rg from watts to Mega Jules")

        # Conversion from watts to Mega Jules
        return rg_watts * 0.0864

    if rg_mj is not None and rg_watts is None and nhours is None:
        print("Conversion of rg from Mega Jules to Watts")

        # Conversion from Mega Jules to watts
        return rg_mj * (1 / 0.0864)

    if rg_mj is not None and rg_watts is None and nhours is not None:
        print("Conversion of rg from Mega Jules to Watts/hour")

        # Conversion from Mega Jules to watts/hour
        return rg_mj * (10**6 / (nhours * 3600))

    elif rg_mj is not None and rg_watts is not None:
        return print("Select one conversion rg_mj or rg_watts")

    else:
        print("No conversions performed")

# %% ../nbs/00_climate_utils.ipynb 31
def declination(doy: int):  # julian day (day of the year)
    "Calculate declination of sun (radians ? ) for a given julian day (DOY)"

    # Hervé's formula for solar declination

    # Sin(23.5*pi/180), 23.5 = Earth declination

    # Constans ------------------------------------------------------------------
    c1 = 0.398749068925246

    c2 = 2 * 3.1416 / 365

    # date of spring
    c3 = 80

    x = c1 * sin((doy - c3) * c2)  # ;

    # Return declination --------------------------------------------------------
    return atan(x / ((1 - x * x) ^ 0.5))
