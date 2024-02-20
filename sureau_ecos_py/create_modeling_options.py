# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/10_create_modeling_options.ipynb.

# %% auto 0
__all__ = ['create_modeling_options']

# %% ../nbs/10_create_modeling_options.ipynb 3
import numpy as np
import collections
from typing import Dict

# %% ../nbs/10_create_modeling_options.ipynb 4
def create_modeling_options(
    time_step_for_evapo: int = 1,  # time step for the main evapotranspiration loop. Should be one of the following 1,2,4,6,8
    reset_swc: bool = False,  # Boolean indicating whether soil layers should be refilled at the beginning of each year
    avoid_water_soil_transfer: bool = True,  # Yet to be implemented. Boolean indicating whether the transfer of water between soil layers should be avoided by disconnecting the soil layers that get refilled from the soil-plant system
    soil_evapo: bool = True,  # Boolean indicating whether soil evaporation should be simulated (True) or not (False)
    defoliation: bool = False,  # Boolean indicating whether trees should loose leaves when`occurs.cavitation` occurs of the above part of plant. Defoliation starts only when PLC_Leaf > 10% .
    threshold_mortality: int = 90,  # Percentange value indicating the percentage loss of conductivity above which the plant is considered dead and simulation stops for the current year.
    transpiration_model: str = ['jarvis', 'granier'],  # Transpiration model type
    etp_formulation: str = 'pt',  # Formulation of ETP to be used, either `pt` (Priestley-Taylor) or `penman` (Penmman)
    rn_formulation: str = 'linacre',  # method to be used to calculate net radiation from global radiation, either `linacre`  or 'linear' (the linear method is not implemnted yet)
    pedo_transfer_formulation: str = [
        'vg',
        'campbell',
    ],  # Unknown parameter definition
    constant_climate: bool = False,  # Boolian indicating whether the climate should be considered constant or not
    comp_options_for_evapo: str = [  # Option to be used for the loops  (voir avec Francois)
        'normal',
        'accurate',
        'fast',
        'custom',
    ],
    custom_small_time_step_in_sec: int = 600,  # Time step in seconds. Use if comp_options_for_evapo is set to `custom`
    lcav: int = 1,  # Unknown parameter definition
    scav: int = 1,  # Unknown parameter definition
    eord: int = 1,  # Unknown parameter definition
    numerical_scheme: str = [  # Unknown parameter definition
        'implicit',
        'semi-implicit',
        'explicit',
    ],
    stomatal_reg_formulation: str = [  # Type of regulation to be used for stomatal response to leaf symplasmic water potential, either `sigmoid` or `piecewise_linear`
        'sigmoid',
        'piecewise_linear',
        'turgor',
    ],
    print_prog: bool = True,  # Unknown parameter definition
) -> Dict:
    'Create a dictionary containing modeling options that can be used as an input in run.SurEauR'

    # Validate the function parameter types -------------------------------------

    assert isinstance(reset_swc, bool), 'reset_swc must be a bool (True/False)'

    assert isinstance(
        avoid_water_soil_transfer, bool
    ), 'avoid_water_soil_transfer must be a bool (True/False)'

    assert isinstance(
        constant_climate, bool
    ), 'constant_climate must be a bool (True/False)'

    assert isinstance(
        defoliation, bool
    ), 'defoliation must be a bool (True/False)'

    assert isinstance(soil_evapo, bool), 'soil_evapo must be a bool (True/False)'

    assert (
        isinstance(threshold_mortality, int) and 50 <= threshold_mortality <= 100
    ), 'threshold_mortality must be a integer between 50 and 100'

    assert etp_formulation in [
        'pt',
        'penman',
    ], f'{etp_formulation} not a valid option, choose "pt" or "penman"'

    assert rn_formulation in [
        'linacre',
        'linear',
    ], f'{rn_formulation} not a valid option, choose "linacre" or "linear"'

    assert (
        comp_options_for_evapo
        in [
            'normal',
            'accurate',
            'fast',
            'custom',
        ]
    ), f'{comp_options_for_evapo} not a valid option, choose "normal", "accurate", "fast" or "custom" '

    assert (
        stomatal_reg_formulation
        in [
            'sigmoid',
            'piecewise_linear',
            'turgor',
        ]
    ), f'{stomatal_reg_formulation} not a valid option, choose "sigmoid", "piecewise_linear" or "turgor" '

    assert transpiration_model in [
        'jarvis',
        'granier',
    ], f'{transpiration_model} not a valid option, choose  "jarvis" or "granier"'

    assert (
        numerical_scheme
        in [
            'implicit',
            'semi-implicit',
            'explicit',
        ]
    ), f'{numerical_scheme} not a valid option, choose  "implicit", "semi-implicit" or "explicit"'

    assert (
        pedo_transfer_formulation
        in [
            'vg',
            'campbell',
        ]
    ), f'{pedo_transfer_formulation} not a valid option, choose "vg" or "campbell" '

    assert time_step_for_evapo in [
        None,
        1,
        2,
        4,
        6,
    ], 'time_step_for_evap must be equal to 1, 2, 4, 6 or None'

    # Create array with time steps for the evapo --------------------------------
    if time_step_for_evapo is None:
        time = np.array([0, 6, 12, 14, 16, 22])

    elif time_step_for_evapo is not None:
        time = np.arange(0, 24, time_step_for_evapo, dtype=int)

    # Create comp_options -------------------------------------------------------

    if time_step_for_evapo is not None:
        comp_options = collections.defaultdict(list)

        # Every 10min, 6min, 3min, 1min
        if comp_options_for_evapo == 'normal':
            # Add key value pairs to the comp_dictionary
            comp_options['numerical_scheme'] = numerical_scheme
            comp_options['nsmalltimesteps'] = time_step_for_evapo * np.array(
                [6, 10, 20, 60]
            )
            comp_options['lsym'] = 1
            comp_options['ssym'] = 1
            comp_options['clapo'] = 1
            comp_options['ctapo'] = 1
            comp_options['eord'] = eord
            comp_options['lcav'] = lcav
            comp_options['scav'] = scav

        # every 10 seconds
        if comp_options_for_evapo == 'accurate':
            comp_options['numerical_scheme'] = numerical_scheme
            comp_options['nsmalltimesteps'] = time_step_for_evapo * np.array(600)
            comp_options['lsym'] = 1
            comp_options['ssym'] = 1
            comp_options['clapo'] = 1
            comp_options['ctapo'] = 1
            comp_options['eord'] = eord
            comp_options['lcav'] = lcav
            comp_options['scav'] = scav

        # every hours, every 10 min
        if comp_options_for_evapo == 'fast':
            comp_options['numerical_scheme'] = numerical_scheme
            comp_options['nsmalltimesteps'] = time_step_for_evapo * np.array(
                1, 6
            )
            comp_options['lsym'] = 1
            comp_options['ssym'] = 1
            comp_options['clapo'] = 1
            comp_options['ctapo'] = 1
            comp_options['eord'] = eord
            comp_options['lcav'] = lcav
            comp_options['scav'] = scav

        # every customSmallTimeStepInSec
        if comp_options_for_evapo == 'custom':
            comp_options['numerical_scheme'] = numerical_scheme
            comp_options['nsmalltimesteps'] = (
                time_step_for_evapo * 3600 / custom_small_time_step_in_sec
            )
            comp_options['lsym'] = 1
            comp_options['ssym'] = 1
            comp_options['clapo'] = 1
            comp_options['ctapo'] = 1
            comp_options['eord'] = eord
            comp_options['lcav'] = lcav
            comp_options['scav'] = scav

        # Create empty dictionary for storing modeling options ------------------
        modeling_options = collections.defaultdict(list)

        # Append parameters to dictionary
        modeling_options['constant_climate'] = constant_climate
        modeling_options['etp_formulation'] = etp_formulation
        modeling_options['rn_formulation'] = rn_formulation
        modeling_options['pedo_transfer_formulation'] = pedo_transfer_formulation
        modeling_options['time_step_for_evapo'] = time_step_for_evapo
        modeling_options['time'] = time
        modeling_options['reset_swc'] = reset_swc
        modeling_options['avoid_water_soil_transfer'] = avoid_water_soil_transfer

        modeling_options['comp_options'] = comp_options

        modeling_options['stomatal_reg_formulation'] = stomatal_reg_formulation
        modeling_options['soil_evapo'] = soil_evapo
        modeling_options['defoliation'] = defoliation
        modeling_options['threshold_mortality'] = threshold_mortality
        modeling_options['transpiration_model'] = transpiration_model
        modeling_options['print_prog'] = print_prog
        modeling_options['stop_simulation_dead_plant'] = print_prog

    return modeling_options
