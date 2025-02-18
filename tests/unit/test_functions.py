import sys
import pytest
from pandas import testing

# import pandas as pd
# import tempfile
# import inspect
# import string
# import re

sys.path.append("src/ontologise")

from utils import (
    extract_peopla_details,
    translate_attribute,
    extract_attribute_information,
    remove_all_leading_relation_markup,
    extract_relation_details,
    remove_all_leading_peopla_markup,
    extract_action_scope,
    remove_all_leading_action_markup,
    extract_action_details,
    is_action_group_directed,
)


# def translate_attribute(x):
#     return {
#         ":": "DATE",
#         "@": "AT",
#     }.get(x, x)


@pytest.mark.parametrize(
    "s_in, s_out_expected",
    # parameters are:
    # (1) the line as read in the Document
    # (2) the scope as expected
    [
        # TEST: Basic
        ("###	vs[A]", True),
        ("###	w/[A]", False),
        ("###	a[A]", None),
    ],
)
def test_is_action_group_directed(s_in, s_out_expected):
    s_out_observed = is_action_group_directed(s_in)
    assert s_out_observed == s_out_expected


@pytest.mark.parametrize(
    "s_in, s_out_expected",
    # parameters are:
    # (1) the line as read in the Document
    # (2) the scope as expected
    [
        # TEST: Basic
        ("###		A", "both"),
        ("###	(	A", "target"),
        ("###	((	A", None),
    ],
)
def test_extract_action_details(s_in, s_out_expected):
    s_out_observed = extract_action_scope(s_in)
    assert s_out_observed == s_out_expected


@pytest.mark.parametrize(
    "s_in, s_out_expected",
    # parameters are:
    # (1) the line as read in the Document
    # (2) the scope as expected
    [
        # TEST: Basic
        ("###		A", "both"),
        ("###	(	A", "target"),
        ("###	((	A", None),
    ],
)
def test_extract_action_scope(s_in, s_out_expected):
    s_out_observed = extract_action_scope(s_in)
    assert s_out_observed == s_out_expected


@pytest.mark.parametrize(
    "s,s_dict_expected",
    # parameters are:
    # (1) the attribute string (with leading ### and white space removed)
    # (2) the dictionary created from that string
    # - @[SCO, REN, LWH, Johnshill] (belongs to, e.g., OF)
    # - :[1762-06] (belongs to, e.g., BORN)
    # - :[1810-11->1818] (belongs to, e.g., EDUCATED)
    # - :[1819-12->] (belongs to, e.g., HEALTH)
    # - :[1820->]~ (belongs to, e.g., RESIDED)
    # - CONDITION[Typhus fever] (belongs to, e.g., HEALTH)
    # - ROLE[Clerk] (belongs to, e.g., OCC)
    # - DUR[1 yr] (belongs to, e.g., OCC)
    [
        # TEST:
        ("A", {"action_text": "A", "inheritance_flag": False}),
        ("A*", {"action_text": "A", "inheritance_flag": True}),
    ],
)
def test_extract_action_details(s, s_dict_expected):
    s_dict_observed = extract_action_details(s)
    assert s_dict_observed == s_dict_expected


@pytest.mark.parametrize(
    "s_in, s_out_expected",
    # parameters are:
    # (1) the line as read in the Document
    # (2) the line as expected following markup removal
    [
        # TEST: Basic
        ("###	(	X", "X"),
        ("###		Y", "Y"),
    ],
)
def test_remove_all_leading_action_markup(s_in, s_out_expected):
    s_out_observed = remove_all_leading_action_markup(s_in)
    assert s_out_observed == s_out_expected


@pytest.mark.parametrize(
    "s_in, s_out_expected",
    # parameters are:
    # (1) the line as read in the Document
    # (2) the line as expected following markup removal
    [
        # TEST: Basic
        ("###	>	*A*", ">	*A*"),
        ("###	>	>	*A*", ">	>	*A*"),
    ],
)
def test_remove_all_leading_relation_markup(s_in, s_out_expected):
    s_out_observed = remove_all_leading_relation_markup(s_in)
    assert s_out_observed == s_out_expected


