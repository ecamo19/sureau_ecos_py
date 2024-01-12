# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/02_plant_utils.ipynb.

# %% auto 0
__all__ = ['rs_comp', 'turgor_comp', 'compute_turgor_from_psi', 'osmo_comp', 'psi_total_symp_comp', 'stomatal_regulation_turgor',
           'plc_comp', 'plc_prime_comp', 'gs_curve', 'compute_gmin', 'compute_emin', 'compute_dfmc',
           'distribute_conductances', 'compute_g_crown', 'convert_flux_from_mmolm2s_to_mm',
           'convert_flux_from_mm_to_mmolm2s', 'calculate_ebound_mm_granier', 'calculate_ebound_granier',
           'convert_f_cm3_to_v_mm', 'compute_tleaf', 'VegetationFile', 'read_vegetation_file']

# %% ../nbs/02_plant_utils.ipynb 3
import os
import warnings
import collections
import numpy as np
import pandas as pd
import pandera as pa
from typing import Dict
from typing import List
from pathlib import Path
from pandera.typing import Series
from .create_modeling_options import create_modeling_options

# %% ../nbs/02_plant_utils.ipynb 4
def rs_comp(
    pi_ft: float,  # Osmotic potential at full turgor (MPa)
    e_symp: float,  # Modulus of elastoicoty of the Symplasm (MPa/%)
    p_min: float,  # Unknown parameter definition
) -> float:
    "Compute Rs from pmin (resolution from Bartlet et al 2012 EcolLett and email Herve Cochard 19/06/2015)"
    return max(
        (
            -1 * (p_min + pi_ft - e_symp)
            - np.sqrt((p_min + pi_ft - e_symp) ** 2 + 4 * (p_min * e_symp))
        )
        / (2 * e_symp),
        1 - pi_ft / p_min,
    )

# %% ../nbs/02_plant_utils.ipynb 5
def turgor_comp(
    pi_ft: float,  # Osmotic potential at full turgor (MPa)
    e_symp: float,  # Modulus of elastoicoty of the Symplasm (MPa/%)
    r_stemp: float,  # Unknown parameter definition
) -> float:
    "Turgor pressure"
    return -pi_ft - e_symp * r_stemp

# %% ../nbs/02_plant_utils.ipynb 6
def compute_turgor_from_psi(
    pi_ft: float,  # Osmotic potential at full turgor (MPa)
    e_symp: float,  # Modulus of elastoicoty of the Symplasm (MPa/%)
    psi: List,  # List of Water potential of the organ (MPa)
) -> np.array:
    "Computes Turgor pressure from Pressure-Volume curves parameters and water potential"

    # Make sure psi is a list
    assert isinstance(
        psi, List
    ), f"psi must be a List with float values (i.e [1] or [1,2,..]) not a {type(psi)}"

    # Compute symplasm relative water deficit (rwd) from each psi value

    # Generates an array of length psi
    rwd_1 = (
        -1 * (np.array(psi) + pi_ft - e_symp)
        - np.sqrt(
            (np.array(psi) + pi_ft - e_symp) ** 2 + 4 * (np.array(psi) * e_symp)
        )
    ) / (2 * e_symp)

    # Generates an array of length psi
    rwd_2 = 1 - pi_ft / np.array(psi)

    # Create empty array for storing values
    rs_array = np.zeros(0, dtype=float)

    for each_rwd_1, each_rwd_2 in zip(rwd_1, rwd_2):
        # Compare relative_water_deficit_1 and relative_water_deficit_2 and store
        # the largest one into array
        rs_array = np.append(rs_array, max(each_rwd_1, each_rwd_2))

    # Calculate turgor
    turgor_array = -pi_ft - e_symp * rs_array

    # Replace negative values inside the turgor array with 0's
    turgor_array[(turgor_array < 0)] = 0

    return turgor_array

# %% ../nbs/02_plant_utils.ipynb 11
# Osmotic potential
def osmo_comp(
    pi_ft: float,  # Osmotic potential at full turgor (MPa)
    r_stemp: float,  # Unknown parameter definition
) -> float:
    "Compute osmotic potential"
    return pi_ft / (1 - r_stemp)

