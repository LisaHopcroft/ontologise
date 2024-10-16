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

table_shortcuts_multiple_expected = pd.DataFrame(
    {
        'ENSLAVED_AT': ['PLACE', 'PLACE', 'PLACE', ],
        'ENSLAVED_ATX': ['1800_TEXT_TEXT:00', '1800_TEXT_TEXT:00', '1800_TEXT_TEXT:00', ],
        'ENSLAVED_DATE': ['1800-01-01', '1800-01-01', '1800-01-01', ],
        'GENDER': ['MALE', 'MALE', 'MALE', ],
        'COLOUR': ['BLUE', 'BLUE', 'BLUE', ],
        'X': ['L1', 'M1', 'N1', ],
        'Y': ['', 'M2', 'N2', ],
        'Z': ['', 'M3', 'N3', ],
    }
)

@pytest.mark.integrationtest

def test_multiple_shortcuts(
    test_name     = "table_shortcuts_multiple",
    settings_file = "settings_colour_shortcuts.yaml",
    expected_df   = table_shortcuts_multiple_expected
    ):

    content_f = DATA_DIR / f"{test_name}.txt"
    settings_f = SETTINGS_DIR / settings_file

    test_doc = Document(content_f,settings_f)
    test_doc.read_document()
    observed_df = test_doc.data_points_df

    testing.assert_frame_equal(observed_df, expected_df)

