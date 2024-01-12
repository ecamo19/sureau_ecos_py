# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/01_soil_utils.ipynb.

# %% auto 0
__all__ = ['compute_b', 'compute_b_gc', 'compute_k_soil', 'compute_k_soil_camp', 'compute_p_soil', 'compute_p_soil_camp',
           'compute_theta_at_given_p_soil', 'compute_theta_at_given_p_soil_camp', 'SoilFile', 'read_soil_file']

# %% ../nbs/01_soil_utils.ipynb 3
import os
import operator
import numpy as np
import collections
import pandas as pd
from math import pi
import pandera as pa
from typing import Dict
from pathlib import Path
from pandera.typing import Series
from .create_modeling_options import create_modeling_options

# %% ../nbs/01_soil_utils.ipynb 4
def compute_b(
    lv: float,  # length of fine root per unit volume
) -> float:
    "Calculate b used to compute the B of the Gardnar-Cowen model"

    return 1 / np.sqrt(pi * lv)

# %% ../nbs/01_soil_utils.ipynb 5
def compute_b_gc(
    la: float,  # Unknown parameter definition
    b: float,  # Unknown parameter definition
    root_radius: float,  # Calculated using the `compute_b` function
) -> float:
    "Calculate B Gardner cowen thhe scaling factor for soil conductance"

    return la * 2 * pi / np.log(b / root_radius)

# %% ../nbs/01_soil_utils.ipynb 6
def compute_k_soil(
    rew: float,  # Unknown parameter definition
    i_vg: float,  # Unknown parameter definition
    n_vg: float,  # Unknown parameter definition
    k_sat_vg: float,  # Unknown parameter definition
    b_gc: float,  # Calculated using the `compute_b_gc` function
) -> float:
    # Create empty dict for storing params --------------------------------------
    k_soil_parameters = collections.defaultdict(list)

    # Compute k_soil ------------------------------------------------------------
    m = 1 - (1 / n_vg)

    k_soil = k_sat_vg * rew ** (i_vg) * (1 - (1 - rew ** (1 / m)) ** m) ** 2

    k_soil_gc = 1000 * b_gc * k_soil

    # Append to dictionary ------------------------------------------------------
    k_soil_parameters["k_soil"] = k_soil
    k_soil_parameters["k_soil_gc"] = k_soil_gc

    return k_soil_parameters

# %% ../nbs/01_soil_utils.ipynb 7
def compute_k_soil_camp(
    sws: float,  # Unknown parameter definition
    tsc: float,  # Unknown parameter definition
    b_camp: float,  # Unknown parameter definition
    k_sat_campbell: float,  # Unknown parameter definition
) -> float:
    return k_sat_campbell * (sws / tsc) ** (-b_camp * 2 + 2)

# %% ../nbs/01_soil_utils.ipynb 8
def compute_p_soil(
    rew: float,  # Unknown parameter definition
    alpha_vg: float,  # Unknown parameter definition
    n_vg: float,  # Unknown parameter definition
) -> float:
    m = 1 - (1 / n_vg)

    # diviser par 10000 pour passer de cm à MPa
    return -1 * ((((1 / rew) ** (1 / m)) - 1) ** (1 / n_vg)) / alpha_vg / 10000

# %% ../nbs/01_soil_utils.ipynb 9
def compute_p_soil_camp(
    sws: float,  # Unknown parameter definition
    tsc: float,  # Unknown parameter definition
    b_camp: float,  # Unknown parameter definition
    psie: float,  # Unknown parameter definition
) -> float:
    return -1 * (psie * ((sws / tsc) ** -b_camp))

# %% ../nbs/01_soil_utils.ipynb 10
def compute_theta_at_given_p_soil(
    psi_target: float,  # Unknown parameter definition
    theta_res: float,  # Unknown parameter definition
    theta_sat: float,  # Unknown parameter definition
    alpha_vg: float,  # Unknown parameter definition
    n_vg: float,  # Unknown parameter definition
) -> float:
    # Assert that values are positive.
    # Using np.testing instead of assert because parameters can be np.arrays OR
    # single values (i.e. 1). assert only works when params are always one
    # type
    # Solution from:
    # https://stackoverflow.com/questions/45987962/why-arent-there-numpy-testing-assert-array-greater-assert-array-less-equal-as

    np.testing.assert_array_compare(
        operator.__gt__,
        np.array(psi_target),
        0,
        err_msg="\nError: psi_target values must be greater than 0\n",
    )

    return theta_res + (theta_sat - theta_res) / (
        1 + (alpha_vg * psi_target * 10000) ** n_vg
    ) ** (1 - 1 / n_vg)

