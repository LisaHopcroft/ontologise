import sys
import pytest
from pandas import testing

# import pandas as pd
# import tempfile
# import inspect
# import string
# import re

sys.path.append("src/ontologise")

from utils import extract_peopla_details


@pytest.mark.parametrize(
    "s,s_dict_expected",
    # parameters are:
    # (1) the peopla string (with leading ### and white space removed)
    # (2) the parsed values from that string
    [
        # TEST: Basic
        (
            "[Surname, First]",
            {
                "place_flag": False,
                "with_flag": False,
                "content": "Surname, First",
                "local_id": None,
                "global_id": None,
                "inheritance_flag": False,
            },
        ),
        # TEST: Basic with local ID
        (
            "[Surname, First](local-id)",
            {
                "place_flag": False,
                "with_flag": False,
                "content": "Surname, First",
                "local_id": "local-id",
                "global_id": None,
                "inheritance_flag": False,
            },
        ),
        # TEST: Basic with global ID
        (
            "[Surname, First]{global-id}",
            {
                "place_flag": False,
                "with_flag": False,
                "content": "Surname, First",
                "local_id": None,
                "global_id": "global-id",
                "inheritance_flag": False,
            },
        ),
        # TEST: Basic with inheritance
        (
            "[Surname, First]*",
            {
                "place_flag": False,
                "with_flag": False,
                "content": "Surname, First",
                "local_id": None,
                "global_id": None,
                "inheritance_flag": True,
            },
        ),
        # TEST: Basic with local and global IDs
        (
            "[Surname, First](local-id){global-id}",
            {
                "place_flag": False,
                "with_flag": False,
                "content": "Surname, First",
                "local_id": "local-id",
                "global_id": "global-id",
                "inheritance_flag": False,
            },
        ),
        # TEST: includes w/ attribute
        (
            "w/[Surname, First](local-id){global-id}",
            {
                "place_flag": False,
                "with_flag": True,
                "content": "Surname, First",
                "local_id": "local-id",
                "global_id": "global-id",
                "inheritance_flag": False,
            },
        ),
        # TEST: includes @ flag
        (
            "@[Place, A](local-id){global-id}",
            {
                "place_flag": True,
                "with_flag": False,
                "content": "Place, A",
                "local_id": "local-id",
                "global_id": "global-id",
                "inheritance_flag": False,
            },
        ),
    ],
)
def test_extract_peopla_details(s, s_dict_expected):
    s_dict_observed = extract_peopla_details(s)
    assert s_dict_observed == s_dict_expected
