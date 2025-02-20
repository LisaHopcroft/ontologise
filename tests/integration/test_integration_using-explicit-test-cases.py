import pytest
from pathlib import Path
import pandas as pd
from pandas import testing
import sys
from collections import defaultdict

sys.path.append("src/ontologise")

from utils import Document, Peopla, Peorel


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
def test_peopla_attributes_of_attributes(
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

    for p in test_doc.all_peoplas:
        ### Print for information
        print(p)
        ### Collect global IDs
        if p.name == peopla_name:
            assert p.attributes[attribute] == attribute_dictionary

    print("++++++++++++++++++++++++++++++++++++++++++++++++")


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
            "pedigree_attributes_A",
            "settings_basic.yaml",
            "C, D",
            "E",
            {"DATE": "YYYY-MM", "AT": "P, Q", "X": "Z"},
        ),
    ],
)
def test_peopla_attributes_in_pedigrees(
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

    for p in test_doc.all_peoplas:
        ### Print for information
        print(p)
        ### Collect global IDs
        if p.name == peopla_name:
            assert p.attributes[attribute] == attribute_dictionary

    print("++++++++++++++++++++++++++++++++++++++++++++++++")


# -----------------------------------------------------------------
# Integration test cases: peopla content evidence
# -----------------------------------------------------------------
# -


@pytest.mark.parametrize(
    "test_name,settings_file,peopla_name,expected_evidence_list",
    # parameters are:
    # (1) content file
    # (2) settings file
    # (3) name of the peopla of interest
    # (4) list of line numbers for evidence
    [
        # TEST: Are the peoplas evidenced correctly
        # Context: 1 peopla with one line of evidence
        ("peopla_content_D", "settings_basic.yaml", "A, B", [7],),
        # TEST: Are the peoplas evidenced correctly
        # Context: 1 peopla with multiple lines of evidence
        ("peopla_content_E1", "settings_basic.yaml", "A, B", [7, 11],),
        # TEST: Are the peoplas evidenced correctly
        # Context: 1 peopla with one line of evidence as a Peopla target
        ("peopla_content_E2", "settings_basic.yaml", "C, D", [9],),
        # TEST: Are the peoplas evidenced correctly
        # Context: 1 peopla with multiple lines of evidence
        ("peopla_content_F9", "settings_basic.yaml", "A, B", [7, 18],),
    ],
)
def test_peopla_evidence_recording(
    test_name, settings_file, peopla_name, expected_evidence_list
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

    for p in test_doc.all_peoplas:
        ### Print for information
        print(p)
        ### Collect global IDs
        if p.name == peopla_name:
            assert p.evidence_reference == expected_evidence_list

    print("++++++++++++++++++++++++++++++++++++++++++++++++")


# -----------------------------------------------------------------
# Integration test cases: peorel content evidence
# -----------------------------------------------------------------
# -


@pytest.mark.parametrize(
    "test_name,settings_file,peopla_is_name,peopla_relation,peopla_to_name,expected_evidence_list",
    # parameters are:
    # (1) content file
    # (2) settings file
    # (3) name of the peopla of interest
    # (4) list of line numbers for evidence
    [
        # TEST: Are the peorels evidenced correctly
        # Context: 1 peorel with one line of evidence
        ("peorel_content_A1", "settings_basic.yaml", "B", "SON", "A", [6],),
        # TEST: Are the peorels evidenced correctly
        # Context: 1 peorel with two lines of evidence
        ("peorel_content_A2", "settings_basic.yaml", "B", "SON", "A", [6, 10],),
        # TEST: Are the peorels evidenced correctly
        # Context: 1 peorel with one line of evidence
        ("peorel_content_B1", "settings_basic.yaml", "B", "SON", "A", [7],),
        # TEST: Are the peorels evidenced correctly
        # Context: 1 peorel with one line of evidence
        ("peorel_content_B2", "settings_basic.yaml", "B", "SON", "A", [7],),
    ],
)
def test_peorel_evidence_recording(
    test_name,
    settings_file,
    peopla_is_name,
    peopla_relation,
    peopla_to_name,
    expected_evidence_list,
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

    for p in test_doc.all_peorels:
        ### Print for information
        print(p)
        ### Collect global IDs
        if (
            p.peopla_is.name == peopla_is_name
            and p.peopla_to.name == peopla_to_name
            and p.relation_text == peopla_relation
        ):
            assert p.evidence_reference == expected_evidence_list

    print("++++++++++++++++++++++++++++++++++++++++++++++++")


# -----------------------------------------------------------------
# Integration test cases: peorel content evidence
# -----------------------------------------------------------------
# -


@pytest.mark.parametrize(
    "test_name,settings_file,peopla_source,peopla_target,action_text,expected_evidence_list",
    # NB. These will only work where there is only one target peopla
    # parameters are:
    # (1) content file
    # (2) settings file
    # (3) name of the source peopla
    # (4) name of the target peopla
    # (5) the action text
    # (6) list of line numbers for evidence
    [
        # TEST: Are the ActionGroups evidenced correctly
        # Context: 1 ActionGroups with one line of evidence
        (
            "secondary_peopla_content_A",
            "settings_basic.yaml",
            "A, B",
            "C, D",
            "J",
            [10],
        ),
        # TEST: Are the ActionGroups evidenced correctly
        # Context: 1 ActionGroups with one line of evidence
        (
            "secondary_peopla_content_B",
            "settings_basic.yaml",
            "A, B",
            "C, D",
            "J",
            [14],
        ),
        # TEST: Are the ActionGroups evidenced correctly
        # Context: 2 ActionGroups with one line of evidence
        ("peopla_content_E1", "settings_basic.yaml", "A, B", "C, D", "P", [9],),
        # TEST: Are the ActionGroups evidenced correctly
        # Context: 2 ActionGroups with one line of evidence
        ("peopla_content_E1", "settings_basic.yaml", "A, B", "E, F", "Q", [13],),
        # TEST: Are the ActionGroups evidenced correctly
        # Context: 2 ActionGroups with one line of evidence
        ("peopla_content_E2", "settings_basic.yaml", "A, B", "C, D", "P", [10],),
        # TEST: Are the ActionGroups evidenced correctly
        # Context: 2 ActionGroups with one line of evidence
        ("peopla_content_E3", "settings_basic.yaml", "A, B", "C, D", "Y", [11],),
        # TEST: Are the ActionGroups evidenced correctly
        # Context: 2 ActionGroups with one line of evidence
        ("peopla_content_Ex", "settings_basic.yaml", "A, B", "C, D", "Y", [11],),
        # TEST: Are the ActionGroups evidenced correctly
        # Context: 2 ActionGroups with one line of evidence
        ("peopla_content_Ex", "settings_basic.yaml", "A, B", "E, F", "Z", [16],),
        # TEST: Are the ActionGroups evidenced correctly
        # Context: 2 ActionGroups with one line of evidence
        ("peopla_content_F9", "settings_basic.yaml", "A, B", "C, D", "Y", [16],),
    ],
)
def test_actiongroup_evidence_recording_single_targets(
    test_name,
    settings_file,
    peopla_source,
    peopla_target,
    action_text,
    expected_evidence_list,
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

    for p in test_doc.all_action_groups:
        ### Print for information
        print(p)
        ### Collect global IDs
        if (
            p.type == action_text
            and p.source_peopla.name == peopla_source
            and p.target_peoplas.pop().name == peopla_target
        ):
            assert p.evidence_reference == expected_evidence_list

    print("++++++++++++++++++++++++++++++++++++++++++++++++")


@pytest.mark.parametrize(
    "test_name,settings_file,expected_num_action_groups,peopla_source,expected_target_peoplas,expected_action_text,expected_evidence_list",
    # parameters are:
    # (1) content file
    # (2) settings file
    # (3) name of the source peopla
    # (4) list of the multiple target peopla
    # (5) the action text
    # (6) list of line numbers for evidence
    [
        (
            # TEST: Are the ActionGroups evidenced correctly
            # Context: 1 ActionGroups with multiple targets
            # TEST: Are the ActionGroups evidenced correctly
            # Context: 1 ActionGroups with multiple targets
            "secondary_peopla_content_C",
            "settings_basic.yaml",
            1,
            "A, B",
            ["D, E", "F, G"],
            "J",
            [11],
        ),
        (
            # TEST: Are the ActionGroups evidenced correctly
            # Context: 1 ActionGroups with multiple targets plus
            #          additional metadata
            # TEST: Are the ActionGroups evidenced correctly
            # Context: 1 ActionGroups with multiple targets plus
            #          additional metadata
            "secondary_peopla_content_D",
            "settings_basic.yaml",
            1,
            "A, B",
            ["D, E", "F, G"],
            "J",
            [15],
        ),
        (
            # TEST: Are the ActionGroups evidenced correctly
            # Context: 1 ActionGroups with multiple targets plus
            #          an intervening relation that could confuse
            #          things
            # TEST: Are the ActionGroups evidenced correctly
            # Context: 1 ActionGroups with multiple targets plus
            #          an intervening relation that could confuse
            #          things
            "secondary_peopla_content_E",
            "settings_basic.yaml",
            1,
            "A, B",
            ["D, E", "F, G"],
            "J",
            [13],
        ),
    ],
)
def test_actiongroup_evidence_recording_multiple_targets(
    test_name,
    settings_file,
    expected_num_action_groups,
    peopla_source,
    expected_target_peoplas,
    expected_action_text,
    expected_evidence_list,
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

    assert len(test_doc.all_action_groups)==expected_num_action_groups

    all_passing = 0

    for p in test_doc.all_action_groups:
        ### Print for information
        print(p)

        if (
            p.type == expected_action_text
            and p.source_peopla.name == peopla_source
        ):

            observed_target_peoplas = []
            for tp in p.target_peoplas:
                observed_target_peoplas.append(tp.name)

            assert len(observed_target_peoplas) == len(expected_target_peoplas)
            assert sorted(observed_target_peoplas) == sorted(expected_target_peoplas)
            assert p.evidence_reference == expected_evidence_list

            all_passing += 1
    
    assert all_passing == expected_num_action_groups

    print("++++++++++++++++++++++++++++++++++++++++++++++++")


@pytest.mark.parametrize(
    "test_name,settings_file,peopla_name,action_list",
    # parameters are:
    # (1) content file
    # (2) settings file
    # (3) name of the peopla of interest
    # (4) name the attribute of interest
    # (5) attribute dictionary of the attribute of interest
    [
        # TEST: Are the peoplas extracted correctly
        # Context: 1 peopla with attributes of attributes
        ("peopla_content_D", "settings_basic.yaml", "A, B", ["V", "W", "Z"],),
    ],
)
def test_split_peopla_attributes(test_name, settings_file, peopla_name, action_list):

    content_f = DATA_DIR / f"{test_name}.txt"
    settings_f = SETTINGS_DIR / settings_file

    test_doc = Document(content_f, settings_f)
    test_doc.read_document()

    print("++++++++++++++++++++++++++++++++++++++++++++++++")
    print(f"Test name: {test_name}")
    print(f"File name: {content_f}")
    print(f"Settings : {settings_f}")
    print("++++++++++++++++++++++++++++++++++++++++++++++++")

    for p in test_doc.all_peoplas:
        ### Print for information
        print(p)
        ### Collect global IDs
        if p.name == peopla_name:
            assert list(p.attributes.keys()).sort() == action_list.sort()

    print("++++++++++++++++++++++++++++++++++++++++++++++++")


# @pytest.mark.parametrize(
#     "test_name,settings_file,secondary_peopla_name,attribute,attribute_dictionary,primary_peopla_name",
#     # parameters are:
#     # (1) content file
#     # (2) settings file
#     # (3) name of the secondary peopla of interest
#     # (4) name the attribute of interest
#     # (5) attribute dictionary of the attribute of interest
#     # (3) name of the primary peopla of interest (who should not have the same attributes)
#     [
#         # TEST: Are the peoplas extracted correctly
#         # Context: 1 peopla with attributes of attributes
#         (
#             "secondary_peopla_content_B",
#             "settings_basic.yaml",
#             "D, E",
#             "F",
#             {"AT": "J", "DATE": "I", "G": "H",},
#             "A, B",
#         ),
#     ],
# )
# def test_secondary_peopla_attributes_of_attributes(
#     test_name,
#     settings_file,
#     secondary_peopla_name,
#     attribute,
#     attribute_dictionary,
#     primary_peopla_name,
# ):

#     content_f = DATA_DIR / f"{test_name}.txt"
#     settings_f = SETTINGS_DIR / settings_file

#     test_doc = Document(content_f, settings_f)
#     test_doc.read_document()

#     print("++++++++++++++++++++++++++++++++++++++++++++++++")
#     print(f"Test name: {test_name}")
#     print(f"File name: {content_f}")
#     print(f"Settings : {settings_f}")
#     print("++++++++++++++++++++++++++++++++++++++++++++++++")

#     ### The given attribute should only exist for the secondary Peopla
#     for p in test_doc.peoplas_primary:
#         ### Print for information
#         p.print_peopla()
#         ### Collect global IDs
#         if p.name == primary_peopla_name:
#             assert attribute not in p.attributes

#     for p in test_doc.peoplas_secondary:
#         ### Print for information
#         p.print_peopla()
#         ### Collect global IDs
#         if p.name == secondary_peopla_name:
#             assert p.attributes[attribute] == attribute_dictionary

#     print("++++++++++++++++++++++++++++++++++++++++++++++++")


# -----------------------------------------------------------------
# Integration test cases: peopla content, checking Peopla numbers
# -----------------------------------------------------------------
# -


@pytest.mark.parametrize(
    "test_name,settings_file,source_peopla,expected_action_group_info",
    # parameters are:
    # (1) content file
    # (2) settings file
    # (3) number of peoplas
    # (4) global IDs of those peoplas
    [
        # TEST: Are the peoplas extracted correctly
        # Context: 1 peopla, no global ID
        (
            "peopla_content_E1",
            "settings_basic.yaml",
            "A, B",
            {
                "C, D": {"type": "P", "directed": True},
                "E, F": {"type": "Q", "directed": False},
            },
        ),
    ],
)
def test_action_group_content_simple(
    test_name, settings_file, source_peopla, expected_action_group_info
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

    observed_dictionary = {}

    for observed_ag in test_doc.all_action_groups:
        ### Print for information
        observed_ag.print_description()

        if observed_ag.source_peopla.name == source_peopla:
            target_peopla_name = observed_ag.target_peoplas[-1].name

            observed_dictionary[target_peopla_name] = {}
            observed_dictionary[target_peopla_name]["type"] = observed_ag.type
            observed_dictionary[target_peopla_name]["directed"] = observed_ag.directed

    assert len(test_doc.all_action_groups) == len(expected_action_group_info)
    assert observed_dictionary == expected_action_group_info

    print("++++++++++++++++++++++++++++++++++++++++++++++++")


@pytest.mark.parametrize(
    "test_name,settings_file,source_peopla,expected_peopla_actions,expected_action_group_actions,expected_inherited_attributes",
    # parameters are:
    # (1) content file
    # (2) settings file
    # (3) number of peoplas
    # (4) global IDs of those peoplas
    [
        # TEST: Are the peoplas extracted correctly
        # Context: 1 peopla, no global ID
        (
            "peopla_content_E2",
            "settings_basic.yaml",
            "A, B",
            ["N"],
            "P",
            {"AT": ["PLACE"], "ATX": ["1800_TEXT_TEXT:00"], "DATE": ["1800-01-01"]},
        ),
    ],
)
def test_action_group_content_with_inheritance(
    test_name,
    settings_file,
    source_peopla,
    expected_peopla_actions,
    expected_action_group_actions,
    expected_inherited_attributes,
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

    observed_peopla_actions = None
    observed_action_group_actions = {}
    observed_inherited_attributes = {}

    for observed_peopla in test_doc.all_peoplas:
        if observed_peopla.name == source_peopla:
            observed_peopla_actions = list(observed_peopla.attributes.keys())

    for observed_ag in test_doc.all_action_groups:
        ### Print for information
        observed_ag.print_description()

        if observed_ag.source_peopla.name == source_peopla:
            observed_action_group_actions = observed_ag.type
            observed_inherited_attributes = dict(observed_ag.attributes)

    assert observed_peopla_actions.sort() == expected_peopla_actions.sort()
    assert observed_action_group_actions == expected_action_group_actions
    assert observed_inherited_attributes == expected_inherited_attributes

    print("++++++++++++++++++++++++++++++++++++++++++++++++")


@pytest.mark.parametrize(
    "test_name,settings_file,expected_peopla_info,expected_action_group_info",
    # parameters are:
    # (1) content file
    # (2) settings file
    # (3) number of peoplas
    # (4) global IDs of those peoplas
    [
        # TEST:
        # - C, D Peopla has X action with @[P, Q] attributes
        # - AG1 - [A, B]/[C,D], Action Y with attributes @[R, S]
        # - AG2 - [A, B]/[E,F], Action Z with no attributes
        (
            "peopla_content_E3",
            "settings_basic.yaml",
            {"C, D": {"action": "X", "attributes": {"AT": "P, Q"}}},
            [
                {
                    "source": "A, B",
                    "target": "C, D",
                    "action": "Y",
                    "attributes": {"AT": "R, S"},
                },
            ],
        ),
    ],
)
def test_complex_action_group_content(
    test_name, settings_file, expected_peopla_info, expected_action_group_info
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

    observed_peopla_info = {}

    for op in test_doc.all_peoplas:
        if op.name in list(expected_peopla_info.keys()):
            observed_peopla_info[op.name] = {}
            for opa in op.attributes.keys():
                observed_peopla_info[op.name]["action"] = opa
                observed_peopla_info[op.name]["attributes"] = op.attributes[opa]

    observed_action_group_info = []

    for ag in test_doc.all_action_groups:
        observed_action_group_info = observed_action_group_info + [
            {
                "source": ag.source_peopla.name,
                "target": ag.target_peoplas[0].name,
                "action": ag.type,
                "attributes": ag.attributes[ag.type],
            }
        ]

    assert observed_peopla_info == expected_peopla_info
    assert observed_action_group_info == expected_action_group_info

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
        print(p)
        ### Collect global IDs
        observed_global_ids = observed_global_ids + [p.global_id]

    assert len(test_doc.all_peoplas) == expected_num_peoplas
    assert observed_global_ids == expected_global_ids

    print("++++++++++++++++++++++++++++++++++++++++++++++++")


@pytest.mark.parametrize(
    "test_name,settings_file,expected_num_peoplas",
    # parameters are:
    # (1) content file
    # (2) settings file
    # (3) number of peoplas
    # (4) global IDs of those peoplas
    [
        ("peopla_content_F1", "settings_basic.yaml", 1),
        ("peopla_content_F2", "settings_basic.yaml", 2),
        ("peopla_content_F3", "settings_basic.yaml", 1),
        ("peopla_content_F4", "settings_basic.yaml", 2),
        ("peopla_content_F5", "settings_basic.yaml", 2),
        ("peopla_content_F6", "settings_basic.yaml", 3),
        pytest.param(
            "peopla_content_F7",
            "settings_basic.yaml",
            0,
            marks=pytest.mark.xfail(reason="Bug (see issue #57)"),
        ),
        pytest.param(
            "peopla_content_F8",
            "settings_basic.yaml",
            0,
            marks=pytest.mark.xfail(reason="Bug (see issue #57)"),
        ),
        ("peopla_content_F9", "settings_basic.yaml", 2),
    ],
)
def test_repeated_peoplas(test_name, settings_file, expected_num_peoplas):

    content_f = DATA_DIR / f"{test_name}.txt"
    settings_f = SETTINGS_DIR / settings_file

    test_doc = Document(content_f, settings_f)
    test_doc.read_document()

    print("++++++++++++++++++++++++++++++++++++++++++++++++")
    print(f"Test name: {test_name}")
    print(f"File name: {content_f}")
    print(f"Settings : {settings_f}")
    print("++++++++++++++++++++++++++++++++++++++++++++++++")

    for p in test_doc.all_peoplas:
        ### Print for information
        print(p)
        ### Collect global IDs

    assert len(test_doc.all_peoplas) == expected_num_peoplas

    print("++++++++++++++++++++++++++++++++++++++++++++++++")


# -----------------------------------------------------------------
# Integration test cases: one to one primary and secondary peoplas
# -----------------------------------------------------------------
# Note that these tests ONLY cover one to one action_groups between
# primary and secondary Peoplas. That is, if there is more than one
# secondary Peopla for a primary Peopla then this test will fail.
# -


# @pytest.mark.parametrize(
#     "test_name,settings_file,expected_primary_peoplas_names,expected_secondary_peoplas_names,action_group_key",
#     # parameters are:
#     # (1) content file
#     # (2) settings file
#     # (3) the expected names of the primary peoplas
#     # (4) the expected names of the secondary peoplas
#     # (5) the attribute that defines the action_group between the two
#     [
#         # TEST: Are the peoplas extracted correctly
#         # Context: 1 primary peopla and 1 secondary peopla, related by J
#         ("secondary_peopla_content_A", "settings_basic.yaml", ["A, B"], ["D, E"], "J",),
#         # TEST: Are the peoplas extracted correctly
#         # Context: 1 primary peopla and 1 secondary peopla (with additional attributes), related by J
#         ("secondary_peopla_content_B", "settings_basic.yaml", ["A, B"], ["D, E"], "J",),
#     ],
# )
# def test_secondary_peopla_content(
#     test_name,
#     settings_file,
#     expected_primary_peoplas_names,
#     expected_secondary_peoplas_names,
#     action_group_key,
# ):

#     content_f = DATA_DIR / f"{test_name}.txt"
#     settings_f = SETTINGS_DIR / settings_file

#     test_doc = Document(content_f, settings_f)
#     test_doc.read_document()

#     print("++++++++++++++++++++++++++++++++++++++++++++++++")
#     print(f"Test name: {test_name}")
#     print(f"File name: {content_f}")
#     print(f"Settings : {settings_f}")
#     print("++++++++++++++++++++++++++++++++++++++++++++++++")

#     for (i, this_peopla) in enumerate(test_doc.peoplas_primary):
#         this_peopla.print_peopla()
#         assert this_peopla.name == expected_primary_peoplas_names[i]
#         assert action_group_key in this_peopla.attributes
#         assert type(this_peopla.attributes[action_group_key]["with"]) is Peopla
#         assert (
#             this_peopla.attributes[action_group_key]["with"].name
#             == expected_secondary_peoplas_names[i]
#         )

#     for (i, this_peopla) in enumerate(test_doc.peoplas_secondary):
#         this_peopla.print_peopla()
#         assert this_peopla.name == expected_secondary_peoplas_names[i]

#     assert len(test_doc.peoplas_primary) == len(expected_primary_peoplas_names)
#     assert len(test_doc.peoplas_secondary) == len(expected_secondary_peoplas_names)

#     print("++++++++++++++++++++++++++++++++++++++++++++++++")


# -----------------------------------------------------------------
# Integration test cases: relationships
# -----------------------------------------------------------------
# - Testing that


@pytest.mark.parametrize(
    "test_name,settings_file,expected_peorels",
    # parameters are:
    # (1) content file
    # (2) settings file
    # (3) number of peoplas
    # (4) global IDs of those peoplas
    [
        # TEST: Basic relation between one source Peopla and one relation
        (
            "peorel_content_A1",
            "settings_basic.yaml",
            [Peorel(Peopla("B"), Peopla("A"), "SON", 1)],
        ),
        # TEST: Basic relation between one source Peopla and one relation
        # Context: checking that the same Peorel isn't recorded twice
        (
            "peorel_content_A2",
            "settings_basic.yaml",
            [Peorel(Peopla("B"), Peopla("A"), "SON", 1)],
        ),
    ],
)
def test_peopla_peorel_parsing(test_name, settings_file, expected_peorels):

    content_f = DATA_DIR / f"{test_name}.txt"
    settings_f = SETTINGS_DIR / settings_file

    test_doc = Document(content_f, settings_f)
    test_doc.read_document()

    print("++++++++++++++++++++++++++++++++++++++++++++++++")
    print(f"Test name: {test_name}")
    print(f"File name: {content_f}")
    print(f"Settings : {settings_f}")
    print("++++++++++++++++++++++++++++++++++++++++++++++++")

    assert len(test_doc.all_peorels) == len(expected_peorels)

    for this_expected_peorel in expected_peorels:
        assert this_expected_peorel in test_doc.all_peorels

    print("++++++++++++++++++++++++++++++++++++++++++++++++")


@pytest.mark.parametrize(
    "test_name,settings_file,expected_peorels",
    # parameters are:
    # (1) content file
    # (2) settings file
    # (3) number of peoplas
    # (4) global IDs of those peoplas
    [
        # TEST: Relation between source and target peoplas and a target relation
        (
            "peorel_content_B1",
            "settings_basic.yaml",
            [
                Peorel(Peopla("C"), Peopla("A"), "SON", 1),
                Peorel(Peopla("C"), Peopla("B"), "SON", 1),
            ],
        ),
        # TEST: Relation between source and target peoplas and a target relation
        (
            "peorel_content_B2",
            "settings_basic.yaml",
            [
                Peorel(Peopla("C"), Peopla("B"), "SON", 1),
            ],
        ),
        # TEST: Relation between source and target peoplas and a target relation
        (
            "peorel_content_B3",
            "settings_basic.yaml",
            [
                Peorel(Peopla("C"), Peopla("A"), "SON", 1),
                Peorel(Peopla("C"), Peopla("B"), "SON", 1),
            ],
        ),
        # TEST: Relation between source and target peoplas and a target relation
        (
            "peorel_content_B4",
            "settings_basic.yaml",
            [
                Peorel(Peopla("C"), Peopla("B"), "SON", 1),
            ],
        ),
        # TEST: Checking that relations are not duplicated
        (
            "peorel_content_B5",
            "settings_basic.yaml",
            [
                Peorel(Peopla("C"), Peopla("A"), "SON", 1),
                Peorel(Peopla("C"), Peopla("B"), "SON", 1),
            ],
        ),
        # TEST: Checking that relations are not duplicated
        (
            "peorel_content_B6",
            "settings_basic.yaml",
            [
                Peorel(Peopla("C"), Peopla("B"), "SON", 1),
            ],
        ),
        # TEST: Checking that relations are not duplicated
        (
            "secondary_peopla_content_F",
            "settings_basic.yaml",
            [
                Peorel(Peopla("M"), Peopla("F, G"), "X", 1),
                Peorel(Peopla("M"), Peopla("A, B"), "X", 1),
            ],
        ),
    ],
)
def test_actiongroup_peorel_parsing(test_name, settings_file, expected_peorels):

    content_f = DATA_DIR / f"{test_name}.txt"
    settings_f = SETTINGS_DIR / settings_file

    test_doc = Document(content_f, settings_f)
    test_doc.read_document()

    print("++++++++++++++++++++++++++++++++++++++++++++++++")
    print(f"Test name: {test_name}")
    print(f"File name: {content_f}")
    print(f"Settings : {settings_f}")
    print("++++++++++++++++++++++++++++++++++++++++++++++++")

    assert len(test_doc.all_peorels) == len(expected_peorels)

    for this_expected_peorel in expected_peorels:
        assert this_expected_peorel in test_doc.all_peorels

    print("++++++++++++++++++++++++++++++++++++++++++++++++")


# -----------------------------------------------------------------
# Integration test cases: inferring gender
# -----------------------------------------------------------------
# - Checking that gender is inferred correctly


@pytest.mark.parametrize(
    "test_name,settings_file,peopla_name,expected_gender,expected_peorel_to,expected_peorel_relation",
    # parameters are:
    # (1) content file
    # (2) settings file
    # (3) number of peoplas
    # (4) global IDs of those peoplas
    [
        # TEST: Checking that SON generates MALE
        ("peorel_content_C1", "settings_basic.yaml", "C", "MALE", "A", "SON",),
        # TEST: Checking that FATHER generates MALE
        ("peorel_content_C1", "settings_basic.yaml", "F", "MALE", "D", "FATHER",),
        # TEST: Checking that DAUG generates FEMALE
        ("peorel_content_C1", "settings_basic.yaml", "I", "FEMALE", "G", "DAUG",),
        # TEST: Checking that MOTHER generates FEMALE
        ("peorel_content_C1", "settings_basic.yaml", "L", "FEMALE", "J", "MOTHER",),
        # TEST: Checking that anything ungendered generates UNKNOWN
        ("peorel_content_C1", "settings_basic.yaml", "O", "UNKNOWN", "M", "X",),
    ],
)
def test_gender_inference_from_relations(
    test_name,
    settings_file,
    peopla_name,
    expected_gender,
    expected_peorel_to,
    expected_peorel_relation,
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

    for this_peopla in test_doc.all_peoplas:

        if this_peopla.name == peopla_name:
            observed_gender = this_peopla.attributes["GENDER"]["value"]
            assert observed_gender == expected_gender

            gender_evidence = this_peopla.attributes["GENDER"]["evidence"].pop()
            assert gender_evidence.peopla_to.name == expected_peorel_to
            assert gender_evidence.relation_text == expected_peorel_relation

    print("++++++++++++++++++++++++++++++++++++++++++++++++")


# -----------------------------------------------------------------
# Integration test cases: inferring gender
# -----------------------------------------------------------------
# - Checking that gender is inferred correctly


@pytest.mark.parametrize(
    "test_name,settings_file,peopla_name,expected_gender,expected_num_evidence,expected_line_reference",
    ### This test will only work where there is a single line of evidence for a gender inference
    # parameters are:
    # (1) content file
    # (2) settings file
    # (3) name of peopla to test
    # (4) their expected gender
    # (4) the expected number of pieces of evidence
    # (4) the expected line reference for that evidence (will only be one in this test case)
    [
        # TEST: Are the gender inferences evidenced correctly
        # Context: Repeated peorel (created for issue #75)
        ("peorel_content_B7", "settings_basic.yaml", "C", "FEMALE", 2, 7),
        # TEST: Are the gender inferences evidenced correctly
        # Context: Repeated peorel (created for issue #75)
        ("peorel_content_B7", "settings_basic.yaml", "D", "FEMALE", 2, 9),
        # TEST: Are the gender inferences evidenced correctly
        # Context: Repeated peorel (created for issue #75)
        ("peorel_content_B8", "settings_basic.yaml", "C", "FEMALE", 2, 7),
        # TEST: Are the gender inferences evidenced correctly
        # Context: Repeated peorel (created for issue #75)
        ("peorel_content_B8", "settings_basic.yaml", "D", "FEMALE", 2, 12),
    ],
)
def test_gender_evidence_is_correct(
    test_name,
    settings_file,
    peopla_name,
    expected_gender,
    expected_num_evidence,
    expected_line_reference,
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

    for this_peopla in test_doc.all_peoplas:

        if this_peopla.name == peopla_name:
            observed_gender = this_peopla.attributes["GENDER"]["value"]
            assert observed_gender == expected_gender

            observed_evidence_list = this_peopla.attributes["GENDER"]["evidence"]
            observed_num_evidences = len(observed_evidence_list)
            assert observed_num_evidences == expected_num_evidence

            for this_evidence_peorel in observed_evidence_list:
                assert len(this_evidence_peorel.evidence_reference) == 1
                assert (
                    this_evidence_peorel.evidence_reference.pop()
                    == expected_line_reference
                )

    print("++++++++++++++++++++++++++++++++++++++++++++++++")


# -----------------------------------------------------------------
# Integration test cases: inferring gender
# -----------------------------------------------------------------
# - Checking that gender is inferred correctly


@pytest.mark.parametrize(
    "test_name,settings_file,expected_num_peorel",
    ### This test will only work where there is a single line of evidence for a gender inference
    # parameters are:
    # (1) content file
    # (2) settings file
    # (3) name of the peopla 'is' to test
    # (4) name of the peopla 'to' to test
    # (4) the expected relation text
    # (4) the expected line reference for that evidence AS STRING (will only be one in this test case)
    [
        # TEST: Are the nested pedigrees being interpreted correctly?
        # One continuous hierarchy
        ("nested_pedigree_A1", "settings_basic.yaml", 12),
        # TEST: Are the nested pedigrees being interpreted correctly?
        # Two separate hierarchies
        ("nested_pedigree_A2", "settings_basic.yaml", 8),
        # TEST: Are the nested pedigrees being interpreted correctly?
        # Hierarchy that includes other information AND a missing target Peopla
        ("nested_pedigree_A3", "settings_basic.yaml", 3),
        # TEST: Are the nested pedigrees being interpreted correctly?
        # Hierarchy that includes other information AND a missing target Peopla
        # As A3 but with 'real' data, other metadata and an extra blank line
        ("nested_pedigree_A3+", "settings_basic.yaml", 3),
        # TEST: Are the nested pedigrees being interpreted correctly?
        # Hierarchy that includes other information AND full target Peoplas
        ("nested_pedigree_A4", "settings_basic.yaml", 4),
        # TEST: Are the nested pedigrees being interpreted correctly?
        # Hierarchy that includes other information AND full target Peoplas
        # As A4 but with 'real' data and other metadata
        ("nested_pedigree_A4+", "settings_basic.yaml", 4),
        # TEST: Are the nested pedigrees being interpreted correctly?
        # Hierarchy that requires breadcrumbs
        ("nested_pedigree_A5", "settings_basic.yaml", 12),
    ],
)
def test_nested_pedigree_num_relations(test_name, settings_file, expected_num_peorel):

    content_f = DATA_DIR / f"{test_name}.txt"
    settings_f = SETTINGS_DIR / settings_file

    test_doc = Document(content_f, settings_f)
    test_doc.read_document()

    print("++++++++++++++++++++++++++++++++++++++++++++++++")
    print(f"Test name: {test_name}")
    print(f"File name: {content_f}")
    print(f"Settings : {settings_f}")
    print("++++++++++++++++++++++++++++++++++++++++++++++++")

    observed_num_peorel = len(test_doc.all_peorels)
    assert observed_num_peorel == expected_num_peorel

    print("++++++++++++++++++++++++++++++++++++++++++++++++")


@pytest.mark.parametrize(
    "test_name,settings_file,peopla_name_is,peopla_name_to,expected_relation_text,expected_line_reference",
    ### This test will only work where there is a single line of evidence for a gender inference
    # parameters are:
    # (1) content file
    # (2) settings file
    # (3) name of the peopla 'is' to test
    # (4) name of the peopla 'to' to test
    # (4) the expected relation text
    # (4) the expected line reference for that evidence AS STRING (will only be one in this test case)
    [
        # TEST: Are the nested pedigrees being interpreted correctly?
        # One continuous hierarchy
        ("nested_pedigree_A1", "settings_basic.yaml", "C", "B", "DAUG", "7"),
        ("nested_pedigree_A1", "settings_basic.yaml", "C", "A", "DAUG", "7"),
        ("nested_pedigree_A1", "settings_basic.yaml", "E", "D", "DAUG", "10"),
        ("nested_pedigree_A1", "settings_basic.yaml", "E", "C", "DAUG", "10"),
        ("nested_pedigree_A1", "settings_basic.yaml", "G", "F", "DAUG", "13"),
        ("nested_pedigree_A1", "settings_basic.yaml", "G", "E", "DAUG", "13"),
        ("nested_pedigree_A1", "settings_basic.yaml", "I", "H", "DAUG", "16"),
        ("nested_pedigree_A1", "settings_basic.yaml", "I", "G", "DAUG", "16"),
        ("nested_pedigree_A1", "settings_basic.yaml", "K", "J", "DAUG", "19"),
        ("nested_pedigree_A1", "settings_basic.yaml", "K", "I", "DAUG", "19"),
        ("nested_pedigree_A1", "settings_basic.yaml", "M", "L", "DAUG", "22"),
        ("nested_pedigree_A1", "settings_basic.yaml", "M", "K", "DAUG", "22"),
        # TEST: Are the nested pedigrees being interpreted correctly?
        # Two separate hierarchies
        ("nested_pedigree_A2", "settings_basic.yaml", "C", "B", "DAUG", "7"),
        ("nested_pedigree_A2", "settings_basic.yaml", "C", "A", "DAUG", "7"),
        ("nested_pedigree_A2", "settings_basic.yaml", "E", "D", "DAUG", "10"),
        ("nested_pedigree_A2", "settings_basic.yaml", "E", "C", "DAUG", "10"),
        ("nested_pedigree_A2", "settings_basic.yaml", "H", "G", "DAUG", "16"),
        ("nested_pedigree_A2", "settings_basic.yaml", "H", "F", "DAUG", "16"),
        ("nested_pedigree_A2", "settings_basic.yaml", "J", "I", "DAUG", "19"),
        ("nested_pedigree_A2", "settings_basic.yaml", "J", "H", "DAUG", "19"),
        # TEST: Are the nested pedigrees being interpreted correctly?
        # Hierarchy that includes other information AND a missing target Peopla
        ("nested_pedigree_A3", "settings_basic.yaml", "B", "A", "DAUG", "6"),
        ("nested_pedigree_A3", "settings_basic.yaml", "K", "J", "SON", "15"),
        ("nested_pedigree_A3", "settings_basic.yaml", "K", "B", "SON", "15"),
        # TEST: Are the nested pedigrees being interpreted correctly?
        # Hierarchy that includes other information AND a missing target Peopla
        # As A3 but with 'real' data, other metadata and an extra blank line
        (
            "nested_pedigree_A3+",
            "settings_basic.yaml",
            "CRAWFURD, Barbara",
            "CRAWFURD, Andrew",
            "DAUG",
            "6",
        ),
        (
            "nested_pedigree_A3+",
            "settings_basic.yaml",
            "LOGAN, John",
            "LOGAN, James",
            "SON",
            "16",
        ),
        (
            "nested_pedigree_A3+",
            "settings_basic.yaml",
            "LOGAN, John",
            "CRAWFURD, Barbara",
            "SON",
            "16",
        ),
        # TEST: Are the nested pedigrees being interpreted correctly?
        # Hierarchy that includes other information AND full target Peoplas
        ("nested_pedigree_A4", "settings_basic.yaml", "B", "A", "DAUG", "7"),
        ("nested_pedigree_A4", "settings_basic.yaml", "B", "D", "DAUG", "7"),
        ("nested_pedigree_A4", "settings_basic.yaml", "K", "J", "SON", "16"),
        ("nested_pedigree_A4", "settings_basic.yaml", "K", "B", "SON", "16"),
        # TEST: Are the nested pedigrees being interpreted correctly?
        # Hierarchy that includes other information AND a missing target Peopla
        # As A4 but with 'real' data and other metadata
        (
            "nested_pedigree_A4+",
            "settings_basic.yaml",
            "CRAWFURD, Barbara",
            "CRAWFURD, Andrew",
            "DAUG",
            "7",
        ),
        (
            "nested_pedigree_A4+",
            "settings_basic.yaml",
            "CRAWFURD, Barbara",
            "LOGAN, .",
            "DAUG",
            "7",
        ),
        (
            "nested_pedigree_A4+",
            "settings_basic.yaml",
            "LOGAN, John",
            "LOGAN, James",
            "SON",
            "17",
        ),
        (
            "nested_pedigree_A4+",
            "settings_basic.yaml",
            "LOGAN, John",
            "CRAWFURD, Barbara",
            "SON",
            "17",
        ),
        # TEST: Are the nested pedigrees being interpreted correctly?
        # Hierarchy that requires breadcrumbs
        ("nested_pedigree_A5", "settings_basic.yaml", "C", "B", "DAUG", "7"),
        ("nested_pedigree_A5", "settings_basic.yaml", "C", "A", "DAUG", "7"),
        ("nested_pedigree_A5", "settings_basic.yaml", "E", "D", "DAUG", "10"),
        ("nested_pedigree_A5", "settings_basic.yaml", "E", "C", "DAUG", "10"),
        ("nested_pedigree_A5", "settings_basic.yaml", "G", "F", "DAUG", "13"),
        ("nested_pedigree_A5", "settings_basic.yaml", "G", "E", "DAUG", "13"),
        ("nested_pedigree_A5", "settings_basic.yaml", "I", "H", "DAUG", "16"),
        ("nested_pedigree_A5", "settings_basic.yaml", "I", "C", "DAUG", "16"),
        ("nested_pedigree_A5", "settings_basic.yaml", "K", "J", "DAUG", "19"),
        ("nested_pedigree_A5", "settings_basic.yaml", "K", "C", "DAUG", "19"),
        ("nested_pedigree_A5", "settings_basic.yaml", "M", "L", "DAUG", "22"),
        ("nested_pedigree_A5", "settings_basic.yaml", "M", "A", "DAUG", "22"),
    ],
)
def test_nested_pedigree_relations_that_should_be_recorded(
    test_name,
    settings_file,
    peopla_name_is,
    peopla_name_to,
    expected_relation_text,
    expected_line_reference,
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

    observed_relations_dict = defaultdict(dict)

    for this_peorel in test_doc.all_peorels:
        evidence_string = ",".join(str(x) for x in this_peorel.evidence_reference)

        if this_peorel.peopla_is.name not in observed_relations_dict:
            observed_relations_dict[this_peorel.peopla_is.name] = {}

        if (
            this_peorel.peopla_to.name
            not in observed_relations_dict[this_peorel.peopla_is.name]
        ):
            observed_relations_dict[this_peorel.peopla_is.name][
                this_peorel.peopla_to.name
            ] = {}

        observed_relations_dict[this_peorel.peopla_is.name][this_peorel.peopla_to.name][
            "text"
        ] = this_peorel.relation_text
        observed_relations_dict[this_peorel.peopla_is.name][this_peorel.peopla_to.name][
            "evidence"
        ] = evidence_string

    assert (
        observed_relations_dict[peopla_name_is][peopla_name_to]["text"]
        == expected_relation_text
    )
    assert (
        observed_relations_dict[peopla_name_is][peopla_name_to]["evidence"]
        == expected_line_reference
    )

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
        "local_id": [None, None, None],
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
        "local_id": [None, None, None, None, None, None],
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
        "local_id": [None, None, None, None, None, None],
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
        "local_id": [None, None, None, None, None, None],
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
        "local_id": [None, None, None, None, None, None],
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
        "local_id": [None, None, None, None, None, None],
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
        "local_id": [None, None, None],
    }
)


table_shortcuts_multiple_G_expected = pd.DataFrame(
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
        "local_id": ["i-1", "j-2", "k-3"],
    }
)


table_shortcuts_multiple_H_expected = pd.DataFrame(
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
        "global_id": [None, "j-2", None],
        "local_id": ["i-1", None, "k-3"],
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
        # TEST: Are global IDs being picked up and assigned correctly?
        # Context: 1 table, 2 shortcuts on one, 1 on the other, no overlapping shortcuts
        (
            "table_shortcuts_multiple_G",
            "settings_colour_shortcuts.yaml",
            table_shortcuts_multiple_G_expected,
        ),
        # TEST: Are global IDs being picked up and assigned correctly?
        # Context: 1 table, 2 shortcuts on one, 1 on the other, no overlapping shortcuts
        (
            "table_shortcuts_multiple_H",
            "settings_colour_shortcuts.yaml",
            table_shortcuts_multiple_H_expected,
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
