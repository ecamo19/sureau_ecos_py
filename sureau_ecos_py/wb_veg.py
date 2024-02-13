# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/17_wb_veg.ipynb.

# %% auto 0
__all__ = ['new_wb_veg', 'compute_pheno_wb_veg', 'update_capacitances_apo_and_sym_wb_veg', 'update_lai_and_stocks_wb_veg',
           'compute_interception_wb_veg', 'compute_water_storage_wb_veg']

# %% ../nbs/17_wb_veg.ipynb 3
import warnings
import collections
import numpy as np
from typing import Dict
from sureau_ecos_py.plant_utils import (
    plc_comp,
    rs_comp,
    compute_dfmc
)

from sureau_ecos_py.create_vegetation_parameters import (
    create_vegetation_parameters
)
from .create_modeling_options import create_modeling_options
from .create_soil_parameters import create_soil_parameters
from .create_stand_parameters import create_stand_parameters

# %% ../nbs/17_wb_veg.ipynb 4
def new_wb_veg(veg_params:Dict # Dictionary created using the `create_vegetation_parameters` function
) -> Dict:

    "Create an object wb_veg from veg_params"

    # Assert parameters ---------------------------------------------------------
    assert (
        isinstance(veg_params, Dict)
    ), f"veg_param must be a Dictionary not a {type(veg_params)}"


    # Add params to wb_veg dictionary -------------------------------------------

    # Create Empty dict
    wb_veg = collections.defaultdict(list)

    # Add veg_params
    wb_veg["params"] = veg_params

    # Add Stem and Leaf turgor point
    wb_veg['params']['psi_tlp_leaf'] = wb_veg["params"]["pifullturgor_leaf"]*wb_veg["params"]["epsilonsym_leaf"]/(wb_veg["params"]["pifullturgor_leaf"]+wb_veg["params"]["epsilonsym_leaf"])
    wb_veg['params']['psi_tlp_stem'] = wb_veg["params"]["pifullturgor_stem"]*wb_veg["params"]["epsilonsym_stem"]/(wb_veg["params"]["pifullturgor_stem"]+wb_veg["params"]["epsilonsym_stem"])

    # Add potentials
    wb_veg['psi_lapo'] = 0
    wb_veg['psi_sapo'] = 0
    wb_veg['psi_lsym'] = 0
    wb_veg['psi_ssym'] = 0

    # FP replaced "mem" by "cav" (when cavitation starts)
    wb_veg['psi_lapo_cav'] = 0
    wb_veg['psi_sapo_cav'] = 0
    wb_veg['psi_all_soil'] = 0

    # Conductance & capacitance (mmol/m2/s/MPa) Here on leaf area basis but they
    # are to be updated as a function symplasm conductance and leaf area hydraulic
    # conductances

    # constant value during simulation
    wb_veg["k_plant"] =  wb_veg["params"]["k_plant_init"]

    # constant value during simulation
    wb_veg["k_lsym"]  =  wb_veg["params"]["k_lsym_init"]

    # constant value during simulation
    wb_veg["k_ssym"]  =  wb_veg["params"]["k_ssyminit"]

    # Value is updated in compute_kplant_wb_veg
    wb_veg["k_rsapo"] =  np.nan

    # Value is updated in compute_kplant_wb_veg
    wb_veg["k_slapo"] =  np.nan

    # Conductance rhisophere for each soil layer
    wb_veg['k_soil_to_stem'] = np.array([np.nan, np.nan, np.nan], dtype=float)

    # Capacitances
    # Symplasm capacitance updated as a function of water content and Leaf area
    # (mmol/m2leaf/MPa) /updated in update.capacitancesSymAndApo()
    # (NM : 25/10/2021)

    wb_veg['c_lsym'] = np.nan
    wb_veg['c_sapo'] = np.nan

    # Leaf and canopy conductance

    # initialised at 0 to compute Tleaf on first time step considering gs = 0
    # and not NA s
    wb_veg['gmin'] = 0

    # Gmin for stem and branches
    wb_veg['gmin_s'] = wb_veg["params"]["gmin_s"]

    # TODO voir si y'a besoin d'initialiser
    # see if there is a need to initialize

    wb_veg['regul_fact'] = 0.01

    # TODO voir pour mettre tout en NA si TranspirationMod = 0
    # see to put everything in NA if TranspirationMod = 0

    wb_veg['gs_bound'] = np.nan

    # initialised to 0 to compute Tleaf on first time step considering gs = 0
    # and not NA
    wb_veg['gs_lim'] = 0
    wb_veg['gcanopy_bound'] = np.nan
    wb_veg['gcanopy_lim'] = np.nan
    wb_veg['g_bl'] = np.nan
    wb_veg['g_crown'] = np.nan

    # Fluxes
    wb_veg['e_prime'] = 0
    wb_veg['e_min'] = 0
    wb_veg['e_min_s'] = 0
    wb_veg['e_bound'] = 0
    wb_veg['e_lim'] = 0
    wb_veg['flux_soil_to_stem'] = np.zeros(3)
    wb_veg['transpiration_mm'] = 0
    wb_veg['e_min_mm'] = 0
    wb_veg['e_min_s_mm'] = 0

    # LAI and LAI-dependent variables
    wb_veg['lai_pheno'] = np.zeros(1)
    wb_veg['lai']      = np.zeros(1)
    wb_veg['canopy_storage_capacity'] = np.zeros(1)

    # rainfall and interception

    # precipitation (ppt) that reach the soil
    wb_veg['ppt_soil'] = 0

    # interceptedWater /quantite d'eau dans la canopee
    wb_veg['intercepted_water_amount'] = 0
    wb_veg['evaporation_intercepted'] = 0
    wb_veg['etpr'] = 0

    # defoliation // no defoliation (add an option to set defoliation due to
    # cavitation of the Plant Above)
    wb_veg['defoliation'] = 0
    wb_veg['lai_dead'] = 0

    # Cavitation
    # percent loss of conductivity in the leaf [%]
    wb_veg["plc_leaf"] = 0

    # percent loss of conductivity in the stem [%]
    wb_veg["plc_stem"] = 0

    # leaf temp
    wb_veg["leaf_temperature"] = np.nan

    # Pheno, parameters if deciduous
    if wb_veg["params"]["foliage"] == "deciduous":

        wb_veg['lai_pheno'] = 0

        # temmpeerature sum to determine budburst
        wb_veg['sum_temperature'] = 0

        # budburst date
        wb_veg['bud_burst_date'] = np.nan

        print("wb_veg params for deciduous forest created")
    else:
        print(f'wb_veg params for {wb_veg["params"]["foliage"]} created')

    # water storage in canopy

    # Fuel moisture content of the dead compartment (gH20/gMS)
    wb_veg['dfmc']     = np.nan

    # Live fuel moisture content of the apoplasmic compartment (gH20/gMS)
    wb_veg['lfmc_apo']  = np.nan

    # Live fuel moisture content of the apoplasmic compartment (gH20/gMS)
    wb_veg['lfmc_symp'] = np.nan

    # live fuel moisture content (gH20/gMS)
    wb_veg['lfmc']     = np.nan

    # Live Canopy dry matter [gMS/m2 soil]
    wb_veg['dm_live_canopy']  = np.nan

    # Dead Canopy dry matter [gMS/m2 soil]
    wb_veg['dm_dead_canopy']  = 0

    # Q leaf apo (mol/m2leaf)
    wb_veg['q_lapo_sat_mmol'] = 0
    wb_veg['q_lapo_sat_l'] = 0

    # Q stem apo (mol/m2leaf)
    wb_veg['q_sapo_sat_mmol'] = 0
    wb_veg['q_sapo_sat_l'] = 0

    # Q leaf symplasm (mol/m2leaf)
    wb_veg['q_lsym_sat_mmol'] = 0
    wb_veg['q_lsym_sat_l']    = 0

    # Q Stem symplasm (mol/m2leaf)
    wb_veg['q_ssym_sat_mmol'] = 0
    wb_veg['q_ssym_sat_l']    = 0

    # Q Stem and Leaf apo and symp in liter/kg TODO 13/08/2021: better in mmol?
    wb_veg['q_lapo_l'] = 0
    wb_veg['q_sapo_l'] = 0
    wb_veg['q_lsym_l'] = 0
    wb_veg['q_ssym_l'] = 0

    wb_veg['delta_q_lapo_mmol_diag'] = 0

    # Water from the cavitated part, term from equations 6 and 7 in the
    # SurEau-Ecos paper
    wb_veg['f_l_cav'] = 0
    wb_veg['f_s_cav'] = 0

    # Compute PLC

    # Leaf
    wb_veg['plc_leaf'] = plc_comp(psi = wb_veg['psi_lapo'],
                                  slope = wb_veg['params']['slope_vc_leaf'],
                                  p50 = wb_veg['params']['p50_vc_leaf']
                                  )
    # Stem
    wb_veg['plc_stem'] = plc_comp(psi = wb_veg['psi_sapo'],
                                  slope = wb_veg['params']['slope_vc_stem'],
                                  p50 = wb_veg['params']['p50_vc_stem']
                                  )


    return wb_veg


