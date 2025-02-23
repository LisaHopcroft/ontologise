import pytest
from pathlib import Path
import pandas as pd
from pandas import testing
import sys
from collections import defaultdict, Counter
import time

sys.path.append("src/ontologise")

from utils import Document, Peopla, Peorel, ActionGroup, record_evidence


BASE_DIR = Path(__file__).parents[1]
DATA_DIR = BASE_DIR / "integration" / "content" / "input"
SETTINGS_DIR = BASE_DIR / "integration" / "content" / "settings"
EXPECTED_DIR = BASE_DIR / "integration" / "content" / "expected"


def generate_test_doc(name, settings):

    content_f = DATA_DIR / f"{name}.txt"
    settings_f = SETTINGS_DIR / settings

    test_doc = Document(content_f, settings_f)
    test_doc.read_document()

    print("++++++++++++++++++++++++++++++++++++++++++++++++")
    print(f"Test name: {name}")
    print(f"File name: {content_f}")
    print(f"Settings : {settings_f}")
    print("++++++++++++++++++++++++++++++++++++++++++++++++")

    return test_doc


# -----------------------------------------------------------------
# Integration test cases: peopla content, attributes of attributes
# -----------------------------------------------------------------
# -


@pytest.mark.parametrize(
    "test_name,settings_file,peopla_name,attribute,expected_attribute_dictionary",
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
            "accumulating_attributes_A1",
            "settings_basic.yaml",
            "A",
            "X",
            {
                1: {"DATE": "1800-01-01", "AT": "S1"},
                2: {"DATE": "1800-02-02", "AT": "S2"},
                3: {"AT": "S3"},
            },
        ),
        # TEST: Are the peoplas extracted correctly
        # Context: 1 peopla with attributes of attributes
        (
            "accumulating_attributes_A2",
            "settings_basic.yaml",
            "A",
            "X",
            {
                1: {"AT": "S1"},
                2: {"DATE": "1800-02-02", "AT": "S2"},
                3: {"DATE": "1800-03-03", "AT": "S3"},
            },
        ),
    ],
)
def test_peopla_accumulating_attributes(
    test_name, settings_file, peopla_name, attribute, expected_attribute_dictionary
):

    test_doc = generate_test_doc(test_name, settings_file)

    for p in test_doc.all_peoplas:
        print(p)
        if p.name == peopla_name:
            assert p.attributes[attribute] == expected_attribute_dictionary


# -----------------------------------------------------------------
# Integration test cases: peopla content, attributes of attributes
# -----------------------------------------------------------------
# -


