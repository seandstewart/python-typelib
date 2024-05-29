from __future__ import annotations

import collections.abc as cabc
import inspect
import re
import typing as t

from typelib import compat, constants, graph
from typelib.unmarshal import routines

T = t.TypeVar("T")


@compat.cache
def unmarshaller(typ: type[T]) -> routines.AbstractUnmarshaller[T]:
    nodes = graph.static_order(typ)
    context: dict[type, routines.AbstractUnmarshaller] = {}
    for node in nodes:
        context[node.type] = _get_unmarshaller(node.type, context=context)

    return context[typ]


def _get_unmarshaller(  # type: ignore[return]
    typ: type[T], context: dict[type, routines.AbstractUnmarshaller[T]]
) -> routines.AbstractUnmarshaller[T]:
    if typ in context:
        return context[typ]

    for check, unmarshaller_cls in _HANDLERS.items():
        if check(typ):
            return unmarshaller_cls(typ, context=context)

    # TODO: fields unmarshaller


_T = t.TypeVar("_T")


_UNRESOLVABLE = frozenset(
    (
        t.Any,
        re.Match,
        type(None),
        constants.empty,
        t.Callable,
        cabc.Callable,
        inspect.Parameter.empty,
    )
)


# Order is IMPORTANT! This is a FIFO queue.
_HANDLERS: t.Mapping[
    t.Callable[[type[T]], bool], type[routines.AbstractUnmarshaller]
] = {
    # # Short-circuit forward refs
    # inspection.isforwardref: ...,
    # # Special handler for Literals
    # inspection.isliteral: ...,
    # # Special handler for Unions...
    # inspection.isuniontype: ...,
    # # Non-intersecting types (order doesn't matter here.
    # inspection.isdatetimetype: ...,
    # inspection.isdatetype: ...,
    # inspection.istimetype: ...,
    # inspection.istimedeltatype: ...,
    # inspection.isuuidtype: ...,
    # inspection.ispatterntype: ...,
    # inspection.ispathtype: ...,
    # inspection.isdecimaltype: ...,
    # inspection.istexttype: ...,
    # # MUST come before subtype check.
    # inspection.isbuiltintype: ...,
    # # Psuedo-structured containers, should check before generics.
    # inspection.istypeddict: ...,
    # inspection.istypedtuple: ...,
    # inspection.isnamedtuple: ...,
    # inspection.isfixedtupletype: ...,
    # # A mapping is a collection so must come before that check.
    # inspection.ismappingtype: ...,
    # # A tuple is a collection so must come before that check.
    # inspection.istupletype: ...,
    # # Generic collection handler
    # inspection.iscollectiontype: ...,
}