# %% ../nbs/02_plant_utils.ipynb 12
def psi_total_symp_comp(
    pi_ft: float,  # Osmotic potential at full turgor (MPa)
    e_symp: float,  # Modulus of elastoicoty of the Symplasm (MPa/%)
    r_stemp: float,  # Unknown parameter definition
) -> float:
    "Compute Total potential"
    turgor = turgor_comp(pi_ft=pi_ft, e_symp=e_symp, r_stemp=r_stemp)

    osmo = osmo_comp(pi_ft=pi_ft, r_stemp=r_stemp)

    return turgor + osmo

# %% ../nbs/02_plant_utils.ipynb 13
def stomatal_regulation_turgor(
    turgor_pressure: float,  # Turgor pressure
    max_turgor_pressure: float,  # Maximum turgor pressure,
    e_max: float,  # Unknown parameter definition
    e_cuti: float,  # Residual Transpiration
) -> np.array:
    "This function computes stomatal regulation if stomatal closure is limited (linearly) by turgor pressure"

    # Create np.array for storing values
    stomatal_reg_array = np.zeros(0, dtype=float)

    # Get the lowest value
    tr = min((e_max * turgor_pressure / max_turgor_pressure), e_max)

    # Append to array
    stomatal_reg_array = np.append(stomatal_reg_array, max(tr, 0))

    # Horrible line but I don't know how to improve it
    # Don't know the meaning of 0 + e_cuti
    horror_line = min(max(max(tr, 0) + e_cuti, 0 + e_cuti), e_max)

    stomatal_reg_array = np.append(stomatal_reg_array, horror_line)

    return stomatal_reg_array

# %% ../nbs/02_plant_utils.ipynb 16
def plc_comp(
    p_min: float,  # Unknown parameter definition
    slope: float,  # Unknown parameter definition
    p50: float,  # Unknown parameter definition
) -> float:
    "Compute Percentage loss of conductivity"

    return 100 / (1 + np.exp(slope / 25 * (p_min - p50)))

# %% ../nbs/02_plant_utils.ipynb 17
def plc_prime_comp(
    plc: float,  # Computed using the `plc_comp` function
    slope: float,  # Unknown parameter definition
) -> float:
    "This function computes PLC Prime from PLC current value"

    return -slope / 25 * plc / 100 * (1 - plc / 100)

# %% ../nbs/02_plant_utils.ipynb 18
def gs_curve(
    x: float,  # Unknown parameter definition
    slope_gs: float,  # Unknown parameter definition
    p50_gs: float,  # Unknown parameter definition
    psi_start_closing: float,  # Unknown parameter definition
    psi_close: float,  # Unknown parameter definition
    pi_ft: float,  # Osmotic potential at full turgor (MPa)
    e_symp: float,  # Modulus of elastoicoty of the Symplasm (MPa/%)
    turgor_pressure_at_gs_max: float,  # Unknown parameter definition
    gs_max: float,  # Unknown parameter definition
    transpiration_model: str = ["jarvis", "granier"],  # Transpiration model type
    stomatal_reg_formulation: str = [
        "sigmoid",
        "piecewise_linear",
        "turgor",
    ],  # type of regulation to be used for stomatal response to leaf symplasmic water potential, either `sigmoid` or `piecewise_linear`
) -> float:
    "To obtain plots of the gs regulation curve"

    assert (
        stomatal_reg_formulation
        in [
            "sigmoid",
            "piecewise_linear",
            "turgor",
        ]
    ), f'{stomatal_reg_formulation} not a valid option, choose "sigmoid", "piecewise_linear" or "turgor" '

    assert transpiration_model in [
        "jarvis",
        "granier",
    ], f'{transpiration_model} not a valid option, choose  "jarvis" or "granier"'

    if transpiration_model == "granier":
        gs_max = 1

    if stomatal_reg_formulation == "sigmoid":
        pl_gs = 1 / (1 + np.exp(slope_gs / 25 * (x - p50_gs)))
        regul_fact = 1 - pl_gs

    if stomatal_reg_formulation == "piecewise_linear":
        regul_fact = (x - psi_close) / (psi_start_closing - psi_close)

        if regul_fact < 0:
            regul_fact = 0

        elif regul_fact > 1:
            regul_fact = 1

        else:
            print(
                "Original code don't take into account regul_fact between 0 and 1"
            )

    if stomatal_reg_formulation == "turgor":
        # Only Rs1 is needed above TLP
        rs1 = (
            -1 * (x + pi_ft - e_symp)
            - np.sqrt((x + pi_ft - e_symp) ** 2 + 4 * (x * e_symp))
        ) / (2 * e_symp)

        # turgor loss point variable created but not used
        turgor_loss_point = (pi_ft * e_symp) / (pi_ft + e_symp)

        turgor = -pi_ft - e_symp * rs1
        regul_fact < -turgor / turgor_pressure_at_gs_max

        if regul_fact < 0:
            regul_fact = 0

        elif regul_fact > 1:
            regul_fact = 1

        else:
            print(
                "Original code don't take into account regul_fact between 0 and 1"
            )

    return regul_fact * gs_max

