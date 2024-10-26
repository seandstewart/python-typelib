from __future__ import annotations

import datetime
import decimal
import fractions
import pathlib
import re
import typing
import uuid

import pytest

from typelib.unmarshals import routines

from tests import models


@pytest.mark.suite(
    bytes=dict(given_input=b"1", expected_output=b"1"),
    string=dict(given_input="1", expected_output=b"1"),
    number=dict(given_input=1, expected_output=b"1"),
    bool=dict(given_input=True, expected_output=b"True"),
    date=dict(given_input=datetime.date(2020, 1, 1), expected_output=b"2020-01-01"),
)
def test_bytes_unmarshaller(given_input, expected_output):
    # Given
    given_unmarshaller = routines.BytesUnmarshaller(bytes, {})
    # When
    output = given_unmarshaller(given_input)
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
    given_unmarshaller = routines.StringUnmarshaller(str, {})
    # When
    output = given_unmarshaller(given_input)
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
    date=dict(given_input=datetime.date(2020, 1, 1), expected_output=1577836800.0),
    iterable=dict(given_input=["1"], expected_output=1),
    mapping=dict(given_input={"value": "1"}, expected_output=1),
)
def test_number_unmarshaller(given_input, given_type, expected_output):
    if isinstance(given_input, dict) and given_type in (float, int):
        pytest.skip(f"{given_type} does not support mapping inputs.")

    # Given
    if given_type is fractions.Fraction and isinstance(given_input, dict):
        given_input = {"numerator": given_input["value"]}

    given_unmarshaller = routines.NumberUnmarshaller(given_type, {})
    expected_output = given_type(expected_output)
    # When
    output = given_unmarshaller(given_input)
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
    given_unmarshaller = routines.DateUnmarshaller(datetime.date, {})
    # When
    output = given_unmarshaller(given_input)
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
        expected_output=datetime.datetime(1969, 12, 31, tzinfo=datetime.timezone.utc),
    ),
    time=dict(
        given_input=datetime.time(tzinfo=datetime.timezone.utc),
        expected_output=datetime.datetime.today()
        .astimezone(tz=datetime.timezone.utc)
        .replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=datetime.timezone.utc
        ),
    ),
)
def test_datetime_unmarshaller(given_input, expected_output):
    # Given
    given_unmarshaller = routines.DateTimeUnmarshaller(datetime.datetime, {})
    # When
    output = given_unmarshaller(given_input)
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
        expected_output=datetime.time(tzinfo=datetime.timezone.utc),
    ),
    time=dict(
        given_input=datetime.time(tzinfo=datetime.timezone.utc),
        expected_output=datetime.time(tzinfo=datetime.timezone.utc),
    ),
)
def test_time_unmarshaller(given_input, expected_output):
    # Given
    given_unmarshaller = routines.TimeUnmarshaller(datetime.time, {})
    # When
    output = given_unmarshaller(given_input)
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
    given_unmarshaller = routines.TimeDeltaUnmarshaller(datetime.timedelta, {})
    # When
    output = given_unmarshaller(given_input)
    # Then
    assert output == expected_output


@pytest.mark.suite(
    bytes_number=dict(
        given_input=b"1",
        expected_output=uuid.UUID(int=1),
    ),
    string_number=dict(
        given_input="1",
        expected_output=uuid.UUID(int=1),
    ),
    number=dict(
        given_input=1,
        expected_output=uuid.UUID(int=1),
    ),
    string=dict(
        given_input="00000000-0000-0000-0000-000000000001",
        expected_output=uuid.UUID(int=1),
    ),
    bytes=dict(
        given_input=b"00000000-0000-0000-0000-000000000001",
        expected_output=uuid.UUID(int=1),
    ),
    uuid=dict(
        given_input=uuid.UUID(int=1),
        expected_output=uuid.UUID(int=1),
    ),
)
def test_uuid_unmarshaller(given_input, expected_output):
    # Given
    given_unmarshaller = routines.UUIDUnmarshaller(uuid.UUID, {})
    # When
    output = given_unmarshaller(given_input)
    # Then
    assert output == expected_output


@pytest.mark.suite(
    bytes=dict(
        given_input=b"1",
        expected_output=re.compile(r"1"),
    ),
    string=dict(
        given_input="1",
        expected_output=re.compile(r"1"),
    ),
    pattern=dict(
        given_input=re.compile(r"1"),
        expected_output=re.compile(r"1"),
    ),
)
def test_pattern_unmarshaller(given_input, expected_output):
    # Given
    given_unmarshaller = routines.PatternUnmarshaller(re.Pattern, {})
    # When
    output = given_unmarshaller(given_input)
    # Then
    assert output == expected_output


