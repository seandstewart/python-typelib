from __future__ import annotations

import abc
import contextlib
import datetime
import decimal
import fractions
import numbers
import pathlib
import re
import typing as tp
import uuid

from typelib import inspection, interchange

T = tp.TypeVar("T")

__all__ = (
    "AbstractUnmarshaller",
    "ContextT",
    "BytesUnmarshaller",
    "StrUnmarshaller",
    "NumberUnmarshaller",
    "DecimalUnmarshaller",
    "FractionUnmarshaller",
    "DateUnmarshaller",
    "DateTimeUnmarshaller",
    "TimeUnmarshaller",
    "TimeDeltaUnmarshaller",
    "UUIDUnmarshaller",
    "PathUnmarshaller",
    "CastUnmarshaller",
    "PatternUnmarshaller",
    "MappingUnmarshaller",
    "IterableUnmarshaller",
    "LiteralUnmarshaller",
    "UnionUnmarshaller",
    "SubscriptedIteratorUnmarshaller",
    "SubscriptedIterableUnmarshaller",
    "SubscriptedMappingUnmarshaller",
    "FixedTupleUnmarshaller",
    "StructuredTypeUnmarshaller",
)


class AbstractUnmarshaller(abc.ABC, tp.Generic[T]):
    context: ContextT
    t: type[T]

    __slots__ = ("t", "origin", "context", "var")

    def __init__(self, t: type[T], context: ContextT, *, var: str | None = None):
        self.t = t
        self.origin = inspection.origin(self.t)
        self.context = context
        self.var = var

    @abc.abstractmethod
    def __call__(self, val: tp.Any) -> T: ...


ContextT: tp.TypeAlias = tp.Mapping[type, AbstractUnmarshaller]
BytesT = tp.TypeVar("BytesT", bound=bytes)


class BytesUnmarshaller(AbstractUnmarshaller[BytesT], tp.Generic[BytesT]):
    def __call__(self, val: tp.Any) -> BytesT:
        if isinstance(val, self.t):
            return val
        # Always encode date/time as ISO strings.
        if isinstance(val, (datetime.date, datetime.time, datetime.timedelta)):
            val = interchange.isoformat(val)
        return self.t(str(val).encode("utf8"))


StrT = tp.TypeVar("StrT", bound=str)


class StrUnmarshaller(AbstractUnmarshaller[StrT]):
    def __call__(self, val: tp.Any) -> StrT:
        # Always decode bytes.
        decoded = interchange.decode(val)
        if isinstance(decoded, self.t):
            return decoded
        # Always encode date/time as ISO strings.
        if isinstance(val, (datetime.date, datetime.time, datetime.timedelta)):
            decoded = interchange.isoformat(val)
        return self.t(decoded)


NumberT = tp.TypeVar("NumberT", bound=numbers.Number)


class NumberUnmarshaller(AbstractUnmarshaller[NumberT]):
    def __call__(self, val: tp.Any) -> NumberT:
        # Always decode bytes.
        decoded = interchange.decode(val)
        if isinstance(decoded, self.t):
            return decoded
        # Represent date/time objects as time since unix epoch.
        if isinstance(val, (datetime.date, datetime.time)):
            decoded = interchange.unixtime(val)
        # Represent deltas as total seconds.
        elif isinstance(val, datetime.timedelta):
            decoded = val.total_seconds()
        # Treat containers as constructor args.
        if inspection.ismappingtype(decoded.__class__):
            return self.t(**decoded)
        if inspection.iscollectiontype(decoded.__class__):
            return self.t(*decoded)
        # Simple cast for non-containers.
        return self.t(decoded)  # type: ignore[call-arg]


DecimalT = tp.TypeVar("DecimalT", bound=decimal.Decimal)
DecimalUnmarshaller = NumberUnmarshaller[DecimalT]

FractionT = tp.TypeVar("FractionT", bound=fractions.Fraction)
FractionUnmarshaller = NumberUnmarshaller[FractionT]


class DateUnmarshaller(AbstractUnmarshaller[datetime.date]):
    def __call__(self, val: tp.Any) -> datetime.date:
        if isinstance(val, self.t) and not isinstance(val, datetime.datetime):
            return val

        # Numbers can be treated as time since epoch.
        if isinstance(val, (int, float)):
            val = datetime.datetime.fromtimestamp(val, tz=datetime.timezone.utc)
        # Always decode bytes.
        decoded = interchange.decode(val)
        # Parse strings.
        date: datetime.date | datetime.time = (
            interchange.dateparse(decoded, self.t)
            if isinstance(decoded, str)
            else decoded
        )
        # Time-only construct is treated as today.
        if isinstance(date, datetime.time):
            return self.t.today()
        # Exact class matching - the parser returns subclasses.
        if date.__class__ is self.t:
            return date
        # Reconstruct as the exact type.
        return self.t(year=date.year, month=date.month, day=date.day)


