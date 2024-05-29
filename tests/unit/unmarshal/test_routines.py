from __future__ import annotations

import datetime
import decimal
import fractions

import pytest
from typelib.unmarshal import routines


@pytest.mark.suite(
    bytes=dict(given_input=b"1", expected_output=b"1"),
    string=dict(given_input="1", expected_output=b"1"),
    number=dict(given_input=1, expected_output=b"1"),
    bool=dict(given_input=True, expected_output=b"True"),
    date=dict(given_input=datetime.date(2020, 1, 1), expected_output=b"2020-01-01"),
)
def test_bytes_unmarshaller(given_input, expected_output):
    # Given
    given_unmarhaller = routines.BytesUnmarshaller(bytes, {})
    # When
    output = given_unmarhaller(given_input)
    # Then
    assert output == expected_output


@pytest.mark.suite(
    bytes=dict(given_input=b"1", expected_output="1"),
    string=dict(given_input="1", expected_output="1"),
    number=dict(given_input=1, expected_output="1"),
    bool=dict(given_input=True, expected_output="True"),
    date=dict(given_input=datetime.date(2020, 1, 1), expected_output="2020-01-01"),
)
def test_str_unmarshaller(given_input, expected_output):
    # Given
    given_unmarhaller = routines.StrUnmarshaller(str, {})
    # When
    output = given_unmarhaller(given_input)
    # Then
    assert output == expected_output


@pytest.mark.suite(
    integer=dict(given_type=int),
    float=dict(given_type=float),
    decimal=dict(given_type=decimal.Decimal),
    fraction=dict(given_type=fractions.Fraction),
)
@pytest.mark.suite(
    bytes=dict(given_input=b"1", expected_output=1),
    string=dict(given_input="1", expected_output=1),
    number=dict(given_input=1, expected_output=1),
    bool=dict(given_input=True, expected_output=1),
    date=dict(given_input=datetime.date(2020, 1, 1), expected_output=1577854800.0),
)
def test_number_unmarshaller(given_input, given_type, expected_output):
    # Given
    given_unmarhaller = routines.NumberUnmarshaller(given_type, {})
    expected_output = given_type(expected_output)
    # When
    output = given_unmarhaller(given_input)
    # Then
    assert output == expected_output
    assert isinstance(output, given_type)


@pytest.mark.suite(
    bytes_number=dict(given_input=b"1", expected_output=datetime.date(1970, 1, 1)),
    string_number=dict(given_input="1", expected_output=datetime.date(1970, 1, 1)),
    number=dict(given_input=1, expected_output=datetime.date(1970, 1, 1)),
    date_bytes=dict(
        given_input=b"1969-12-31",
        expected_output=datetime.date(1969, 12, 31),
    ),
    date_string=dict(
        given_input="1969-12-31",
        expected_output=datetime.date(1969, 12, 31),
    ),
    date_string_partial=dict(
        given_input="1969-12",
        expected_output=datetime.date(1969, 12, 1),
    ),
    date=dict(
        given_input=datetime.date(1969, 12, 31),
        expected_output=datetime.date(1969, 12, 31),
    ),
    datetime=dict(
        given_input=datetime.datetime(1969, 12, 31),
        expected_output=datetime.date(1969, 12, 31),
    ),
    time=dict(
        given_input=datetime.time(0),
        expected_output=datetime.date.today(),
    ),
)
def test_date_unmarshaller(given_input, expected_output):
    # Given
    given_unmarhaller = routines.DateUnmarshaller(datetime.date, {})
    # When
    output = given_unmarhaller(given_input)
    # Then
    assert output == expected_output


