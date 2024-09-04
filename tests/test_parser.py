import sys
import pytest
import tempfile
import inspect
import unittest

sys.path.append("src/ontologise")

from utils import Document

def extract_default_values_hash(f):
    v = inspect.signature(f).parameters.items()
    v_hash = {}

    for _, val in enumerate(v):
        param_name = val[0]
        param_default = inspect.signature(f).parameters[param_name].default
        if not isinstance(param_default, list):
            param_default = [param_default]
        v_hash.update({param_name.upper(): param_default})

    return( v_hash )

def generate_file_header_string(
    title="RECORD_TYPE",
    at=", ".join(["A", "B", "C", "D", "E"]),
    atx="1800_TEXT_TEXT:00",
    date="1800-01-01",
):

    """Returns an example header string using default values."""

    file_header_string = f"""
#[{title}]
##AT:	{at}
##ATX:	{atx}
##DATE:	{date}

"""

    return file_header_string

@pytest.fixture()
def document_with_two_sources(
    title=["A", "B"], at=["C", "D"], atx=["E", "F"], date=["G", "H"],
):
    """Returns an example header for testing."""

    test_file_content = ""

    for i in range(0, len(title)):
        this_text = generate_file_header_string(title[i], at[i], atx[i], date[i])

        test_file_content = f"{test_file_content}{this_text}"

    temp_f = tempfile.NamedTemporaryFile()

    with open(temp_f.name, "w") as d:
        d.writelines(test_file_content)

    test_doc = Document(temp_f.name)
    test_doc.read_document()

    return test_doc

document_with_two_sources_defaults = extract_default_values_hash(document_with_two_sources)

@pytest.mark.parametrize("tag", document_with_two_sources_defaults.keys())
def test_header_parse(document_with_two_sources, tag):
    assert (
        document_with_two_sources.get_header_information(tag)
        == document_with_two_sources_defaults[tag]
    )


extra_header_tag = extra_header_value = "TEST"

extra_tag_list = list(document_with_two_sources_defaults.keys()) + [extra_header_value]
extra_tag_list.remove("TITLE")
extra_tag_list_string = "\n".join(["  - {}".format(t) for t in extra_tag_list])

extra_tag_settings = f"header_tags:\n{extra_tag_list_string}"


@pytest.fixture()
def document_with_extra_header_tag():
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
    test_file_content = generate_file_header_string()

    test_file_content = f"""
{test_file_content}
##{extra_header_tag}:\t{extra_header_value}\n
"""

    temp_f1 = tempfile.NamedTemporaryFile()
    with open(temp_f1.name, "w") as d:
        d.writelines(test_file_content)

    # Create the settings yaml file
    temp_f2 = tempfile.NamedTemporaryFile()
    with open(temp_f2.name, "w") as d:
        d.writelines(extra_tag_settings)

    test_doc = Document(file=temp_f1.name, settings_file=temp_f2.name)

    test_doc.read_document()
    test_doc.print_header_information()

    return test_doc


def test_extra_header_tag_is_absent(document_with_two_sources):
    """
    Testing that an extra header tag is absent when it should be.
    """
    assert document_with_two_sources.get_header_information(extra_header_tag) == []


def test_extra_header_tag_is_present(document_with_extra_header_tag):
    """
    Testing that an extra header tag is present when it should be
    (the extra header tag having been provided via the settings.yaml file).
    """
    assert document_with_extra_header_tag.get_header_information(extra_header_tag) == [
        extra_header_value
    ]


def generate_peopla_object(
        name="A",
        type="person",
        attribute=["X"],
        marker=["*"]
):

    peopla_string = f"""###\t{"@" if type=="place" else ""}[{name}]"""

    if isinstance(attribute, list):
        for i, v in enumerate(attribute):
            peopla_string = f"""{peopla_string}
###\t\t{v}{marker[i]}"""
    else:
        peopla_string = f"""{peopla_string}
###\t\t{attribute}{marker}"""

    return f"""{peopla_string}

"""


@pytest.fixture()
def document_with_two_peopla(
    name=["A", "B"],
    type=["person", "place"],
    attribute=["X", "Y"],
    marker=["*", ""],
):
    """Returns an example peopla string for testing."""

    test_file_content = generate_file_header_string()

    for i in range(0, len(name)):
        this_text = generate_peopla_object(
            name[i], type[i], attribute[i], marker[i]
        )

        test_file_content = f"{test_file_content}{this_text}"

    temp_f = tempfile.NamedTemporaryFile()

    with open(temp_f.name, "w") as d:
        d.writelines(test_file_content)

    test_doc = Document(temp_f.name)
    test_doc.read_document()

    return test_doc


@pytest.fixture()
def document_with_two_peopla_attributes(
    name="A",
    type="person",
    attribute=["X", "Y"],
    marker=["*", ""],
):
    test_file_content = generate_file_header_string()

    this_text = generate_peopla_object(name, type, attribute, marker)

    test_file_content = f"{test_file_content}{this_text}"

    temp_f = tempfile.NamedTemporaryFile()

    with open(temp_f.name, "w") as d:
        d.writelines(test_file_content)

    test_doc = Document(temp_f.name)
    test_doc.read_document()

    return test_doc


document_with_two_peopla_defaults = extract_default_values_hash(
    document_with_two_peopla
)

document_with_two_peopla_attributes_defaults = extract_default_values_hash(
    document_with_two_peopla_attributes
)

generate_file_header_string_defaults = extract_default_values_hash(
    generate_file_header_string
)

def test_default_peopla_parse(document_with_two_peopla):

    for i in range(0, len(document_with_two_peopla.peoplas)):
        p = document_with_two_peopla.peoplas[i]
        assert p.name == document_with_two_peopla_defaults["NAME"][i]
        assert p.type == document_with_two_peopla_defaults["TYPE"][i]

        attr = next(iter(p.attributes.keys()))
        assert attr == document_with_two_peopla_defaults["ATTRIBUTE"][i]

        hash_for_comparison = {}
        if document_with_two_peopla_defaults["MARKER"][i]=="*":
            hash_for_comparison = generate_file_header_string_defaults
            try:
                hash_for_comparison.pop("TITLE")
            except KeyError:
                pass

        assert dict(p.attributes[attr]) == hash_for_comparison


def test_two_attribute_peopla_parse(document_with_two_peopla_attributes):

    for i in range(0, len(document_with_two_peopla_attributes.peoplas)):
        p = document_with_two_peopla_attributes.peoplas[i]
        assert p.name == document_with_two_peopla_attributes_defaults["NAME"][i]
        assert p.type == document_with_two_peopla_attributes_defaults["TYPE"][i]

        attr = next(iter(p.attributes.keys()))
        assert attr == document_with_two_peopla_attributes_defaults["ATTRIBUTE"][i]

        hash_for_comparison = {}
        if document_with_two_peopla_attributes_defaults["MARKER"][i] == "*":
            hash_for_comparison = generate_file_header_string_defaults
            try:
                hash_for_comparison.pop("TITLE")
            except KeyError:
                pass

        assert dict(p.attributes[attr]) == hash_for_comparison