# %% ../nbs/17_wb_veg.ipynb 11
def compute_pheno_wb_veg(wb_veg:Dict, # Dictionary created using the `new_wb_veg` function
                         temperature:float, # daily tempeature  (degC)
                         day_of_year:int,
                         ) -> Dict:

    "Compute phenology and leaf area index (lai) for wb_veg dictionary in sureau_ecos_py"
    # Assert parameters ---------------------------------------------------------

    # wb_veg
    assert (
        isinstance(wb_veg, Dict)
    ), f"wb_veg must be a Dictionary not a {type(wb_veg)}"

    # Temperature
    assert (
        -40 <= temperature <= 70
    ), "Unrealistic air temperature, value must be a value between -40 and 70"

    # Day of year
    assert (
        isinstance(day_of_year, int) and 366 >= day_of_year >= 1
    ), "day_of_year must be a integer value between 1-366"


    # Set to initial parameters at the beggining of the year --------------------
    if day_of_year == 1:
        print(f'Setting initial parameters at the beggining of the year (day number:{day_of_year})')

        if wb_veg['params']['foliage'] ==  "evergreen":

            wb_veg['lai_pheno'] = wb_veg['params']['lai_max']

        elif wb_veg['params']['foliage'] ==  "deciduous":
            wb_veg['lai_pheno'] = 0
            wb_veg['sum_temperature'] = 0
            wb_veg['bud_burst_date'] = np.nan

        elif wb_veg['params']['foliage'] ==  "forced":
            wb_veg['lai_pheno'] = 0
            wb_veg['sum_temperature'] = 0
            wb_veg['bud_burst_date'] = np.nan

        else:
            raise ValueError(
                'Error in setting initial parameters in compute_pheno_wb_veg function'
        )

    # Setting parameters for deciduous vegetation -------------------------------
    if wb_veg['params']['foliage'] ==  "deciduous":

        # if no budburst
        if np.isnan(wb_veg['bud_burst_date']):

            if temperature > wb_veg['params']['t_base'] and day_of_year >= wb_veg['params']['day_start']:

                # Update sum_temperature if temp > t_base
                wb_veg['sum_temperature'] = wb_veg['sum_temperature'] + temperature

            elif wb_veg['sum_temperature'] > wb_veg['params']['f_crit']:
                wb_veg['bud_burst_date'] = day_of_year

            else:
                raise ValueError(
                'Error setting sum_temperature for deciduous vegetation in compute_pheno_wb_veg function'
                )

        # loss of leaves on day 270
        elif day_of_year >= 280:
            wb_veg['lai_pheno'] = np.maximum(0, wb_veg['lai'] - np.maximum(0, wb_veg['params']['lai_max']/wb_veg['params']['nbday_lai']))


        elif np.isnan(wb_veg['bud_burst_date']) is False:

            # if bud break and leaf construction period
            if day_of_year < wb_veg['bud_burst_date'] + wb_veg['params']['nbday_lai']:
                wb_veg['lai_pheno'] = wb_veg['lai_pheno'] + np.maximum(0, wb_veg['params']['lai_max']/wb_veg['params']['nbday_lai'])

            else:
                raise ValueError(
                    'Error setting lai_pheno for deciduous vegetation in compute_pheno_wb_veg function'
                )

        else:
            raise ValueError(
                'Error setting parameters for deciduous vegetation in compute_pheno_wb_veg function'
                )

    # Setting parameters for forced vegetation ----------------------------------
    if wb_veg['params']['foliage'] ==  "forced":

        # No bud_burst_date
        if np.isnan(wb_veg['bud_burst_date']):
            if day_of_year >= wb_veg['params']['day_start_forced']:
                wb_veg['bud_burst_date'] = day_of_year

            else:
                raise ValueError(
                    'Error setting bud_burst_date for forced vegetation in compute_pheno_wb_veg function'
                )

        #  Leaf shedding
        elif day_of_year >= wb_veg['params']['day_end_forced']:
            wb_veg['lai_pheno'] = np.maximum(0, wb_veg['lai'] - np.maximum(0, wb_veg['params']['lai_max']/wb_veg['params']['nbday_lai']))

        elif np.isnan(wb_veg['bud_burst_date']) is False:

            # After bud burst and before full LAI
            if day_of_year < wb_veg['bud_burst_date'] + wb_veg['params']['nbday_lai']:
                wb_veg['lai_pheno'] = wb_veg['lai_pheno'] + np.maximum(0, wb_veg['params']['lai_max']/wb_veg['params']['nbday_lai'])

            else:
                raise ValueError(
                    'Error setting lai_pheno for forced vegetation in compute_pheno_wb_veg function'
                    )

        else:
            raise ValueError(
                'Error setting parameters for forced vegetation in compute_pheno_wb_veg function'
                )


    return wb_veg

