# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/10_create_simulation_parameters.ipynb.

# %% auto 0
__all__ = ["create_simulation_parameters"]

# %% ../nbs/10_create_simulation_parameters.ipynb 3
import collections
import os
import shutil


# %% ../nbs/10_create_simulation_parameters.ipynb 4
def create_simulation_parameters(
    main_dir: str,
    start_year_simulation: int,  # Integer indicating the starting year for the simulation
    end_year_simulation: int,  # Integer indicating the ending year for the simulation (must match the dates of the input climate data file)
    output_path: str,  # Path of output result file.
    output_type: str = None,  # The output variables of the model that should be written in the output model file.
    resolution_output: str = "subdaily",  # the resolution chosen to write variables in files, `subdaily`, `daily` or `yearly`.
    overwrite: bool = False,  # Indicates whether the output result file can be overwritten if it already exists
):
    """
    Create a dictionary with the simulation parameters to run SureauEcos. Can be used as an input in
    """

    simulation_parameters = collections.defaultdict(list)

    assert isinstance(main_dir, str)
    if not os.path.isdir(main_dir):
        return f"Directory: {main_dir}, does not exist, check presence or spelling"

    simulation_parameters["main_dir"] = main_dir

    # Make sure that resolution output only has three options
    assert resolution_output in [
        "subdaily",
        "daily",
        "yearly",
    ], f'{resolution_output} not a valid option, select "subdaily", "daily" or "yearly"'

    simulation_parameters["resolution_output"] = resolution_output

    assert isinstance(output_type, str)
    if output_type is None:
        if resolution_output == "subdaily":
            simulation_parameters["output_type"] = "simple_subdaily"

        elif resolution_output == "daily":
            simulation_parameters["output_type"] = "simple_daily"

        elif resolution_output == "yearly":
            simulation_parameters["output_type"] = "simple_yearly"
    else:
        simulation_parameters["output_type"] = output_type

    # Create directory for storing output

    assert isinstance(output_path, str)
    output_path = os.path.join(output_path, "sureau_output")

    if not os.path.exists(output_path):
        os.mkdir(output_path)
        simulation_parameters["output_path"] = output_path

    elif os.path.exists(output_path) and overwrite is True:
        shutil.rmtree(output_path)
        os.makedirs(output_path)
        simulation_parameters["output_path"] = output_path

    elif os.path.exists(output_path) and overwrite is False:
        return "file already exists and 'overwrite' option is set to False, change 'outputPath' or set 'overwrite' to True"

    # Compare end_year_simulation is larger than start_year_simulation
    assert (
        start_year_simulation <= end_year_simulation
    ), "Make sure that `end_year_simulation` is larger than or equal `start_year_simulation`"

    simulation_parameters["start_year_simulation"] = start_year_simulation
    simulation_parameters["end_year_simulation"] = end_year_simulation

    return simulation_parameters
