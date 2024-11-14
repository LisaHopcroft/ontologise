import sys
import pytest
import pandas as pd
import tempfile
import inspect
import string
import re
from pandas import testing


sys.path.append("src/ontologise")

from utils import Document, read_settings_file


def extract_default_values_hash(f):
    """
    Extract the default parameter values of a function

    A function that will, for a given function f(), extract the default
    values of f() and save them in a dictionary.

    :param f: the function to be analysed

    :returns: a dictionary containing the default values for the fuction f
    """
    v = inspect.signature(f).parameters.items()
    v_hash = {}

    for _, val in enumerate(v):
        param_name = val[0]
        param_default = inspect.signature(f).parameters[param_name].default
        if not isinstance(param_default, list):
            param_default = [param_default]
        v_hash.update({param_name.upper(): param_default})

    return v_hash


def generate_file_header_string(
    title="RECORD_TYPE",
    at=", ".join(["A", "B", "C", "D", "E"]),
    atx="1800_TEXT_TEXT:00",
    date="1800-01-01",
):
    """
    Create a header for a marked up Ontologise file

    :param title: the title of the document (default: "RECORD_TYPE")
    :param at: the at (location) value to be used (default: "A, B, C, D, E")
    :param atx: the atx value to be used (default: "1800_TEXT_TEXT:00")
    :param date: the date value to be used (default: "1800-01-01")

    :returns: a string of the header
    """

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
    """
    Python fixture that creates a document that contains two sources

    :param title: list of source titles to be included in the document
    :param at: list of at values to be included in the document
    :param atx: list of atx values to be included in the document
    :param date: list of date values to be included in the document
    """

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


document_with_two_sources_defaults = extract_default_values_hash(
    document_with_two_sources
)


@pytest.mark.parametrize("tag", document_with_two_sources_defaults.keys())
def test_header_parse(document_with_two_sources, tag):
    """
    For each expected header tag, check that the information from the
    header has been parsed and stored correctly in the Document, for
    each expected header tag
    """
    assert (
        document_with_two_sources.get_header_information(tag)
        == document_with_two_sources_defaults[tag]
    )


# Creating a test to ensure that, if an additional header value is included,
# this is parsed and stored correctly in the Document.
extra_header_tag = extra_header_value = "TEST"

extra_tag_list = list(document_with_two_sources_defaults.keys()) + [extra_header_value]
extra_tag_list.remove("TITLE")
extra_tag_list_string = "\n".join(["  - {}".format(t) for t in extra_tag_list])

extra_tag_settings = f"header_tags:\n{extra_tag_list_string}\n"


