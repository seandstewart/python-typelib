"""The API for unmarshalling simple Python objects into higher-order Python types."""

from __future__ import annotations

import typing as tp

from typelib import ctx, graph
from typelib.py import compat, inspection, refs
from typelib.unmarshal import routines

T = tp.TypeVar("T")

__all__ = (
    "unmarshal",
    "unmarshaller",
    "DelayedUnmarshaller",
)


def unmarshal(typ: type[T] | refs.ForwardRef | str, value: tp.Any) -> T:
    """Unmarshal `value` into `typ`.

    Args:
        typ: The type annotation or reference to unmarshal into.
        value: The value to unmarshal.
    """
    routine = unmarshaller(typ)
    unmarshalled = routine(value)
    return unmarshalled


@compat.cache
def unmarshaller(
    typ: type[T] | refs.ForwardRef | compat.TypeAliasType | str,
) -> routines.AbstractUnmarshaller[T]:
    """Get an un-marshaller routine for a given type.

    Args:
        typ: The type annotation to generate an unmarshaller for.
             May be a type, type alias, [`typing.ForwardRef`][], or string reference.
    """
    nodes = graph.static_order(typ)
    context: dict[type | graph.TypeNode, routines.AbstractUnmarshaller] = (
        ctx.TypeContext()
    )
    if not nodes:
        return routines.NoOpUnmarshaller(t=typ, context=context, var=None)  # type: ignore[arg-type]

    # "root" type will always be the final node in the sequence.
    root = nodes[-1]
    for node in nodes:
        context[node] = _get_unmarshaller(node, context=context)

    return context[root]


def _get_unmarshaller(  # type: ignore[return]
    node: graph.TypeNode,
    context: routines.ContextT,
) -> routines.AbstractUnmarshaller[T]:
    if node in context:
        return context[node]

    for check, unmarshaller_cls in _HANDLERS.items():
        if check(node.type):
            return unmarshaller_cls(node.type, context=context, var=node.var)

    return routines.StructuredTypeUnmarshaller(node.type, context=context, var=node.var)


class DelayedUnmarshaller(routines.AbstractUnmarshaller[T]):
    def __init__(
        self, t: type[T], context: routines.ContextT, *, var: str | None = None
    ):
        super().__init__(t, context, var=var)
        self._resolved: routines.AbstractUnmarshaller[T] | None = None

    @property
    def resolved(self) -> routines.AbstractUnmarshaller[T]:
        if self._resolved is None:
            self._resolved = unmarshaller(self.t)
            for attr in self._resolved.__slots__:
                setattr(self, attr, getattr(self._resolved, attr))
        return self._resolved

    def __call__(self, val: tp.Any) -> T:
        unmarshalled = self.resolved(val)
        return unmarshalled


# Order is IMPORTANT! This is a FIFO queue.
_HANDLERS: tp.Mapping[
    tp.Callable[[type[T]], bool], type[routines.AbstractUnmarshaller]
] = {
    # Short-circuit forward refs
    inspection.isforwardref: DelayedUnmarshaller,
    inspection.isunresolvable: routines.NoOpUnmarshaller,
    inspection.isnonetype: routines.NoneTypeUnmarshaller,
    # Special handler for Literals
    inspection.isliteral: routines.LiteralUnmarshaller,
    # Special handler for Unions...
    inspection.isuniontype: routines.UnionUnmarshaller,
    # Non-intersecting types (order doesn't matter here.
    inspection.isdatetimetype: routines.DateTimeUnmarshaller,
    inspection.isdatetype: routines.DateUnmarshaller,
    inspection.istimetype: routines.TimeUnmarshaller,
    inspection.istimedeltatype: routines.TimeDeltaUnmarshaller,
    inspection.isuuidtype: routines.UUIDUnmarshaller,
    inspection.ispatterntype: routines.PatternUnmarshaller,
    inspection.ispathtype: routines.PathUnmarshaller,
    inspection.isdecimaltype: routines.DecimalUnmarshaller,
    inspection.isfractiontype: routines.FractionUnmarshaller,
    inspection.isnumbertype: routines.NumberUnmarshaller,
    inspection.isstringtype: routines.StringUnmarshaller,
    inspection.isbytestype: routines.BytesUnmarshaller,
    # Psuedo-structured containers, should check before generics.
    inspection.istypeddict: routines.StructuredTypeUnmarshaller,
    inspection.istypedtuple: routines.StructuredTypeUnmarshaller,
    inspection.isnamedtuple: routines.StructuredTypeUnmarshaller,
    inspection.isfixedtupletype: routines.FixedTupleUnmarshaller,
    (
        lambda t: inspection.issubscriptedgeneric(t) and inspection.ismappingtype(t)
    ): routines.SubscriptedMappingUnmarshaller,
    (
        lambda t: inspection.issubscriptedgeneric(t) and inspection.isiteratortype(t)
    ): routines.SubscriptedIteratorUnmarshaller,
    (
        lambda t: inspection.issubscriptedgeneric(t) and inspection.isiterabletype(t)
    ): routines.SubscriptedIterableUnmarshaller,
    # A mapping is a collection so must come before that check.
    inspection.ismappingtype: routines.MappingUnmarshaller,
    # Generic iterator handler
    inspection.isiteratortype: routines.NoOpUnmarshaller,
    # Generic Iterable handler
    inspection.isiterabletype: routines.IterableUnmarshaller,
}
