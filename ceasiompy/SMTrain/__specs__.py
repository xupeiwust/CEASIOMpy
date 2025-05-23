from pathlib import Path
import streamlit as st
from ceasiompy.utils.moduleinterfaces import CPACSInOut
from ceasiompy.utils.commonxpath import SMTRAIN_XPATH

# ===== Module Status =====
# True if the module is active
# False if the module is disabled (not working or not ready)
module_status = False

# ===== Results directory path =====

RESULTS_DIR = Path("Results", "SurrogateModels")

# ===== CPACS inputs and outputs =====

cpacs_inout = CPACSInOut()

include_gui = True

# ----- Input -----

cpacs_inout.add_input(
    var_name="Objectives",
    var_type=str,
    default_value="cl",
    unit="-",
    descr="""Objective function list for the surrogate model to predict \n Warning !
    The parameters name must match the ones in the CSV file !""",
    xpath=SMTRAIN_XPATH + "/objective",
    gui=include_gui,
    gui_name="Objective",
    gui_group="Global settings",
)

cpacs_inout.add_input(
    var_name="trainig_part",
    var_type=float,
    default_value="0.9",
    descr="Defining the percentage of the data to use to train the model in [0;1]",
    xpath=SMTRAIN_XPATH + "/trainingPercentage",
    gui=include_gui,
    gui_name="% of training data",
    gui_group="Global settings",
)

cpacs_inout.add_input(
    var_name="Show_validation_plots",
    var_type=bool,
    default_value=True,
    unit=None,
    descr="Choose if the validation plots must be shown or not",
    xpath=SMTRAIN_XPATH + "/showPlots",
    gui=include_gui,
    gui_name="Show plots",
    gui_group="Global settings",
)

cpacs_inout.add_input(
    var_name="Aeromap",
    var_type=bool,
    default_value=False,
    unit=None,
    descr="""If only the aeromap has to be used""",
    xpath=SMTRAIN_XPATH + "/useAeromap",
    gui=include_gui,
    gui_name="Use an aeromap",
    gui_group="Aeromap settings",
)

cpacs_inout.add_input(
    var_name="",
    var_type=list,
    default_value=st.session_state.cpacs.get_aeromap_uid_list(),
    unit=None,
    descr="Name of the aero map to evaluate",
    xpath=SMTRAIN_XPATH + "/aeroMapUID",
    gui=True,
    gui_name="__AEROMAP_SELECTION",
    gui_group="Aeromap settings",
)

cpacs_inout.add_input(
    var_name="data_file",
    var_type="pathtype",
    default_value="-",
    descr="CSV file to be used to train a model",
    xpath=SMTRAIN_XPATH + "/trainFile",
    gui=include_gui,
    gui_name="Training dataset",
    gui_group="Training options",
)

cpacs_inout.add_input(
    var_name="type",
    var_type=list,
    default_value=["KRG", "KPLSK", "KPLS", "LS"],
    unit=None,
    descr="Type of surrogate model to choose from",
    xpath=SMTRAIN_XPATH + "/modelType",
    gui=include_gui,
    gui_name="Type of surrogate",
    gui_group="Training options",
)


# ----- Output -----

# cpacs_inout.add_output(
#     var_name='output',
#     default_value='-',
#     unit='1',
#     descr='Description of the output',
#     xpath='/cpacs/toolspecific/CEASIOMpy/test/myOutput',
# )