# %% ../nbs/17_wb_veg.ipynb 19
def update_capacitances_apo_and_sym_wb_veg(wb_veg:Dict, # Dictionary created using the `new_wb_veg` function
    ) -> Dict:

    "Update symplasmic plant capacitances for trunk and leaves"

    # Assert parameters ---------------------------------------------------------
    # wb_veg
    assert (
        isinstance(wb_veg, Dict)
    ), f"wb_veg must be a Dictionary not a {type(wb_veg)}"

    # NM minimal double to avoid-INF --------------------------------------------
    dbxmin = 1e-100

    # Compute the relative water content of the symplasm ------------------------
    rwc_lsym = 1 - rs_comp(pi_ft = wb_veg['params']['pifullturgor_leaf'],
                           e_symp = wb_veg['params']['epsilonsym_leaf'],
                           psi = wb_veg['psi_lsym'] - dbxmin
                           )
    # Compute the derivative of the relative water content of the symplasm
    if wb_veg['psi_lsym'] > wb_veg['params']['psi_tlp_leaf']:

        # FP derivative of -Pi0- Eps(1-RWC)+Pi0/RWC
        rwc_lsym_prime = rwc_lsym / (-wb_veg['params']['pifullturgor_leaf'] - wb_veg['psi_lsym'] - wb_veg['params']['epsilonsym_leaf'] + 2 * wb_veg['params']['epsilonsym_leaf'] * rwc_lsym)

    else:
        # FP derivative of Pi0/Psi
        rwc_lsym_prime = -wb_veg['params']['pifullturgor_leaf'] / wb_veg['psi_lsym']**2


    # Compute the leaf capacitance (mmol/MPa/m2_sol)
    if wb_veg['lai'] == 0:
        wb_veg['c_lsym'] = 0

    else:
        wb_veg['c_lsym'] = wb_veg['q_lsym_sat_mmol_per_leaf_area'] * rwc_lsym_prime

    # Stem symplasmic canopy water content --------------------------------------
    rwc_ssym = 1 - rs_comp(pi_ft = wb_veg['params']['pifullturgor_stem'],
                           e_symp = wb_veg['params']['epsilonsym_stem'],
                           psi = wb_veg['psi_ssym'] - dbxmin
                           )

    # Compute the derivative of the relative water content of the symplasm
    if wb_veg['psi_ssym'] > wb_veg['params']['psi_tlp_stem']:

        # FP derivative of -Pi0- Eps(1-RWC)+Pi0/RWC
        rwc_ssym_prime = rwc_ssym / (-wb_veg['params']['pifullturgor_stem'] - wb_veg['psi_ssym'] - wb_veg['params']['epsilonsym_stem'] + 2 * wb_veg['params']['epsilonsym_stem'] * rwc_ssym)

    else:
        # FP derivative of Pi0/Psi
        rwc_ssym_prime = -wb_veg['params']['pifullturgor_stem'] / wb_veg['psi_ssym']**2


    # Compute the capacitance (mmol/MPa/m2_leaf)
    # Stem capacitance per leaf area can only decrease with LAI
    # (cannot increase when LAI<1 )
    wb_veg['c_ssym'] = wb_veg['q_ssym_sat_mmol_per_leaf_area'] * rwc_ssym_prime

    # Add c_sapo and c_lapo -----------------------------------------------------
    wb_veg['c_sapo'] = wb_veg['params']['c_sapoinit']
    wb_veg['c_lapo'] = wb_veg['params']['c_lapoinit']

    return wb_veg