@pytest.fixture()
def document_with_extra_header_tag():
    """
    Python fixture that:
    - creates a temporary document with an extra header tag
    - creates a temporary settings file that also contains that header tag
    - parses that document according to those settings
    - returns the parsed document
    """

    # Create the header
    test_file_content = generate_file_header_string()

    test_file_content = f"""
{test_file_content.rstrip()}
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

    print( "file name: "     + temp_f1.name )
    print( "settings file: " + temp_f2.name )

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


def generate_peopla_object(name="A", type="person", attribute=["X"], marker=["*"]):
    """
    Create text to represent a peopla object for a marked up Ontologise file

    :param name: the name of the peopla object (default: "A")
    :param type: the type of peopla object - person or place (default: "person")
    :param attribute: any attribute(s) to attach to the peopla object (default: ["X"])
    :param marker: any marker(s) to be included for each attribute (default: ["*"])

    :returns: a string of the peopla object
    """

    # To check: that type is in the expected list of options
    # To check: that the number of attributes matches the number of markers

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
    name=["A", "B"], type=["person", "place"], attribute=["X", "Y"], marker=["*", ""],
):
    """
    Python fixture that:
    - creates a temporary document containing two peopla (1 person, 1 place) with one attribute each
    - one of these attributes includes inheritance of document properties (by virtue of the '*' marker)
    - parses that document according to default settings
    - returns the parsed document
    """

    test_file_content = generate_file_header_string()

    for i in range(0, len(name)):
        this_text = generate_peopla_object(name[i], type[i], attribute[i], marker[i])

        test_file_content = f"{test_file_content}{this_text}"

    temp_f = tempfile.NamedTemporaryFile()

    with open(temp_f.name, "w") as d:
        d.writelines(test_file_content)

    test_doc = Document(temp_f.name)
    test_doc.read_document()

    return test_doc


@pytest.fixture()
def document_with_two_peopla_attributes(
    name="A", type="person", attribute=["X", "Y"], marker=["*", ""],
):
    """
    Python fixture that:
    - creates a temporary document containing 1 peopla with 2 attributes
    - one of these attributes includes inheritance of document properties (by virtue of the '*' marker)
    - parses that document according to default settings
    - returns the parsed document
    """

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
    """
    Testing that information has been extracted appropriately from
    the document that contains two peopla (1 person, 1 place), each
    with one attribute. One of the attributes includes inheritance
    of document properties.
    """
    for i in range(0, len(document_with_two_peopla.peoplas)):
        p = document_with_two_peopla.peoplas[i]
        assert p.name == document_with_two_peopla_defaults["NAME"][i]
        assert p.type == document_with_two_peopla_defaults["TYPE"][i]

        attr = next(iter(p.attributes.keys()))
        assert attr == document_with_two_peopla_defaults["ATTRIBUTE"][i]

        hash_for_comparison = {}
        if document_with_two_peopla_defaults["MARKER"][i] == "*":
            hash_for_comparison = generate_file_header_string_defaults
            try:
                hash_for_comparison.pop("TITLE")
            except KeyError:
                pass

        assert dict(p.attributes[attr]) == hash_for_comparison


def test_two_attribute_peopla_parse(document_with_two_peopla_attributes):
    """
    Testing that information has been extracted appropriately from
    the document that contains 1 peopla with two attributes. One of
    the attributes includes inheritance of document properties.
    """
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


def generate_shortcut_header(
    shortcut_content=[["ENSLAVED*", "!MALE"], ["ENSLAVED*", "!FEMALE"],]
):
    """
    Generates text for a shortcut header to be used in a marked up Ontologise file

    For example:

    shortcut_content=[
        ["A*", "!M"],
        ["B*", "!N"],
    ]

    will generate the header:

    ----------------------------------------------------------------------
    ### ^1:
    ###     A*
    ###     !M
    ### ^2:
    ###     B*
    ###     !N
    ----------------------------------------------------------------------

    :param shortcut_content: A nested list of shortcut content

    :returns: a string of the shortcut header object
    """

    shortcut_string = "-" * 70
    shortcut_string += "\n"

    for i, t in enumerate(shortcut_content):
        shortcut_string += f"###\t^{i+1}:\n"
        for j in t:
            shortcut_string += f"###\t\t{j}\n"

    shortcut_string += "-" * 70

    return shortcut_string


def generate_data_points(
    columns=list(string.ascii_uppercase[23:26]),
    shortcut_labels=["", "", "1"],
    datapoint_content=[["L1"], ["M1", "M2", "M3"], ["N1", "N2", "N3", "N4"]],
):
    """
    Generates text for a table to be used in a marked up Ontologise file
    
    :param columns: A list of the columns in the table
    :param shortcut_labels: A list of the shortcut labels to be added to the table to autogenerate columns
    :param datapoint_content: A nested list of the datapoints to be included in the table

    :returns: a string of the table object (the header and datapoints)
    """

    shortcut_markers = [re.sub(r"^(\d+)$", r"^\1", i) for i in shortcut_labels]
    column_list = [x + y for x, y in zip(columns, shortcut_markers)]
    column_string = "\\t".join(column_list)

    datapoint_strings = [f"""###\\t{column_string}"""]

    for d in datapoint_content:
        datapoint_strings.append("\t".join(d))

    datapoint_strings.append("[/]")
    datapoint_strings.append("###\\tEND")

    return "\n".join(datapoint_strings)


generate_shortcut_header_defaults = extract_default_values_hash(
    generate_shortcut_header
)

generate_data_points_defaults = extract_default_values_hash(generate_data_points)


@pytest.fixture()
def document_with_datapoints():
    """
    Python fixture that:
    - creates a temporary document containing a table (which contains autogenerated and inheritance markers)
    - parses that document according to default settings
    - returns the parsed document
    """

    test_file_content = f"""
{generate_file_header_string()}

{generate_shortcut_header()}

{generate_data_points()}
"""

    temp_f = tempfile.NamedTemporaryFile()

    with open(temp_f.name, "w") as d:
        d.writelines(test_file_content)

    test_doc = Document(temp_f.name)
    test_doc.read_document()

    return test_doc


