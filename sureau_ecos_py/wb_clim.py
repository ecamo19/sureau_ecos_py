# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/17_wg_clim.ipynb.

# %% auto 0
__all__ = ['new_wb_clim', 'new_wb_clim_hour']

# %% ../nbs/17_wg_clim.ipynb 3
import warnings
import collections
import numpy as np
from typing import Dict
from pandera.typing import DataFrame
from sureau_ecos_py.climate_utils import (
    day_length,
    potential_par,
    compute_pet,
    rg_units_conversion,
    compute_vpd_from_t_rh,
    calculate_rh_diurnal_pattern,
    rg_watt_ppfd_umol_conversions,
    calculate_radiation_diurnal_pattern,
    calculate_temperature_diurnal_pattern,
)
from sureau_ecos_py.create_simulation_parameters import (
    create_simulation_parameters,
)
from .create_climate_data import create_climate_data
from .create_modeling_options import create_modeling_options

# %% ../nbs/17_wg_clim.ipynb 4
def new_wb_clim(
    climate_data: DataFrame,  # Dataframe created using the `create_climate_data` function
    year: int,  # Year, __No definition found__
    day_of_year: int,  # Day of the year
) -> Dict:  # Dictionary containing parameters to run the model
    "Create a list with all necessary daily climate values to run SureauR from climate_data"

    # Assert parameters ---------------------------------------------------------

    # Year
    assert (
        isinstance(year, int) and 3000 >= year > 0
    ), "year must be a integer value between 0-3000"

    # Day of year
    assert (
        isinstance(day_of_year, int) and 366 >= day_of_year >= 1
    ), "day_of_year must be a integer value between 1-366"

    # Assert row index start at 1 and not at 0
    assert (
        np.array(climate_data.index)[0] != 0
    ), "First row index is 0 and should be 1. Fix before proceeding"

    # Create wb_clim dictionary -------------------------------------------------

    # Check that year and day_of_year are present inside the dataframe
    if (
        year in climate_data["year"].values
        and day_of_year in climate_data["day_of_year"].values
    ):
        # Make sure there are no rows with the same date
        if (
            len(
                climate_data[
                    (climate_data["year"] == year)
                    & (climate_data["day_of_year"] == day_of_year)
                ]
            )
            == 1
        ):
            # Get row index in climate frame based on year and doy
            row_index = climate_data[
                (climate_data["year"] == year)
                & (climate_data["day_of_year"] == day_of_year)
            ].index[0]

            # Transfrom row to a dictionary with params
            wb_clim_dict = collections.defaultdict(
                list, dict(climate_data.loc[row_index])
            )

        else:
            raise ValueError(
                "Erroneous climate data format : duplicated lines ?"
            )

    else:
        raise ValueError(
            f"year:{year} and/or day_of_year:{day_of_year} not found in climate dataframe"
        )

    # Add parameters to dictionary ----------------------------------------------
    wb_clim_dict["net_radiation"] = float("NAN")
    wb_clim_dict["etp"] = float("NAN")

    wb_clim_dict["vpd"] = compute_vpd_from_t_rh(
        relative_humidity=wb_clim_dict["RHair_mean"],
        temperature=wb_clim_dict["Tair_mean"],
    )

    # Rename parameters
    wb_clim_dict["ppt"] = wb_clim_dict["PPT_sum"]
    wb_clim_dict["rg"] = wb_clim_dict["RG_sum"]

    # Delete old parameters
    del wb_clim_dict["PPT_sum"]
    del wb_clim_dict["RG_sum"]

    # Add Temperature from previous and next days -------------------------------

    # Adding warning in case there row index start a 0 and not 1

    # cas normal

    # if the row_index is not the first nor the last
    if row_index != 1 and row_index != climate_data.shape[0]:
        wb_clim_dict["Tair_min_prev"] = climate_data.loc[row_index - 1][
            "Tair_min"
        ]
        wb_clim_dict["Tair_min_next"] = climate_data.loc[row_index + 1][
            "Tair_min"
        ]
        wb_clim_dict["Tair_max_prev"] = climate_data.loc[row_index - 1][
            "Tair_max"
        ]

        return wb_clim_dict

    # si premier jour de le la simu

    # if the row_index is the first
    elif row_index == 1:
        print("Firts day of the simulation. Tair is the same as the current")

        wb_clim_dict["Tair_min_prev"] = climate_data.loc[row_index]["Tair_min"]
        wb_clim_dict["Tair_min_next"] = climate_data.loc[row_index + 1][
            "Tair_min"
        ]
        wb_clim_dict["Tair_max_prev"] = climate_data.loc[row_index]["Tair_max"]

        return wb_clim_dict

    elif row_index == climate_data.shape[0]:
        print(
            "Last day of the simulation. Tair_min_next is the same as the Tair_min"
        )

        wb_clim_dict["Tair_min_prev"] = climate_data.loc[row_index - 1][
            "Tair_min"
        ]
        wb_clim_dict["Tair_min_next"] = climate_data.loc[row_index]["Tair_min"]
        wb_clim_dict["Tair_max_prev"] = climate_data.loc[row_index - 1][
            "Tair_max"
        ]

        return wb_clim_dict

    else:
        raise ValueError(
            "Error setting previous and next temperature conditions"
        )