@pytest.mark.suite(
    bytes=dict(
        given_input=b"/my/path",
        expected_output=pathlib.Path("/my/path"),
    ),
    string=dict(
        given_input="/my/path",
        expected_output=pathlib.Path("/my/path"),
    ),
    path=dict(
        given_input=pathlib.Path("/my/path"),
        expected_output=pathlib.Path("/my/path"),
    ),
)
def test_path_unmarshaller(given_input, expected_output):
    # Given
    given_unmarshaller = routines.PathUnmarshaller(pathlib.Path, {})
    # When
    output = given_unmarshaller(given_input)
    # Then
    assert output == expected_output


@pytest.mark.suite(
    bytes_literal=dict(
        given_input=b"{'field': 'value'}",
        expected_output={"field": "value"},
    ),
    string_literal=dict(
        given_input="{'field': 'value'}",
        expected_output={"field": "value"},
    ),
    bytes_json=dict(
        given_input=b'{"field": "value"}',
        expected_output={"field": "value"},
    ),
    string_json=dict(
        given_input='{"field": "value"}',
        expected_output={"field": "value"},
    ),
    dict=dict(
        given_input={"field": "value"},
        expected_output={"field": "value"},
    ),
)
def test_mapping_unmarshaller(given_input, expected_output):
    # Given
    given_unmarshaller = routines.MappingUnmarshaller(typing.Mapping, {})
    # When
    output = given_unmarshaller(given_input)
    # Then
    assert output == expected_output


@pytest.mark.suite(
    bytes_literal=dict(
        given_input=b"{'field', 'value'}",
        expected_output={"field", "value"},
    ),
    string_literal=dict(
        given_input="('field', 'value')",
        expected_output=("field", "value"),
    ),
    bytes_json=dict(
        given_input=b'["field", "value"]',
        expected_output=["field", "value"],
    ),
    string_json=dict(
        given_input='["field", "value"]',
        expected_output=["field", "value"],
    ),
    dict=dict(
        given_input={"field": "value"},
        expected_output={"field": "value"},
    ),
    list=dict(
        given_input=["field", "value"],
        expected_output=["field", "value"],
    ),
)
def test_iterable_unmarshaller(given_input, expected_output):
    # Given
    given_unmarshaller = routines.IterableUnmarshaller(typing.Iterable, {})
    # When
    output = given_unmarshaller(given_input)
    # Then
    assert output == expected_output


@pytest.mark.suite(
    bytes=dict(
        given_input=b"1",
        given_literal=typing.Literal[1],
        given_context={},
        expected_output=1,
    ),
    string=dict(
        given_input="1",
        given_literal=typing.Literal[1],
        given_context={},
        expected_output=1,
    ),
    integer=dict(
        given_input=1,
        given_literal=typing.Literal[1],
        given_context={},
        expected_output=1,
    ),
    json=dict(
        given_input="true",
        given_literal=typing.Literal[True],
        given_context={},
        expected_output=True,
    ),
)
def test_literal_unmarshaller(
    given_input, given_literal, given_context, expected_output
):
    # Given
    given_unmarshaller = routines.LiteralUnmarshaller(given_literal, given_context)
    # When
    output = given_unmarshaller(given_input)
    # Then
    assert output == expected_output


@pytest.mark.suite(
    bytes_number=dict(
        given_input=b"1",
        given_union=typing.Union[int, str],
        given_context={
            int: routines.NumberUnmarshaller(int, {}),
            str: routines.StringUnmarshaller(str, {}),
        },
        expected_output=1,
    ),
    string_number=dict(
        given_input="1",
        given_union=typing.Union[int, str],
        given_context={
            int: routines.NumberUnmarshaller(int, {}),
            str: routines.StringUnmarshaller(str, {}),
        },
        expected_output=1,
    ),
    bytes=dict(
        given_input=b"bytes",
        given_union=typing.Union[int, str],
        given_context={
            int: routines.NumberUnmarshaller(int, {}),
            str: routines.StringUnmarshaller(str, {}),
        },
        expected_output="bytes",
    ),
    string=dict(
        given_input="string",
        given_union=typing.Union[int, str],
        given_context={
            int: routines.NumberUnmarshaller(int, {}),
            str: routines.StringUnmarshaller(str, {}),
        },
        expected_output="string",
    ),
    integer=dict(
        given_input=1,
        given_union=typing.Union[int, str],
        given_context={
            int: routines.NumberUnmarshaller(int, {}),
            str: routines.StringUnmarshaller(str, {}),
        },
        expected_output=1,
    ),
    float=dict(
        given_input=1.0,
        given_union=typing.Union[int, str],
        given_context={
            int: routines.NumberUnmarshaller(int, {}),
            str: routines.StringUnmarshaller(str, {}),
        },
        expected_output=1,
    ),
    optional_date_none=dict(
        given_input=None,
        given_union=typing.Optional[datetime.date],
        given_context={
            datetime.date: routines.DateUnmarshaller(datetime.date, {}),
            type(None): routines.NoOpUnmarshaller(type(None), {}),
        },
        expected_output=None,
    ),
    optional_date_date=dict(
        given_input=datetime.date.today().isoformat(),
        given_union=typing.Optional[datetime.date],
        given_context={
            datetime.date: routines.DateUnmarshaller(datetime.date, {}),
            type(None): routines.NoneTypeUnmarshaller(type(None), {}),
        },
        expected_output=datetime.date.today(),
    ),
)
def test_union_unmarshaller(given_input, given_union, given_context, expected_output):
    # Given
    given_unmarshaller = routines.UnionUnmarshaller(given_union, given_context)
    # When
    output = given_unmarshaller(given_input)
    # Then
    assert output == expected_output