# %% ../nbs/02_plant_utils.ipynb 19
def compute_gmin(
    leaf_temp: float,  # Temperature of the leaf (degC)
    gmin_20: float,  # leaf conductance at 20 degC
    t_phase: float,  # Temperature for phase transition of gmin
    q10_1: float,  # Q10 values for g_min= f(T) below T_phase
    q10_2: float,  # Q10 values for g_cuti = f(T) above T_phase
    gmin_temp_off=False,  # Unknown parameter definition
) -> float:
    "Calculate minimum conductance (gmin) following Cochard et al. (2019)"

    print("original R code have a ambiguous gmin_temp_off specification")
    if gmin_temp_off is False:
        if leaf_temp <= t_phase:
            gmin = gmin_20 * q10_1 ** ((leaf_temp - 20) / 10)
            return gmin

        elif leaf_temp > t_phase:
            gmin = (
                gmin_20
                * q10_1 ** ((t_phase - 20) / 10)
                * q10_2 ** ((leaf_temp - t_phase) / 10)
            )
            return gmin

    else:
        gmin = gmin_20
        return gmin

# %% ../nbs/02_plant_utils.ipynb 20
def compute_emin(
    gmin: float,  # minimum conductance
    vpd: float,  # Vapor Pressure Deficit  (kPa)
    g_bl: float,  # Unknown parameter definition
    g_crown: float,  # Unknown parameter definition. Use `compute_g_crown`
    air_pressure: float = 101.3,  # Surface air pressure (kPa)
) -> float:
    "Calculate minimum transpiration (emin)"

    gmin_tot = 1 / (1 / gmin + 1 / g_bl + 1 / g_crown)
    return gmin_tot * (vpd / air_pressure)

# %% ../nbs/02_plant_utils.ipynb 21
def compute_dfmc(
    vpd: float,  # Vapor pressure deficit (kPA)
    fm0=5.43,  # Minimum fuel moisture content (% dry weight)
    fm1=52.91,  # Maximum fuel moisture content (% dry weight)
    m=0.64,  # Rate of decay
) -> float:  # Fuel moisture content (% dry weight)
    "Compute dead fuel moisture content from VPD following De Dios et al. (2015)"
    return fm0 + fm1 * np.exp(-m * vpd)

# %% ../nbs/02_plant_utils.ipynb 22
def distribute_conductances(
    k_plant_init: float,  # Conductance of the plant from root to leaf
    ri: float,  # Root distribution within the soil layers.
    frac_leaf_sym: float = 0.4,  # Proportion of k_plant_init assigned to the leaf (apoplasm to symplasm pathway)
) -> Dict:
    "Calcultate hydraulic conductances in the different portions of the plant (trunk, leaf and root) according to predetermined rules"

    frac_rt = (2 / 3) * (1 - frac_leaf_sym)

    fract_tl = (1 / 3) * (1 - frac_leaf_sym)

    k_rsapo_init = 1 / (frac_rt / k_plant_init) * ri

    k_slapo_init = 1 / (fract_tl / k_plant_init)

    k_lsym_init = 1 / (frac_leaf_sym / k_plant_init)

    # TODO: AJOUTE UN CALCUL DES CONDUCTANCE ICI POUR CHECK DU CALCUL? e.g.:
    # k_PlantInit <-  1/ (1 /sum(k_RSApoInit) + 1/k_SLApoInit + 1/k_LSymInit)

    dictionary = {
        "k_slapo_init": k_slapo_init,
        "k_lsym_init": k_lsym_init,
        "k_rsapo_init": k_rsapo_init,
        "k_plant_init": k_plant_init,
    }

    return collections.defaultdict(list, dictionary)

# %% ../nbs/02_plant_utils.ipynb 25
def compute_g_crown(
    g_crown0: float,  # Unknown parameter definition
    wind_speed: float,  # Unknown parameter definition
) -> float:
    "Calcultate g_crown"

    # to avoid very high conductance values
    wind_speed = max(0.1, wind_speed)

    return g_crown0 * wind_speed**0.6