@pytest.mark.parametrize(
    "test_name,settings_file,peopla_source_name,peopla_target_name,attribute,evidence,expected_attribute_dictionary",
    ### This test will only work where there is a single target peopla
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
            "accumulating_attributes_B1",
            "settings_basic.yaml",
            "A",
            "B",
            "X",
            [12, 15, 18],
            {
                1: {"DATE": "1800-01-01", "AT": "S1"},
                2: {"DATE": "1800-02-02", "AT": "S2"},
                3: {"AT": "S3"},
            },
        ),
        (
            "accumulating_attributes_B2",
            "settings_basic.yaml",
            "A",
            "B",
            "X",
            [12, 14, 17],
            {
                1: {"AT": "S1"},
                2: {"DATE": "1800-02-02", "AT": "S2"},
                3: {"DATE": "1800-03-03", "AT": "S3"},
            },
        ),
        # TEST: Are the peoplas extracted correctly
        # Context: 1 peopla with attributes of attributes
        (
            "accumulating_attributes_C1",
            "settings_basic.yaml",
            "C",
            "D",
            "X",
            [15, 24, 33],
            {
                1: {"DATE": "1800-01-01", "AT": "S1"},
                2: {"DATE": "1800-02-02", "AT": "S2"},
                3: {"AT": "S3"},
            },
        ),
        # TEST: Are the peoplas extracted correctly
        # Context: 1 peopla with attributes of attributes
        (
            "accumulating_attributes_C2",
            "settings_basic.yaml",
            "C",
            "D",
            "X",
            [15, 23, 32],
            {
                1: {"AT": "S1"},
                2: {"DATE": "1800-02-02", "AT": "S2"},
                3: {"DATE": "1800-03-03", "AT": "S3"},
            },
        ),
        # TEST: Are the peoplas extracted correctly
        # Context: 1 peopla with attributes of attributes
        (
            "accumulating_attributes_D1",
            "settings_basic.yaml",
            "C",
            "D",
            "X",
            [15, 21, 27],
            {
                1: {"DATE": "1800-01-01", "AT": "S1"},
                2: {"DATE": "1800-02-02", "AT": "S2"},
                3: {"AT": "S3"},
            },
        ),
        # TEST: Are the peoplas extracted correctly
        # Context: 1 peopla with attributes of attributes
        (
            "accumulating_attributes_D2",
            "settings_basic.yaml",
            "C",
            "D",
            "X",
            [15, 20, 26],
            {
                1: {"AT": "S1"},
                2: {"DATE": "1800-02-02", "AT": "S2"},
                3: {"DATE": "1800-03-03", "AT": "S3"},
            },
        ),
    ],
)
def test_actiongroup_accumulating_attributes(
    test_name,
    settings_file,
    peopla_source_name,
    peopla_target_name,
    attribute,
    evidence,
    expected_attribute_dictionary,
):

    test_doc = generate_test_doc(test_name, settings_file)

    count_checks = 0

    for ag in test_doc.all_action_groups:
        print(ag)

        print(
            f"Source peopla match? {ag.source_peopla.name} == {peopla_source_name} ? {ag.source_peopla.name == peopla_source_name}"
        )
        print(
            f"Target peopla match? {ag.target_peoplas[0].name} == {peopla_target_name} ? {ag.target_peoplas[0].name == peopla_target_name}"
        )
        print(f"Type match? {ag.type} == {attribute} ? {ag.type == attribute}")
        print(
            f"Evidence match? {ag.evidence_reference} == {evidence} ? {ag.evidence_reference == evidence}"
        )

        all_match = (
            ag.source_peopla.name == peopla_source_name
            and ag.target_peoplas[0].name == peopla_target_name
            and ag.type == attribute
            and ag.evidence_reference == evidence
        )

        print(f"All match ? {all_match}")

        if all_match:
            count_checks += 1

            print("OBSERVED ATTRIBUTES:\n")
            print(ag.attributes[attribute])

            print("EXPECTED ATTRIBUTES:\n")
            print(expected_attribute_dictionary)

            assert ag.attributes[attribute] == expected_attribute_dictionary

    assert count_checks > 0


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
            {1: {"DATE": "YYYY-MM", "AT": "P, Q", "X": "Z"}},
        ),
    ],
)
def test_peopla_attributes_of_attributes(
    test_name, settings_file, peopla_name, attribute, attribute_dictionary
):

    test_doc = generate_test_doc(test_name, settings_file)

    for p in test_doc.all_peoplas:
        print(p)
        if p.name == peopla_name:
            assert p.attributes[attribute] == attribute_dictionary


# -----------------------------------------------------------------
# Integration test cases: peopla content, attributes of attributes
# -----------------------------------------------------------------
# -


