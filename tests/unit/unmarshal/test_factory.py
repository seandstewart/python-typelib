from __future__ import annotations

import dataclasses

import pytest
from typelib.unmarshal import factory


@dataclasses.dataclass
class RecursiveType:
    cycle: RecursiveType | None = None


@dataclasses.dataclass
class IndirectCycleType:
    indirect: CycleType


@dataclasses.dataclass
class CycleType:
    cycle: IndirectCycleType | None = None


@pytest.mark.suite(
    recursive=dict(
        given_type=RecursiveType,
        given_input={"cycle": {"cycle": {}}},
        expected_output=RecursiveType(cycle=RecursiveType(cycle=RecursiveType())),
    ),
    indirect=dict(
        given_type=IndirectCycleType,
        given_input={"indirect": {"cycle": {"indirect": {}}}},
        expected_output=IndirectCycleType(
            indirect=CycleType(cycle=IndirectCycleType(indirect=CycleType()))
        ),
    ),
)
def test_cyclic_unmarshal(given_type, given_input, expected_output):
    # When
    output = factory.unmarshal(given_type, given_input)
    # Then
    assert output == expected_output