# %% ../nbs/02_plant_utils.ipynb 26
def convert_flux_from_mmolm2s_to_mm(
    x: float,  # The amount of water in mm (L.m-2soil)
    time_step: float,  # Time step (in hours)
    lai: float,  # Leaf area index of the stand (m2leaf.m-2soil)
) -> float:
    "Convert an instantaneous flux in mmol.m-2Leaf.s-1 to a amount in mm (L.m2soil) over a defined time period"
    return x * (lai * time_step * 3600 * 18) / 10**6

# %% ../nbs/02_plant_utils.ipynb 27
def convert_flux_from_mm_to_mmolm2s(
    x: float,  # The amount of water in mm (L.m-2soil)
    time_step: float,  # Time step (in hours)
    lai: float,  # Leaf area index of the stand (m2leaf.m-2soil)
) -> float:
    "Convert flux in L.m-2soil to an instantaneous flux in mmol/m-2leaf.s-1 over a defined time period"
    if lai > 0:
        return (10**6 * x) / (lai * time_step * 3600 * 18)

    else:
        return 0

# %% ../nbs/02_plant_utils.ipynb 28
def calculate_ebound_mm_granier(
    etp: float,  # Unknown parameter definition
    lai: float,  # Leaf area index of the stand (m2leaf.m-2soil)
    a: float = -0.006,  # Unknown parameter definition
    b: float = 0.134,  # Unknown parameter definition
    c: float = 0,  # Unknown parameter definition
) -> float:
    "No description found in R source code"

    # Get the maximum value
    # Example of np.maximum: np.maximum(5, [1,2,6]) == array([5, 5, 6])
    return np.maximum(0, etp * (a * lai**2 + b * lai + c))

# %% ../nbs/02_plant_utils.ipynb 29
def calculate_ebound_granier(
    etp: float,  # Unknown parameter definition
    lai: float,  # Leaf area index of the stand (m2leaf.m-2soil)
    time_step: float,  # Time step (in hours)
) -> float:
    "No description found in R source code"

    ebound_mm = calculate_ebound_mm_granier(etp=etp, lai=lai)

    return convert_flux_from_mm_to_mmolm2s(
        x=ebound_mm, time_step=time_step, lai=lai
    )

# %% ../nbs/02_plant_utils.ipynb 32
def convert_f_cm3_to_v_mm(
    x: float,  # Soil value to be converted (in m3.m-3)
    rock_fragment_content: float,  # Rock fragment content of the soil layer (%)
    layer_thickness: float,  # Thickness of the soil layer (in m)
) -> float:  # y soil parameter in mm
    "Convert soil parameter from from cm3.cm-3 to mm according to thickness and rock fragment content"
    return x * (1 - (rock_fragment_content / 100)) * layer_thickness * 1000