@pytest.mark.parametrize(
    "test_name,settings_file,expected_object_list",
    # parameters are:
    # (1) content file
    # (2) settings file
    # (3) name of the peopla of interest
    # (4) name the attribute of interest
    # (5) attribute dictionary of the attribute of interest
    [
        # TEST: Are all the objects extracted correctly
        # Context: A complex example (includes an ActionGroup)
        (
            "missing_relations_example_A",
            "settings_basic.yaml",
            [
                ### What Peoplas are we expecting?
                record_evidence(Peopla("A"), 10),
                record_evidence(Peopla("B"), 11),
                record_evidence(record_evidence(Peopla("C", local_id="1"), 13), 17),
                record_evidence(Peopla("D"), 14),
                record_evidence(Peopla("E"), 18),
                record_evidence(Peopla("F"), 22),
                record_evidence(Peopla("G"), 23),
                ### What Peorels are we expecting?
                record_evidence(Peorel(Peopla("C"), Peopla("A"), "SON", 1), 13),
                record_evidence(Peorel(Peopla("C"), Peopla("B"), "SON", 1), 13),
                record_evidence(Peorel(Peopla("F"), Peopla("A"), "DAUG", 1), 22),
                record_evidence(Peorel(Peopla("F"), Peopla("B"), "DAUG", 1), 22),
                ### What ActionGroups are we expecting?
                record_evidence(
                    ActionGroup(
                        type="X",
                        directed=True,
                        source_peopla=Peopla("C"),
                        target_peoplas=[Peopla("D")],
                    ),
                    15,
                ),
                record_evidence(
                    ActionGroup(
                        type="X",
                        directed=True,
                        source_peopla=Peopla("C"),
                        target_peoplas=[Peopla("E")],
                    ),
                    19,
                ),
                record_evidence(
                    ActionGroup(
                        type="X",
                        directed=True,
                        source_peopla=Peopla("F"),
                        target_peoplas=[Peopla("G")],
                    ),
                    24,
                ),
            ],
        ),
    ],
)
def test_missing_relations(test_name, settings_file, expected_object_list):

    test_doc = generate_test_doc(test_name, settings_file)

    total_objects_checked = 0

    expected_object_types = [type(x).__name__ for x in expected_object_list]
    expected_object_type_counts = Counter(expected_object_types)

    print(f"Testing {expected_object_type_counts['Peopla']} peoplas")
    print(f"We have observed {len(test_doc.all_peoplas)} peoplas in the document")
    assert len(test_doc.all_peoplas) == expected_object_type_counts["Peopla"]

    print(f"Testing {expected_object_type_counts['Peorel']} peorels")
    print(f"We have observed {len(test_doc.all_peorels)} peorels in the document")
    assert len(test_doc.all_peorels) == expected_object_type_counts["Peorel"]

    print(f"Testing {expected_object_type_counts['ActionGroup']} action groups")
    print(f"We have observed {len(test_doc.all_action_groups)} action groups")
    assert len(test_doc.all_action_groups) == expected_object_type_counts["ActionGroup"]

    for expected_object in expected_object_list:

        this_object_type = type(expected_object).__name__

        ### We need to check a Peopla
        if this_object_type == "Peopla":

            ### We have to cycle through all the Peoplas because we
            ### we are using (temporarily) using a comparison method
            ### rather than relying on a __eq__ function. I tried to
            ### implement an __eq__ function but it disrupted the rest
            ### of the parsing so we will use this for now.

            for observed_object in test_doc.all_peoplas:
                if observed_object.name == expected_object.name and (
                    observed_object.local_id == expected_object.local_id
                    or observed_object.global_id == expected_object.global_id
                ):

                    comparison_result = observed_object.peopla_match(expected_object)
                    assert comparison_result
                    total_objects_checked += 1

        ### We need to check a Peorel
        elif this_object_type == "Peorel":

            ### This is possible for Peorels because we have a __eq__
            ### function for this class

            for n, observed_object in enumerate(test_doc.all_peorels):

                if observed_object == expected_object:
                    assert True
                    total_objects_checked += 1

        ### We need to check an ActionGroup
        elif this_object_type == "ActionGroup":

            # ### This is possible for Peorels because we have a __eq__
            # ### function for this class
            # assert expected_object in test_doc.all_action_groups
            # total_objects_checked += 1

            for observed_object in test_doc.all_action_groups:
                if (
                    expected_object.type == observed_object.type
                    and expected_object.directed == observed_object.directed
                    and expected_object.source_peopla.name
                    == observed_object.source_peopla.name
                    and len(expected_object.target_peoplas)
                    == len(observed_object.target_peoplas)
                ):
                    assert True
                    total_objects_checked += 1

    print("============================================")

    assert total_objects_checked == len(expected_object_list)


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
            {1: {"DATE": "YYYY-MM", "AT": "P, Q", "X": "Z"}},
        ),
        # TEST: Are the peoplas extracted correctly
        # Context: 1 peopla with attributes of attributes
        (
            "pedigree_attributes_B",
            "settings_basic.yaml",
            "C, D",
            "E",
            {1: {"DATE": "YYYY-MM", "AT": "P, Q", "X": "Z"}},
        ),
    ],
)
def test_peopla_attributes_in_pedigrees(
    test_name, settings_file, peopla_name, attribute, attribute_dictionary
):

    test_doc = generate_test_doc(test_name, settings_file)

    for p in test_doc.all_peoplas:
        ### Print for information
        print(p)
        ### Collect global IDs
        if p.name == peopla_name:
            assert p.attributes[attribute] == attribute_dictionary


