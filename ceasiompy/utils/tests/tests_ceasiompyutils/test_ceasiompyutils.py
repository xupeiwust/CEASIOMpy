"""
CEASIOMpy: Conceptual Aircraft Design Software

Developed by CFS ENGINEERING, 1015 Lausanne, Switzerland

Test functions for 'utils/ceasiompyutils.py'


| Author : Aidan Jungo
| Creation: 2022-02-10

"""

# =================================================================================================
#   IMPORTS
# =================================================================================================

import os
import shutil
from pathlib import Path
import pytest
from ceasiompy.utils.ceasiompyutils import (
    aircraft_name,
    change_working_dir,
    get_aeromap_list_from_xpath,
    get_install_path,
    get_part_type,
    get_results_directory,
    remove_file_type_in_dir,
    run_software,
)
from ceasiompy.utils.commonpaths import CPACS_FILES_PATH
from cpacspy.cpacsfunctions import open_tixi
from cpacspy.cpacspy import CPACS

MODULE_DIR = Path(__file__).parent
TMP_DIR = Path(MODULE_DIR, "tmp")
LOGFILE = Path(TMP_DIR, "logfile_python.log")

# =================================================================================================
#   CLASSES
# =================================================================================================


# =================================================================================================
#   FUNCTIONS
# =================================================================================================


def test_change_working_dir():
    """Test the function (context manager) change_working_dir."""

    default_cwd = Path.cwd()

    os.chdir(str(MODULE_DIR))

    with change_working_dir(TMP_DIR):
        assert Path.cwd() == TMP_DIR

    assert Path.cwd() == MODULE_DIR

    os.chdir(str(default_cwd))


def test_get_aeromap_list_from_xpath():

    cpacs = CPACS(Path(CPACS_FILES_PATH, "D150_simple.xml"))

    not_define_xpath = "/cpacs/toolspecific/CEASIOMpy/newListOfAeromap"
    aeromap_list = get_aeromap_list_from_xpath(cpacs, not_define_xpath)
    assert aeromap_list == ["aeromap_empty", "test_apm"]

    not_define_xpath_2 = "/cpacs/toolspecific/CEASIOMpy/newListOfAeromap2"
    aeromap_list = get_aeromap_list_from_xpath(cpacs, not_define_xpath_2, empty_if_not_found=True)
    assert aeromap_list == []

    cpacs.tixi.updateTextElement(not_define_xpath, "test_apm")
    aeromap_list = get_aeromap_list_from_xpath(cpacs, not_define_xpath)
    assert aeromap_list == ["test_apm"]


def test_get_results_directory():

    with change_working_dir(TMP_DIR):

        results_dir = get_results_directory("ExportCSV")
        assert results_dir == Path(Path.cwd(), "Results", "ExportCSV")

        results_dir = get_results_directory("CPACS2SUMO")
        assert results_dir == Path(Path.cwd(), "Results", "CPACS2SUMO")

        if results_dir.parent.exists():
            shutil.rmtree(results_dir.parent)

    with pytest.raises(ValueError):
        results_dir = get_results_directory("NotExistingModule")


@pytest.mark.skip(reason="Not implemented yet")
def test_run_module():
    """Test the function run_module."""

    # TODO: how to test this function?


def test_get_install_path():
    """Test the function 'get_install_path'."""

    assert isinstance(get_install_path("python"), Path)

    assert get_install_path("NotExistingSoftware") is None

    # with pytest.raises(SoftwareNotInstalled):
    #    get_install_path("NotExistingSoftware", raise_error=True)


def test_run_software():
    """Test the function 'run_software'."""

    run_software("python", ["-c", "print('Hello World!')"], TMP_DIR)

    assert LOGFILE.exists()

    with open(LOGFILE, "r") as f:
        assert "Hello World!" in f.readlines()[0]


def test_aircraft_name():
    """Test the function aircraft_name."""

    # Get name form the CPACS file path
    cpacs_in = Path(CPACS_FILES_PATH, "D150_simple.xml")
    assert aircraft_name(cpacs_in) == "D150"

    # Get name form TIXI handle
    tixi = open_tixi(cpacs_in)
    assert aircraft_name(tixi) == "D150"


def test_get_part_type():
    """Test the function get_part_type on the D150"""

    cpacs_in = Path(CPACS_FILES_PATH, "simple_engine.xml")
    cpacs = CPACS(cpacs_in)

    tixi = cpacs.tixi

    assert get_part_type(tixi, "Wing") == "wing"
    assert get_part_type(tixi, "Wing_mirrored") == "wing"
    assert get_part_type(tixi, "SimpleFuselage") == "fuselage"
    assert get_part_type(tixi, "SimpleEngine") == "engine"
    assert get_part_type(tixi, "SimpleEngine_mirrored") == "engine"
    assert get_part_type(tixi, "Pylon") == "pylon"
    assert get_part_type(tixi, "Pylon_mirrored") == "pylon"


def test_remove_file_type_in_dir():
    """Test the function 'remove_file_type_in_dir'"""

    with pytest.raises(FileNotFoundError):
        remove_file_type_in_dir(Path("ThisDirectoryDoesNotExist"), ".txt")

    test_file_1 = Path(TMP_DIR, "test_file.txt")
    test_file_1.touch()

    test_file_2 = Path(TMP_DIR, "test_file.brep")
    test_file_2.touch()

    remove_file_type_in_dir(TMP_DIR, [".txt", ".brep"])

    assert not test_file_1.exists()
    assert not test_file_2.exists()
    assert LOGFILE.exists()


# =================================================================================================
#    MAIN
# =================================================================================================

if __name__ == "__main__":

    print("Test configfile.py")
    print("To run test use the following command:")
    print(">> pytest -v")
