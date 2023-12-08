# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/12_create_climate_data.ipynb.

# %% auto 0
__all__ = ['ClimateDataValidation', 'create_climate_data']

# %% ../nbs/12_create_climate_data.ipynb 3
import pandas as pd
from pathlib import Path
from typing import Dict
import os
import pandera as pa
from pandera.typing import DataFrame, Series
import numpy as np

from .create_modeling_options import create_modeling_options
from .create_simulation_parameters import create_simulation_parameters

# %% ../nbs/12_create_climate_data.ipynb 4
# This class is created for validating the input climate dataframe
# If the data don't follow the structure in the class the function will fail
class ClimateDataValidation(pa.SchemaModel):
    "Schema for validating the climate data"

    DATE: Series[np.datetime64] = pa.Field(description="date with format 1991/12/23")
    Tair_min: Series[float] = pa.Field(
        description="minimum air temperature of the day (degC)"
    )
    Tair_max: Series[float] = pa.Field(
        description=" maximum air temperature of the day (degC)"
    )
    Tair_mean: Series[float] = pa.Field(
        description="mean air temperature of the day (degC)"
    )
    RG_sum: Series[float] = pa.Field(ge=0, description="global radiation (MJ/m2)")

    PPT_sum: Series[float] = pa.Field(ge=0, description="precipitation (mm)")

    RHair_min: Series[float] = pa.Field(
        ge=0, le=100, description="minimum relative humidity of the day (%)"
    )
    RHair_max: Series[float] = pa.Field(
        ge=0,
        le=100,
        description="maximum relative humidity of the day (%)",
        coerce=True,
    )
    RHair_mean: Series[float] = pa.Field(
        ge=0, le=100, description="mean relative humidity of the day (%)"
    )
    WS_mean: Series[float] = pa.Field(
        ge=0, description="mean wind speed of the day (m/s)"
    )


@pa.check_types(lazy=True)
def create_climate_data(
    simulation_parameters: Dict,  # Dictionary created using the `create_simulation_parameters` function
    modeling_options: Dict,  # Dictionary created using the `create_modeling_options` function
    file_path: Path,  # Path to the input CSV climate file. i.e. path/to/file/climate.csv
    sep: str = ";",  # CSV file separator can be ',' or ';'
) -> DataFrame[ClimateDataValidation]:
    "Create a climate data.frame to run SureauR. Read input climate data select the desired period and put it in the right format to run `run.SurEauR` Also check data consistency and input variables according to modeling options (see \code{create.modeling.options} and simulation parameters (see \code{create.simulation.parameters)"

    # Make sure that simulation_parameters and modeling_options are dictionaries-
    assert isinstance(
        simulation_parameters, Dict
    ), f"simulation_parameters must be a dictionary not a {type(simulation_parameters)}"

    assert isinstance(
        modeling_options, Dict
    ), f"modeling_options must be a dictionary not a {type(modeling_options)}"

    # Read file if it exists and climateData not provided, error otherwise ------

    if os.path.exists(file_path):
        try:
            climate_data = pd.read_csv(
                file_path, sep=sep, header=0, parse_dates=["DATE"], dayfirst=True
            )

        except pa.errors.SchemaErrors as err:
            print(err)
    else:
        print(f"file: {file_path}, does not exist, check presence or spelling")

    # Create climate data based on constant_climate parameter -------------------

    if modeling_options["constant_climate"] is False:
        # Break DATE into year,month, day_of_year, day_of_month columns

        # Create function for extracting the day of the year (from 0 to 365)
        def get_day_of_year(date):
            return pd.Period(date, freq="H").day_of_year

        # Map function over each row and create new column
        climate_data["day_of_year"] = pd.DataFrame(
            map(get_day_of_year, climate_data["DATE"])
        )

        # Get the day of the month (from 1 to 31)
        climate_data["day_of_month"] = pd.DatetimeIndex(climate_data["DATE"]).day

        # Get the month (from 1 to 12)
        climate_data["month"] = pd.DatetimeIndex(climate_data["DATE"]).month

        # Get the year
        climate_data["year"] = pd.DatetimeIndex(climate_data["DATE"]).year

        # Filter data based on start_year_simulation and end_year_simulation
        # parameters specified in similation_parameters dictionary
        climate_data = climate_data.loc[
            (climate_data["year"] >= simulation_parameters["start_year_simulation"])
            & (climate_data["year"] <= simulation_parameters["end_year_simulation"])
        ]

        print(
            f'{climate_data.shape[0]} days were selected in the input climate file, covering the period: {climate_data["year"].min()} - {climate_data["year"].max()}'
        )

        return climate_data

    if modeling_options["constant_climate"] is True:
        # Use a List Comprehension to create a sequence of dates with the format
        # Day/Month/Year
        date_ref = [
            each_date.strftime("%d-%m-%Y")
            for each_date in pd.date_range(
                start=f'01/01/{simulation_parameters["start_year_simulation"]}',
                end=f'31/12/{simulation_parameters["end_year_simulation"]}',
                freq="D",
            )
        ]

        # Get the first row of the climate_data
        constant_climate_data = climate_data.loc[:0]

        # Repeat it based on the lenght of date_ref. This is done for creating a
        # constant climate
        constant_climate_data = constant_climate_data.loc[
            constant_climate_data.index.repeat(len(date_ref))
        ]

        # Substitute the old dates with the new ones
        constant_climate_data.DATE = pd.to_datetime(date_ref, format="%d-%m-%Y")

        # Break DATE into year,month, day_of_year, day_of_month columns ---------

        # Create function for extracting the day of the year (from 0 to 365)
        def get_day_of_year(date):
            return pd.Period(date, freq="H").day_of_year

        # Map function over each row and create new column
        constant_climate_data["day_of_year"] = pd.DataFrame(
            map(get_day_of_year, constant_climate_data["DATE"])
        )

        # Get the day of the month (from 1 to 31)
        constant_climate_data["day_of_month"] = pd.DatetimeIndex(
            constant_climate_data["DATE"]
        ).day

        # Get the month (from 1 to 12)
        constant_climate_data["month"] = pd.DatetimeIndex(
            constant_climate_data["DATE"]
        ).month

        # Get the year
        constant_climate_data["year"] = pd.DatetimeIndex(
            constant_climate_data["DATE"]
        ).year

        print(
            f'{constant_climate_data.shape[0]} days of the period: {constant_climate_data["year"].min()} - {constant_climate_data["year"].max()} have the same climatic conditions'
        )

        return constant_climate_data