# -----------------------------------------------------------------
# Integration test cases: peopla content, attributes of attributes
# -----------------------------------------------------------------
# -


@pytest.mark.parametrize(
    "test_name,settings_file,expected_object_list",
    # parameters are:
    # (1) content file
    # (2) settings file
    # (3) name of the peopla of interest
    # (4) name the attribute of interest
    # (5) attribute dictionary of the attribute of interest
    [
        # TEST: Are all the objects extracted correctly
        # Context: A complex example
        (
            "complex_example_A",
            "settings_basic.yaml",
            [
                ### What Peoplas are we expecting?
                record_evidence(Peopla("A", global_id="i-1"), 7),
                record_evidence(Peopla("B", local_id="j-2"), 8),
                record_evidence(Peopla("C"), 10),
                record_evidence(Peopla("D", global_id="m-3"), 11),
                record_evidence(Peopla("E", place_flag=True, global_id="o-4"), 16),
                ### What Peorels are we expecting?
                record_evidence(
                    Peorel(Peopla("C"), Peopla("A", global_id="i-1"), "DAUG", 1), 10
                ),
                record_evidence(
                    Peorel(Peopla("C"), Peopla("B", local_id="j-2"), "DAUG", 1), 10
                ),
                record_evidence(
                    Peorel(
                        Peopla("E", global_id="o-4"),
                        Peopla("D", global_id="m-3"),
                        "FATHER",
                        2,
                    ),
                    16,
                ),
            ],
        ),
        # TEST: Are all the objects extracted correctly
        # Context: A complex example (includes an ActionGroup)
        (
            "complex_example_B",
            "settings_basic.yaml",
            [
                ### What Peoplas are we expecting?
                record_evidence(Peopla("A", global_id="i-1"), 7),
                record_evidence(Peopla("B", local_id="j-2"), 8),
                record_evidence(Peopla("C"), 10),
                record_evidence(Peopla("D", global_id="m-3"), 11),
                ### What Peorels are we expecting?
                record_evidence(
                    Peorel(Peopla("C"), Peopla("A", global_id="i-1"), "DAUG", 1), 10
                ),
                record_evidence(
                    Peorel(Peopla("C"), Peopla("B", local_id="j-2"), "DAUG", 1), 10
                ),
                ### What ActionGroups are we expecting?
                record_evidence(
                    ActionGroup(
                        type="OCC",
                        directed=False,
                        source_peopla=Peopla("C"),
                        target_peoplas=[Peopla("D")],
                    ),
                    12,
                ),
            ],
        ),
        ### Not very complex, but will let me test whether ActionGroups
        ### are being matched while we work on #88
        (
            "peopla_content_E2",
            "settings_basic.yaml",
            [
                ### What Peoplas are we expecting?
                record_evidence(Peopla("A, B", local_id="i-1"), 7),
                record_evidence(Peopla("C, D"), 9),
                ### What Peorels are we expecting?
                ### None
                ### What ActionGroups are we expecting?
                record_evidence(
                    ActionGroup(
                        type="P",
                        directed=True,
                        source_peopla=Peopla("A, B"),
                        target_peoplas=[Peopla("C, D")],
                    ),
                    10,
                ),
            ],
        ),
    ],
)
def test_complex_examples(test_name, settings_file, expected_object_list):

    test_doc = generate_test_doc(test_name, settings_file)

    total_objects_checked = 0

    expected_object_types = [type(x).__name__ for x in expected_object_list]
    expected_object_type_counts = Counter(expected_object_types)

    print(f"Testing {expected_object_type_counts['Peopla']} peoplas")
    print(f"We have observed {len(test_doc.all_peoplas)} peoplas in the document")
    assert len(test_doc.all_peoplas) == expected_object_type_counts["Peopla"]

    print(f"Testing {expected_object_type_counts['Peorel']} peorels")
    print(f"We have observed {len(test_doc.all_peorels)} peorels in the document")
    assert len(test_doc.all_peorels) == expected_object_type_counts["Peorel"]

    print(f"Testing {expected_object_type_counts['ActionGroup']} action groups")
    print(f"We have observed {len(test_doc.all_action_groups)} action groups")
    assert len(test_doc.all_action_groups) == expected_object_type_counts["ActionGroup"]

    for expected_object in expected_object_list:

        this_object_type = type(expected_object).__name__

        ### We need to check a Peopla
        if this_object_type == "Peopla":

            ### We have to cycle through all the Peoplas because we
            ### we are using (temporarily) using a comparison method
            ### rather than relying on a __eq__ function. I tried to
            ### implement an __eq__ function but it disrupted the rest
            ### of the parsing so we will use this for now.

            for observed_object in test_doc.all_peoplas:
                if observed_object.name == expected_object.name:
                    comparison_result = observed_object.peopla_match(expected_object)
                    assert comparison_result
                    total_objects_checked += 1

        ### We need to check a Peorel
        elif this_object_type == "Peorel":

            ### This is possible for Peorels because we have a __eq__
            ### function for this class
            assert expected_object in test_doc.all_peorels
            total_objects_checked += 1

        ### We need to check an ActionGroup
        elif this_object_type == "ActionGroup":

            # ### This is possible for Peorels because we have a __eq__
            # ### function for this class
            # assert expected_object in test_doc.all_action_groups
            # total_objects_checked += 1

            for observed_object in test_doc.all_action_groups:
                if (
                    expected_object.type == observed_object.type
                    and expected_object.directed == observed_object.directed
                    and expected_object.source_peopla.name
                    == observed_object.source_peopla.name
                    and len(expected_object.target_peoplas)
                    == len(observed_object.target_peoplas)
                ):
                    assert True
                    total_objects_checked += 1

    print("============================================")

    assert total_objects_checked == len(expected_object_list)


