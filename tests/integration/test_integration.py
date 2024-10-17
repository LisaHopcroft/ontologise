import sys
import pytest
from pathlib import Path
import pandas as pd
import tempfile
import inspect
import string
import re
import os
from pandas import testing

sys.path.append("src/ontologise")
sys.path.append("tests/integration/content")

BASE_DIR = Path(__file__).parents[1]
DATA_DIR = BASE_DIR / "integration" / "content" / "input"
SETTINGS_DIR = BASE_DIR / "integration" / "content" / "settings"
EXPECTED_DIR = BASE_DIR / "integration" / "content" / "expected"


from utils import Document, read_settings_file


### -----------------------------------------------------------------
### Integration test cases
### -----------------------------------------------------------------
### - Testing that one table shortcut works
### - Testing that multiple table shortcuts work
###   input: content/table_shortcuts_multiple.txt

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
    }
)


@pytest.mark.parametrize(
    "test_name,settings_file,expected_df",
    [
        ### TEST: Are multiple table shortcut values inherited appropriately in
        ###       the eventual data table?
        ### Context: 1 table, 2 shortcuts
        (
            "table_shortcuts_multiple_A",
            "settings_colour_shortcuts.yaml",
            table_shortcuts_multiple_A_expected,
        ),
        ### TEST: Are multiple table shortcut values inherited appropriately in
        ###       the eventual data table?
        ### Context: 2 tables, 2 shortcuts on each, 1 overlapping shortcut
        (
            "table_shortcuts_multiple_B",
            "settings_colour_shortcuts.yaml",
            table_shortcuts_multiple_B_expected,
        ),
        ### TEST: Are multiple table shortcut values inherited appropriately in
        ###       the eventual data table?
        ### Context: 2 tables, 2 shortcuts on each, no overlapping shortcuts
        (
            "table_shortcuts_multiple_C",
            "settings_colour_shortcuts.yaml",
            table_shortcuts_multiple_C_expected,
        ),
        ### TEST: Are multiple table shortcut values inherited appropriately in
        ###       the eventual data table?
        ### Context: 2 tables, 2 shortcuts on each, no overlapping shortcuts, one
        ###          additional shortcut on FIRST table
        (
            "table_shortcuts_multiple_D1",
            "settings_colour-shape_shortcuts.yaml",
            table_shortcuts_multiple_D1_expected,
        ),
        ### TEST: Are multiple table shortcut values inherited appropriately in
        ###       the eventual data table?
        ### Context: 2 tables, 2 shortcuts on each, no overlapping shortcuts, one
        ###          additional shortcut on SECOND table
        pytest.param(
            "table_shortcuts_multiple_D2",
            "settings_colour-shape_shortcuts.yaml",
            table_shortcuts_multiple_D2_expected,
            marks=pytest.mark.xfail(reason="Bug (see issue #36)"),
        ),
        ### TEST: Are multiple table shortcut values inherited appropriately in
        ###       the eventual data table?
        ### Context: 2 tables, 2 shortcuts on one, 1 on the other, no overlapping shortcuts
        (
            "table_shortcuts_multiple_E",
            "settings_colour_shortcuts.yaml",
            table_shortcuts_multiple_E_expected,
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
    print("OBSERVED\n")
    print(observed_df)
    print("++++++++++++++++++++++++++++++++++++++++++++++++")
    print("EXPECTED\n")
    print(expected_df)
    print("++++++++++++++++++++++++++++++++++++++++++++++++")

    testing.assert_frame_equal(observed_df, expected_df)
