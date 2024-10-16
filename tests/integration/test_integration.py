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

@pytest.mark.integrationtest

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


@pytest.fixture()
def document_with_datapoints():
    """Returns an example datapoint file testing."""

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


def generate_shortcut_header(
    shortcut_content=[
        ["ENSLAVED*", "!MALE"],
        ["ENSLAVED*", "!FEMALE"],
    ]
):

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


def create_default_datapoint_df( ):
    print( generate_file_header_string_defaults )

    print("-------\n")
    print(generate_shortcut_header_defaults)

    print("-------\n")
    print(generate_data_points_defaults)

    print("-------\n")
    default_settings = read_settings_file( Document().settings_file )

    print( default_settings )

    default_shortcut_mappings_dict = dict(
        pair for d in default_settings.get("shortcut_mappings") for pair in d.items()
    )
    print(default_shortcut_mappings_dict)

    ###      ENSLAVED_AT       ENSLAVED_ATX ENSLAVED_DATE GENDER   X    Y   Z
    ###   0  A, B, C, D, E  1800_TEXT_TEXT:00    1800-01-01   MALE  L1
    ###   1  A, B, C, D, E  1800_TEXT_TEXT:00    1800-01-01   MALE  M1  M2  M3
    ###   2  A, B, C, D, E  1800_TEXT_TEXT:00    1800-01-01   MALE  N1  N2  N3

    ### How many datapoints are we expecting?
    num_datapoints = len( generate_data_points_defaults["DATAPOINT_CONTENT"] )

    ### Are any shortcut labels used? --- Taking the last label for now
    relevant_shortcut_label = int(generate_data_points_defaults["SHORTCUT_LABELS"][-1])
    relevant_shortcut = generate_shortcut_header_defaults["SHORTCUT_CONTENT"][
        relevant_shortcut_label-1]

    print( relevant_shortcut )
    relevant_inheritance_shortcuts = [
        m.replace("*","") for m in relevant_shortcut if re.match(r"^[A-Z]+\*$", m)
    ]

    relevant_autogenerate_shortcuts = [
        m.replace("!", "") for m in relevant_shortcut if re.match(r"^![A-Z]+$", m)
    ]

    print ("inheritance shortcuts")
    print( relevant_inheritance_shortcuts )

    print("autogeneration shortcuts")
    print(relevant_autogenerate_shortcuts)

    skeleton_df = pd.DataFrame.from_dict(generate_file_header_string_defaults)
    skeleton_df = skeleton_df[default_settings.get("header_tags")]

    default_df_tmp = {var: skeleton_df for var in relevant_inheritance_shortcuts}
    for k in default_df_tmp.keys():
        default_df_tmp[k] = default_df_tmp[k].add_prefix(f"{k}_")

    default_df = pd.concat(default_df_tmp.values(), axis=1)

    for auto_generate_content in relevant_autogenerate_shortcuts:
        column_name = default_shortcut_mappings_dict[auto_generate_content]
        column_value = auto_generate_content
        default_df[ column_name ] = column_value

    default_df = ( 
        default_df.loc[default_df.index.repeat(num_datapoints)]
        .reset_index()
        .drop( columns=['index'] )
    )

    ### Add the extra columns from the data table
    datapoint_list = generate_data_points_defaults["COLUMNS"]
    datapoint_content = generate_data_points_defaults['DATAPOINT_CONTENT']

    for i, data_item in enumerate( datapoint_content ):
        if len(data_item) < num_datapoints:
            data_item += [""] * (num_datapoints - len(data_item))
        elif len(data_item) > num_datapoints:
            data_item = data_item[:num_datapoints]

        datapoint_content[i] = data_item

    print( datapoint_list )
    print( datapoint_content )

    datapoint_df = pd.DataFrame(datapoint_content, columns=datapoint_list)

    default_df = default_df.join( datapoint_df )

    return( default_df )


def test_datapoint_parse(document_with_datapoints):

    expected = create_default_datapoint_df()
    observed = document_with_datapoints.data_points_df

    testing.assert_frame_equal(observed, expected)

# def test_datapoint_parse_with_multiple_shortcuts():
#     assert False

# asdf = f"""
# {generate_file_header_string()}

# {generate_shortcut_header()}

# {generate_data_points()}
# """

# temp_f = "data/testout.txt"
# with open(temp_f, "w") as d:
#     d.writelines(asdf)