class DateTimeUnmarshaller(AbstractUnmarshaller[datetime.datetime]):
    def __call__(self, val: tp.Any) -> datetime.datetime:
        if isinstance(val, self.t):
            return val

        # Numbers can be treated as time since epoch.
        if isinstance(val, (int, float)):
            val = datetime.datetime.fromtimestamp(val, tz=datetime.timezone.utc)
        # Always decode bytes.
        decoded = interchange.decode(val)
        # Parse strings.
        dt: datetime.datetime | datetime.date | datetime.time = (
            interchange.dateparse(decoded, self.t)
            if isinstance(decoded, str)
            else decoded
        )
        # If we have a time object, default to today.
        if isinstance(dt, datetime.time):
            return self.t.now(tz=dt.tzinfo).replace(
                hour=dt.hour,
                minute=dt.minute,
                second=dt.second,
                microsecond=dt.microsecond,
                tzinfo=dt.tzinfo,
            )
        # Exact class matching.
        if dt.__class__ is self.t:
            return dt  # type: ignore[return-value]
        # Subclass check for datetimes.
        if isinstance(dt, datetime.datetime):
            return self.t(
                year=dt.year,
                month=dt.month,
                day=dt.day,
                hour=dt.hour,
                minute=dt.minute,
                second=dt.second,
                microsecond=dt.microsecond,
                tzinfo=dt.tzinfo,
                fold=dt.fold,
            )
        # Implicit: we have a date object.
        return self.t(year=dt.year, month=dt.month, day=dt.day)


class TimeUnmarshaller(AbstractUnmarshaller[datetime.time]):
    def __call__(self, val: tp.Any) -> datetime.time:
        if isinstance(val, self.t):
            return val
        if isinstance(val, (int, float)):
            return (
                datetime.datetime.fromtimestamp(val, tz=datetime.timezone.utc)
                .time()
                # datetime.time() strips tzinfo...
                .replace(tzinfo=datetime.timezone.utc)
            )
        decoded = interchange.decode(val)
        dt: datetime.datetime | datetime.date | datetime.time = (
            interchange.dateparse(decoded, self.t)
            if isinstance(decoded, str)
            else decoded
        )

        if isinstance(dt, datetime.datetime):
            dt = dt.time()
        elif isinstance(dt, datetime.date):
            dt = self.t()

        if dt.__class__ is self.t:
            return dt

        return self.t(
            hour=dt.hour,
            minute=dt.minute,
            second=dt.second,
            microsecond=dt.microsecond,
            tzinfo=dt.tzinfo,
            fold=dt.fold,
        )


class TimeDeltaUnmarshaller(AbstractUnmarshaller[datetime.timedelta]):
    def __call__(self, val: tp.Any) -> datetime.timedelta:
        if isinstance(val, (int, float)):
            return self.t(seconds=int(val))

        decoded = interchange.decode(val)
        td: datetime.timedelta = (
            interchange.dateparse(decoded, self.t)
            if isinstance(decoded, str)
            else decoded
        )

        if td.__class__ is self.t:
            return td

        return self.t(seconds=td.total_seconds())


class UUIDUnmarshaller(AbstractUnmarshaller[uuid.UUID]):
    def __call__(self, val: tp.Any) -> uuid.UUID:
        decoded = (
            interchange.strload(val) if inspection.istexttype(val.__class__) else val
        )
        if isinstance(decoded, int):
            return self.t(int=decoded)
        return self.t(decoded)


class PatternUnmarshaller(AbstractUnmarshaller[re.Pattern]):
    def __call__(self, val: tp.Any) -> re.Pattern:
        decoded = interchange.decode(val)
        return re.compile(decoded)


class CastUnmarshaller(AbstractUnmarshaller[T]):
    __slots__ = ("caster",)

    def __init__(self, t: type[T], context: ContextT):
        super().__init__(t, context)
        self.caster: tp.Callable[[tp.Any], T] = self.origin  # type: ignore[assignment]

    def __call__(self, val: tp.Any) -> T:
        # Try to load the string, if this is JSON or a literal expression.
        decoded = (
            interchange.strload(val) if inspection.istexttype(val.__class__) else val
        )
        # Short-circuit cast if we have the type we want.
        if decoded.__class__ is self.origin:
            return decoded
        # Cast the decoded value to the type.
        return self.caster(decoded)


PathUnmarshaller = CastUnmarshaller[pathlib.Path]
MappingUnmarshaller = CastUnmarshaller[tp.Mapping]
IterableUnmarshaller = CastUnmarshaller[tp.Iterable]

_LTVT = tp.TypeVarTuple("_LTVT")
_LT = tp.TypeVar("_LT")