# %% ../nbs/17_wb_veg.ipynb 20
def update_lai_and_stocks_wb_veg(wb_veg:Dict, # Dictionary created using the `new_wb_veg` function
                                modeling_options: Dict, # Dictionary created using the `create_modeling_options` function
                                ) -> Dict:
    "Update leaf area index (LAI) as a function of lai_pheno and caviation and update LAI dependent parameters"

    # Assert parameters ---------------------------------------------------------

    # wb_veg
    assert (
        isinstance(wb_veg, Dict)
    ), f"wb_veg must be a Dictionary not a {type(wb_veg)}"


    # Make sure that modeling_options is a dictionary
    assert isinstance(
        modeling_options, Dict
    ), f"modeling_options must be a dictionary not a {type(modeling_options)}"

    # Set lai_dead parameter ----------------------------------------------------

    # Cavitation does not affect LAI
    if modeling_options['defoliation'] is False:
        wb_veg['lai_dead'] = 0

    # Cavitation does affect LAI
    elif modeling_options['defoliation'] is True:

        # Leaf shedding because of cavitation. Starts only if PLCabove > 10%
        if wb_veg['plc_leaf'] > 10:
            wb_veg['lai_dead'] = np.maximum(0, wb_veg['lai_pheno'] * wb_veg['plc_leaf'] / 100)

        else:
            wb_veg['lai_dead'] = 0
    else:
        raise ValueError(
                    'Error setting lai_dead in update_lai_and_stocks_wb_veg function'
                    )

    # Update lai ----------------------------------------------------------------
    wb_veg['lai'] = wb_veg['lai_pheno'] - wb_veg['lai_dead']

    # Update LAI-dependent variables --------------------------------------------
    wb_veg['fcc'] = (1 - np.exp(-wb_veg['params']['k'] * wb_veg['lai']))
    wb_veg['canopy_storage_capacity'] = 1.5 * wb_veg['lai']

    # Update water storing capacities of the dead and living canopy -------------
    # Water storing capacities of the living component
    wb_veg['dm_live_canopy'] = wb_veg['lai'] * wb_veg['params']['lma']

    # water storing capacities of the dead component
    wb_veg['dm_dead_canopy'] = wb_veg['lai_dead'] * wb_veg['params']['lma']

    # Calculate symplastic water content ----------------------------------------

    # Leaf symplastic water content in l/m2 (i.e. mm)
    wb_veg['q_lsym_sat_l'] = (1 / (wb_veg['params']['ldmc'] / 1000) - 1) * wb_veg['dm_live_canopy'] * (1 - wb_veg['params']['apofrac_leaf'])/1000

    wb_veg['q_lsym_sat_mmol'] = wb_veg['q_lsym_sat_l'] * 1000000/18

    # Calculate q_lsym_sat_mmol_per_leaf_area
    if wb_veg['lai'] == 0:
        wb_veg['q_lsym_sat_mmol_per_leaf_area'] = 0

    else:
        wb_veg['q_lsym_sat_mmol_per_leaf_area'] = wb_veg['q_lsym_sat_mmol'] / np.maximum(1, wb_veg['lai'])

    # Stem symplastic water content in l/m2 (i.e. mm)
    wb_veg['q_ssym_sat_l'] = wb_veg['params']['vol_stem'] * wb_veg['params']['symfrac_stem']

    wb_veg['q_ssym_sat_mmol'] = wb_veg['q_ssym_sat_l'] * 1000000/18

    # used max(1,LAI) to avoid that Q_SSym_sat_mmol_perLeafArea--> inF when
    # LAI --> 0 (limit imposed by computing water fluxes by m2leaf)
    wb_veg['q_ssym_sat_mmol_per_leaf_area'] = wb_veg['q_ssym_sat_mmol'] / np.maximum(1, wb_veg['lai'])


    # Calculate apoplastic water content ----------------------------------------
    # Leaf apoplastic water content in l/m2 (i.e. mm)
    wb_veg['q_lapo_sat_l'] = (1 / (wb_veg['params']['ldmc'] / 1000) - 1) * wb_veg['dm_live_canopy'] * (wb_veg['params']['apofrac_leaf'])/1000

    wb_veg['q_lapo_sat_mmol'] = wb_veg['q_lapo_sat_l'] * 1000000/18

    # Calculate q_lsym_sat_mmol_per_leaf_area
    if wb_veg['lai'] == 0:
        wb_veg['q_lapo_sat_mmol_per_leaf_area'] = 0

    else:
        wb_veg['q_lapo_sat_mmol_per_leaf_area'] = wb_veg['q_lapo_sat_mmol'] / np.maximum(1, wb_veg['lai'])

    # Stem apoplastic water content in l/m2 (i.e. mm)
    wb_veg['q_sapo_sat_l'] = wb_veg['params']['vol_stem'] * wb_veg['params']['apofrac_stem']

    wb_veg['q_sapo_sat_mmol'] = wb_veg['q_sapo_sat_l'] * 1000000/18

    # Used max(1,LAI) to avoid that Q_SApo_sat_mmol_perLeafArea--> inF when
    # LAI --> 0 (limit imposed by computing water fluxes by m2leaf)
    wb_veg['q_s_sat_mmol_per_leaf_area'] = wb_veg['q_sapo_sat_mmol'] / np.maximum(1, wb_veg['lai'])

    return update_capacitances_apo_and_sym_wb_veg(wb_veg)

