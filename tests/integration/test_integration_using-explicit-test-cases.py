import pytest
from pathlib import Path
import pandas as pd
from pandas import testing
import sys

sys.path.append("src/ontologise")

from utils import Document, Peopla


BASE_DIR = Path(__file__).parents[1]
DATA_DIR = BASE_DIR / "integration" / "content" / "input"
SETTINGS_DIR = BASE_DIR / "integration" / "content" / "settings"
EXPECTED_DIR = BASE_DIR / "integration" / "content" / "expected"


# -----------------------------------------------------------------
# Integration test cases: peopla content, attributes of attributes
# -----------------------------------------------------------------
# -


@pytest.mark.parametrize(
    "test_name,settings_file,peopla_name,attribute,attribute_dictionary",
    # parameters are:
    # (1) content file
    # (2) settings file
    # (3) name of the peopla of interest
    # (4) name the attribute of interest
    # (5) attribute dictionary of the attribute of interest
    [
        # TEST: Are the peoplas extracted correctly
        # Context: 1 peopla with attributes of attributes
        (
            "peopla_content_D",
            "settings_basic.yaml",
            "A, B",
            "C",
            {"DATE": "YYYY-MM", "AT": "P, Q", "X": "Z"},
        ),
    ],
)
def test_primary_peopla_attributes_of_attributes(
    test_name, settings_file, peopla_name, attribute, attribute_dictionary
):

    content_f = DATA_DIR / f"{test_name}.txt"
    settings_f = SETTINGS_DIR / settings_file

    test_doc = Document(content_f, settings_f)
    test_doc.read_document()

    print("++++++++++++++++++++++++++++++++++++++++++++++++")
    print(f"Test name: {test_name}")
    print(f"File name: {content_f}")
    print(f"Settings : {settings_f}")
    print("++++++++++++++++++++++++++++++++++++++++++++++++")

    for p in test_doc.peoplas_primary:
        ### Print for information
        p.print_peopla()
        ### Collect global IDs
        if p.name == peopla_name:
            assert p.attributes[attribute] == attribute_dictionary

    print("++++++++++++++++++++++++++++++++++++++++++++++++")


@pytest.mark.parametrize(
    "test_name,settings_file,secondary_peopla_name,attribute,attribute_dictionary,primary_peopla_name",
    # parameters are:
    # (1) content file
    # (2) settings file
    # (3) name of the secondary peopla of interest
    # (4) name the attribute of interest
    # (5) attribute dictionary of the attribute of interest
    # (3) name of the primary peopla of interest (who should not have the same attributes)
    [
        # TEST: Are the peoplas extracted correctly
        # Context: 1 peopla with attributes of attributes
        (
            "secondary_peopla_content_B",
            "settings_basic.yaml",
            "D, E",
            "F",
            {
                "AT": "J",
                "DATE": "I",
                "G": "H",
            },
            "A, B",
        ),
    ],
)
def test_secondary_peopla_attributes_of_attributes(
    test_name, settings_file, secondary_peopla_name, attribute, attribute_dictionary, primary_peopla_name
):

    content_f = DATA_DIR / f"{test_name}.txt"
    settings_f = SETTINGS_DIR / settings_file

    test_doc = Document(content_f, settings_f)
    test_doc.read_document()

    print("++++++++++++++++++++++++++++++++++++++++++++++++")
    print(f"Test name: {test_name}")
    print(f"File name: {content_f}")
    print(f"Settings : {settings_f}")
    print("++++++++++++++++++++++++++++++++++++++++++++++++")

    ### The given attribute should only exist for the secondary Peopla
    for p in test_doc.peoplas_primary:
        ### Print for information
        p.print_peopla()
        ### Collect global IDs
        if p.name == primary_peopla_name:
            assert attribute not in p.attributes
    
    for p in test_doc.peoplas_secondary:
        ### Print for information
        p.print_peopla()
        ### Collect global IDs
        if p.name == secondary_peopla_name:
            assert p.attributes[attribute] == attribute_dictionary


    print("++++++++++++++++++++++++++++++++++++++++++++++++")