@pytest.mark.suite(
    bytes_literal=dict(
        given_input=b"{'field': '1'}",
        given_mapping=typing.Mapping[str, int],
        given_context={
            int: routines.NumberUnmarshaller(int, {}),
            str: routines.StringUnmarshaller(str, {}),
        },
        expected_output={"field": 1},
    ),
    string_literal=dict(
        given_input="{'field': '1'}",
        given_mapping=typing.Mapping[str, int],
        given_context={
            int: routines.NumberUnmarshaller(int, {}),
            str: routines.StringUnmarshaller(str, {}),
        },
        expected_output={"field": 1},
    ),
    bytes_json=dict(
        given_input=b'{"field": "1"}',
        given_mapping=typing.Mapping[str, int],
        given_context={
            int: routines.NumberUnmarshaller(int, {}),
            str: routines.StringUnmarshaller(str, {}),
        },
        expected_output={"field": 1},
    ),
    string_json=dict(
        given_input='{"field": "1"}',
        given_mapping=typing.Mapping[str, int],
        given_context={
            int: routines.NumberUnmarshaller(int, {}),
            str: routines.StringUnmarshaller(str, {}),
        },
        expected_output={"field": 1},
    ),
    dict=dict(
        given_input={b"field": "1"},
        given_mapping=typing.Mapping[str, int],
        given_context={
            int: routines.NumberUnmarshaller(int, {}),
            str: routines.StringUnmarshaller(str, {}),
        },
        expected_output={"field": 1},
    ),
)
def test_subscripted_mapping_unmarshaller(
    given_input, given_mapping, given_context, expected_output
):
    # Given
    given_unmarshaller = routines.SubscriptedMappingUnmarshaller(
        given_mapping, given_context
    )
    # When
    output = given_unmarshaller(given_input)
    # Then
    assert output == expected_output


@pytest.mark.suite(
    generic_iterable=dict(
        given_iterable=typing.Iterable[int],
        given_context={
            int: routines.NumberUnmarshaller(int, {}),
        },
        expected_output=[2, 1],
    ),
    list=dict(
        given_iterable=list[int],
        given_context={
            int: routines.NumberUnmarshaller(int, {}),
        },
        expected_output=[2, 1],
    ),
    tuple=dict(
        given_iterable=tuple[int, ...],
        given_context={
            int: routines.NumberUnmarshaller(int, {}),
        },
        expected_output=(2, 1),
    ),
    set=dict(
        given_iterable=set[int],
        given_context={
            int: routines.NumberUnmarshaller(int, {}),
        },
        expected_output={2, 1},
    ),
)
@pytest.mark.suite(
    bytes_literal=dict(
        given_input=b"('2', '1')",
    ),
    string_literal=dict(
        given_input="('2', '1')",
    ),
    json=dict(
        given_input='["2", "1"]',
    ),
)
def test_subscripted_iterable_unmarshaller(
    given_input, given_iterable, given_context, expected_output
):
    # Given
    given_unmarshaller = routines.SubscriptedIterableUnmarshaller(
        given_iterable, given_context
    )
    # When
    output = given_unmarshaller(given_input)
    # Then
    assert output == expected_output


@pytest.mark.suite(
    generic_iterator=dict(
        given_iterator=typing.Iterator[int],
        given_context={
            int: routines.NumberUnmarshaller(int, {}),
        },
        expected_output={2, 1},
    ),
)
@pytest.mark.suite(
    bytes_literal=dict(
        given_input=b"('2', '1')",
    ),
    string_literal=dict(
        given_input="('2', '1')",
    ),
    json=dict(
        given_input='["2", "1"]',
    ),
    generator=dict(
        given_input=(str(i) for i in range(1, 3)),
    ),
)
def test_subscripted_iterator_unmarshaller(
    given_input, given_iterator, given_context, expected_output
):
    # Given
    given_unmarshaller = routines.SubscriptedIteratorUnmarshaller(
        given_iterator, given_context
    )
    # When
    output = {*given_unmarshaller(given_input)}
    # Then
    assert output == expected_output


