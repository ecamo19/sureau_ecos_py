# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/17_wg_clim.ipynb.

# %% auto 0
__all__ = ['new_wb_clim', 'new_wb_clim_hour']

# %% ../nbs/17_wg_clim.ipynb 3
import collections
from typing import Dict
from pandera.typing import DataFrame
from .climate_utils import compute_vpd_from_t_rh

from sureau_ecos_py.create_simulation_parameters import (
    create_simulation_parameters,
)

from .create_climate_data import create_climate_data
from .create_modeling_options import create_modeling_options



# %% ../nbs/17_wg_clim.ipynb 4
def new_wb_clim(
    climate_data:DataFrame, # Dataframe created using the `create_climate_data` function
    year:int, # Year, __No definition found__
    day_of_year:int # Day of the year, __No definition found__


) -> Dict:  # Dictionary containing parameters to run the model
    "Create a list with all necessary daily climate values to run SureauR from climate_data"

    # Assert parameters ---------------------------------------------------------

    # Year
    assert isinstance(
        year, int
    ) and 3000 >= year > 0,"year must be a integer value between 0-3000"

    # Day of year
    assert isinstance(
        day_of_year, int
    ) and 366 >= day_of_year >= 1, "day_of_year must be a integer value between 1-365"

    # Create wb_clim dictionary -------------------------------------------------

    # Check that year and day_of_year are present inside the dataframe
    if year in climate_data['year'].values and day_of_year in climate_data['day_of_year'].values:

        # Get row index in climate frame based on year and doy
        row_index = climate_data[(climate_data['year'] == year) & (climate_data['day_of_year'] == day_of_year)].index[0]

        # Transfrom row to a dictionary with params
        wb_clim_dict = collections.defaultdict(list, dict(climate_data.loc[row_index]))

    else:
        raise ValueError(
            f"year:{year} and/or day_of_year:{day_of_year} not found in climate dataframe"
        )

    # Add parameters to dictionary ----------------------------------------------
    wb_clim_dict['net_radiation'] = float("NAN")
    wb_clim_dict['etp'] = float("NAN")
    wb_clim_dict['vpd'] = compute_vpd_from_t_rh(relative_humidity = wb_clim_dict['RHair_mean'],
                                                temperature= wb_clim_dict['Tair_mean']
                                                )

    # Add Temperature from previous and next days

    # cas normal

    # if the row_index is not the first nor the last
    if row_index != 0 and row_index != climate_data.shape[0]:
        wb_clim_dict['Tair_min_prev'] = climate_data.loc[row_index - 1]['Tair_min']
        wb_clim_dict['Tair_min_next'] = climate_data.loc[row_index + 1]['Tair_min']
        wb_clim_dict['Tair_max_prev'] = climate_data.loc[row_index - 1]['Tair_max']

        return wb_clim_dict

    # si premier jour de le la simu

    # if the row_index is the first
    elif row_index == 0:
        print('Firts day of the simulation, previous Tair is the same as the current')

        wb_clim_dict['Tair_min_prev'] = climate_data.loc[row_index]['Tair_min']
        wb_clim_dict['Tair_min_next'] = climate_data.loc[row_index + 1]['Tair_min']
        wb_clim_dict['Tair_max_prev'] = climate_data.loc[row_index]['Tair_max']

        return wb_clim_dict

    elif row_index == climate_data.shape[0]:
        print('Last day of the simulation, next Tair_min_next is the same as the Tair_min')

        wb_clim_dict['Tair_min_prev'] = climate_data.loc[row_index - 1]['Tair_min']
        wb_clim_dict['Tair_min_next'] = climate_data.loc[row_index]['Tair_min']
        wb_clim_dict['Tair_max_prev'] = climate_data.loc[row_index - 1]['Tair_max']

        return wb_clim_dict

    else:
        raise ValueError(
            "Error setting previous and following temperature conditions"
        )


# %% ../nbs/17_wg_clim.ipynb 10
def new_wb_clim_hour(
    wb_clim:Dict, # Dictionary created using the `new_wb_clim` function
    wb_veg:Dict, # __No definition found__
    latitude:float,  # Value indicating the latitude of the stand
    longitude:float,  # Value indicating the longitude of the stand
    modeling_options:Dict,  # Dictionary created using the `create_modeling_options` function
    pt_coeff: float,  # An empirical constant accounting for the vapor pressure deficit and resistance values Typically, α is 1.26 for open bodies of water, but has a wide range of values from less than 1 (humid conditions) to almost 2 (arid conditions).


) -> Dict:  # Dictionary containing parameters to run the model
    "Create a list with interpolated climate data at the required time step"

    pass