# -----------------------------------------------------------------
# Integration test cases: peopla content, checking Peopla numbers
# -----------------------------------------------------------------
# -

@pytest.mark.parametrize(
    "test_name,settings_file,expected_num_peoplas,expected_global_ids",
    # parameters are:
    # (1) content file
    # (2) settings file
    # (3) number of peoplas
    # (4) global IDs of those peoplas
    [
        # TEST: Are the peoplas extracted correctly
        # Context: 1 peopla, no global ID
        ("peopla_content_A", "settings_basic.yaml", 1, [None]),
        # TEST: Are the peoplas extracted correctly
        # Context: 1 peopla, with a global ID
        ("peopla_content_B", "settings_basic.yaml", 1, ["i-1"]),
        # TEST: Are the peoplas extracted correctly
        # Context: 2 peopla, the first has a global ID
        ("peopla_content_C", "settings_basic.yaml", 2, ["i-1", None]),
    ],
)
def test_peopla_content(
    test_name, settings_file, expected_num_peoplas, expected_global_ids
):

    content_f = DATA_DIR / f"{test_name}.txt"
    settings_f = SETTINGS_DIR / settings_file

    test_doc = Document(content_f, settings_f)
    test_doc.read_document()

    print("++++++++++++++++++++++++++++++++++++++++++++++++")
    print(f"Test name: {test_name}")
    print(f"File name: {content_f}")
    print(f"Settings : {settings_f}")
    print("++++++++++++++++++++++++++++++++++++++++++++++++")

    observed_global_ids = []
    for p in test_doc.all_peoplas:
        ### Print for information
        p.print_peopla()
        ### Collect global IDs
        observed_global_ids = observed_global_ids + [p.global_id]

    assert len(test_doc.all_peoplas) == expected_num_peoplas
    assert observed_global_ids == expected_global_ids

    print("++++++++++++++++++++++++++++++++++++++++++++++++")


# -----------------------------------------------------------------
# Integration test cases: one to one primary and secondary peoplas
# -----------------------------------------------------------------
# Note that these tests ONLY cover one to one action_groups between
# primary and secondary Peoplas. That is, if there is more than one
# secondary Peopla for a primary Peopla then this test will fail.
# -


@pytest.mark.parametrize(
    "test_name,settings_file,expected_primary_peoplas_names,expected_secondary_peoplas_names,action_group_key",
    # parameters are:
    # (1) content file
    # (2) settings file
    # (3) the expected names of the primary peoplas
    # (4) the expected names of the secondary peoplas
    # (5) the attribute that defines the action_group between the two
    [
        # TEST: Are the peoplas extracted correctly
        # Context: 1 primary peopla and 1 secondary peopla, related by J
        (
            "secondary_peopla_content_A",
            "settings_basic.yaml",
            ["A, B"],
            ["D, E"],
            "J",
        ),
        # TEST: Are the peoplas extracted correctly
        # Context: 1 primary peopla and 1 secondary peopla (with additional attributes), related by J
        (
            "secondary_peopla_content_B", "settings_basic.yaml", ["A, B"], ["D, E"], "J",
        ),
    ],
)
def test_secondary_peopla_content(
    test_name,
    settings_file,
    expected_primary_peoplas_names,
    expected_secondary_peoplas_names,
    action_group_key,
):

    content_f = DATA_DIR / f"{test_name}.txt"
    settings_f = SETTINGS_DIR / settings_file

    test_doc = Document(content_f, settings_f)
    test_doc.read_document()

    print("++++++++++++++++++++++++++++++++++++++++++++++++")
    print(f"Test name: {test_name}")
    print(f"File name: {content_f}")
    print(f"Settings : {settings_f}")
    print("++++++++++++++++++++++++++++++++++++++++++++++++")

    for (i, this_peopla) in enumerate(test_doc.peoplas_primary):
        this_peopla.print_peopla()
        assert this_peopla.name == expected_primary_peoplas_names[i]
        assert action_group_key in this_peopla.attributes
        assert type(this_peopla.attributes[action_group_key]["with"]) is Peopla
        assert (
            this_peopla.attributes[action_group_key]["with"].name
            == expected_secondary_peoplas_names[i]
        )

    for (i, this_peopla) in enumerate(test_doc.peoplas_secondary):
        this_peopla.print_peopla()
        assert this_peopla.name == expected_secondary_peoplas_names[i]

    assert len(test_doc.peoplas_primary) == len(expected_primary_peoplas_names)
    assert len(test_doc.peoplas_secondary) == len(expected_secondary_peoplas_names)

    print("++++++++++++++++++++++++++++++++++++++++++++++++")