# %% ../nbs/01_soil_utils.ipynb 14
def compute_theta_at_given_p_soil_camp(
    theta_sat: float,  # Unknown parameter definition
    psi_target: float,  # Unknown parameter definition
    psie: float,  # Unknown parameter definition
    b_camp: float,  # Unknown parameter definition
) -> float:
    # Assert that values are negative.
    # Using np.testing instead of assert because parameters can be np.arrays OR
    # single values (i.e. 1). assert only works when params are always one
    # type

    np.testing.assert_array_less(
        np.array(psie), 0, err_msg="\nError: psie values must be negative\n"
    )

    np.testing.assert_array_less(
        np.array(b_camp), 0, err_msg="\nError: b_camp values must be negative\n"
    )

    np.testing.assert_array_less(
        np.array(psi_target),
        0,
        err_msg="\nError: psi_target values must be negative\n",
    )

    return theta_sat * (psi_target / psie) ** (1 / b_camp)

# %% ../nbs/01_soil_utils.ipynb 18
# This class was created for validating the input dataframe
# If the data don't follow the structure specified the function will fail
class SoilFile(pa.SchemaModel):
    "Schema for validating the input soil parameter file"

    Name: Series[str] = pa.Field(description="Parameter names")
    Value: Series[float] = pa.Field(description="Parameter values")

    # Added for making sure that it only accepts the columns specified above
    class Config:
        strict = True


def read_soil_file(
    file_path: Path,  # Path to a csv file containing parameter values i.e path/to/file_name.csv
    modeling_options: Dict = None,  # Dictionary created using the `create_modeling_options` function
    sep: str = ";",  # CSV file separator can be ',' or ';'
) -> Dict:
    "Function for reading a data frame containing information about soil characteristics"

    # Assert parameters ---------------------------------------------------------
    # Make sure that modeling_options is a dictionary
    assert isinstance(
        modeling_options, Dict
    ), f"modeling_options must be a dictionary not a {type(modeling_options)}"

    # Make sure the file_path exist
    assert os.path.exists(
        file_path
    ), f"Path: {file_path} not found, check spelling"

    # Read data frame -----------------------------------------------------------

    soil_data = pd.read_csv(file_path, header=0, sep=sep)

    # Raise error if soil data don't follow the SoilFile Schema
    SoilFile.validate(soil_data, lazy=True)

    # Setting common parameters for WB_soil (regardless of the options) ---------
    if modeling_options["pedo_transfer_formulation"] == "vg":
        # 14 params
        params = np.array(
            [
                "rfc_1",
                "rfc_2",
                "rfc_3",
                "depth_1",
                "depth_2",
                "depth_3",
                "wilting_point",
                "alpha_vg",
                "n_vg",
                "i_vg",
                "ksat_vg",
                "saturation_capacity_vg",
                "residual_capacity_vg",
                "g_soil_0",
            ],
            dtype=object,
        )

    if modeling_options["pedo_transfer_formulation"] == "campbell":
        # 12 params
        params = np.array(
            [
                "rfc_1",
                "rfc_2",
                "rfc_3",
                "depth_1",
                "depth_2",
                "depth_3",
                "wilting_point",
                "ksat_campbell",
                "saturation_capacity_campbell",
                "b_camp",
                "psie",
                "g_soil_0",
            ],
            dtype=object,
        )

    # Get only the required params ----------------------------------------------
    soil_data = soil_data[soil_data["Name"].isin(params)]

    # Make sure that no parameters are missing (12 or 14) -----------------------
    for each_parameter in params:
        # Raise error if a parameter is missing from params
        if each_parameter not in np.array(soil_data["Name"]):
            raise ValueError(
                f"{each_parameter} not provided in input soil parameter CSV file, check presence or spelling\n"
            )

    # Make sure there are no duplicate parameters -------------------------------
    if len(soil_data["Name"]) is not len(set(soil_data["Name"])):
        raise ValueError(
            "Parameter repeated several times in input soil parameter file"
        )

    # Get values in the dataframe and get rid of the colnames. Save everything
    # in to a list for later convert it to a Dictionary
    soil_data = soil_data.values.tolist()

    return collections.defaultdict(list, dict(soil_data))
