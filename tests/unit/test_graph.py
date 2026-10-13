from __future__ import annotations

import dataclasses
import typing
from unittest import mock

import pytest

from typelib import graph
from typelib.py import refs

from tests import models


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
    nested_type_alias=dict(
        given_type=models.NestedTypeAliasType,
        expected_nodes=[
            graph.TypeNode(type=int),
            graph.TypeNode(type=models.ListAlias, unwrapped=list[int], var="alias"),
            graph.TypeNode(type=models.NestedTypeAliasType),
        ],
    ),
    nested_generic=dict(
        given_type=models.NestedGeneric[int],
        expected_nodes=[
            graph.TypeNode(type=int),
            graph.TypeNode(
                type=mock.ANY,  # The bound typevar, which is hard to replicate
                unwrapped=int,
                var="field",
            ),
            graph.TypeNode(
                type=models.SimpleGeneric[mock.ANY],
                var="gen",
            ),
            graph.TypeNode(type=models.NestedGeneric[int]),
        ],
    ),
    legacy_nested_generic=dict(
        given_type=models.LegacyNestedGeneric[int],
        expected_nodes=[
            graph.TypeNode(type=int),
            graph.TypeNode(
                type=mock.ANY,  # The bound typevar, which is hard to replicate
                unwrapped=int,
                var="field",
            ),
            graph.TypeNode(
                type=models.LegacySimpleGeneric[mock.ANY],
                var="gen",
            ),
            graph.TypeNode(type=models.LegacyNestedGeneric[int]),
        ],
    ),
    recursive_generic_alias=dict(
        given_type=models.Tree[int],
        expected_nodes=[
            graph.TypeNode(type=str),
            graph.TypeNode(
                type=models.Tree[int], unwrapped=models.Tree[int], cyclic=True
            ),
            graph.TypeNode(type=int),
            graph.TypeNode(type=models.Tree[int] | int),
            graph.TypeNode(
                type=models.Tree[int], unwrapped=dict[str, models.Tree[int] | int]
            ),
        ],
    ),
    recursive_generic_class=dict(
        given_type=models.Node[int],
        expected_nodes=[
            graph.TypeNode(type=int),
            graph.TypeNode(type=int, var="value"),
            graph.TypeNode(
                type=models.Node[int], unwrapped=models.Node[int], cyclic=True
            ),
            graph.TypeNode(type=list[models.Node[int]], var="children"),
            graph.TypeNode(type=models.Node[int]),
        ],
    ),
)
def test_static_order(given_type, expected_nodes):
    # When
    nodes = graph.static_order(given_type)
    # Then
    assert nodes == expected_nodes
