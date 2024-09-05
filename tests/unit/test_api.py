from __future__ import annotations

import pytest

import typelib

from tests import models


@pytest.mark.suite(
    dataclass=dict(
        given_input=models.Data(field="field", value=0),
        expected_output=b'{"field":"field","value":0}',
    )
)
def test_encode(given_input, expected_output):
    # When
    output = typelib.encode(given_input)
    # Then
    assert output == expected_output


@pytest.mark.suite(
    dataclass=dict(
        given_input=b'{"field":"field","value":0}',
        given_type=models.Data,
        expected_output=models.Data(field="field", value=0),
    )
)
def test_decode(given_input, given_type, expected_output):
    # When
    output = typelib.decode(given_type, given_input)
    # Then
    assert output == expected_output


@pytest.mark.suite(
    dataclass=dict(
        given_input=models.Data(field="field", value=0),
        expected_output={"field": "field", "value": 0},
    )
)
def test_marshal(given_input, expected_output):
    # When
    output = typelib.marshal(given_input)
    # Then
    assert output == expected_output


@pytest.mark.suite(
    dataclass=dict(
        given_input={"field": "field", "value": 0},
        given_type=models.Data,
        expected_output=models.Data(field="field", value=0),
    )
)
def test_unmarshal(given_input, given_type, expected_output):
    # When
    output = typelib.unmarshal(given_type, given_input)
    # Then
    assert output == expected_output


@pytest.mark.suite(
    dataclass=dict(
        given_input=b'{"field":"field","value":0}',
        given_type=models.Data,
        expected_output=models.Data(field="field", value=0),
    )
)
def test_codec(given_input, given_type, expected_output):
    # When
    protocol = typelib.codec(given_type)
    decoded = protocol.decode(given_input)
    encoded = protocol.encode(decoded)
    # Then
    assert decoded == expected_output
    assert encoded == given_input