# %% ../nbs/02_plant_utils.ipynb 33
def compute_tleaf(
    t_air: float,  # Air temperature (degC)
    par: float,  # Unknown parameter definition
    potential_par: float,  # Unknown parameter definition. Calculated using `potential_par` function?
    wind_speed: float,  # Unknown parameter definition (m/s)
    relative_humidity: int,  # Air relative_humidity(%)
    gs: float,  # Stomatal conductance
    g_cuti: float,  # leaf conductance
    e_inst: float,  # Unknown parameter definition
    psi_leaf: float,  # Unknown parameter definition
    leaf_size: float = 50,  # Characteristic dimension from vegetation params in mm i.e. 1 (pine needle) to 3000 (banana leaf)
    leaf_angle: int = 45,  # Leaf angle (depuis le plan horizontal : 0-90 deg)
    turn_off_eb: bool = False,  # Unknown parameter definition. Tleaf Energy balance?
    transpiration_model: str = ["jarvis", "granier"],  # Transpiration model type
) -> Dict:  # Dictionary with parameters
    "Compute leaf temperature and Vapour Pressure deficit"

    # Assert parameters -----------------------------------------------------
    assert (
        0 <= relative_humidity <= 100
    ), "relative_humidity must be a value between 0 and 100"

    assert (
        -40 <= t_air <= 70
    ), "Unrealistic air temperature, value must be a value between -40 and 70"

    assert isinstance(
        turn_off_eb, bool
    ), "turn_off_eb must be boolean (True or False)"

    assert 0 <= leaf_angle <= 90, "leaf_angle must be a value between 0 and 90"

    assert transpiration_model in [
        "jarvis",
        "granier",
    ], f'{transpiration_model} not a valid option, choose  "jarvis" or "granier"'

    # Constants -------------------------------------------------------------

    # Force minimum wind speed to avoid excessive heating
    wind_speed = np.maximum(wind_speed, 0.1)

    # Calculate short-wave radiation (W/m2) # from µmol/m2/s to Watts/m2
    short_wave_radiation = par * 0.5495

    # Absorptance to short_wave_radiation (%)
    abs_short_wave_radiation = 0.5

    # # Unknown meaning of g_flat
    g_flat = 0.00662

    # Coefficient in rbl equation m
    g_cyl = 0.00403

    # # Unknown meaning of j_flat
    j_flat = 0.5

    # Coefficient in rbl equation  none
    j_cyl = 0.6

    # Emissivity none
    emiss_leaf = 0.97

    # Stefan-Boltzman constant   W m-2 K-4
    stefan_boltzman_const = 5.6704e-8

    # Density of dry air kg/m3
    dry_air_density = 1.292

    # Heat capacity of dry air  J kg-1 K-1
    heat_capacity_dry_air = 1010

    # Psychrometric constant kPa K-1
    psychro_constant = 0.066

    # Coefficient in esat equation kPa
    e_sat_coeff_a = 0.61121

    # Coefficient in esat equation none
    e_sat_coeff_b = 17.502

    # Coefficient in esat equation °C
    e_sat_coeff_z = 240.97

    # Original comment found in the source code
    # VARAIBLE CALCULEES
    # rst  #  stomatal resistance s m-1 (not needed)
    # esat #  saturation vapor pressure    kPa
    # ea   # water vapor pressure of the air    kPa
    # em_air # air emissivity
    # s   # slope of esat/T curve    kPa oC-1
    # SWRabs #   absorbed short-wave radiation    W m-2
    # LWRin  # incoming long-wave radiation    W m-2
    # LWRouti # isothermal outgoing long-wave radiation    W m-2
    # Rni # isothermal net radiation    W m-2
    # rr # radiative resistance    s m-1
    # rblr # boundary-layer + radiative resistance    s m-1
    # ym #  modified psychrometric constant    kPa K-1
    # rbl # leaf boundary-layer resistance    s m-1
    # Delta_T  # leaf-to-air temperature difference    degC
    # Tleaf, Tleaf_NonLinear # leaf temperature    degC

    # Create cloud_cover var
    if potential_par > 0:
        cloud_cover = par / potential_par

    else:
        cloud_cover = 0

    if cloud_cover > 1:
        cloud_cover = 1

    # ; #kPa  Unknown meaning of e_sat
    e_sat = e_sat_coeff_a * np.exp(
        e_sat_coeff_b * t_air / (t_air + e_sat_coeff_z)
    )

    # Unknown meaning of ea
    ea = e_sat * (relative_humidity / 100)

    # Unknown meaning of s
    s = e_sat * e_sat_coeff_b * e_sat_coeff_z / ((t_air + e_sat_coeff_z) ** 2)

    #  Unknown meaning of em_air
    em_air = (1 - 0.84 * cloud_cover) * 1.31 * (
        (10 * ea / (t_air + 273.15)) ** 0.14285714
    ) + 0.84 * cloud_cover

    # Update VPD with esat and ea (why?)
    vpd_x = e_sat - ea

    # Bilan radiatif --------------------------------------------------------

    # Radiation absorbed by leaves
    swr_abs = (
        abs_short_wave_radiation
        * np.cos(leaf_angle * 3.1416 / 180)
        * short_wave_radiation
    )

    # Incoming long-wave radiation (W m-2) for clear and cloudy sky
    lwr_in = em_air * stefan_boltzman_const * (t_air + 273.15) ** 4

    # Outcoming long-wave radiation (W m-2) for clear and cloudy sky
    lwr_outi = emiss_leaf * stefan_boltzman_const * (t_air + 273.15) ** 4

    # isothermal net radiation
    rni = swr_abs + lwr_in - lwr_outi

    # Radiative resistance
    rad_res = (
        dry_air_density
        * heat_capacity_dry_air
        / (4 * emiss_leaf * stefan_boltzman_const * (t_air + 273.15) ** 3)
    )

    # Boundary layer resistance
    if leaf_size > 3:
        # Unknown meaning of rbl
        rbl = 1 / (
            1.5
            * g_flat
            * ((wind_speed**j_flat) / ((leaf_size / 1000) ** (1 - j_flat)))
        )

    else:
        # a needle, formula for a cylinder. I am assuming that this comment
        # belongs to the following line

        # Unknown meaning of rbl
        rbl = 1 / (
            1.5
            * g_cyl
            * ((wind_speed**j_cyl) / ((leaf_size / 1000) ** (1 - j_cyl)))
        )  # A flat leaf if > 3mm

    # leaf boundary layer conductance in mmol/s/m2
    g_bl = 1 / rbl * 1000 * 40

    # Unknown meaning of rblr
    rblr = 1 / (1 / rbl + 1 / rad_res)

    # Include the gs term into the energy balance
    if transpiration_model == "jarvis":
        if (gs + g_cuti) > 0:
            # Unknown meaning of rst
            rst = 1 / (gs + g_cuti) * 1000 * 40

        else:
            # Unknown meaning of rst
            rst = 9999.99

    if transpiration_model == "granier":
        # Unknown meaning of g
        g = e_inst / vpd_x * 101.3

        if g > 0:
            # Unknown meaning of rbl
            rst = 1 / (g) * 1000 * 40

        else:
            # Unknown meaning of rbl
            rst = 9999.99

    # Unknown meaning of ym
    ym = psychro_constant * (rst / rblr)

    # Compute Tleaf with linear approximation -------------------------------
    delta_t = (
        ym * rni * rblr / (dry_air_density * heat_capacity_dry_air) - vpd_x
    ) / (s + ym)

    t_leaf = t_air + delta_t

    # Create a copy of t_leaf. I don't understand why this is done
    # t_leaf_copy =  t_leaf

    # Saturation vapour water pressure at Tair in Pa from Buck's equation
    e_sat_air = 611.21 * np.exp(
        (18.678 - t_air / 234.5) * t_air / (257.14 + t_air)
    )

    # Vapour water pressure at Tair and RHair
    e_air = e_sat_air * relative_humidity / 100

    # Calculate VPD air
    vpd_air = (e_sat_air - e_air) / 1000

    # Saturation vapour water pressure at Tair in Pa from Buck's equation
    e_sat_leaf = 611.21 * np.exp(
        (18.678 - t_leaf / 234.5) * t_leaf / (257.14 + t_leaf)
    )

    # Unknown meaning of e
    e = e_sat_leaf * np.exp(psi_leaf * 2.16947115 / (t_leaf + 273.15))

    # effect of leaf water potential on e
    # vpd between leaf and air in kPa
    vpd_leaf = np.maximum(0, (e - e_air) / 1000)

    if turn_off_eb is False:
        vecres = collections.defaultdict(
            list,
            {
                "t_leaf": t_leaf,
                "g_bl": g_bl,
                "vpd_leaf": vpd_leaf,
                "vpd_air": vpd_air,
                "delta_t": delta_t,
            },
        )

    # If turn off energy balance Tleaf = Tair
    if turn_off_eb is True:
        vecres = np.array([t_air, g_bl, vpd_leaf, vpd_air])

        vecres = collections.defaultdict(
            list,
            {
                "t_air": t_air,
                "g_bl": g_bl,
                "vpd_leaf": vpd_leaf,
                "vpd_air": vpd_air,
            },
        )

    return vecres

