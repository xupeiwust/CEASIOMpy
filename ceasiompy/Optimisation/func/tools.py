"""
CEASIOMpy: Conceptual Aircraft Design Software.

Developed by CFS ENGINEERING, 1015 Lausanne, Switzerland

This module contains the tools used for data creation and manipulation of the
Optimisation and PredictiveTool modules.


| Author : Vivien Riolo
| Creation: 2020-05-26

TODO
----
    * Some tools may be usefull for other modules, maybe write an new one in
    the 'utils' folder ?

"""

# =================================================================================================
#   IMPORTS
# =================================================================================================

import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import openmdao.api as om
import pandas as pd
from ceasiompy import log


# Not an exhaustive list
accronym_dict = {
    "maximum_take_off_mass": "mtom",
    "range": "rng",
    "zero_fuel_mass": "zfm",
    "operating_empty_mass": "oem",
}

# =================================================================================================
# CLASSES
# =================================================================================================


# =================================================================================================
# FUNCTIONS
# =================================================================================================

# -------------- MISCELLANEOUS ---------------- #
# ----------------------------------------------#


def launch_external_program(path):
    """Launches an application with a predefined CSV to open.

    Args:
        path (str):

    Returns:
        None.

    """

    # TODO: Use function 'run_software' when this module will be refactore
    OS = sys.platform
    log.info("Identified OS : " + OS)
    if OS == "linux":
        os.system("libreoffice " + str(path))
    elif OS == "win32":
        os.system("Start excel.exe " + str(path))
    elif OS == "darwin":
        os.system(
            r"/Applications/Microsoft\ Excel.app/Contents/MacOS/Microsoft\ Excel " + str(path)
        )

    input("Press ENTER to continue...")


# ---------------- FUNCTIONS FOR POST-PROCESSING ------------------ #
# ------------------------------------------------------------------#


def display_results(prob, optim_var_dict, Rt):
    """Display variable history on terminal.

    All the variables that were used in the routine and that saved in
    optim_var_dict are displayed on terminal with their bounds and their value
    history.

    Args:
        Rt (class) : Routine parameters
        prob (class) : OpenMDAO problem object
        optim_var_dict (dict) : Variable dictionnary

    """

    log.info("=========================================")
    log.info("min = " + str(prob["objective.{}".format(Rt.objective)]))

    for name, (
        val_type,
        listval,
        minval,
        maxval,
        _,
        _,
    ) in optim_var_dict.items():
        if val_type == "des":
            log.info(name + " = " + str(prob["indeps." + name]))
            log.info("Min :" + str(minval) + " Max : " + str(maxval))

    log.info("Variable history :")

    for name, (
        val_type,
        listval,
        minval,
        maxval,
        _,
        _,
    ) in optim_var_dict.items():
        if val_type == "des":
            log.info(name + " => " + str(listval))
    log.info("=========================================")


def read_results(optim_dir_path, optim_var_dict=None):
    """Read sql file and converts data to dataframe.

    This is mainly to facilitate data manipulation by avoiding dealing with
    the pre-implemented CaseReader dictionnary whose architecture is not
    convenient.

    Args:
        optim_dir_path (Path): Path to the SQL file directory.
        optim_var_dict (dct): Contains the variables.

    Returns:
        df (DataFrame) : Contains all parameters of the routine

    """

    if optim_var_dict is None:
        optim_var_dict = {}

    # # Read recorded options
    # cr = om.CaseReader(optim_dir_path + '/Driver_recorder.sql')

    # cases = cr.get_cases()

    # # Initiates dictionnaries
    # case1 = cr.get_case(0)
    obj = {}
    des = {}
    const = {}

    # Retrieve data from optim variables
    for name, infos in optim_var_dict.items():
        if infos[0] == "obj":
            obj[name] = np.array(infos[1])
        if infos[0] == "des":
            des[name] = np.array(infos[1])
        if infos[0] == "const":
            const[name] = np.array(infos[1])

    df_o = pd.DataFrame(obj).transpose()
    df_d = pd.DataFrame(des).transpose()
    df_c = pd.DataFrame(const).transpose()

    df_o.insert(0, "type", "obj")
    df_d.insert(0, "type", "des")
    df_c.insert(0, "type", "const")

    df = pd.concat([df_o, df_d, df_c], axis=0)
    df.sort_values("type", 0, ignore_index=True, ascending=False)

    # Add get and set commands
    df.insert(1, "getcmd", "-")
    df.insert(2, "setcmd", "-")
    for v in df.index:
        if v in optim_var_dict:
            df.loc[v, "getcmd"] = optim_var_dict[v][4]
            df.loc[v, "setcmd"] = optim_var_dict[v][5]

    df["initial value"] = df[0]

    return df