# -----------------------------------------------------------------
# Integration test cases: shortcuts
# -----------------------------------------------------------------
# - Testing that one table shortcut works
# - Testing that multiple table shortcuts work

table_shortcuts_multiple_A_expected = pd.DataFrame(
    {
        "ENSLAVED_AT": ["PLACE", "PLACE", "PLACE",],
        "ENSLAVED_ATX": [
            "1800_TEXT_TEXT:00",
            "1800_TEXT_TEXT:00",
            "1800_TEXT_TEXT:00",
        ],
        "ENSLAVED_DATE": ["1800-01-01", "1800-01-01", "1800-01-01",],
        "GENDER": ["MALE", "MALE", "MALE",],
        "COLOUR": ["BLUE", "BLUE", "BLUE",],
        "X": ["L1", "M1", "N1",],
        "Y": ["", "M2", "N2",],
        "Z": ["", "M3", "N3",],
        "global_id": [None, None, None],
    }
)


table_shortcuts_multiple_B_expected = pd.DataFrame(
    {
        "ENSLAVED_AT": ["PLACE", "PLACE", "PLACE", "PLACE", "PLACE", "PLACE",],
        "ENSLAVED_ATX": [
            "1800_TEXT_TEXT:00",
            "1800_TEXT_TEXT:00",
            "1800_TEXT_TEXT:00",
            "1800_TEXT_TEXT:00",
            "1800_TEXT_TEXT:00",
            "1800_TEXT_TEXT:00",
        ],
        "ENSLAVED_DATE": [
            "1800-01-01",
            "1800-01-01",
            "1800-01-01",
            "1800-01-01",
            "1800-01-01",
            "1800-01-01",
        ],
        "GENDER": ["MALE", "MALE", "MALE", "FEMALE", "FEMALE", "FEMALE",],
        "COLOUR": ["BLUE", "BLUE", "BLUE", "BLUE", "BLUE", "BLUE",],
        "X": ["L1", "M1", "N1", "O1", "P1", "Q1",],
        "Y": ["", "M2", "N2", "", "P2", "Q2",],
        "Z": ["", "M3", "N3", "", "P3", "Q3",],
        "global_id": [None, None, None, None, None, None],
    }
)


table_shortcuts_multiple_C_expected = pd.DataFrame(
    {
        "ENSLAVED_AT": ["PLACE", "PLACE", "PLACE", "PLACE", "PLACE", "PLACE",],
        "ENSLAVED_ATX": [
            "1800_TEXT_TEXT:00",
            "1800_TEXT_TEXT:00",
            "1800_TEXT_TEXT:00",
            "1800_TEXT_TEXT:00",
            "1800_TEXT_TEXT:00",
            "1800_TEXT_TEXT:00",
        ],
        "ENSLAVED_DATE": [
            "1800-01-01",
            "1800-01-01",
            "1800-01-01",
            "1800-01-01",
            "1800-01-01",
            "1800-01-01",
        ],
        "GENDER": ["MALE", "MALE", "MALE", "FEMALE", "FEMALE", "FEMALE",],
        "COLOUR": ["BLUE", "BLUE", "BLUE", "RED", "RED", "RED",],
        "X": ["L1", "M1", "N1", "O1", "P1", "Q1",],
        "Y": ["", "M2", "N2", "", "P2", "Q2",],
        "Z": ["", "M3", "N3", "", "P3", "Q3",],
        "global_id": [None, None, None, None, None, None],
    }
)


