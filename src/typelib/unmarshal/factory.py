from __future__ import annotations

import typing as tp

from typelib import compat, graph, inspection, refs
from typelib.unmarshal import routines

T = tp.TypeVar("T")


@compat.cache
def unmarshaller(
    typ: type[T] | refs.ForwardRef | str,
) -> routines.AbstractUnmarshaller[T]:
    nodes = graph.static_order(typ)
    context: dict[type, routines.AbstractUnmarshaller] = {}
    if not nodes:
        return NoOpUnmarshaller(t=typ, context=context, var=None)  # type: ignore[arg-type]

    # "root" type will always be the final node in the sequence.
    root = nodes[-1].type
    for node in nodes:
        context[node.type] = _get_unmarshaller(node, context=context)

    return context[root]


def _get_unmarshaller(  # type: ignore[return]
    node: graph.TypeNode, context: dict[type, routines.AbstractUnmarshaller[T]]
) -> routines.AbstractUnmarshaller[T]:
    if node.type in context:
        return context[node.type]

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
            self._resolved.__class__.__init__(
                self,  # type: ignore[arg-type]
                self._resolved.t,  # type: ignore[arg-type]
                self._resolved.context,  # type: ignore[arg-type]
                var=self.var,
            )
        return self._resolved

    def __call__(self, val: tp.Any) -> T:
        return self.resolved(val)


class NoOpUnmarshaller(routines.AbstractUnmarshaller[T]):
    def __call__(self, val: tp.Any) -> T:
        return tp.cast(T, val)


# Order is IMPORTANT! This is a FIFO queue.
_HANDLERS: tp.Mapping[
    tp.Callable[[type[T]], bool], type[routines.AbstractUnmarshaller]
] = {
    # Short-circuit forward refs
    inspection.isforwardref: DelayedUnmarshaller,
    inspection.isunresolvable: NoOpUnmarshaller,
    # Special handler for Literals
    # inspection.isliteral: ...,
    # Special handler for Unions...
    # inspection.isuniontype: ...,
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
    inspection.isstringtype: routines.StrUnmarshaller,
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
    inspection.isiteratortype: NoOpUnmarshaller[tp.Iterator],
    # Generic Iterable handler
    inspection.isiterabletype: routines.IterableUnmarshaller,
}