def save_results(optim_dir_path, optim_var_dict=None):
    """Save routine results to CSV.

    Add the variable history to the CSV paramater file and save it to the
    corresponding working directory. This comes in handy for generating
    data for surrogate models.

    Args:
        optim_dir_path (str) : Path to the routine working directory.

    """

    if optim_var_dict is None:
        optim_var_dict = {}

    log.info("Variables will be saved")

    # Get variable infos
    df = read_results(optim_dir_path, optim_var_dict)

    df.to_csv(
        Path(optim_dir_path, "Variable_history.csv"), index=True, na_rep="-", index_label="Name"
    )

    log.info(f"Results have been saved at {optim_dir_path}")


# ---------------- FUNCTIONS FOR PLOTTING ------------------ #
# -----------------------------------------------------------#


def plot_results(optim_dir_path, routine_type, optim_var_dict=None):
    """Generate plots of the routine.

    Draw plots to vizualize the data. The evolution of each problem parameter
    appears in a subplot.

    Args:
        optim_dir_path (str) : Path to the routine working directory.
        routine_type (str) : Type of the routine, can be DoE or Optim

    """

    if optim_var_dict is None:
        optim_var_dict = {}

    df = read_results(optim_dir_path, optim_var_dict)

    obj = [i for i in df.index if df["type"][i] == "obj"]
    des = [i for i in df.index if df["type"][i] == "des"]
    const = [i for i in df.index if df["type"][i] == "const"]

    df.pop("type")
    df.pop("getcmd")
    df.pop("setcmd")
    df = df.transpose()
    nbC = min(len(des), 5)
    df.iloc[1:-1].plot(subplots=True, layout=(-1, nbC), style=".-")

    # Save figure (TODO: could be improved)
    fig_path = Path(optim_dir_path, "plot_variable.png")
    plt.savefig(fig_path)

    plot_objective(optim_dir_path)

    if routine_type == "DoE":
        gen_plot(optim_dir_path, df, obj, des)
        gen_plot(optim_dir_path, df, obj, const)


def plot_objective(optim_dir_path):
    """Plot the objective function.

    This function is used to compute the objective function from the case
    recorder as defined in the routine, e.g. cl/cd or cl/mtom.

    Args:
        optim_dir_path (dct): Path to the case recorder.

    """

    cr = om.CaseReader(Path(optim_dir_path, "Driver_recorder.sql"))

    cases = cr.get_cases()
    case1 = cr.get_case(0)
    obj = {}

    for k, v in dict(case1.get_objectives()).items():
        obj[k.replace("objective.", "")] = v

    for case in cases:
        for key, val in case.get_objectives().items():
            key = key.replace("objective.", "")
            obj[key] = np.append(obj[key], val)
    df_o = pd.DataFrame(obj).transpose()
    df_o = df_o.drop(0, 1)
    df_o = df_o.transpose()
    nbC = min(len(obj), 5)

    df_o.plot(subplots=True, layout=(-1, nbC), style=".-")

    # plt.show()

    # Save figure (TODO: could be improved)
    fig_path = Path(optim_dir_path, "plot_objective_function.png")
    plt.savefig(fig_path)