class LiteralUnmarshaller(AbstractUnmarshaller, tp.Generic[*_LTVT]):
    __slots__ = ("values",)

    def __init__(self, t: type[T], context: ContextT):
        super().__init__(t, context)
        self.values = inspection.get_args(t)

    def __call__(self, val: tp.Any) -> tp.Literal[*_LTVT]:  # type: ignore[valid-type]
        if val in self.values:
            return val
        decoded = (
            interchange.strload(val) if inspection.istexttype(val.__class__) else val
        )
        if decoded in self.values:
            return decoded

        raise ValueError(f"{decoded!r} is not one of {self.values!r}")


class UnionUnmarshaller(AbstractUnmarshaller, tp.Generic[*_LTVT]):
    __slots__ = ("stack", "ordered_routines")

    def __init__(self, t: type[T], context: ContextT):
        super().__init__(t, context)
        self.stack = inspection.get_args(t)
        self.ordered_routines = [self.context[typ] for typ in self.stack]

    def __call__(self, val: tp.Any) -> tp.Union[*_LTVT]:  # type: ignore[valid-type]
        for routine in self.ordered_routines:
            with contextlib.suppress(ValueError, TypeError, SyntaxError):
                unmarshalled = routine(val)
                return unmarshalled

        raise ValueError(f"{val!r} is not one of types {self.stack!r}")


_KT = tp.TypeVar("_KT")
_VT = tp.TypeVar("_VT")


class SubscriptedMappingUnmarshaller(AbstractUnmarshaller[tp.Mapping[_KT, _VT]]):
    __slots__ = (
        "keys",
        "values",
    )

    def __init__(self, t: type[tp.Mapping[_KT, _VT]], context: ContextT) -> None:
        super().__init__(t=t, context=context)
        key_t, value_t = inspection.get_args(t)
        self.keys = context[key_t]
        self.values = context[value_t]

    def __call__(self, val: tp.Any) -> tp.Mapping[_KT, _VT]:
        # Always decode bytes.
        decoded = interchange.strload(val)
        keys = self.keys
        values = self.values
        return self.origin(
            ((keys(k), values(v)) for k, v in interchange.iteritems(decoded))
        )


class SubscriptedIterableUnmarshaller(AbstractUnmarshaller[tp.Iterable[_VT]]):
    __slots__ = ("values",)

    def __init__(self, t: type[tp.Iterable[_VT]], context: ContextT) -> None:
        super().__init__(t=t, context=context)
        (value_t,) = inspection.get_args(t)
        self.values = context[value_t]

    def __call__(self, val: tp.Any) -> tp.Iterable[_VT]:
        # Always decode bytes.
        decoded = interchange.strload(val)
        values = self.values
        return self.origin((values(v) for v in interchange.itervalues(decoded)))


class SubscriptedIteratorUnmarshaller(AbstractUnmarshaller[tp.Iterator[_VT]]):
    __slots__ = ("values",)

    def __init__(self, t: type[tp.Iterator[_VT]], context: ContextT) -> None:
        super().__init__(t=t, context=context)
        (value_t,) = inspection.get_args(t)
        self.values = context[value_t]

    def __call__(self, val: tp.Any) -> tp.Iterator[_VT]:
        # Always decode bytes.
        decoded = interchange.strload(val)
        values = self.values
        return (values(v) for v in interchange.itervalues(decoded))


_TVT = tp.TypeVarTuple("_TVT")


class FixedTupleUnmarshaller(AbstractUnmarshaller[tuple[*_TVT]]):
    __slots__ = ("ordered_routines", "stack")

    def __init__(self, t: type[tuple[*_TVT]], context: ContextT) -> None:
        super().__init__(t, context)
        self.stack = inspection.get_args(t)
        self.ordered_routines = [self.context[vt] for vt in self.stack]

    def __call__(self, val: tp.Any) -> tuple[*_TVT]:
        decoded = interchange.strload(val)
        return self.origin(
            routine(v)
            for routine, v in zip(
                self.ordered_routines, interchange.itervalues(decoded)
            )
        )


_ST = tp.TypeVar("_ST")


class StructuredTypeUnmarshaller(AbstractUnmarshaller[_ST]):
    __slots__ = ("fields_by_var",)

    def __init__(self, t: type[_ST], context: ContextT) -> None:
        super().__init__(t, context)
        self.fields_by_var = {m.var: m for m in self.context.values()}

    def __call__(self, val: tp.Any) -> _ST:
        decoded = (
            interchange.strload(val) if inspection.istexttype(val.__class__) else val
        )
        fields = self.fields_by_var
        kwargs = {
            f: fields[f](v) for f, v in interchange.iteritems(decoded) if f in fields
        }
        return self.t(**kwargs)