# %% ../nbs/02_plant_utils.ipynb 37
class VegetationFile(pa.SchemaModel):
    "Schema for validating the input CSV spreadsheet with trait parameters."

    # setting commomn params for WB_veg (regardless of the options) -------------
    apofrac_leaf: Series[float] = pa.Field(
        description="Apoplasmic Fraction (Unitless) in leaves", coerce=True
    )
    apofrac_stem: Series[float] = pa.Field(
        description="Stem apoplasmic fraction of the wood water volume",
        coerce=True,
    )
    betarootprofile: Series[float] = pa.Field(
        description="Parameter for the distribution of roots in the soil (unitless??)",
        coerce=True,
    )
    canopystorageparam: Series[float] = pa.Field(
        description="Depth of water that can be retained by leaves and trunks per unit of leaf area index (l/m2leaf, used to compute the canopy water storage capacity as a function of LAI)",
        coerce=True,
    )
    c_lapoinit: Series[float] = pa.Field(
        description="Capacitance of the leaf apoplasm", coerce=True
    )
    c_sapoinit: Series[float] = pa.Field(
        description="Capacitance of the stem apoplasm", coerce=True
    )
    epsilonsym_leaf: Series[float] = pa.Field(
        description="Modulus of elasticity (MPa) in leaves", coerce=True
    )
    epsilonsym_stem: Series[float] = pa.Field(
        description="Modulus of elasticity of the stem symplasm", coerce=True
    )
    foliage: Series[str] = pa.Field(
        isin=["evergreen", "deciduous", "forced"], description="Vegetation type"
    )
    froottoleaf: Series[float] = pa.Field(
        description="Root to leaf ratio (unitless??)", coerce=True
    )
    ftrbtoleaf: Series[float] = pa.Field(
        description="No definition found", coerce=True
    )
    gmin20: Series[float] = pa.Field(
        description="Minimum conductance (gmin, mmol/m2leaf/s) at the reference temperature (same as cuticular conductance)",
        coerce=True,
    )
    gmin_s: Series[float] = pa.Field(
        description="Conductance (gmin) of the stem (same as k_plant??)",
        coerce=True,
    )
    k_ssyminit: Series[float] = pa.Field(
        description="No definition found", coerce=True
    )
    k: Series[float] = pa.Field(
        description="Light extinction coefficient (Unitless??) of the vegetation layer",
        coerce=True,
    )
    k_plantinit: Series[float] = pa.Field(
        description="Hydaulic conductance ( [mmol/MPa/s/m2leaf]) of the plant from soil to leaves",
        coerce=True,
    )
    ldmc: Series[float] = pa.Field(
        ge=0,
        description="Leaf dry matter content (mgMS/g) measured for fully watered leaves",
        coerce=True,
    )
    lma: Series[float] = pa.Field(
        description="Leaf mass per area (g/m2leaf)", coerce=True
    )
    p50_vc_leaf: Series[float] = pa.Field(
        description="Water potential (MPa) causing 50% Cavitation in the vulnerability curve",
        coerce=True,
    )
    p50_vc_stem: Series[float] = pa.Field(
        description="Water potential causing 50 % loss of stem hydraulic conductance",
        coerce=True,
    )
    pifullturgor_stem: Series[float] = pa.Field(
        description="Osmotic potential at full turgor of the stem symplasm",
        coerce=True,
    )
    pifullturgor_leaf: Series[float] = pa.Field(
        description="Osmotic Potentia (MPa) at full turgor in leaves",
        coerce=True,
    )
    q10_1_gmin: Series[float] = pa.Field(
        description="Q10 (unitless??) value for gmin = f(T) <= Tphase_gmin",
        coerce=True,
    )
    q10_2_gmin: Series[float] = pa.Field(
        description="Q10 unitless??) value for gmin = f(T)  > Tphase_gmin",
        coerce=True,
    )
    rootradius: Series[float] = pa.Field(
        description="radius of roots (m)", coerce=True
    )
    symfrac_stem: Series[float] = pa.Field(
        description="Stem symplasmic fraction of the wood water volume",
        coerce=True,
    )
    slope_vc_leaf: Series[float] = pa.Field(
        description="Slope (%/MPa) of the vulnerability curve", coerce=True
    )
    slope_vc_stem: Series[float] = pa.Field(
        description="Slope of rate of stem embolism spread at ψ50,S", coerce=True
    )
    tphase_gmin: Series[float] = pa.Field(
        description="Temperature for phase transition (degC) of minimum conductance",
        coerce=True,
    )
    vol_stem: Series[float] = pa.Field(
        description="Volume of tissue of the stem (includes the root, trunk and branches)",
        coerce=True,
    )


