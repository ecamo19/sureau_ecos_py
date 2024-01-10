# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/14_create_soil_parameters.ipynb.

# %% auto 0
__all__ = ['create_soil_parameters']

# %% ../nbs/14_create_soil_parameters.ipynb 3
import os
import warnings
import collections
import numpy as np
from pathlib import Path
from typing import Dict, List
from sureau_ecos_py.soil_utils import (
    read_soil_file,
    compute_theta_at_given_p_soil,
    compute_theta_at_given_p_soil_camp,
)
from .plant_utils import convert_f_cm3_to_v_mm
from .create_modeling_options import create_modeling_options

# %% ../nbs/14_create_soil_parameters.ipynb 4
def create_soil_parameters(
    file_path: Path,  # Path to a csv file containing parameter values i.e path/to/parameter_values.csv
    modeling_options: Dict = None,  # Dictionary created using the `create_modeling_options` function
    list_of_parameters: List = None,  # A list containing the necessary input parameters instead of reading them in file. Will only be used if 'file_path' arguement is not provided
    default_soil: bool = False,  # A logical value indicating whether a default soil should be used  to run tests
    offset_psoil: int = 0,  # A numerical value indicating the offset in soil water potential (MPa)
    psoil_at_field_capacity: int = -33,  # Unknown parameter definition
) -> Dict:  # Dictionary containing parameters
    "Create a Dictionary with soil parameters to run SureauR"


    # Assert parameters ---------------------------------------------------------

    # Make file_path and/or list_of_parameters are present

    # Raise error if file_path and list_of_parameters both are missing
    if file_path is None and list_of_parameters is None:
        raise ValueError(
            "Both file_path and list_of_parameters are missing, provide one of them"
        )

    # Raise error if file_path and list_of_parameters both are provided
    if file_path is not None and list_of_parameters is not None:
        raise ValueError(
            "Both file_path and list_of_parameters are provided, only one of these two arguments should be used"
        )

    # file_path

    # Make sure the file_path exist or is None
    assert file_path is None or os.path.exists(
        file_path
    ), f"Path: {file_path} not found, check spelling or set file_path = None"

    # offset_psoil
    assert (
        offset_psoil >= 0
    ), "offset_psoil must be an integer greater than or equal to 0"


    # psoil_at_field_capacity
    if modeling_options["pedo_transfer_formulation"] == 'campbell':
        assert (
             psoil_at_field_capacity < 0
        ), "psoil_at_field_capacity must be negative for campbell pedo_transfer_formulation"

    if modeling_options["pedo_transfer_formulation"] == 'vg':
        assert (
             psoil_at_field_capacity >= 0
        ), "psoil_at_field_capacity must be positive for vg pedo_transfer_formulation"


    # Create soil_params dictionary ---------------------------------------------
    soil_params = collections.defaultdict(list)

    # Add offset_psoil and psoil_at_field_capacity to dictionary

    print(f"There is an offset on Psoil of {offset_psoil} MPa")
    soil_params["offset_psoil"] = offset_psoil

    print(f"Psoil at field capacity = {psoil_at_field_capacity/1000} MPa")

    soil_params["psoil_at_field_capacity"] = psoil_at_field_capacity / 1000


    # default soil for tests ----------------------------------------------------
    if default_soil is True:
        warnings.warn("Default soil used (Van-Genuchten Formulation)")

        soil_params["pedo_transfer_formulation"] = "vg"

        # Rock fragment content
        soil_params["rock_fragment_content"] = np.array([40, 75, 90])

        # Soil depth
        soil_params["depth"] = np.array([0.3, 1, 4], dtype=float)

        # Add soil layer thickness
        soil_params["layer_thickness"] = np.array([0, 0, 0], dtype=float)

        # Layer 1
        soil_params["layer_thickness"][0] = soil_params["depth"][0]

        # Layer 2
        soil_params["layer_thickness"][1] = (
            soil_params["depth"][1] - soil_params["depth"][0]
        )

        # Layer 3
        soil_params["layer_thickness"][2] = (
            soil_params["depth"][2] - soil_params["depth"][1]
        )

        # g_soil0
        soil_params["g_soil0"] = 30

        # Van Genuchten parameters

        # Shape parameters of the relationship between soil water content and
        # soil water potential
        soil_params["alpha_vg"] = np.repeat(0.0035, 3)

        # Shape parameters of the relationship betwen soil water content and
        # soil water potential
        soil_params["n_vg"] = np.repeat(1.55, 3)

        # m parameters Van Genuchten equations
        soil_params["m"] = 1 - (1 / soil_params["n_vg"])

        # Shape parameters of the relationship between soil water content and
        # soil water potential
        soil_params["i_vg"] = np.repeat(0.5, 3)

        # Soil conductivity at saturation (mol/m/s/Mpa)
        soil_params["ksat_vg"] = np.repeat(1.69, 3)

        # Fraction of water at saturation capacity (cm3/cm3)
        soil_params["saturation_capacity_vg"] = np.repeat(0.5, 3)

        # Fraction of residual water (cm3/cm3)
        soil_params["residual_capacity_vg"] = np.repeat(0.1, 3)

        # add computation of wilting point
        soil_params["wilting_point"] = compute_theta_at_given_p_soil(
            psi_target=1.5,
            theta_res=soil_params["residual_capacity_vg"],
            theta_sat=soil_params["saturation_capacity_vg"],
            alpha_vg=soil_params["alpha_vg"],
            n_vg=soil_params["n_vg"],
        )
        # add computation of field capacity from functions
        soil_params["field_capacity"] = compute_theta_at_given_p_soil(
            psi_target=psoil_at_field_capacity,
            theta_res=soil_params["residual_capacity_vg"],
            theta_sat=soil_params["saturation_capacity_vg"],
            alpha_vg=soil_params["alpha_vg"],
            n_vg=soil_params["n_vg"],
        )
        # Soil offset_psoil
        soil_params["offset_psoil"] = offset_psoil

    # Soil characteristics ------------------------------------------------------
    if default_soil is False:
        if modeling_options is None:
            warnings.warn(
                "modeling_options' is missing. Van Genuchten used as default"
            )
            soil_params["pedo_transfer_formulation"] = "vg"

        if modeling_options is not None:
            print(
                f'You are using {modeling_options["pedo_transfer_formulation"]} pedotransfer formulation'
            )

            # Get pedo_transfer_formulation
            soil_params["pedo_transfer_formulation"] = modeling_options[
                "pedo_transfer_formulation"
            ]

        # Read soil file from csv data frame
        if file_path is not None:
            soil_params_csv_file = read_soil_file(file_path, modeling_options)

        # Read list_of_parameters
        if list_of_parameters is not None:
            print("This option has not been implemented yet")
            # soil_params_csv_file = list_of_parameters


        # set soil parameters that are independent of the Pedo-tranfert
        # formulation

        # Add soil depths
        soil_params["soil_depths"] = np.array(
            [
                soil_params_csv_file["depth_1"],
                soil_params_csv_file["depth_2"],
                soil_params_csv_file["depth_3"],
            ]
        )

        # Add soil layer thickness
        soil_params["layer_thickness"] = np.array([0, 0, 0], dtype=float)

        # Layer 1
        soil_params["layer_thickness"][0] = soil_params["soil_depths"][0]

        # Layer 2
        soil_params["layer_thickness"][1] = (
            soil_params["soil_depths"][1] - soil_params["soil_depths"][0]
        )

        # Layer 3
        soil_params["layer_thickness"][2] = (
            soil_params["soil_depths"][2] - soil_params["soil_depths"][1]
        )

        # g_soil
        soil_params["g_soil_0"] = soil_params_csv_file["g_soil_0"]

        # Add rock fragment content
        soil_params["rock_fragment_content"] = np.array(
            [
                soil_params_csv_file["rfc_1"],
                soil_params_csv_file["rfc_2"],
                soil_params_csv_file["rfc_3"],
            ]
        )

        # Add soil params for vg formulation ------------------------------------
        if soil_params["pedo_transfer_formulation"] == "vg":
            # Shape parameters of the relationship between soil water content and
            # soil water potential

            # Shape parameter 1
            soil_params["alpha_vg"] = np.repeat(
                soil_params_csv_file["alpha_vg"], 3
            )

            # Shape parameter 2
            soil_params["n_vg"] = np.repeat(soil_params_csv_file["n_vg"], 3)

            # Shape parameter 3
            soil_params["i_vg"] = np.repeat(soil_params_csv_file["i_vg"], 3)

            # Soil conductivity at saturation (mol/m/s/Mpa)
            soil_params["ksat_vg"] = np.repeat(
                soil_params_csv_file["ksat_vg"], 3
            )

            # Fraction of water at saturation capacity (cm3/cm3)
            soil_params["saturation_capacity_vg"] = np.repeat(
                soil_params_csv_file["saturation_capacity_vg"], 3
            )

            # Fraction of residual water (cm3/cm3)
            soil_params["residual_capacity_vg"] = np.repeat(
                soil_params_csv_file["residual_capacity_vg"], 3
            )

            # Add computation of wilting point
            soil_params["wilting_point"] = compute_theta_at_given_p_soil(
                psi_target=1.5,
                theta_res=soil_params_csv_file["residual_capacity_vg"],
                theta_sat=soil_params_csv_file["saturation_capacity_vg"],
                alpha_vg=soil_params_csv_file["alpha_vg"],
                n_vg=soil_params_csv_file["n_vg"],
            )

            # Add computation of field capacity from functions
            soil_params["field_capacity"] = compute_theta_at_given_p_soil(
                psi_target=psoil_at_field_capacity,
                theta_res=soil_params_csv_file["residual_capacity_vg"],
                theta_sat=soil_params_csv_file["saturation_capacity_vg"],
                alpha_vg=soil_params_csv_file["alpha_vg"],
                n_vg=soil_params_csv_file["n_vg"],
            )

            # Add v_field_capacity
            soil_params["v_field_capacity"] = convert_f_cm3_to_v_mm(
                x=soil_params["field_capacity"],
                rock_fragment_content=soil_params["rock_fragment_content"],
                layer_thickness=soil_params["layer_thickness"],
            )

            # Add v_saturation_capacity_vg
            soil_params["v_saturation_capacity_vg"] = convert_f_cm3_to_v_mm(
                x=soil_params["saturation_capacity_vg"],
                rock_fragment_content=soil_params["rock_fragment_content"],
                layer_thickness=soil_params["layer_thickness"],
            )
            # Add v_residual_capacity_vg
            soil_params["v_residual_capacity_vg"] = convert_f_cm3_to_v_mm(
                x=soil_params["residual_capacity_vg"],
                rock_fragment_content=soil_params["rock_fragment_content"],
                layer_thickness=soil_params["layer_thickness"],
            )

            # Add v_wilting_point
            soil_params["v_wilting_point"] = convert_f_cm3_to_v_mm(
                x=soil_params["wilting_point"],
                rock_fragment_content=soil_params["rock_fragment_content"],
                layer_thickness=soil_params["layer_thickness"],
            )

            # Duplicate v_saturation_capacity, Don't know why
            soil_params["v_saturation_capacity"] = soil_params[
                "v_saturation_capacity_vg"
            ]

            # For diagnostic, Unknown reason why
            soil_params["v_soil_storage_capacity_wilt"] = np.sum(
                soil_params["v_field_capacity"]
            ) - np.sum(soil_params["v_wilting_point"])
            soil_params["v_soil_storage_capacity_res"] = np.sum(
                soil_params["v_field_capacity"]
            ) - np.sum(soil_params["v_residual_capacity_vg"])
            soil_params["v_soil_storage_capacity"] = soil_params[
                "v_soil_storage_capacity_wilt"
            ]

            print(
                f'Available water capacity Wilting: {soil_params["v_soil_storage_capacity_wilt"]} mm'
            )
            print(
                f'Available water capacity Residual: {soil_params["v_soil_storage_capacity_res"]} mm'
            )

            print('Can soil_params["v_soil_storage_capacity"] be negative?? Ask')

        # Add soil params for campbell formulation ------------------------------
        if soil_params["pedo_transfer_formulation"] == "campbell":
            # Shape parameters of the relationship between soil water content and
            # soil water potential

            # Shape parameter 1
            soil_params["b_campbell"] = np.repeat(
                soil_params_csv_file["b_camp"], 3
            )

            # Shape parameter 2
            soil_params["psie"] = np.repeat(soil_params_csv_file["psie"], 3)

            # Soil conductivity at saturation (mol/m/s/Mpa)
            # Value not repeated 3 times as the ksat_vg param
            soil_params["ksat_campbell"] = soil_params_csv_file["ksat_campbell"]

            # Fraction of water at saturation capacity (cm3/cm3)
            soil_params["saturation_capacity_campbell"] = np.repeat(
                soil_params_csv_file["saturation_capacity_campbell"], 3
            )

            # Add wilting point
            soil_params["wilting_point"] = compute_theta_at_given_p_soil_camp(
                psi_target=-1.5,
                theta_sat=soil_params["saturation_capacity_campbell"],
                psie=soil_params["psie"],
                b_camp=soil_params["b_campbell"],
            )
            # Add field capacity
            soil_params["field_capacity"] = compute_theta_at_given_p_soil_camp(
                psi_target=soil_params["psoil_at_field_capacity"],
                theta_sat=soil_params["saturation_capacity_campbell"],
                psie=soil_params["psie"],
                b_camp=soil_params["b_campbell"],
            )
            # Add residual capacity camp,Fraction of residual water  (cm3/cm3)
            soil_params[
                "residual_capacity_campbell"
            ] = compute_theta_at_given_p_soil_camp(
                psi_target=-100,
                theta_sat=soil_params["saturation_capacity_campbell"],
                psie=soil_params["psie"],
                b_camp=soil_params["b_campbell"],
            )

            # Water values

            # Add v_field_capacity
            soil_params["v_field_capacity"] = convert_f_cm3_to_v_mm(
                x=soil_params["field_capacity"],
                rock_fragment_content=soil_params["rock_fragment_content"],
                layer_thickness=soil_params["layer_thickness"],
            )
            # Add v_saturation_capacity_campbell
            soil_params[
                "v_saturation_capacity_campbell"
            ] = convert_f_cm3_to_v_mm(
                x=soil_params["saturation_capacity_campbell"],
                rock_fragment_content=soil_params["rock_fragment_content"],
                layer_thickness=soil_params["layer_thickness"],
            )

            # Add v_residual_capacity_campbell
            soil_params["v_residual_capacity_campbell"] = convert_f_cm3_to_v_mm(
                x=soil_params["residual_capacity_campbell"],
                rock_fragment_content=soil_params["rock_fragment_content"],
                layer_thickness=soil_params["layer_thickness"],
            )

            # Add v_wilting_point
            soil_params["v_wilting_point"] = convert_f_cm3_to_v_mm(
                x=soil_params["wilting_point"],
                rock_fragment_content=soil_params["rock_fragment_content"],
                layer_thickness=soil_params["layer_thickness"],
            )

            # Duplicate v_saturation_capacity, Don't know why
            soil_params["v_saturation_capacity"] = soil_params[
                "v_saturation_capacity_campbell"
            ]

            # For diagnostic (TAW)
            soil_params["v_soil_storage_capacity_wilt_campbell"] = np.sum(
                soil_params["v_field_capacity"]
            ) - np.sum(soil_params["v_wilting_point"])

            soil_params["v_soil_storage_capacity_res_campbell"] = np.sum(
                soil_params["v_field_capacity"]
            ) - np.sum(soil_params["v_residual_capacity_campbell"])

            soil_params["v_soil_storage_capacity"] = soil_params[
                "v_soil_storage_capacity_wilt_campbell"
            ]

            print(
                f'Available water capacity Wilting: {soil_params["v_soil_storage_capacity_wilt_campbell"]} mm'
            )
            print(
                f'Available water capacity Residual: {soil_params["v_soil_storage_capacity_res_campbell"]} mm'
            )

            print('Can soil_params["v_soil_storage_capacity"] be negative?? Ask')

    return soil_params