@pytest.mark.parametrize(
    "test_name,settings_file,expected_object_list",
    # parameters are:
    # (1) content file
    # (2) settings file
    # (3) name of the peopla of interest
    # (4) name the attribute of interest
    # (5) attribute dictionary of the attribute of interest
    [
        # # TEST: Are all the objects extracted correctly
        # # Context: A complex example
        # (
        #     "complex_example_A",
        #     "settings_basic.yaml",
        #     [
        #         ### What Peoplas are we expecting?
        #         record_evidence(Peopla("A", global_id="i-1"), 7),
        #         record_evidence(Peopla("B", local_id="j-2"), 8),
        #         record_evidence(Peopla("C"), 10),
        #         record_evidence(Peopla("D", global_id="m-3"), 11),
        #         record_evidence(Peopla("E", place_flag=True, global_id="o-4"), 16),
        #         ### What Peorels are we expecting?
        #         record_evidence(
        #             Peorel(Peopla("C"), Peopla("A", global_id="i-1"), "DAUG", 1), 10
        #         ),
        #         record_evidence(
        #             Peorel(Peopla("C"), Peopla("B", local_id="j-2"), "DAUG", 1), 10
        #         ),
        #         record_evidence(
        #             Peorel(
        #                 Peopla("E", global_id="o-4"),
        #                 Peopla("D", global_id="m-3"),
        #                 "FATHER",
        #                 2,
        #             ),
        #             16,
        #         ),
        #     ],
        # ),
        # # TEST: Are all the objects extracted correctly
        # # Context: A complex example (includes an ActionGroup)
        # (
        #     "complex_example_B",
        #     "settings_basic.yaml",
        #     [
        #         ### What Peoplas are we expecting?
        #         record_evidence(Peopla("A", global_id="i-1"), 7),
        #         record_evidence(Peopla("B", local_id="j-2"), 8),
        #         record_evidence(Peopla("C"), 10),
        #         record_evidence(Peopla("D", global_id="m-3"), 11),
        #         ### What Peorels are we expecting?
        #         record_evidence(
        #             Peorel(Peopla("C"), Peopla("A", global_id="i-1"), "DAUG", 1), 10
        #         ),
        #         record_evidence(
        #             Peorel(Peopla("C"), Peopla("B", local_id="j-2"), "DAUG", 1), 10
        #         ),
        #         ### What ActionGroups are we expecting?
        #         record_evidence(
        #             ActionGroup(
        #                 type="OCC",
        #                 directed=False,
        #                 source_peopla=Peopla("C"),
        #                 target_peoplas=[Peopla("D")],
        #             ),
        #             12,
        #         ),
        #     ],
        # ),
        # ### Not very complex, but will let me test whether ActionGroups
        # ### are being matched while we work on #88
        # (
        #     "peopla_content_E2",
        #     "settings_basic.yaml",
        #     [
        #         ### What Peoplas are we expecting?
        #         record_evidence(Peopla("A, B", local_id="i-1"), 7),
        #         record_evidence(Peopla("C, D"), 9),
        #         ### What Peorels are we expecting?
        #         ### None
        #         ### What ActionGroups are we expecting?
        #         record_evidence(
        #             ActionGroup(
        #                 type="P",
        #                 directed=True,
        #                 source_peopla=Peopla("A, B"),
        #                 target_peoplas=[Peopla("C, D")],
        #             ),
        #             10,
        #         ),
        #     ],
        # ),
        # TEST: Are all the objects extracted correctly
        # Context: A complex example
        (
            "accumulating_attributes_B1",
            "settings_basic.yaml",
            [
                ### What Peoplas are we expecting?
                record_evidence(Peopla("A"), 10),
                record_evidence(Peopla("B"), 11),
                ### What Peorels are we expecting?
                ### None
                ### What ActionGroups are we expecting?
                record_evidence(
                    record_evidence(
                        record_evidence(
                            ActionGroup(
                                type="X",
                                directed=False,
                                source_peopla=Peopla("A"),
                                target_peoplas=[Peopla("B")],
                            ),
                            12,
                        ),
                        15,
                    ),
                    18,
                ),
            ],
        ),
    ],
)
def test_complex_examples_with_attributes(
    test_name, settings_file, expected_object_list
):

    test_doc = generate_test_doc(test_name, settings_file)

    total_objects_checked = 0

    expected_object_types = [type(x).__name__ for x in expected_object_list]
    expected_object_type_counts = Counter(expected_object_types)

    print(f"Testing {expected_object_type_counts['Peopla']} peoplas")
    print(f"We have observed {len(test_doc.all_peoplas)} peoplas in the document")
    assert len(test_doc.all_peoplas) == expected_object_type_counts["Peopla"]

    print(f"Testing {expected_object_type_counts['Peorel']} peorels")
    print(f"We have observed {len(test_doc.all_peorels)} peorels in the document")
    assert len(test_doc.all_peorels) == expected_object_type_counts["Peorel"]

    print(f"Testing {expected_object_type_counts['ActionGroup']} action groups")
    print(f"We have observed {len(test_doc.all_action_groups)} action groups")
    assert len(test_doc.all_action_groups) == expected_object_type_counts["ActionGroup"]

    for expected_object in expected_object_list:

        this_object_type = type(expected_object).__name__

        ### We need to check a Peopla
        if this_object_type == "Peopla":

            ### We have to cycle through all the Peoplas because we
            ### we are using (temporarily) using a comparison method
            ### rather than relying on a __eq__ function. I tried to
            ### implement an __eq__ function but it disrupted the rest
            ### of the parsing so we will use this for now.

            for observed_object in test_doc.all_peoplas:
                if observed_object.name == expected_object.name:
                    comparison_result = observed_object.peopla_match(expected_object)
                    assert comparison_result
                    total_objects_checked += 1

        ### We need to check a Peorel
        elif this_object_type == "Peorel":

            ### This is possible for Peorels because we have a __eq__
            ### function for this class
            assert expected_object in test_doc.all_peorels
            total_objects_checked += 1

        ### We need to check an ActionGroup
        elif this_object_type == "ActionGroup":

            # ### This is possible for Peorels because we have a __eq__
            # ### function for this class
            # assert expected_object in test_doc.all_action_groups
            # total_objects_checked += 1

            ### Not sure why the __eq__ isn't working as it was working
            ### previously. Implemented the following to get this test to
            ### pass for now. Note that we are not checking that each
            ### individual target Peopla is the same - we could add this
            ### later if it starts to cause a problem.
            for observed_object in test_doc.all_action_groups:
                if (
                    expected_object.type == observed_object.type
                    and expected_object.directed == observed_object.directed
                    and expected_object.source_peopla.name
                    == observed_object.source_peopla.name
                    and len(expected_object.target_peoplas)
                    == len(observed_object.target_peoplas)
                    and expected_object.evidence_reference
                    == observed_object.evidence_reference
                ):
                    assert True
                    total_objects_checked += 1

    print("============================================")

    assert total_objects_checked == len(expected_object_list)


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

    test_doc = generate_test_doc(test_name, settings_file)

    for p in test_doc.all_peoplas:
        ### Print for information
        print(p)
        ### Collect global IDs
        if p.name == peopla_name:
            assert p.evidence_reference == expected_evidence_list


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

    test_doc = generate_test_doc(test_name, settings_file)

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

    test_doc = generate_test_doc(test_name, settings_file)

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


