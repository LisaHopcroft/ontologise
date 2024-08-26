import pytest
import tempfile
from pathlib import Path
import sys, os

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