table_shortcuts_multiple_D1_expected = pd.DataFrame(
    {
        "ENSLAVED_AT": ["PLACE", "PLACE", "PLACE", "PLACE", "PLACE", "PLACE",],
        "ENSLAVED_ATX": [
            "1800_TEXT_TEXT:00",
            "1800_TEXT_TEXT:00",
            "1800_TEXT_TEXT:00",
            "1800_TEXT_TEXT:00",
            "1800_TEXT_TEXT:00",
            "1800_TEXT_TEXT:00",
        ],
        "ENSLAVED_DATE": [
            "1800-01-01",
            "1800-01-01",
            "1800-01-01",
            "1800-01-01",
            "1800-01-01",
            "1800-01-01",
        ],
        "GENDER": ["MALE", "MALE", "MALE", "FEMALE", "FEMALE", "FEMALE",],
        "COLOUR": ["BLUE", "BLUE", "BLUE", "RED", "RED", "RED",],
        "SHAPE": ["CIRCLE", "CIRCLE", "CIRCLE", None, None, None,],
        "X": ["L1", "M1", "N1", "O1", "P1", "Q1",],
        "Y": ["", "M2", "N2", "", "P2", "Q2",],
        "Z": ["", "M3", "N3", "", "P3", "Q3",],
        "global_id": [None, None, None, None, None, None],
    }
)


table_shortcuts_multiple_D2_expected = pd.DataFrame(
    {
        "ENSLAVED_AT": ["PLACE", "PLACE", "PLACE", "PLACE", "PLACE", "PLACE",],
        "ENSLAVED_ATX": [
            "1800_TEXT_TEXT:00",
            "1800_TEXT_TEXT:00",
            "1800_TEXT_TEXT:00",
            "1800_TEXT_TEXT:00",
            "1800_TEXT_TEXT:00",
            "1800_TEXT_TEXT:00",
        ],
        "ENSLAVED_DATE": [
            "1800-01-01",
            "1800-01-01",
            "1800-01-01",
            "1800-01-01",
            "1800-01-01",
            "1800-01-01",
        ],
        "GENDER": ["MALE", "MALE", "MALE", "FEMALE", "FEMALE", "FEMALE",],
        "COLOUR": ["BLUE", "BLUE", "BLUE", "RED", "RED", "RED",],
        "SHAPE": [None, None, None, "CIRCLE", "CIRCLE", "CIRCLE",],
        "X": ["L1", "M1", "N1", "O1", "P1", "Q1",],
        "Y": ["", "M2", "N2", "", "P2", "Q2",],
        "Z": ["", "M3", "N3", "", "P3", "Q3",],
        "global_id": [None, None, None, None, None, None],
    }
)

table_shortcuts_multiple_E_expected = pd.DataFrame(
    {
        "ENSLAVED_AT": ["PLACE", "PLACE", "PLACE", "PLACE", "PLACE", "PLACE",],
        "ENSLAVED_ATX": [
            "1800_TEXT_TEXT:00",
            "1800_TEXT_TEXT:00",
            "1800_TEXT_TEXT:00",
            "1800_TEXT_TEXT:00",
            "1800_TEXT_TEXT:00",
            "1800_TEXT_TEXT:00",
        ],
        "ENSLAVED_DATE": [
            "1800-01-01",
            "1800-01-01",
            "1800-01-01",
            "1800-01-01",
            "1800-01-01",
            "1800-01-01",
        ],
        "GENDER": ["MALE", "MALE", "MALE", "FEMALE", "FEMALE", "FEMALE",],
        "COLOUR": ["BLUE", "BLUE", "BLUE", None, None, None,],
        "X": ["L1", "M1", "N1", "O1", "P1", "Q1",],
        "Y": ["", "M2", "N2", "", "P2", "Q2",],
        "Z": ["", "M3", "N3", "", "P3", "Q3",],
        "global_id": [None, None, None, None, None, None],
    }
)


