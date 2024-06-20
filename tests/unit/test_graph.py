from __future__ import annotations

import dataclasses
import sys
import typing

import pytest
from typelib import graph, refs


@dataclasses.dataclass
class Simple:
    field: int


@dataclasses.dataclass
class Complex:
    field: Simple


@dataclasses.dataclass
class Cyclic:
    field: Cyclic | None


@dataclasses.dataclass
class NoTypes:
    field: typing.Any


@pytest.mark.suite(
    stdlib=dict(given_type=str, expected_nodes=[graph.TypeNode(type=str)]),
    collection=dict(
        given_type="dict[str, int]",
        expected_nodes=[
            graph.TypeNode(type=str),
            graph.TypeNode(type=int),
            graph.TypeNode(type=refs.evaluate(refs.forwardref("dict[str, int]"))),
        ],
    ),
    nested_collection=dict(
        given_type="dict[str, dict[str, list[int]]]",
        expected_nodes=[
            graph.TypeNode(type=str),
            graph.TypeNode(type=int),
            graph.TypeNode(type=refs.evaluate(refs.forwardref("list[int]"))),
            graph.TypeNode(type=refs.evaluate(refs.forwardref("dict[str, list[int]]"))),
            graph.TypeNode(
                type=refs.evaluate(refs.forwardref("dict[str, dict[str, list[int]]]"))
            ),
        ],
    ),
    simple_class=dict(
        given_type=Simple,
        expected_nodes=[
            graph.TypeNode(type=int, var="field"),
            graph.TypeNode(type=Simple),
        ],
    ),
    complex_class=dict(
        given_type=Complex,
        expected_nodes=[
            graph.TypeNode(type=int, var="field"),
            graph.TypeNode(type=Simple, var="field"),
            graph.TypeNode(type=Complex),
        ],
    ),
    cyclic_class=dict(
        given_type=Cyclic,
        expected_nodes=[
            graph.TypeNode(
                type=refs.forwardref(
                    "Cyclic", is_argument=True, module=Cyclic.__module__
                ),
                cyclic=True,
            ),
            graph.TypeNode(type=type(None)),
            graph.TypeNode(
                type=refs.evaluate(
                    refs.forwardref("Cyclic | None", module=Cyclic.__module__),
                ),
                var="field",
            ),
            graph.TypeNode(type=Cyclic),
        ],
    ),
    any_type=dict(given_type=NoTypes, expected_nodes=[graph.TypeNode(type=NoTypes)]),
)
@pytest.mark.skipif(sys.version_info < (3, 10), reason="py3.10+")
def test_static_order(given_type, expected_nodes):
    # When
    nodes = graph.static_order(given_type)
    # Then
    assert nodes == expected_nodes
