from __future__ import annotations

import typing as tp

from typelib import compat, ctx, graph, inspection, interchange, refs
from typelib.marshal import routines

T = tp.TypeVar("T")

__all__ = (
    "marshal",
    "marshaller",
    "DelayedMarshaller",
)


def marshal(
    value: tp.Any, *, t: type[T] | refs.ForwardRef | str | None = None
) -> interchange.MarshalledValueT:
    """Marshal :py:param:`value` into :py:param:`typ`."""
    typ = value.__class__ if t is None else t
    routine: routines.AbstractMarshaller[T] = marshaller(typ)
    unmarshalled = routine(value)
    return unmarshalled


@compat.cache
def marshaller(
    typ: type[T] | refs.ForwardRef | compat.TypeAliasType | str,
) -> routines.AbstractMarshaller[T]:
    """Get an un-marshaller routine for a given type.

    Args:
        typ: The type annotation to generate an unmarshaller for.
             May be a type, a :py:class:`typing.ForwardRef`, or string reference.
    """
    nodes = graph.static_order(typ)
    context: dict[type, routines.AbstractMarshaller] = ctx.TypeContext()
    if not nodes:
        return routines.NoOpMarshaller(t=typ, context=context, var=None)  # type: ignore[arg-type]

    # "root" type will always be the final node in the sequence.
    root = nodes[-1].type
    for node in nodes:
        context[node.type] = _get_unmarshaller(node, context=context)

    return context[root]


def _get_unmarshaller(  # type: ignore[return]
    node: graph.TypeNode, context: dict[type, routines.AbstractMarshaller[T]]
) -> routines.AbstractMarshaller[T]:
    if node.type in context:
        return context[node.type]

    for check, unmarshaller_cls in _HANDLERS.items():
        if check(node.type):
            return unmarshaller_cls(node.type, context=context, var=node.var)

    return routines.StructuredTypeMarshaller(node.type, context=context, var=node.var)


class DelayedMarshaller(routines.AbstractMarshaller[T]):
    def __init__(
        self, t: type[T], context: routines.ContextT, *, var: str | None = None
    ):
        super().__init__(t, context, var=var)
        self._resolved: routines.AbstractMarshaller[T] | None = None

    @property
    def resolved(self) -> routines.AbstractMarshaller[T]:
        if self._resolved is None:
            self._resolved = marshaller(self.t)
            for attr in self._resolved.__slots__:
                setattr(self, attr, getattr(self._resolved, attr))
        return self._resolved

    def __call__(self, val: T) -> interchange.MarshalledValueT:
        unmarshalled = self.resolved(val)
        return unmarshalled


# Order is IMPORTANT! This is a FIFO queue.
_HANDLERS: tp.Mapping[
    tp.Callable[[type[T]], bool], type[routines.AbstractMarshaller]
] = {
    # Short-circuit forward refs
    inspection.isforwardref: DelayedMarshaller,
    inspection.isunresolvable: routines.NoOpMarshaller,
    inspection.isnonetype: routines.NoOpMarshaller,
    # Special handler for Literals
    inspection.isliteral: routines.LiteralMarshaller,
    # Special handler for Unions...
    inspection.isuniontype: routines.UnionMarshaller,
    # Non-intersecting types (order doesn't matter here.
    inspection.isdatetimetype: routines.DateTimeMarshaller,
    inspection.isdatetype: routines.DateMarshaller,
    inspection.istimetype: routines.TimeMarshaller,
    inspection.istimedeltatype: routines.TimeDeltaMarshaller,
    inspection.isuuidtype: routines.UUIDMarshaller,
    inspection.ispatterntype: routines.PatternMarshaller,
    inspection.ispathtype: routines.PathMarshaller,
    inspection.isdecimaltype: routines.DecimalMarshaller,
    inspection.isfractiontype: routines.FractionMarshaller,
    inspection.isintegertype: routines.IntegerMarshaller,
    inspection.isfloattype: routines.FloatMarshaller,
    inspection.isstringtype: routines.StringMarshaller,
    inspection.isbytestype: routines.BytesMarshaller,
    # Psuedo-structured containers, should check before generics.
    inspection.istypeddict: routines.StructuredTypeMarshaller,
    inspection.istypedtuple: routines.StructuredTypeMarshaller,
    inspection.isnamedtuple: routines.StructuredTypeMarshaller,
    inspection.isfixedtupletype: routines.FixedTupleMarshaller,
    (
        lambda t: inspection.issubscriptedgeneric(t) and inspection.ismappingtype(t)
    ): routines.SubscriptedMappingMarshaller,
    (
        lambda t: inspection.issubscriptedgeneric(t) and inspection.isiterabletype(t)
    ): routines.SubscriptedIterableMarshaller,
    # A mapping is a collection so must come before that check.
    inspection.ismappingtype: routines.MappingMarshaller,
    # Generic Iterable handler
    inspection.isiterabletype: routines.IterableMarshaller,
}