# %% ../nbs/17_wb_veg.ipynb 23
def compute_interception_wb_veg(wb_veg:Dict, # Dictionary created using the `new_wb_veg` function
                                ppt:float, # precipitation (mm) that reach the soil
    ) -> Dict:

    "Rain interception by canopy/stock of water in the canopy reservoir (one vegetation layer only)"

    # Assert parameters ---------------------------------------------------------

    # wb_veg
    assert (
        isinstance(wb_veg, Dict)
    ), f"wb_veg must be a Dictionary not a {type(wb_veg)}"

    assert (
        isinstance(ppt, float) or isinstance(ppt, int)
    ), "Precipitation must be a numeric value"


    # Calculate intercepted water amount ----------------------------------------

    # No overflow
    if ppt * wb_veg['fcc'] <= (wb_veg['canopy_storage_capacity'] - wb_veg['intercepted_water_amount']):

        wb_veg['ppt_soil'] = ppt * (1 - wb_veg['fcc'])
        wb_veg['intercepted_water_amount'] = wb_veg['intercepted_water_amount'] + (ppt * wb_veg['fcc'])

    # Overflow
    elif  ppt * wb_veg['fcc'] > (wb_veg['canopy_storage_capacity'] - wb_veg['intercepted_water_amount']):

        wb_veg['ppt_soil'] = ppt - (wb_veg['canopy_storage_capacity'] - wb_veg['intercepted_water_amount'])
        wb_veg['intercepted_water_amount'] = wb_veg['canopy_storage_capacity']

    else:
        raise ValueError(
                    'Error calculating intercepted water amount in compute_interception_wb_veg function'
                    )

    return wb_veg

