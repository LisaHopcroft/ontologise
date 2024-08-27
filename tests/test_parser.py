import sys
import pytest
import tempfile
from pathlib import Path

sys.path.append("src/ontologise")

from utils import Document


def generate_file_header(
    record_type="RECORD_TYPE",
    at_string=", ".join(["A", "B", "C", "D", "E"]),
    atx_string="1800_TEXT_TEXT:00",
    date_string="1800-01-01",
):

    """Returns an example header for testing."""

    file_header_string = f"""
#[{record_type}]
##AT:	{at_string}
##ATX:	{atx_string}
##DATE:	{date_string}
"""

    return file_header_string


@pytest.fixture()
def document_object_to_test(
    record_types=["RECORD TYPE 1", "RECORD TYPE 2"],
    at_strings=["LIST, OF, THINGS", "ANOTHER, LIST, OF, THINGS"],
    atx_strings=["1800_TEXT_TEXT:00", "1850_TEXT_TEXT:01"],
    date_strings=["1800-01-01", "1850-01-01"],
):
    """Returns an example header for testing."""

    test_file_content = ""

    for i in range(0, len(record_types)):
        this_text = generate_file_header(
            record_types[i], at_strings[i], atx_strings[i], date_strings[i]
        )

        test_file_content = f"{test_file_content}{this_text}"

    temp_f = tempfile.NamedTemporaryFile()

    with open(temp_f.name, "w") as d:
        d.writelines(test_file_content)

    test_doc = Document(temp_f.name)
    test_doc.read_document()

    return test_doc

def test_header_parse(document_object_to_test):
    assert document_object_to_test.get_header_information('TITLE') == [
        "RECORD TYPE 1",
        "RECORD TYPE 2",
    ]

def test_at_parse(document_object_to_test):
    assert document_object_to_test.get_header_information("AT") == [
        "LIST, OF, THINGS",
        "ANOTHER, LIST, OF, THINGS",
    ]

def test_atx_parse(document_object_to_test):
    assert document_object_to_test.get_header_information("ATX") == [
        "1800_TEXT_TEXT:00", "1850_TEXT_TEXT:01"
    ]

def test_date_parse(document_object_to_test):
    assert document_object_to_test.get_header_information("DATE") == [
        "1800-01-01",
        "1850-01-01",
    ]


extra_header_tag = extra_header_value = "TEST"

@pytest.fixture()
def create_file_with_extra_header_tag(
    record_types=["A"],
    at_strings=["B"],
    atx_strings=["C"],
    date_strings=["D"],
):
    """
    Returns an example Document object that has an extra tag
    in the header, and has been parsed using an appropriate
    settings file. The expectation is that this value is picked
    up (because this tag is included in the settings file) and
    added to the header attribute of the Document.

    This expectation is tested in the test:
    - `test_extra_header_tag_is_present`

    The opposite is also tested, i.e., that nothing is returned
    when the header tag is not specified in the settings file.

    This expectation is tested in the test:
    - `test_extra_header_tag_is_absent`
    """

    # Create the header
    test_file_content = generate_file_header(
        record_types, at_strings, atx_strings, date_strings
    )
    test_file_content = (
        f"""
{test_file_content}
##{extra_header_tag}:\t{extra_header_value}\n
"""
    )

    temp_f1 = tempfile.NamedTemporaryFile()
    with open(temp_f1.name, "w") as d:
        d.writelines(test_file_content)

    # Create the settings yaml file
    settings_content = f"""header_tags:
    - AT
    - ATX
    - DATE
    - {extra_header_value}
    """

    temp_f2 = tempfile.NamedTemporaryFile()
    with open(temp_f2.name, "w") as d:
        d.writelines(settings_content)

    test_doc = Document(file = temp_f1.name,
                        settings_file = temp_f2.name)

    test_doc.read_document()
    test_doc.print_header_information()

    return test_doc


def test_extra_header_tag_is_absent(document_object_to_test):
    """
    Testing that an extra header tag is absent when it should be.
    """
    assert document_object_to_test.get_header_information(extra_header_tag) == []


def test_extra_header_tag_is_present(create_file_with_extra_header_tag):
    """
    Testing that an extra header tag is present when it should be
    (the extra header tag having been provided via the settings.yaml file).
    """
    assert create_file_with_extra_header_tag.get_header_information(
        extra_header_tag
    ) == [extra_header_value]