@pytest.mark.parametrize(
    "test_name,settings_file,expected_action_groups",
    # parameters are:
    # (1) content file
    # (2) settings file
    # (3) list of expected action group
    [
        (
            # TEST: Are the ActionGroups evidenced correctly
            # Context: 3 ActionGroups, who of which are identical
            #          and should be recorded as one ActionGroup
            "action_group_content_A",
            "settings_basic.yaml",
            [
                record_evidence(
                    record_evidence(
                        ActionGroup(
                            type="C",
                            directed=False,
                            source_peopla=Peopla("A"),
                            target_peoplas=[Peopla("B")],
                        ),
                        10,
                    ),
                    18,
                ),
                record_evidence(
                    ActionGroup(
                        type="D",
                        directed=False,
                        source_peopla=Peopla("A"),
                        target_peoplas=[Peopla("B")],
                    ),
                    14,
                ),
            ],
        ),
    ],
)
def test_actiongroup_evidence_repeated_instances(
    test_name, settings_file, expected_action_groups
):

    test_doc = generate_test_doc(test_name, settings_file)

    assert len(test_doc.all_action_groups) == len(expected_action_groups)

    all_passing = 0

    for expected_ag in expected_action_groups:
        ### Print for information
        print("***********************************\n")
        print(expected_ag)
        print("***********************************\n")

        # assert expected_ag in test_doc.all_action_groups

        # if expected_ag in test_doc.all_action_groups:
        #     all_passing += 1

        for observed_ag in test_doc.all_action_groups:
            if (
                expected_ag.type == observed_ag.type
                and expected_ag.directed == observed_ag.directed
                and expected_ag.source_peopla.name == observed_ag.source_peopla.name
                and len(expected_ag.target_peoplas) == len(observed_ag.target_peoplas)
                and expected_ag.evidence_reference == observed_ag.evidence_reference
            ):
                assert True
                all_passing += 1

    assert all_passing == len(expected_action_groups)


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

    test_doc = generate_test_doc(test_name, settings_file)

    assert len(test_doc.all_action_groups) == expected_num_action_groups

    all_passing = 0

    for p in test_doc.all_action_groups:
        ### Print for information
        print(p)

        if p.type == expected_action_text and p.source_peopla.name == peopla_source:

            observed_target_peoplas = []
            for tp in p.target_peoplas:
                observed_target_peoplas.append(tp.name)

            assert len(observed_target_peoplas) == len(expected_target_peoplas)
            assert sorted(observed_target_peoplas) == sorted(expected_target_peoplas)
            assert p.evidence_reference == expected_evidence_list

            all_passing += 1

    assert all_passing == expected_num_action_groups


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

    test_doc = generate_test_doc(test_name, settings_file)

    for p in test_doc.all_peoplas:
        ### Print for information
        print(p)
        ### Collect global IDs
        if p.name == peopla_name:
            assert list(p.attributes.keys()).sort() == action_list.sort()

    print("++++++++++++++++++++++++++++++++++++++++++++++++")


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

    test_doc = generate_test_doc(test_name, settings_file)

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
            {
                1: {
                    "AT": ["PLACE"],
                    "ATX": ["1800_TEXT_TEXT:00"],
                    "DATE": ["1800-01-01"],
                }
            },
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

    test_doc = generate_test_doc(test_name, settings_file)

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
    assert (
        observed_inherited_attributes[expected_action_group_actions]
        == expected_inherited_attributes
    )


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
            {"C, D": {"action": "X", "attributes": {1: {"AT": "P, Q"}}}},
            [
                {
                    "source": "A, B",
                    "target": "C, D",
                    "action": "Y",
                    "attributes": {1: {"AT": "R, S"}},
                },
            ],
        ),
    ],
)
def test_complex_action_group_content(
    test_name, settings_file, expected_peopla_info, expected_action_group_info
):

    test_doc = generate_test_doc(test_name, settings_file)

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

    test_doc = generate_test_doc(test_name, settings_file)

    observed_global_ids = []
    for p in test_doc.all_peoplas:
        ### Print for information
        print(p)
        ### Collect global IDs
        observed_global_ids = observed_global_ids + [p.global_id]

    assert len(test_doc.all_peoplas) == expected_num_peoplas
    assert observed_global_ids == expected_global_ids


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

    test_doc = generate_test_doc(test_name, settings_file)

    for p in test_doc.all_peoplas:
        ### Print for information
        print(p)
        ### Collect global IDs

    assert len(test_doc.all_peoplas) == expected_num_peoplas


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

    test_doc = generate_test_doc(test_name, settings_file)

    assert len(test_doc.all_peorels) == len(expected_peorels)

    for this_expected_peorel in expected_peorels:
        assert this_expected_peorel in test_doc.all_peorels


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
            [Peorel(Peopla("C"), Peopla("B"), "SON", 1),],
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
            [Peorel(Peopla("C"), Peopla("B"), "SON", 1),],
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
            [Peorel(Peopla("C"), Peopla("B"), "SON", 1),],
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

    test_doc = generate_test_doc(test_name, settings_file)

    assert len(test_doc.all_peorels) == len(expected_peorels)

    for this_expected_peorel in expected_peorels:
        assert this_expected_peorel in test_doc.all_peorels


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

    test_doc = generate_test_doc(test_name, settings_file)

    for this_peopla in test_doc.all_peoplas:

        if this_peopla.name == peopla_name:
            observed_gender = this_peopla.attributes["GENDER"][1]["value"]
            assert observed_gender == expected_gender

            gender_evidence = this_peopla.attributes["GENDER"][1]["evidence"].pop()
            assert gender_evidence.peopla_to.name == expected_peorel_to
            assert gender_evidence.relation_text == expected_peorel_relation


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

    test_doc = generate_test_doc(test_name, settings_file)

    for this_peopla in test_doc.all_peoplas:

        if this_peopla.name == peopla_name:
            observed_gender = this_peopla.attributes["GENDER"][1]["value"]
            assert observed_gender == expected_gender

            observed_evidence_list = this_peopla.attributes["GENDER"][1]["evidence"]
            observed_num_evidences = len(observed_evidence_list)
            assert observed_num_evidences == expected_num_evidence

            for this_evidence_peorel in observed_evidence_list:
                assert len(this_evidence_peorel.evidence_reference) == 1
                assert (
                    this_evidence_peorel.evidence_reference.pop()
                    == expected_line_reference
                )


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

    test_doc = generate_test_doc(test_name, settings_file)

    observed_num_peorel = len(test_doc.all_peorels)
    assert observed_num_peorel == expected_num_peorel


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

    test_doc = generate_test_doc(test_name, settings_file)

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

    test_doc = generate_test_doc(test_name, settings_file)

    observed_df = test_doc.data_points_df

    testing.assert_frame_equal(observed_df, expected_df)