# %% ../nbs/17_wg_clim.ipynb 10
def new_wb_clim_hour(
    wb_clim: Dict,  # Dictionary created using the `new_wb_clim` function
    wb_veg: Dict,  # __No definition found__
    latitude: float,  # Value indicating the latitude of the stand
    longitude: float,  # Value indicating the longitude of the stand
    modeling_options: Dict,  # Dictionary created using the `create_modeling_options` function
    pt_coeff: float,  # An empirical constant accounting for the vapor pressure deficit and resistance values Typically, α is 1.26 for open bodies of water, but has a wide range of values from less than 1 (humid conditions) to almost 2 (arid conditions).
) -> Dict:  # Dictionary containing parameters to run the model
    "Create a list with interpolated climate data at the required time step"

    # Assert parameters ---------------------------------------------------------

    # wb_clim
    assert isinstance(
        wb_clim, Dict
    ), f"wb_clim must be a Dictionary not a {type(wb_clim)}"

    # wb_veg
    assert isinstance(
        wb_veg, Dict
    ), f"wb_veg must be a Dictionary not a {type(wb_veg)}"

    # modeling_options
    assert isinstance(
        modeling_options, Dict
    ), f"modeling_options must be a Dictionary not a {type(modeling_options)}"

    # Latitude and longitude
    assert (
        isinstance(latitude, float) and isinstance(longitude, float)
    ), "Missing latitude and/or longitude. Provide latitude and/or longitude as Coordinates points i.e. latitude = 41.40338, longitude = 2.17403"

    # pt_coeff
    assert isinstance(
        pt_coeff, float
    ), f"pt_coeff must be a float i.e. 2.0001 not a {type(pt_coeff)}"

    # Calculate day_lenght ------------------------------------------------------
    if modeling_options["constant_climate"] is False:
        # calculate sunrise, sunset and daylength (in seconds from midgnight)
        # depends of DAY, latt and lon
        # sunrise_sunset_daylen <- as.numeric(daylength(lat = lat, long = lon,
        # jd = WBclim$DOY, 0)) * 3600 #

        # Calculate day_length
        sunrise_sunset_daylength_hours = day_length(
            latitude=latitude, day_of_year=wb_clim["day_of_year"]
        )

        # Create empty dict
        sunrise_sunset_daylength_seconds = collections.defaultdict(list)

        # Transform arrays to seconds: Loop over the dictionary for getting each
        # array
        for each_key, each_array in sunrise_sunset_daylength_hours.items():
            sunrise_sunset_daylength_seconds[each_key] = np.where(
                # Convert only the values between 0 and 24
                ((each_array >= 0) & (each_array <= 24)),
                each_array * 3600,
                # leave 99 or -99
                each_array,
            )

    else:
        warnings.warn(
            "Parameter constant_climate in modeling_options set to True, using default parameters"
        )

        warnings.warn(
            "Sunrise, sunset and daylenght units are hours for constant_climate"
        )

        # Calculate day_length
        sunrise_sunset_daylength_hours = day_length(
            latitude=0.0, day_of_year=166
        )

        # Create empty dict
        sunrise_sunset_daylength_seconds = collections.defaultdict(list)

        # Transform arrays to seconds: Loop over the dictionary for getting each
        # array
        for each_key, each_array in sunrise_sunset_daylength_hours.items():
            # Convert only the values between 0 and 24 and leave 99 or -99
            sunrise_sunset_daylength_seconds[each_key] = np.where(
                ((each_array >= 0) & (each_array <= 24)),
                each_array * 3600,
                each_array,
            )

    # Set new values for days with day_length equal to 24 hours -----------------
    if sunrise_sunset_daylength_seconds["day_length"] == 24 * 3600:
        print("Days with no nights")
        sunrise_sunset_daylength_seconds["sunrise"] = 0
        sunrise_sunset_daylength_seconds["sunset"] = 24 * 3600
        sunrise_sunset_daylength_seconds["day_length"] = 24 * 3600

    # Set new values for days with day_length equal to 0 hours ------------------
    if sunrise_sunset_daylength_seconds["day_length"] == 0:
        print("Days with no daylight")
        sunrise_sunset_daylength_seconds["sunrise"] = 12 * 3600
        sunrise_sunset_daylength_seconds["sunset"] = 12 * 3600

        sunrise_sunset_daylength_seconds["day_length"] = 0

    # Desegregation at the hourly time step -------------------------------------
    time_hour = np.arange(0, 24)

    # time relative to sunset (in seconds)
    warnings.warn(
        "Issue #3 in gitlab not solved. Comment in R code say time relative to sunset but sunrise was used instead."
    )
    time_relative_to_sunset_sec = (
        time_hour * 3600
    ) - sunrise_sunset_daylength_seconds["sunrise"]

    # Calculate radiation  ------------------------------------------------------
    radiation = []

    if sunrise_sunset_daylength_seconds["day_length"] == 0:
        warnings.warn(
            "day_length is 0 using 0.001 in calculate_radiation_diurnal_pattern function"
        )

        for each_time_step in time_relative_to_sunset_sec:
            radiation.append(
                calculate_radiation_diurnal_pattern(
                    time_of_day=each_time_step,
                    # 0.001 added to avoid division by 0
                    day_length=(0.001),
                )
            )

    elif sunrise_sunset_daylength_seconds["day_length"] > 0:
        for each_time_step in time_relative_to_sunset_sec:
            radiation.append(
                calculate_radiation_diurnal_pattern(
                    time_of_day=each_time_step,
                    day_length=sunrise_sunset_daylength_seconds["day_length"],
                )
            )

    else:
        raise ValueError(
            f"Is day_length:{sunrise_sunset_daylength_seconds['day_length']} negative?"
        )

    # Convert flatten np.array
    radiation = np.array(radiation).flatten()

    # Set 0 radiation at night
    radiation[
        (time_relative_to_sunset_sec < 0)
        | ((time_hour * 3600) >= sunrise_sunset_daylength_seconds["sunset"])
    ] = 0

    # Create wb_clim_hour dictionary --------------------------------------------

    # Empty dict
    wb_clim_hour = collections.defaultdict(list)

    # Add parameters ------------------------------------------------------------
    wb_clim_hour["rg"] = wb_clim["rg"] * radiation * 3600

    wb_clim_hour["rn"] = wb_clim["net_radiation"] * radiation * 3600

    # Get Photosyntetic Photon Flux Density (aka PAR) from rg
    wb_clim_hour["par"] = rg_watt_ppfd_umol_conversions(
        rg=rg_units_conversion(
            rg_mj=wb_clim_hour["rg"],
            nhours=1,
            selected_conversion="mj_to_watts_hour",
        ),
        selected_conversion="rg_watts_to_ppfd_umol",
    )

    # Potential par
    wb_clim_hour["potential_par"] = potential_par(
        time_of_day_in_hours=time_hour,
        latitude=latitude,
        day_of_year=wb_clim["day_of_year"],
    )

    # Air temperature
    air_temperature = []
    for each_time_step in time_relative_to_sunset_sec:
        air_temperature.append(
            calculate_temperature_diurnal_pattern(
                time_of_day=each_time_step,
                tmin=wb_clim["Tair_min"],
                tmax=wb_clim["Tair_max"],
                tmin_prev=wb_clim["Tair_min_prev"],
                tmax_prev=wb_clim["Tair_max_prev"],
                tmin_next=wb_clim["Tair_min_next"],
                day_length=sunrise_sunset_daylength_seconds["day_length"],
            )
        )

    # Convert air_temperature to flatten np.array
    wb_clim_hour["tair_mean"] = np.array(air_temperature).flatten()

    # Air relative humidity
    relative_humidity = np.empty((0), float)
    for each_tair_temp in wb_clim_hour["tair_mean"]:
        relative_humidity = np.append(
            relative_humidity,
            calculate_rh_diurnal_pattern(
                temperature=each_tair_temp,
                tmin=wb_clim["Tair_min"],
                # 0.0000001 added to prevent crash when
                # tmin = tmax
                tmax=wb_clim["Tair_max"] + 0.0000001,
                rhmin=wb_clim["RHair_min"],
                # 0.0000001 added to prevent crash when
                # RHair_min = RHair_max
                rhmax=wb_clim["RHair_max"] + 0.0000001,
            ),
        )

    # Give a value of 0.5 if negative values are found
    relative_humidity[relative_humidity < 0] = 0.5

    # Convert relative_humidity to flatten np.array
    wb_clim_hour["rhair_mean"] = relative_humidity

    # Wind Speed
    warnings.warn(
        "No time interpolation for wind speed. Assumed to be constant during the day"
    )

    wb_clim_hour["wind_speed"] = np.repeat(wb_clim["WS_mean"], 24)

    # VPD
    wb_clim_hour["vpd"] = compute_vpd_from_t_rh(
        relative_humidity=wb_clim_hour["rhair_mean"],
        temperature=wb_clim_hour["tair_mean"],
    )

    # PET
    if modeling_options["etp_formulation"] == "pt":
        compute_pet(
            tmoy=wb_clim_hour["tair_mean"],
            net_radiation=wb_clim_hour["rn"],
            pt_coeff=pt_coeff,
            formulation="pt",
        )

    elif modeling_options["etp_formulation"] == "pm":
        compute_pet(
            tmoy=wb_clim_hour["tair_mean"],
            net_radiation=wb_clim_hour["rn"],
            wind_speed_u=wb_clim_hour["wind_speed"],
            vpd=wb_clim_hour["vpd"],
            formulation="pm",
        )

    else:
        raise ValueError("Error calculating PET in new_wb_clim_hour function")

    return wb_clim_hour
