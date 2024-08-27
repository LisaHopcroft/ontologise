import sys
import pytest
import tempfile
import inspect

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
def default_document(
    title=["A", "B"],
    at=["C", "D"],
    atx=["E", "F"],
    date=["G", "H"],
):
    """Returns an example header for testing."""

    test_file_content = ""

    for i in range(0, len(title)):
        this_text = generate_file_header(
            title[i], at[i], atx[i], date[i]
        )

        test_file_content = f"{test_file_content}{this_text}"

    temp_f = tempfile.NamedTemporaryFile()

    with open(temp_f.name, "w") as d:
        d.writelines(test_file_content)

    test_doc = Document(temp_f.name)
    test_doc.read_document()

    return test_doc

default_header_values = inspect.signature(default_document).parameters.items()
default_header_values_hash = {}

for i, val in enumerate(default_header_values):
    param_name = val[0]
    param_default = inspect.signature(default_document).parameters[param_name].default
    default_header_values_hash.update({param_name.upper(): param_default})


@pytest.mark.parametrize("tag", default_header_values_hash.keys())
def test_header_parse(default_document,tag):
    assert (
        default_document.get_header_information(tag)
        == default_header_values_hash[tag]
    )


extra_header_tag = extra_header_value = "TEST"

extra_tag_list = list(default_header_values_hash.keys()) + [ extra_header_value ]
extra_tag_list.remove("TITLE")
extra_tag_list_string = "\n".join(
    ["  - {}".format(t) for t in extra_tag_list]
)

extra_tag_settings = f"header_tags:\n{extra_tag_list_string}"

@pytest.fixture()
def create_file_with_extra_header_tag():
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
    test_file_content = generate_file_header()

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
    temp_f2 = tempfile.NamedTemporaryFile()
    with open(temp_f2.name, "w") as d:
        d.writelines(extra_tag_settings)

    test_doc = Document(file = temp_f1.name,
                        settings_file = temp_f2.name)

    test_doc.read_document()
    test_doc.print_header_information()

    return test_doc


def test_extra_header_tag_is_absent(default_document):
    """
    Testing that an extra header tag is absent when it should be.
    """
    assert default_document.get_header_information(extra_header_tag) == []


def test_extra_header_tag_is_present(create_file_with_extra_header_tag):
    """
    Testing that an extra header tag is present when it should be
    (the extra header tag having been provided via the settings.yaml file).
    """
    assert create_file_with_extra_header_tag.get_header_information(
        extra_header_tag
    ) == [extra_header_value]
