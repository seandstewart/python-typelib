import datetime
import decimal
import fractions
import pathlib
import re
import typing
import uuid

import pytest

import typelib
from typelib.py import compat, refs

from tests import models


@pytest.mark.suite(
    forwardref=dict(
        given_type=refs.forwardref("decimal.Decimal"),
        given_input="1.0",
        expected_unmarshal_output=decimal.Decimal("1.0"),
        expected_marshal_output="1.0",
    ),
    unresolvable=dict(
        given_type=...,
        given_input="foo",
        expected_unmarshal_output="foo",
        expected_marshal_output="foo",
    ),
    nonetype=dict(
        given_type=None,
        given_input=None,
        expected_unmarshal_output=None,
        expected_marshal_output=None,
    ),
    literal=dict(
        given_type=typing.Literal[1, 2, 3],
        given_input="2",
        expected_unmarshal_output=2,
        expected_marshal_output=2,
    ),
    union=dict(
        given_type=typing.Union[int, str],
        given_input="2",
        expected_unmarshal_output=2,
        expected_marshal_output=2,
    ),
    datetime=dict(
        given_type=datetime.datetime,
        given_input=0,
        expected_unmarshal_output=datetime.datetime.fromtimestamp(
            0, datetime.timezone.utc
        ),
        expected_marshal_output=datetime.datetime.fromtimestamp(
            0, datetime.timezone.utc
        ).isoformat(),
    ),
    date=dict(
        given_type=datetime.date,
        given_input=0,
        expected_unmarshal_output=datetime.datetime.fromtimestamp(
            0, datetime.timezone.utc
        ).date(),
        expected_marshal_output=datetime.datetime.fromtimestamp(
            0, datetime.timezone.utc
        )
        .date()
        .isoformat(),
    ),
    time=dict(
        given_type=datetime.time,
        given_input=0,
        expected_unmarshal_output=datetime.datetime.fromtimestamp(
            0, tz=datetime.timezone.utc
        )
        .time()
        .replace(tzinfo=datetime.timezone.utc),
        expected_marshal_output=datetime.datetime.fromtimestamp(
            0, tz=datetime.timezone.utc
        )
        .time()
        .replace(tzinfo=datetime.timezone.utc)
        .isoformat(),
    ),
    timedelta=dict(
        given_type=datetime.timedelta,
        given_input=0,
        expected_unmarshal_output=datetime.timedelta(seconds=0),
        expected_marshal_output="PT",
    ),
    uuid=dict(
        given_type=uuid.UUID,
        given_input=0,
        expected_unmarshal_output=uuid.UUID(int=0),
        expected_marshal_output=str(uuid.UUID(int=0)),
    ),
    pattern=dict(
        given_type=re.Pattern,
        given_input="1",
        expected_unmarshal_output=re.compile("1"),
        expected_marshal_output=re.compile("1").pattern,
    ),
    path=dict(
        given_type=pathlib.Path,
        given_input="/path/to/file",
        expected_unmarshal_output=pathlib.Path("/path/to/file"),
        expected_marshal_output=str(pathlib.Path("/path/to/file")),
    ),
    decimal=dict(
        given_type=decimal.Decimal,
        given_input="1.0",
        expected_unmarshal_output=decimal.Decimal("1.0"),
        expected_marshal_output="1.0",
    ),
    fraction=dict(
        given_type=fractions.Fraction,
        given_input="1/2",
        expected_unmarshal_output=fractions.Fraction("1/2"),
        expected_marshal_output="1/2",
    ),
    string=dict(
        given_type=str,
        given_input=1,
        expected_unmarshal_output="1",
        expected_marshal_output="1",
    ),
    bytes=dict(
        given_type=bytes,
        given_input=1,
        expected_unmarshal_output=b"1",
        expected_marshal_output=b"1",
    ),
    bytearray=dict(
        given_type=bytearray,
        given_input=1,
        expected_unmarshal_output=bytearray(b"1"),
        expected_marshal_output=bytearray(b"1"),
    ),
    memoryview=dict(
        given_type=memoryview,
        given_input="foo",
        expected_unmarshal_output=memoryview(b"foo"),
        expected_marshal_output=b"foo",
    ),
    typeddict=dict(
        given_type=models.TDict,
        given_input={"field": 1, "value": "2"},
        expected_unmarshal_output=models.TDict(field="1", value=2),
        expected_marshal_output=dict(field="1", value=2),
    ),
    direct_recursive=dict(
        given_type=models.RecursiveType,
        given_input={"cycle": {"cycle": {}}},
        expected_unmarshal_output=models.RecursiveType(
            cycle=models.RecursiveType(cycle=models.RecursiveType())
        ),
        expected_marshal_output={"cycle": {"cycle": {"cycle": None}}},
    ),
    indirect_recursive=dict(
        given_type=models.IndirectCycleType,
        given_input={"indirect": {"cycle": {"indirect": {}}}},
        expected_unmarshal_output=models.IndirectCycleType(
            indirect=models.CycleType(
                cycle=models.IndirectCycleType(indirect=models.CycleType())
            )
        ),
        expected_marshal_output={"indirect": {"cycle": {"indirect": {"cycle": None}}}},
    ),
    type_alias_type=dict(
        given_type=compat.TypeAliasType("IntList", "list[int]"),
        given_input='["1", "2"]',
        expected_unmarshal_output=[1, 2],
        expected_marshal_output=[1, 2],
    ),
)
def test_protocol(
    given_type, given_input, expected_unmarshal_output, expected_marshal_output
):
    # Given
    codec = typelib.codec(given_type)
    # When
    unmarshal_output = codec.unmarshal(given_input)
    marshal_output = codec.marshal(unmarshal_output)
    encode_output = codec.encode(unmarshal_output)
    decode_output = codec.decode(encode_output)
    # Then
    assert unmarshal_output == expected_unmarshal_output
    assert marshal_output == expected_marshal_output
    assert decode_output == expected_unmarshal_output