def create_default_datapoint_df():
    """
    Generates a dataframe representing the datapoints as they should
    be stored when all default parameters are used for the constructor
    funtionsl.
    
    :returns: a data frame of the datapoints
    """

    # Relevant defaults to be used in this function:
    # - generate_file_header_string_defaults (from generate_file_header_string())
    # - generate_shortcut_header_defaults (from generate_shortcut_header())
    # - generate_data_points_defaults (from generate_data_points())

    # Also need to extract the settings as represented by the
    # default settings file, and then represented them as a dictionary
    default_settings = read_settings_file(Document().settings_file)

    default_shortcut_mappings_dict = dict(
        pair for d in default_settings.get("shortcut_mappings") for pair in d.items()
    )

    # An example datapoint table, for reference:
    #      ENSLAVED_AT       ENSLAVED_ATX ENSLAVED_DATE GENDER   X    Y   Z
    #   0  A, B, C, D, E  1800_TEXT_TEXT:00    1800-01-01   MALE  L1
    #   1  A, B, C, D, E  1800_TEXT_TEXT:00    1800-01-01   MALE  M1  M2  M3
    #   2  A, B, C, D, E  1800_TEXT_TEXT:00    1800-01-01   MALE  N1  N2  N3

    # How many datapoints are we expecting?
    num_datapoints = len(generate_data_points_defaults["DATAPOINT_CONTENT"])

    # Are any shortcut labels used? --- Taking the last label for now
    relevant_shortcut_label = int(generate_data_points_defaults["SHORTCUT_LABELS"][-1])
    relevant_shortcut = generate_shortcut_header_defaults["SHORTCUT_CONTENT"][
        relevant_shortcut_label - 1
    ]

    # Are any of these shortcut labels an inheritance marker?
    relevant_inheritance_shortcuts = [
        m.replace("*", "") for m in relevant_shortcut if re.match(r"^[A-Z]+\*$", m)
    ]

    # Are any of these shortcut labels an autogeneration marker?
    relevant_autogenerate_shortcuts = [
        m.replace("!", "") for m in relevant_shortcut if re.match(r"^![A-Z]+$", m)
    ]

    # Starting to build the dataframe of datapoints

    # (1) Add columns for the header tags.
    #     For the example above, this will look like:
    #     AT                ATX                 DATE
    #     A, B, C, D, E     1800_TEXT_TEXT:00   1800-01-01
    skeleton_df = pd.DataFrame.from_dict(generate_file_header_string_defaults)
    skeleton_df = skeleton_df[default_settings.get("header_tags")]

    # (2) Repeat these columns for each column with inheritance (adding a prefix).
    #     For the example above, this will look like:
    #     ENSLAVED_AT       ENSLAVED_ATX        ENSLAVED_DATE
    #     A, B, C, D, E     1800_TEXT_TEXT:00   1800-01-01
    # NB. copies of the skeleton table are taken for each relevant_inheritance_shortcuts
    #     are maintained in a list, before being concatenated into a single dataframe
    default_df_tmp = {var: skeleton_df for var in relevant_inheritance_shortcuts}
    for k in default_df_tmp.keys():
        default_df_tmp[k] = default_df_tmp[k].add_prefix(f"{k}_")
    default_df = pd.concat(default_df_tmp.values(), axis=1)

    # (3) Add any autogenerated content.
    #     For the example above, this will look like:
    #     ENSLAVED_AT       ENSLAVED_ATX        ENSLAVED_DATE   GENDER
    #     A, B, C, D, E     1800_TEXT_TEXT:00   1800-01-01      MALE
    for auto_generate_content in relevant_autogenerate_shortcuts:
        column_name = default_shortcut_mappings_dict[auto_generate_content]
        column_value = auto_generate_content
        default_df[column_name] = column_value

    # (4) Repeat these values for the number of datapoints that are known to exist.
    #     For the example above, this will look like:
    #     ENSLAVED_AT       ENSLAVED_ATX        ENSLAVED_DATE   GENDER
    #     A, B, C, D, E     1800_TEXT_TEXT:00   1800-01-01      MALE
    #     A, B, C, D, E     1800_TEXT_TEXT:00   1800-01-01      MALE
    #     A, B, C, D, E     1800_TEXT_TEXT:00   1800-01-01      MALE
    default_df = (
        default_df.loc[default_df.index.repeat(num_datapoints)]
        .reset_index()
        .drop(columns=["index"])
    )

    # (5) Create a dataframe for the datapoints that are known to exist and join
    #     this to the already created default_df.
    #     For the example above, this will look like:
    #     ENSLAVED_AT       ENSLAVED_ATX        ENSLAVED_DATE   GENDER  X   Y   Z
    #     A, B, C, D, E     1800_TEXT_TEXT:00   1800-01-01      MALE    L1
    #     A, B, C, D, E     1800_TEXT_TEXT:00   1800-01-01      MALE    M1  M2  M3
    #     A, B, C, D, E     1800_TEXT_TEXT:00   1800-01-01      MALE    N1  N2  N3
    datapoint_list = generate_data_points_defaults["COLUMNS"]
    datapoint_content = generate_data_points_defaults["DATAPOINT_CONTENT"]

    for i, data_item in enumerate(datapoint_content):
        if len(data_item) < num_datapoints:
            data_item += [""] * (num_datapoints - len(data_item))
        elif len(data_item) > num_datapoints:
            data_item = data_item[:num_datapoints]

        datapoint_content[i] = data_item

    datapoint_df = pd.DataFrame(datapoint_content, columns=datapoint_list)
    default_df = default_df.join(datapoint_df)

    # (6) Add the global_id column
    default_df[ "global_id"] = None

    # (7) Return the dataframe
    return default_df


def test_datapoint_parse(document_with_datapoints):
    """
    Testing that information has been extracted appropriately from
    the document that contains datapoints.
    """
    expected = create_default_datapoint_df()
    observed = document_with_datapoints.data_points_df

    testing.assert_frame_equal(observed, expected)