@pytest.mark.suite(
    bytes_number=dict(
        given_input=b"1",
        expected_output=datetime.datetime(
            1970, 1, 1, second=1, tzinfo=datetime.timezone.utc
        ),
    ),
    string_number=dict(
        given_input="1",
        expected_output=datetime.datetime(
            1970, 1, 1, second=1, tzinfo=datetime.timezone.utc
        ),
    ),
    number=dict(
        given_input=1,
        expected_output=datetime.datetime(
            1970, 1, 1, second=1, tzinfo=datetime.timezone.utc
        ),
    ),
    date_bytes=dict(
        given_input=b"1969-12-31",
        expected_output=datetime.datetime(1969, 12, 31, tzinfo=datetime.timezone.utc),
    ),
    date_string=dict(
        given_input="1969-12-31",
        expected_output=datetime.datetime(1969, 12, 31, tzinfo=datetime.timezone.utc),
    ),
    date_string_partial=dict(
        given_input="1969-12",
        expected_output=datetime.datetime(1969, 12, 1, tzinfo=datetime.timezone.utc),
    ),
    datetime=dict(
        given_input=datetime.datetime(1969, 12, 31),
        expected_output=datetime.datetime(1969, 12, 31),
    ),
    date=dict(
        given_input=datetime.date(1969, 12, 31),
        expected_output=datetime.datetime(1969, 12, 31),
    ),
    time=dict(
        given_input=datetime.time(tzinfo=datetime.timezone.utc),
        expected_output=datetime.datetime.today().replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=datetime.timezone.utc
        ),
    ),
)
def test_datetime_unmarshaller(given_input, expected_output):
    # Given
    given_unmarhaller = routines.DateTimeUnmarshaller(datetime.datetime, {})
    # When
    output = given_unmarhaller(given_input)
    # Then
    assert output == expected_output


@pytest.mark.suite(
    bytes_number=dict(
        given_input=b"1",
        expected_output=datetime.time(second=1, tzinfo=datetime.timezone.utc),
    ),
    string_number=dict(
        given_input="1",
        expected_output=datetime.time(second=1, tzinfo=datetime.timezone.utc),
    ),
    number=dict(
        given_input=1,
        expected_output=datetime.time(second=1, tzinfo=datetime.timezone.utc),
    ),
    date_bytes=dict(
        given_input=b"1969-12-31",
        expected_output=datetime.time(tzinfo=datetime.timezone.utc),
    ),
    date_string=dict(
        given_input="1969-12-31",
        expected_output=datetime.time(tzinfo=datetime.timezone.utc),
    ),
    date_string_partial=dict(
        given_input="1969-12",
        expected_output=datetime.time(tzinfo=datetime.timezone.utc),
    ),
    time_string=dict(
        given_input="01:00:00+00:00",
        expected_output=datetime.time(hour=1, tzinfo=datetime.timezone.utc),
    ),
    datetime_string=dict(
        given_input="1969-12-31T01:00:00+00:00",
        expected_output=datetime.time(hour=1, tzinfo=datetime.timezone.utc),
    ),
    datetime=dict(
        given_input=datetime.datetime(1969, 12, 31, minute=1),
        expected_output=datetime.time(minute=1),
    ),
    date=dict(
        given_input=datetime.date(1969, 12, 31),
        expected_output=datetime.time(),
    ),
    time=dict(
        given_input=datetime.time(tzinfo=datetime.timezone.utc),
        expected_output=datetime.time(tzinfo=datetime.timezone.utc),
    ),
)
def test_time_unmarshaller(given_input, expected_output):
    # Given
    given_unmarhaller = routines.TimeUnmarshaller(datetime.time, {})
    # When
    output = given_unmarhaller(given_input)
    # Then
    assert output == expected_output


@pytest.mark.suite(
    bytes_number=dict(
        given_input=b"1",
        expected_output=datetime.timedelta(seconds=1),
    ),
    string_number=dict(
        given_input="1",
        expected_output=datetime.timedelta(seconds=1),
    ),
    number=dict(
        given_input=1,
        expected_output=datetime.timedelta(seconds=1),
    ),
    period=dict(
        given_input="PT1S",
        expected_output=datetime.timedelta(seconds=1),
    ),
    timedelta=dict(
        given_input=datetime.timedelta(seconds=1),
        expected_output=datetime.timedelta(seconds=1),
    ),
)
def test_timedelta_unmarshaller(given_input, expected_output):
    # Given
    given_unmarhaller = routines.TimeDeltaUnmarshaller(datetime.timedelta, {})
    # When
    output = given_unmarhaller(given_input)
    # Then
    assert output == expected_output
