from __future__ import annotations

import dataclasses

from typelib.py import classes


def test_slotted():
    # Given
    @dataclasses.dataclass
    class GivenClass:
        field: str

    expected_slots = (*(f.name for f in dataclasses.fields(GivenClass)),)

    # When
    Slotted = classes.slotted(GivenClass, weakref=False)
    # Then
    assert Slotted.__slots__ == expected_slots


def test_slotted_dict():
    # Given
    @dataclasses.dataclass
    class GivenClass:
        field: str

    expected_slots = (*(f.name for f in dataclasses.fields(GivenClass)), "__dict__")

    # When
    Slotted = classes.slotted(GivenClass, dict=True, weakref=False)
    # Then
    assert Slotted.__slots__ == expected_slots


def test_slotted_weakref():
    # Given
    @dataclasses.dataclass
    class GivenClass:
        field: str

    expected_slots = (*(f.name for f in dataclasses.fields(GivenClass)), "__weakref__")

    # When
    Slotted = classes.slotted(GivenClass, dict=False, weakref=True)
    # Then
    assert Slotted.__slots__ == expected_slots


def test_slotted_weakref_dict():
    # Given
    @dataclasses.dataclass
    class GivenClass:
        field: str

    expected_slots = (
        *(f.name for f in dataclasses.fields(GivenClass)),
        "__dict__",
        "__weakref__",
    )

    # When
    Slotted = classes.slotted(GivenClass, dict=True, weakref=True)
    # Then
    assert Slotted.__slots__ == expected_slots


def test_slotted_setstate():
    # Given
    @dataclasses.dataclass(frozen=True)
    class GivenClass:
        field: str

    expected_slots = (*(f.name for f in dataclasses.fields(GivenClass)),)
    # When
    Slotted = classes.slotted(GivenClass, weakref=False)
    # Then
    assert Slotted.__slots__ == expected_slots
    assert hasattr(Slotted, "__setstate__")
