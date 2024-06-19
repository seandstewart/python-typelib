from __future__ import annotations

import abc
import contextlib
import datetime
import decimal
import fractions
import pathlib
import re
import typing as tp
import uuid

from typelib import inspection, interchange

T = tp.TypeVar("T")

__all__ = (
    "AbstractMarshaller",
    "ContextT",
    "BytesMarshaller",
    "StringMarshaller",
    "IntegerMarshaller",
    "FloatMarshaller",
    "DecimalMarshaller",
    "FractionMarshaller",
    "DateMarshaller",
    "DateTimeMarshaller",
    "TimeMarshaller",
    "TimeDeltaMarshaller",
    "UUIDMarshaller",
    "PathMarshaller",
    "PatternMarshaller",
    "MappingMarshaller",
    "IterableMarshaller",
    "LiteralMarshaller",
    "UnionMarshaller",
    "SubscriptedIterableMarshaller",
    "SubscriptedMappingMarshaller",
    "FixedTupleMarshaller",
    "StructuredTypeMarshaller",
)


class AbstractMarshaller(abc.ABC, tp.Generic[T]):
    context: ContextT
    t: type[T]

    __slots__ = ("t", "origin", "context", "var")

    def __repr__(self):
        return f"<{self.__class__.__name__}(type={self.t!r}, origin={self.origin!r}, var={self.var!r})>"

    def __init__(self, t: type[T], context: ContextT, *, var: str | None = None):
        self.t = t
        self.origin = inspection.origin(self.t)
        self.context = context
        self.var = var

    @abc.abstractmethod
    def __call__(self, val: T) -> interchange.MarshalledValueT: ...


ContextT: tp.TypeAlias = tp.Mapping[type, AbstractMarshaller]


class NoOpMarshaller(AbstractMarshaller[T], tp.Generic[T]):
    def __call__(self, val: T) -> interchange.MarshalledValueT:
        return val  # type: ignore[return-value]


BytesMarshaller = NoOpMarshaller[bytes]


class CastMarshaller(AbstractMarshaller[T], tp.Generic[T]):
    def __call__(self, val: T) -> interchange.MarshalledValueT:
        return self.origin(val)


IntegerMarshaller = CastMarshaller[int]
FloatMarshaller = CastMarshaller[float]


class ToStringMarshaller(AbstractMarshaller[T], tp.Generic[T]):
    def __call__(self, val: T) -> str:
        return str(val)


StringMarshaller = ToStringMarshaller[str]

DecimalT = tp.TypeVar("DecimalT", bound=decimal.Decimal)
DecimalMarshaller = ToStringMarshaller[DecimalT]

FractionT = tp.TypeVar("FractionT", bound=fractions.Fraction)
FractionMarshaller = ToStringMarshaller[FractionT]

UUIDT = tp.TypeVar("UUIDT", bound=uuid.UUID)
UUIDMarshaller = ToStringMarshaller[UUIDT]

PathT = tp.TypeVar("PathT", bound=pathlib.Path)
PathMarshaller = ToStringMarshaller[PathT]


PatternT = tp.TypeVar("PatternT", bound=re.Pattern)


class PatternMarshaller(AbstractMarshaller[PatternT]):
    def __call__(self, val: PatternT) -> str:
        return val.pattern


DateOrTimeT = tp.TypeVar(
    "DateOrTimeT", datetime.date, datetime.time, datetime.timedelta
)


class ToISOTimeMarshaller(AbstractMarshaller[DateOrTimeT], tp.Generic[DateOrTimeT]):
    def __call__(self, val: DateOrTimeT) -> str:
        return interchange.isoformat(val)


DateT = tp.TypeVar("DateT", bound=datetime.date)
DateMarshaller = ToISOTimeMarshaller[DateT]

DateTimeT = tp.TypeVar("DateTimeT", bound=datetime.datetime)
DateTimeMarshaller = ToISOTimeMarshaller[DateTimeT]

TimeT = tp.TypeVar("TimeT", bound=datetime.time)
TimeMarshaller = ToISOTimeMarshaller[TimeT]

TimeDeltaT = tp.TypeVar("TimeDeltaT", bound=datetime.timedelta)
TimeDeltaMarshaller = ToISOTimeMarshaller[TimeDeltaT]


LiteralT = tp.TypeVar("LiteralT")


