"""Utilities for working with types as graphs.

Examples: Typical Usage
    >>> import dataclasses
    >>> from typelib import graph
    >>> graph.static_order(dict[str, str])
    [TypeNode(type=<class 'str'>, var=None, cyclic=False), TypeNode(type=dict[str, str], var=None, cyclic=False)]
    >>>
    >>> @dataclasses.dataclass
    ... class Class:
    ...     attr: str
    ...
    >>> graph.static_order(Class)
    [TypeNode(type=<class 'str'>, var='attr', cyclic=False), TypeNode(type=<class '__main__.Class'>, var=None, cyclic=False)]

"""

from __future__ import annotations

import collections
import dataclasses
import graphlib
import inspect
import typing

from typelib import constants
from typelib.py import classes, compat, inspection, refs

__all__ = ("static_order", "itertypes", "get_type_graph")


@compat.cache
def static_order(
    t: type | str | refs.ForwardRef | compat.TypeAliasType,
) -> typing.Sequence[TypeNode]:
    """Get an ordered iterable of types which resolve into the root type provided.

    Args:
        t: The type to extract an ordered stack from.

    Note:
        The order of types is guaranteed to rank from edges to root. If there are
        multiple edges, the order of those edges is not guaranteed.

        This function is memoized to avoid the cost of re-computing a type annotation
        multiple times at runtime, which would be wasted effort, as types don't change
        at runtime.

        To avoid memoization, you can make use of [`itertypes`][typelib.graph.itertypes].
    """
    # We want to leverage the cache if possible, hence the recursive call.
    #   Shouldn't actually recurse more than once or twice.
    if inspection.istypealiastype(t):
        return static_order(t.__value__)
    if isinstance(t, (str, refs.ForwardRef)):
        ref = refs.forwardref(t) if isinstance(t, str) else t
        t = refs.evaluate(ref)
        return static_order(t)

    return [*itertypes(t)]


def itertypes(
    t: type | str | refs.ForwardRef | compat.TypeAliasType,
) -> typing.Iterable[TypeNode]:
    """Iterate over the type-graph represented by `t` from edges to root.

    Args:
        t: The "root" type.

    Yields:
        [`TypeNode`][typelib.graph.TypeNode]

    Note:
        We will build a graph of types with the given type `t` as the root node,
        then iterate from the outermost leaves back to the root using BFS.

        This is computationally expensive, so you are encouraged to use
        [`static_order`][typelib.graph.static_order] instead of
        [`itertypes`][typelib.graph.itertypes].
    """
    if inspection.istypealiastype(t):
        t = t.__value__
    if isinstance(t, (str, refs.ForwardRef)):  # pragma: no cover
        ref = refs.forwardref(t) if isinstance(t, str) else t
        t = refs.evaluate(ref)

    graph = get_type_graph(t)  # type: ignore[arg-type]
    yield from graph.static_order()


def get_type_graph(t: type) -> graphlib.TopologicalSorter[TypeNode]:
    """Get a directed graph of the type(s) this annotation represents,

    Args:
        t: A type annotation.

    Returns:
        [`graphlib.TopologicalSorter`][]

    Note:
        A key aspect of building a directed graph of a given type is pre-emptive
        detection and termination of cycles in the graph. If we detect a cycle, we
        will wrap the type in a [`typing.ForwardRef`][] and mark the
        [`TypeNode`][typelib.graph.TypeNode] instance as `cyclic=True`.

        Consumers of the graph can "delay" the resolution of a forward reference until
        the graph's `static_order()` has been exhausted, at which point they have
        enough type information to resolve into the real type. (At least one layer down).

        Resolution of cyclic/recursive types is always (necessarily) lazy and should only
        resolve one level deep on each attempt, otherwise we will find ourselves stuck
        in a closed loop which never terminates (infinite recursion).
    """
    graph: graphlib.TopologicalSorter = graphlib.TopologicalSorter()
    root = TypeNode(t)
    stack = collections.deque([root])
    visited = {root.type}
    while stack:
        parent = stack.popleft()
        if inspection.isliteral(parent.type):
            graph.add(parent)
            continue

        predecessors = []
        for var, child in _level(parent.type):
            # If no type was provided, there's no reason to do further processing.
            if child in (constants.empty, typing.Any):
                continue

            # Only subscripted generics or non-stdlib types can be cyclic.
            #   i.e., we may get `str` or `datetime` any number of times,
            #   that's not cyclic, so we can just add it to the graph.
            is_visited = child in visited
            is_subscripted = inspection.issubscriptedgeneric(child)
            is_stdlib = inspection.isstdlibtype(child)
            can_be_cyclic = is_subscripted or is_stdlib is False
            # We detected a cyclic type,
            #   wrap in a ForwardRef and don't add it to the stack
            #   This will terminate this edge to prevent infinite cycles.
            if is_visited and can_be_cyclic:
                qualname = inspection.qualname(child)
                *rest, refname = qualname.split(".", maxsplit=1)
                is_argument = var is not None
                module = ".".join(rest) or getattr(child, "__module__", None)
                if module in (None, "__main__") and rest:
                    module = rest[0]
                is_class = inspect.isclass(child)
                ref = refs.forwardref(
                    refname, is_argument=is_argument, module=module, is_class=is_class
                )
                node = TypeNode(ref, var=var, cyclic=True)
            # Otherwise, add the type to the stack and track that it's been seen.
            else:
                node = TypeNode(type=child, var=var)
                visited.add(node.type)
                stack.append(node)
            # Flag the type as a "predecessor" of the parent type.
            #   This lets us resolve child types first when we iterate over the graph.
            predecessors.append(node)
        # Add the parent type and its predecessors to the graph.
        graph.add(parent, *predecessors)

    return graph


@classes.slotted(dict=False, weakref=True)
@dataclasses.dataclass(unsafe_hash=True)
class TypeNode:
    """A "node" in a type graph."""

    type: typing.Any
    """The type annotation for this node."""
    var: str | None = None
    """The variable or parameter name associated to the type annotation for this node."""
    cyclic: bool = dataclasses.field(default=False, hash=False, compare=False)
    """Whether this type annotation is cyclic."""


def _level(t: typing.Any) -> typing.Iterable[tuple[str | None, type]]:
    args = inspection.args(t)
    # Only pull annotations from the signature if this is a user-defined type.
    is_structured = inspection.isstructuredtype(t)
    members = inspection.get_type_hints(t, exhaustive=is_structured)
    yield from ((None, t) for t in args)
    yield from members.items()