def read_vegetation_file(
    file_path: Path,  # Path to a csv file containing parameter values i.e path/to/file_name.csv
    modeling_options: Dict,  # Dictionary created using the `create_modeling_options` function
    sep: str = ";",  # CSV file separator can be ',' or ';'
) -> Dict:
    "Function for reading a data frame containing information about vegetation characteristics"

    # Assert parameters ---------------------------------------------------------

    # Make sure that modeling_options is a dictionary
    assert modeling_options is None or isinstance(
        modeling_options, Dict
    ), f"modeling_options must be a dictionary not a {type(modeling_options)}"

    # Make sure the file_path exist
    assert os.path.exists(
        file_path
    ), f"Path: {file_path} not found, check spelling or presence"

    # Read CSV data frame -------------------------------------------------------
    vegetation_csv_data = pd.read_csv(file_path, header=0, sep=sep)

    # Raise error if soil data don't follow the VegetationFile Schema
    VegetationFile.validate(vegetation_csv_data, lazy=True)

    # Remove the dots and numbers in column names. This is done for detecting
    # duplicated colnames since pandas reads columns with the same name as col1
    # col1.1, col1.2 etc
    vegetation_csv_data.columns = vegetation_csv_data.columns.str.replace(
        r"\.\d+", "", regex=True
    )

    # Raise error if duplicated coulmn names exists
    if len(vegetation_csv_data.columns) is not len(
        set(vegetation_csv_data.columns)
    ):
        duplicated_params = []

        # Save duplicated parameters into list
        for each_param, each_count in collections.Counter(
            vegetation_csv_data.columns
        ).items():
            if each_count > 1:
                duplicated_params.append(each_param)

        # Raise error
        raise ValueError(
            f"{duplicated_params} repeated several times in input dataframe. Please make sure that each column is unique"
        )

    # Create dictionary with params ---------------------------------------------
    # Reshape dataframe for converting it to a list
    vegetation_csv_data = pd.DataFrame(
        vegetation_csv_data.melt(ignore_index=True).reset_index()[
            ["variable", "value"]
        ]
    )

    # Transform data to a list and then create dictionary
    vegetation_parameters = collections.defaultdict(
        list,
        {
            each_cell[0]: each_cell[1]
            for each_cell in vegetation_csv_data.values.tolist()
        },
    )

    # Add frac_leaf_sym if not provided -----------------------------------------
    if "frac_leaf_sym" not in vegetation_parameters:
        print("frac_leaf_sym' set to 0.4")
        vegetation_parameters["frac_leaf_sym"] = 0.4

    # Read modeling_options dictionary ------------------------------------------

    # stomatal_reg_formulation traits
    # Set parameters for stomatal regulation of vegetation according to the type
    # of stomatal regulation
    if modeling_options["stomatal_reg_formulation"] == "piecewise_linear":
        stomatal_regulation_params = ["psi_start_closing", "psi_close"]

    elif modeling_options["stomatal_reg_formulation"] == "sigmoid":
        stomatal_regulation_params = ["p12_gs", "p88_gs"]

    elif modeling_options["stomatal_reg_formulation"] == "turgor":
        stomatal_regulation_params = ["turgor_pressure_at_gs_max"]

    # Check if traits stomatal_reg_formulation are missing in the
    # vegetation_parameters
    for each_stomatal_regulation_param in stomatal_regulation_params:
        if each_stomatal_regulation_param not in vegetation_parameters:
            raise ValueError(
                f'Trait {each_stomatal_regulation_param} for {modeling_options["stomatal_reg_formulation"]} stomatal_reg_formulation is missing. Add it to the CSV file'
            )

    # transpiration_model traits
    if modeling_options["transpiration_model"] == "jarvis":
        transpiration_model_params = [
            "g_crown0",
            "gs_max",
            "gs_night",
            "jarvis_par",
            "tgs_sens",
            "tgs_optim",
        ]

    elif modeling_options["transpiration_model"] == "granier":
        raise ValueError(print("granier option have been not implemented yet"))

    # Check if traits for modeling_options["transpiration_model"] are missing in
    # the vegetation_parameters
    for each_transpiration_model_param in transpiration_model_params:
        if each_transpiration_model_param not in vegetation_parameters:
            raise ValueError(
                f'Trait {each_transpiration_model_param} for {modeling_options["transpiration_model"]} transpiration model is missing. Add it to the CSV file'
            )

    # Foliage traits
    if vegetation_parameters["foliage"] == "deciduous":
        foliage_params = ["t_base", "f_crit", "day_start", "nbday_lai"]

    elif vegetation_parameters["foliage"] == "forced":
        foliage_params = ["day_start_forced", "day_end_forced", "nbday_lai"]

    else:
        warnings.warn("Foliage evergreen has no params")
        foliage_params = []

    # Check if traits for foliage type are missing in the vegetation_parameters
    for each_foliage_param in foliage_params:
        if each_foliage_param not in vegetation_parameters:
            raise ValueError(
                f'Trait {each_foliage_param} for {vegetation_parameters["foliage"]} foliage is missing. Add it to the CSV file'
            )

    # ETP parameters for PT or PM
    if modeling_options["etp_formulation"] == "pt":
        if "pt_coeff" not in vegetation_parameters:
            raise ValueError(
                'pt_coeff for "pt" etp_formulation is missing. Add it to the CSV file'
            )

    elif modeling_options["etp_formulation"] == "penman":
        raise ValueError(print("penman option have been not implemented yet"))

    return vegetation_parameters