def gen_plot(optim_dir_path, df, yvars, xvars):
    """Generate scatter plot

    Generate a scatter plot from a dataframe based on its column entries.

    Args:
        df (DataFrame) : Contains the data.
        yvars (lst) : Label of the functions in df.
        xvars (lst) : Label of the variables in df.

    """

    plt.figure()
    nbC = min(len(xvars), 5)
    if nbC == 0:
        nbC = 1
    nbR = int(len(yvars) * np.ceil(len(xvars) / nbC))
    r = 0
    c = 1
    for o in yvars:
        for d in xvars:
            plt.subplot(nbR, nbC, c + r * nbC)
            plt.scatter(df[d], df[o])
            plt.xlabel(d)
            if c == 1:
                plt.ylabel(o)
            c += 1
            if c >= nbC:
                r += 1
                c = 0
        r += 1
        c = 0

    # plt.show()

    # Save figure (TODO: could be improved)
    fig_path = Path(optim_dir_path, "plot_doe_variables.png")
    plt.savefig(fig_path)


# ----------------- FUNCTIONS FOR OPTIMISATION PARAMETERS ----------------- #
# --------------------------------------------------------------------------#


def is_digit(value):
    """Check if a string value is a float.

    This function comes in as more flexible than the implementde isdigit()
    function, as it also enbales to check for floats and not just integers.

    Args:
        value (str) : Chain of character that may contain something else than
        a digit or a dot.

    Returns:
        Boolean.

    """

    if isinstance(value, list):
        return False

    try:
        float(value)
        return True
    except ValueError:
        return False


def change_var_name(name):
    """Modify the variable name

    Checks for special characters and replaces them with '_' which can be taken
    as a variable name for the OpenMDAO problem, and checks if an accronym is used.

    Ex : 'maximum take off mass' -> 'mtom'

    Args:
        name (str): variable name.

    Returns:
        new_name (str): new variable_name.

    """

    log.info("Check variable name {}".format(name))

    if "range" in name or "payload" in name:
        for s in name:
            if s in ["[", "]"]:
                name = name.replace(s, "_")
        log.info("Variable name was changed to {}".format(name))

    if name in accronym_dict:
        log.info("Variable name was changed to {}".format(accronym_dict[name]))
        return accronym_dict[name]

    return name


def add_type(entry, outputs, objective, var):
    """Add variable type to the dictionary.

    Verifies if the entry of a module is listed in its outputs. If it is the
    case it will be set as a constraint ('const') by default, except if
    the entry is found in the expression of the objective function where it is
    then labelled as 'obj'. Else it will be marked as a design variable as it
    belongs to the module input.

    Args:
        name (str) : Name of a variable
        outputs (lst) : List of the modules' output
        objective (str) : Objective function
        var (dct) : Variable dictionary

    """

    if entry in outputs:
        if not isinstance(entry, str):
            entry = entry.var_name
        if entry in objective:
            var["type"].append("obj")
            log.info("Added type : obj")
        else:
            var["type"].append("const")
            log.info("Added type : const")
    else:
        var["type"].append("des")
        log.info("Added type : des")


def add_bounds(value, var):
    """Add upper and lower bound.

    20% of the initial value is added and substracted to create the
    boundaries.

    Args:
    value (str) : Initial value of the variable
    var (dct) : Variable dictionary

    """

    if value in ["False", "True"]:
        lower = "-"
        upper = "-"
    elif value.isdigit():
        value = int(value)
        lower = round(value - abs(0.2 * value))
        upper = round(value + abs(0.2 * value))
        if lower == upper:
            lower -= 1
            upper += 1
    else:
        value = float(value)
        lower = round(value - abs(0.2 * value))
        upper = round(value + abs(0.2 * value))
        if lower == upper:
            lower -= 1.0
            upper += 1.0

    var["min"].append(lower)
    var["max"].append(upper)


# =================================================================================================
#    MAIN
# =================================================================================================


if __name__ == "__main__":

    log.info("Nothing to execute!")