class LiteralMarshaller(AbstractMarshaller[LiteralT], tp.Generic[LiteralT]):
    __slots__ = ("values",)

    def __init__(self, t: type[LiteralT], context: ContextT, *, var: str | None = None):
        super().__init__(t, context, var=var)
        self.values = inspection.get_args(t)

    def __call__(self, val: LiteralT) -> interchange.MarshalledValueT:
        if val in self.values:
            return val  # type: ignore[return-value]

        raise ValueError(f"{val!r} is not one of {self.values!r}")


UnionT = tp.TypeVar("UnionT")


class UnionMarshaller(AbstractMarshaller[UnionT], tp.Generic[UnionT]):
    __slots__ = ("stack", "ordered_routines")

    def __init__(self, t: type[UnionT], context: ContextT, *, var: str | None = None):
        super().__init__(t, context, var=var)
        self.stack = inspection.get_args(t)
        self.ordered_routines = [self.context[typ] for typ in self.stack]

    def __call__(self, val: UnionT) -> interchange.MarshalledValueT:
        for routine in self.ordered_routines:
            with contextlib.suppress(ValueError, TypeError, SyntaxError):
                unmarshalled = routine(val)
                return unmarshalled

        raise ValueError(f"{val!r} is not one of types {self.stack!r}")


MappingT = tp.TypeVar("MappingT", bound=tp.Mapping)


class MappingMarshaller(AbstractMarshaller[MappingT], tp.Generic[MappingT]):
    def __call__(self, val: MappingT) -> MarshalledMappingT:
        return {**val}


IterableT = tp.TypeVar("IterableT", bound=tp.Iterable)


class IterableMarshaller(AbstractMarshaller[IterableT], tp.Generic[IterableT]):
    def __call__(self, val: IterableT) -> MarshalledIterableT:
        return [*val]


class SubscriptedMappingMarshaller(AbstractMarshaller[MappingT], tp.Generic[MappingT]):
    __slots__ = (
        "keys",
        "values",
    )

    def __init__(self, t: type[MappingT], context: ContextT, *, var: str | None = None):
        super().__init__(t, context, var=var)
        key_t, value_t = inspection.get_args(t)
        self.keys = context[key_t]
        self.values = context[value_t]

    def __call__(self, val: MappingT) -> MarshalledMappingT:
        keys = self.keys
        values = self.values
        return {keys(k): values(v) for k, v in interchange.iteritems(val)}  # type: ignore[misc]


class SubscriptedIterableMarshaller(
    AbstractMarshaller[IterableT], tp.Generic[IterableT]
):
    __slots__ = ("values",)

    def __init__(
        self, t: type[IterableT], context: ContextT, *, var: str | None = None
    ):
        super().__init__(t=t, context=context, var=var)
        # supporting tuple[str, ...]
        (value_t, *_) = inspection.get_args(t)
        self.values = context[value_t]

    def __call__(self, val: IterableT) -> MarshalledIterableT:
        # Always decode bytes.
        values = self.values
        return [values(v) for v in interchange.itervalues(val)]


_TVT = tp.TypeVarTuple("_TVT")
_TupleT: tp.TypeAlias = "tuple[*_TVT]"


class FixedTupleMarshaller(AbstractMarshaller[_TupleT]):
    __slots__ = ("ordered_routines", "stack")

    def __init__(self, t: type[_TupleT], context: ContextT, *, var: str | None = None):
        super().__init__(t, context, var=var)
        self.stack = inspection.get_args(t)
        self.ordered_routines = [self.context[vt] for vt in self.stack]

    def __call__(self, val: _TupleT) -> MarshalledIterableT:
        return [
            routine(v)
            for routine, v in zip(self.ordered_routines, interchange.itervalues(val))
        ]


_ST = tp.TypeVar("_ST")


class StructuredTypeMarshaller(AbstractMarshaller[_ST]):
    __slots__ = ("fields_by_var",)

    def __init__(self, t: type[_ST], context: ContextT, *, var: str | None = None):
        super().__init__(t, context, var=var)
        self.fields_by_var = {m.var: m for m in self.context.values() if m.var}

    def __call__(self, val: _ST) -> MarshalledMappingT:
        fields = self.fields_by_var
        return {f: fields[f](v) for f, v in interchange.iteritems(val) if f in fields}


MarshalledMappingT: tp.TypeAlias = dict[
    interchange.PythonPrimitiveT, interchange.MarshalledValueT
]
MarshalledIterableT: tp.TypeAlias = list[interchange.MarshalledValueT]
