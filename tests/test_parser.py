import pytest


@pytest.fixture()
def file_header(
    record_type="RECORD_TYPE",
    at_string=", ".join(["A", "B", "C", "D", "E"]),
    atx_string="1800_TEXT_TEXT:00",
    date_string="1800-01-01",
):

    """Returns an example header for testing."""

    file_header_string = (
        f"""
#[{record_type}]
##AT:	{at_string}
##ATX:	{atx_string}
##DATE:	{date_string}
""",
    )

    return file_header_string


def test_header_parse(file_header):
    assert 1 == 1
