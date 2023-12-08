# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/09_9_read_soil_file.ipynb.

# %% auto 0
__all__ = ['SoilFile', 'read_soil_file']

# %% ../nbs/09_9_read_soil_file.ipynb 3
from pathlib import Path
import os
import pandas as pd
from typing import Dict
from .create_modeling_options import create_modeling_options
import numpy as np
import collections
from pandera.typing import Series
import pandera as pa

# %% ../nbs/09_9_read_soil_file.ipynb 4
# This class was created for validating the input dataframe
# If the data don't follow the structure specified the function will fail


class SoilFile(pa.SchemaModel):
    "Schema for validating the input soil parameter file"

    Name: Series[str] = pa.Field(description="Parameter names")
    Value: Series[float] = pa.Field(description="Parameter values")


def read_soil_file(
    file_path: Path,  # Path to a csv file containing parameter values i.e path/to/file_name.csv
    modeling_options: Dict = None,  # Dictionary created using the `create_modeling_options` function
    sep: str = ";",  # CSV file separator can be ',' or ';'
) -> Dict:
    "Function for reading a data frame containing information about soil characteristics"

    # Make sure that modeling_options is a dictionary ---------------------------
    assert isinstance(
        modeling_options, Dict
    ), f"modeling_options must be a dictionary not a {type(modeling_options)}"

    # Read data frame -----------------------------------------------------------
    if os.path.exists(file_path):
        # Read file
        soil_data = pd.read_csv(file_path, header=0, sep=sep)

        # Raise error if soil data don't follow the SoilFile Schema
        SoilFile.validate(soil_data)

    else:
        print(f"file: {file_path}, does not exist, check presence or spelling")

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
                f"{each_parameter} not provided in input soil parameter file, check presence or spelling\n"
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