@pytest.mark.suite(
    bytes_literal=dict(
        given_input=b"['field', '1']",
        given_tuple=tuple[str, int],
        given_context={
            int: routines.NumberUnmarshaller(int, {}),
            str: routines.StringUnmarshaller(str, {}),
        },
        expected_output=("field", 1),
    ),
    string_literal=dict(
        given_input="['field', '1']",
        given_tuple=tuple[str, int],
        given_context={
            int: routines.NumberUnmarshaller(int, {}),
            str: routines.StringUnmarshaller(str, {}),
        },
        expected_output=("field", 1),
    ),
    bytes_json=dict(
        given_input=b'["field", "1"]',
        given_tuple=tuple[str, int],
        given_context={
            int: routines.NumberUnmarshaller(int, {}),
            str: routines.StringUnmarshaller(str, {}),
        },
        expected_output=("field", 1),
    ),
    string_json=dict(
        given_input='["field", "1"]',
        given_tuple=tuple[str, int],
        given_context={
            int: routines.NumberUnmarshaller(int, {}),
            str: routines.StringUnmarshaller(str, {}),
        },
        expected_output=("field", 1),
    ),
    dict=dict(
        given_input=[b"field", "1"],
        given_tuple=tuple[str, int],
        given_context={
            int: routines.NumberUnmarshaller(int, {}),
            str: routines.StringUnmarshaller(str, {}),
        },
        expected_output=("field", 1),
    ),
)
def test_fixed_tuple_unmarshaller(
    given_input, given_tuple, given_context, expected_output
):
    # Given
    given_unmarshaller = routines.FixedTupleUnmarshaller(given_tuple, given_context)
    # When
    output = given_unmarshaller(given_input)
    # Then
    assert output == expected_output


@pytest.mark.suite(
    context=dict(
        given_context={
            int: routines.NumberUnmarshaller(int, {}, var="value"),
            str: routines.StringUnmarshaller(str, {}, var="field"),
        },
    ),
)
@pytest.mark.suite(
    dataclass=dict(
        given_cls=models.Data,
        expected_output=models.Data(field="data", value=1),
    ),
    vanilla=dict(
        given_cls=models.Vanilla,
        expected_output=models.Vanilla(field="data", value=1),
    ),
    vanilla_with_hints=dict(
        given_cls=models.VanillaWithHints,
        expected_output=models.VanillaWithHints(field="data", value=1),
    ),
    named_tuple=dict(
        given_cls=models.NTuple,
        expected_output=models.NTuple(field="data", value=1),
    ),
    typed_dict=dict(
        given_cls=models.TDict,
        expected_output=models.TDict(field="data", value=1),
    ),
)
@pytest.mark.suite(
    bytes_literal=dict(
        given_input=b"{'field': 'data', 'value': b'1'}",
    ),
    string_literal=dict(
        given_input="{'field': 'data', 'value': b'1'}",
    ),
    json=dict(
        given_input='{"field": "data", "value": "1"}',
    ),
    dataclass=dict(
        given_input=models.Data(field="data", value=1),
    ),
    vanilla=dict(
        given_input=models.Vanilla(field="data", value=1),
    ),
    vanilla_with_hints=dict(
        given_input=models.VanillaWithHints(field="data", value=1),
    ),
    named_tuple=dict(
        given_input=models.NTuple(field="data", value=1),
    ),
    typed_dict=dict(
        given_input=models.TDict(field="data", value=1),
    ),
)
def test_structured_type_unmarshaller(
    given_input, given_cls, given_context, expected_output
):
    # Given
    given_unmarshaller = routines.StructuredTypeUnmarshaller(given_cls, given_context)
    # When
    output = given_unmarshaller(given_input)
    # Then
    assert output == expected_output


def test_invalid_literal():
    # Given
    given_unmarshaller = routines.LiteralUnmarshaller(typing.Literal[1], {})
    given_value = 2
    expected_exception = ValueError
    # When/Then
    with pytest.raises(expected_exception):
        given_unmarshaller(given_value)


def test_invalid_union():
    # Given
    given_unmarshaller = routines.UnionUnmarshaller(
        typing.Union[int, float],
        {
            int: routines.NumberUnmarshaller(int, {}),
            float: routines.NumberUnmarshaller(float, {}),
        },
    )
    given_value = "value"
    expected_exception = ValueError
    # When/Then
    with pytest.raises(expected_exception):
        given_unmarshaller(given_value)


def test_enum_unmarshaller():
    # Given
    given_unmarshaller = routines.EnumUnmarshaller(models.GivenEnum, {})
    given_value = models.GivenEnum.one.value
    expected_value = models.GivenEnum.one
    # When
    unmarshalled = given_unmarshaller(given_value)
    # Then
    assert unmarshalled == expected_value