# %% ../nbs/17_wb_veg.ipynb 26
def compute_water_storage_wb_veg(wb_veg:Dict, # Dictionary created using the `new_wb_veg` function
                                vpd:float,  # Vapor Pressure Deficit (kPa)
) -> Dict:

    "Compute water stocks in leaves/wood in SUREAU_ECOS (one vegetation layer only)"

    # Assert parameters ---------------------------------------------------------

    # wb_veg
    assert (
        isinstance(wb_veg, Dict)
    ), f"wb_veg must be a Dictionary not a {type(wb_veg)}"

    assert (
        isinstance(vpd, float) or isinstance(vpd, int)
    ), "VPD must be a numeric value"

    # Symplasmic canopy water content of the leaves -----------------------------

    # Relative water content (unitless)
    rwc_lsym = 1 - rs_comp(pi_ft = wb_veg['params']['pifullturgor_leaf'],
                           e_symp = wb_veg['params']['epsilonsym_leaf'],
                           psi = wb_veg['psi_lsym']
                           )

    q_lsym = np.maximum(0, rwc_lsym)* wb_veg['q_lsym_sat_l']
    wb_veg['q_lsym_l'] = q_lsym
    wb_veg['lfmc_symp'] = 100 * (q_lsym / (wb_veg["dm_live_canopy"] * (1 - wb_veg["params"]['apofrac_leaf']) / 1000))

    # Apoplasmic water content of the leaves ------------------------------------
    q_lapo = (1 - wb_veg['plc_leaf']/100) * wb_veg['q_lapo_sat_l']
    wb_veg['q_lapo_l'] = q_lapo

    #  LFMC of Apo (relative moisture content to dry mass), gH20/gMS
    wb_veg['lfmc_apo'] = 100 * (q_lapo / (wb_veg['dm_live_canopy'] * wb_veg['params']['apofrac_leaf'] / 1000))

    # LFMC leaf total (Apo+Symp) ------------------------------------------------
    wb_veg['lfmc'] = 100 * (q_lapo + q_lsym) / (wb_veg['dm_live_canopy'] / 1000)

    # Symplasmic canopy water content of the stem -------------------------------
    # Relative water content (unitless)
    rwc_ssym = 1 - rs_comp(pi_ft = wb_veg['params']['pifullturgor_stem'],
                           e_symp = wb_veg['params']['epsilonsym_stem'],
                           psi = wb_veg['psi_ssym']
                           )

    q_ssym = np.maximum(0, rwc_ssym) * wb_veg['q_ssym_sat_l']
    wb_veg['q_ssym_l'] = q_ssym

    # Apoplasmic water content of the stem --------------------------------------
    q_sapo = (1 - wb_veg['plc_stem']/100) *  wb_veg['q_sapo_sat_l']
    wb_veg['q_sapo_l'] = q_sapo

    # FMC canopy ----------------------------------------------------------------
    # Dead FMC [%]
    wb_veg['dfmc'] <- compute_dfmc(vpd)

    # Water quantity of dead foliage (l/m2 sol ou mm)
    q_ldead = (wb_veg['dfmc'] / 100) * wb_veg['dm_dead_canopy'] / 1000
    wb_veg['fmc_canopy'] = 100 * (q_lapo + q_lsym + q_ldead) / (wb_veg["dm_live_canopy"] / 1000 + wb_veg["dm_dead_canopy"] / 1000)

    return wb_veg