table_shortcuts_multiple_F_expected = pd.DataFrame(
    {
        "ENSLAVED_AT": ["PLACE", "PLACE", "PLACE",],
        "ENSLAVED_ATX": [
            "1800_TEXT_TEXT:00",
            "1800_TEXT_TEXT:00",
            "1800_TEXT_TEXT:00",
        ],
        "ENSLAVED_DATE": ["1800-01-01", "1800-01-01", "1800-01-01",],
        "GENDER": ["MALE", "MALE", "MALE",],
        "COLOUR": ["BLUE", "BLUE", "BLUE",],
        "X": ["L1", "M1", "N1",],
        "Y": ["", "M2", "N2",],
        "Z": ["", "M3", "N3",],
        "global_id": ["i-1", "j-2", "k-3"],
    }
)


@pytest.mark.parametrize(
    "test_name,settings_file,expected_df",
    [
        # TEST: Are multiple table shortcut values inherited appropriately in
        #       the eventual data table?
        # Context: 1 table, 2 shortcuts
        (
            "table_shortcuts_multiple_A",
            "settings_colour_shortcuts.yaml",
            table_shortcuts_multiple_A_expected,
        ),
        # TEST: Are multiple table shortcut values inherited appropriately in
        #       the eventual data table?
        # Context: 2 tables, 2 shortcuts on each, 1 overlapping shortcut
        (
            "table_shortcuts_multiple_B",
            "settings_colour_shortcuts.yaml",
            table_shortcuts_multiple_B_expected,
        ),
        # TEST: Are multiple table shortcut values inherited appropriately in
        #       the eventual data table?
        # Context: 2 tables, 2 shortcuts on each, no overlapping shortcuts
        (
            "table_shortcuts_multiple_C",
            "settings_colour_shortcuts.yaml",
            table_shortcuts_multiple_C_expected,
        ),
        # TEST: Are multiple table shortcut values inherited appropriately in
        #       the eventual data table?
        # Context: 2 tables, 2 shortcuts on each, no overlapping shortcuts, one
        #          additional shortcut on FIRST table
        (
            "table_shortcuts_multiple_D1",
            "settings_colour-shape_shortcuts.yaml",
            table_shortcuts_multiple_D1_expected,
        ),
        # TEST: Are multiple table shortcut values inherited appropriately in
        #       the eventual data table?
        # Context: 2 tables, 2 shortcuts on each, no overlapping shortcuts, one
        #          additional shortcut on SECOND table
        pytest.param(
            "table_shortcuts_multiple_D2",
            "settings_colour-shape_shortcuts.yaml",
            table_shortcuts_multiple_D2_expected,
            marks=pytest.mark.xfail(reason="Bug (see issue #36)"),
        ),
        # TEST: Are multiple table shortcut values inherited appropriately in
        #       the eventual data table?
        # Context: 2 tables, 2 shortcuts on one, 1 on the other, no overlapping shortcuts
        (
            "table_shortcuts_multiple_E",
            "settings_colour_shortcuts.yaml",
            table_shortcuts_multiple_E_expected,
        ),
        # TEST: Are global IDs being picked up and assigned correctly?
        # Context: 1 table, 2 shortcuts on one, 1 on the other, no overlapping shortcuts
        (
            "table_shortcuts_multiple_F",
            "settings_colour_shortcuts.yaml",
            table_shortcuts_multiple_F_expected,
        ),
    ],
)
def test_datapoint_extraction(test_name, settings_file, expected_df):

    content_f = DATA_DIR / f"{test_name}.txt"
    settings_f = SETTINGS_DIR / settings_file

    test_doc = Document(content_f, settings_f)
    test_doc.read_document()
    observed_df = test_doc.data_points_df

    print("++++++++++++++++++++++++++++++++++++++++++++++++")
    print(f"Test name: {test_name}")
    print(f"File name: {content_f}")
    print(f"Settings : {settings_f}")
    print("++++++++++++++++++++++++++++++++++++++++++++++++")
    print("OBSERVED\n")
    print(observed_df)
    print("++++++++++++++++++++++++++++++++++++++++++++++++")
    print("EXPECTED\n")
    print(expected_df)
    print("++++++++++++++++++++++++++++++++++++++++++++++++")

    testing.assert_frame_equal(observed_df, expected_df)
