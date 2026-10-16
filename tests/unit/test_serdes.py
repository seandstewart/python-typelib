from __future__ import annotations

import dataclasses
import types

import pytest

from typelib import serdes


@dataclasses.dataclass
class DataClass:
    a: int
    b: str


class VariadicClass:
    def __init__(self, a, b=2, *args, **kwargs):
        self.a = a
        self.b = b


class PositionalOnlyClass:
    def __init__(self, a, /):
        self.a = a


@pytest.mark.suite(
    namespace=dict(
        given_value=types.SimpleNamespace(a=1, b="x"),
        expected_items=[("a", 1), ("b", "x")],
    ),
    empty_namespace=dict(
        given_value=types.SimpleNamespace(),
        expected_items=[],
    ),
    dataclass=dict(
        given_value=DataClass(a=1, b="x"),
        expected_items=[("a", 1), ("b", "x")],
    ),
    variadic_class=dict(
        given_value=VariadicClass(1),
        expected_items=[("a", 1), ("b", 2)],
    ),
    positional_only_class=dict(
        given_value=PositionalOnlyClass(1),
        expected_items=[("a", 1)],
    ),
    mapping=dict(
        given_value={"a": 1, "b": "x"},
        expected_items=[("a", 1), ("b", "x")],
    ),
    list_of_pairs=dict(
        given_value=[("a", 1), ("b", "x")],
        expected_items=[("a", 1), ("b", "x")],
    ),
)
def test_iteritems(given_value, expected_items):
    # When
    actual_items = [*serdes.iteritems(given_value)]
    # Then
    assert actual_items == expected_items