@pytest.mark.parametrize(
    "s_in, s_out_expected",
    # parameters are:
    # (1) the line as read in the Document
    # (2) the line as expected following markup removal
    [
        # TEST: Basic
        ("###	[A, B]", "[A, B]"),
        ("###	[A, B](n){i-0}", "[A, B](n){i-0}"),
        ("###	[M'A, B]", "[M'A, B]"),
        ("###	vs[A, B]", "[A, B]"),
        ("###	w/[A, B]", "[A, B]"),
        ("###	(>	[A, B]", "[A, B]"),
        ("###	>	[A, B]", "[A, B]"),
        ("###	>	>	[A, B]", "[A, B]"),
        ("###	@[C, D]", "@[C, D]"),
    ],
)
def test_remove_all_leading_peopla_markup(s_in, s_out_expected):
    s_out_observed = remove_all_leading_peopla_markup(s_in)
    assert s_out_observed == s_out_expected


@pytest.mark.parametrize(
    "s_in, s_out_expected",
    # parameters are:
    # (1) the attribute tag/symbol in
    # (2) the expected tag/symbol out (as to be used in a dictionary)
    [
        # TEST: Basic
        (":", "DATE"),
        ("@", "AT"),
        ("X", "X"),
    ],
)
def test_translate_attribute(s_in, s_out_expected):
    s_out_observed = translate_attribute(s_in)
    assert s_out_observed == s_out_expected


@pytest.mark.parametrize(
    "s,s_dict_expected",
    # parameters are:
    # (1) the attribute string (with leading ### and white space removed)
    # (2) the dictionary created from that string
    # - @[SCO, REN, LWH, Johnshill] (belongs to, e.g., OF)
    # - :[1762-06] (belongs to, e.g., BORN)
    # - :[1810-11->1818] (belongs to, e.g., EDUCATED)
    # - :[1819-12->] (belongs to, e.g., HEALTH)
    # - :[1820->]~ (belongs to, e.g., RESIDED)
    # - CONDITION[Typhus fever] (belongs to, e.g., HEALTH)
    # - ROLE[Clerk] (belongs to, e.g., OCC)
    # - DUR[1 yr] (belongs to, e.g., OCC)
    [
        # TEST: @ symbol
        ("@[P]", {"AT": "P"}),
        # TEST: : date
        (":[YYYY-MM]", {"DATE": "YYYY-MM"}),
        # TEST: approximate : date
        (":[YYYY-MM]~", {"DATE": "approx. YYYY-MM"}),
        # TEST: all other attributes
        ("A[B]", {"A": "B"}),
    ],
)
def test_extract_attribute_information(s, s_dict_expected):
    s_dict_observed = extract_attribute_information(s)
    assert s_dict_observed == s_dict_expected


@pytest.mark.parametrize(
    "s,s_dict_expected",
    # parameters are:
    # (1) the relation string (SON/DAUG/FATHER/MOTHER)
    # (2) the relation depth
    [
        # TEST:
        (">	*MOTHER*", {"relation_text": "MOTHER", "relation_depth": 1}),
        # TEST:
        (">	>	*SON*", {"relation_text": "SON", "relation_depth": 2}),
        # TEST:
        (">	>	>	*DAUG*", {"relation_text": "DAUG", "relation_depth": 3}),
        
    ],
)
def test_extract_relation_details(s, s_dict_expected):
    s_dict_observed = extract_relation_details(s)
    assert s_dict_observed == s_dict_expected


@pytest.mark.parametrize(
    "exception_s",
    # parameters are:
    # (1) the relation string (SON/DAUG/FATHER/MOTHER)
    # (2) the relation depth
    [
        # TEST:
        (">	*SON *"),
        # TEST:
        (">	* SON*"),
        # TEST:
        (">	*S*"),
    ],
)
def test_extract_relation_exception(exception_s):
    with pytest.raises(Exception):
        extract_relation_details(exception_s)

@pytest.mark.parametrize(
    "s,s_dict_expected",
    # parameters are:
    # (1) the peopla string (with leading ### and white space removed)
    # (2) the parsed values from that string
    [
        # TEST: Basic
        (
            "###	[Surname, First]",
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
            "###	[Surname, First](local-id)",
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
            "###	[Surname, First]{global-id}",
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
            "###	[Surname, First]*",
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
            "###	[Surname, First](local-id){global-id}",
            {
                "place_flag": False,
                "with_flag": False,
                "content": "Surname, First",
                "local_id": "local-id",
                "global_id": "global-id",
                "inheritance_flag": False,
            },
        ),
        # TEST: includes @ flag
        (
            "###	@[Place, A](local-id){global-id}",
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
