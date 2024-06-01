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
    "StringUnmarshaller",
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

    def __repr__(self):
        return f"<{self.__class__.__name__}(type={self.t!r}, origin={self.origin!r}, var={self.var!r})>"

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


StringT = tp.TypeVar("StringT", bound=str)


class StringUnmarshaller(AbstractUnmarshaller[StringT], tp.Generic[StringT]):
    def __call__(self, val: tp.Any) -> StringT:
        # Always decode bytes.
        decoded = interchange.decode(val)
        if isinstance(decoded, self.t):
            return decoded
        # Always encode date/time as ISO strings.
        if isinstance(val, (datetime.date, datetime.time, datetime.timedelta)):
            decoded = interchange.isoformat(val)
        return self.t(decoded)


NumberT = tp.TypeVar("NumberT", bound=numbers.Number)


class NumberUnmarshaller(AbstractUnmarshaller[NumberT], tp.Generic[NumberT]):
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


DateT = tp.TypeVar("DateT", bound=datetime.date)


class DateUnmarshaller(AbstractUnmarshaller[DateT], tp.Generic[DateT]):
    def __call__(self, val: tp.Any) -> DateT:
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
            return date  # type: ignore[return-value]
        # Reconstruct as the exact type.
        return self.t(year=date.year, month=date.month, day=date.day)


DateTimeT = tp.TypeVar("DateTimeT", bound=datetime.datetime)


class DateTimeUnmarshaller(
    AbstractUnmarshaller[datetime.datetime], tp.Generic[DateTimeT]
):
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


TimeT = tp.TypeVar("TimeT", bound=datetime.time)


class TimeUnmarshaller(AbstractUnmarshaller[TimeT], tp.Generic[TimeT]):
    def __call__(self, val: tp.Any) -> TimeT:
        if isinstance(val, self.t):
            return val

        decoded = interchange.decode(val)
        if isinstance(decoded, (int, float)):
            decoded = (
                datetime.datetime.fromtimestamp(val, tz=datetime.timezone.utc)
                .time()
                # datetime.time() strips tzinfo...
                .replace(tzinfo=datetime.timezone.utc)
            )
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
            return dt  # type: ignore[return-value]

        return self.t(
            hour=dt.hour,
            minute=dt.minute,
            second=dt.second,
            microsecond=dt.microsecond,
            tzinfo=dt.tzinfo,
            fold=dt.fold,
        )


TimeDeltaT = tp.TypeVar("TimeDeltaT", bound=datetime.timedelta)


class TimeDeltaUnmarshaller(AbstractUnmarshaller[TimeDeltaT], tp.Generic[TimeDeltaT]):
    def __call__(self, val: tp.Any) -> TimeDeltaT:
        if isinstance(val, (int, float)):
            return self.t(seconds=int(val))

        decoded = interchange.decode(val)
        td: datetime.timedelta = (
            interchange.dateparse(decoded, self.t)
            if isinstance(decoded, str)
            else decoded
        )

        if td.__class__ is self.t:
            return td  # type: ignore[return-value]

        return self.t(seconds=td.total_seconds())


UUIDT = tp.TypeVar("UUIDT", bound=uuid.UUID)


class UUIDUnmarshaller(AbstractUnmarshaller[UUIDT], tp.Generic[UUIDT]):
    def __call__(self, val: tp.Any) -> UUIDT:
        decoded = interchange.load(val)
        if isinstance(decoded, int):
            return self.t(int=decoded)
        if isinstance(decoded, self.t):
            return decoded
        return self.t(decoded)  # type: ignore[arg-type]


PatternT = tp.TypeVar("PatternT", bound=re.Pattern)


class PatternUnmarshaller(AbstractUnmarshaller[PatternT], tp.Generic[PatternT]):
    def __call__(self, val: tp.Any) -> PatternT:
        decoded = interchange.decode(val)
        return re.compile(decoded)  # type: ignore[return-value]


class CastUnmarshaller(AbstractUnmarshaller[T]):
    __slots__ = ("caster",)

    def __init__(self, t: type[T], context: ContextT, *, var: str | None = None):
        super().__init__(t, context, var=var)
        self.caster: tp.Callable[[tp.Any], T] = self.origin  # type: ignore[assignment]

    def __call__(self, val: tp.Any) -> T:
        # Try to load the string, if this is JSON or a literal expression.
        decoded = interchange.load(val)
        # Short-circuit cast if we have the type we want.
        if isinstance(decoded, self.t):
            return decoded
        # Cast the decoded value to the type.
        return self.caster(decoded)


PathUnmarshaller = CastUnmarshaller[pathlib.Path]
MappingUnmarshaller = CastUnmarshaller[tp.Mapping]
IterableUnmarshaller = CastUnmarshaller[tp.Iterable]


LiteralT = tp.TypeVar("LiteralT")


class LiteralUnmarshaller(AbstractUnmarshaller[LiteralT], tp.Generic[LiteralT]):
    __slots__ = ("values",)

    def __init__(self, t: type[LiteralT], context: ContextT, *, var: str | None = None):
        super().__init__(t, context, var=var)
        self.values = inspection.get_args(t)

    def __call__(self, val: tp.Any) -> LiteralT:
        if val in self.values:
            return val
        decoded = interchange.load(val)
        if decoded in self.values:
            return decoded  # type: ignore[return-value]

        raise ValueError(f"{decoded!r} is not one of {self.values!r}")


UnionT = tp.TypeVar("UnionT")


class UnionUnmarshaller(AbstractUnmarshaller[UnionT], tp.Generic[UnionT]):
    __slots__ = ("stack", "ordered_routines")

    def __init__(self, t: type[UnionT], context: ContextT, *, var: str | None = None):
        super().__init__(t, context, var=var)
        self.stack = inspection.get_args(t)
        self.ordered_routines = [self.context[typ] for typ in self.stack]

    def __call__(self, val: tp.Any) -> UnionT:
        for routine in self.ordered_routines:
            with contextlib.suppress(ValueError, TypeError, SyntaxError):
                unmarshalled = routine(val)
                return unmarshalled

        raise ValueError(f"{val!r} is not one of types {self.stack!r}")


_KT = tp.TypeVar("_KT")
_VT = tp.TypeVar("_VT")


MappingT = tp.TypeVar("MappingT", bound=tp.Mapping)


class SubscriptedMappingUnmarshaller(
    AbstractUnmarshaller[MappingT], tp.Generic[MappingT]
):
    __slots__ = (
        "keys",
        "values",
    )

    def __init__(self, t: type[MappingT], context: ContextT, *, var: str | None = None):
        super().__init__(t, context, var=var)
        key_t, value_t = inspection.get_args(t)
        self.keys = context[key_t]
        self.values = context[value_t]

    def __call__(self, val: tp.Any) -> MappingT:
        # Always decode bytes.
        decoded = interchange.load(val)
        keys = self.keys
        values = self.values
        return self.origin(
            ((keys(k), values(v)) for k, v in interchange.iteritems(decoded))
        )


IterableT = tp.TypeVar("IterableT", bound=tp.Iterable)


class SubscriptedIterableUnmarshaller(
    AbstractUnmarshaller[IterableT], tp.Generic[IterableT]
):
    __slots__ = ("values",)

    def __init__(
        self, t: type[IterableT], context: ContextT, *, var: str | None = None
    ):
        super().__init__(t=t, context=context, var=var)
        # supporting tuple[str, ...]
        (value_t, *_) = inspection.get_args(t)
        self.values = context[value_t]

    def __call__(self, val: tp.Any) -> IterableT:
        # Always decode bytes.
        decoded = interchange.load(val)
        values = self.values
        return self.origin((values(v) for v in interchange.itervalues(decoded)))


IteratorT = tp.TypeVar("IteratorT", bound=tp.Iterator)


class SubscriptedIteratorUnmarshaller(
    AbstractUnmarshaller[IteratorT], tp.Generic[IteratorT]
):
    __slots__ = ("values",)

    def __init__(
        self, t: type[IteratorT], context: ContextT, *, var: str | None = None
    ):
        super().__init__(t, context, var=var)
        (value_t,) = inspection.get_args(t)
        self.values = context[value_t]

    def __call__(self, val: tp.Any) -> IteratorT:
        # Always decode bytes.
        decoded = interchange.load(val)
        values = self.values
        it: IteratorT = (values(v) for v in interchange.itervalues(decoded))  # type: ignore[assignment]
        return it


_TVT = tp.TypeVarTuple("_TVT")


class FixedTupleUnmarshaller(AbstractUnmarshaller[tuple[*_TVT]]):
    __slots__ = ("ordered_routines", "stack")

    def __init__(
        self, t: type[tuple[*_TVT]], context: ContextT, *, var: str | None = None
    ):
        super().__init__(t, context, var=var)
        self.stack = inspection.get_args(t)
        self.ordered_routines = [self.context[vt] for vt in self.stack]

    def __call__(self, val: tp.Any) -> tuple[*_TVT]:
        decoded = interchange.load(val)
        return self.origin(
            routine(v)
            for routine, v in zip(
                self.ordered_routines, interchange.itervalues(decoded)
            )
        )


_ST = tp.TypeVar("_ST")


class StructuredTypeUnmarshaller(AbstractUnmarshaller[_ST]):
    __slots__ = ("fields_by_var",)

    def __init__(self, t: type[_ST], context: ContextT, *, var: str | None = None):
        super().__init__(t, context, var=var)
        self.fields_by_var = {m.var: m for m in self.context.values() if m.var}

    def __call__(self, val: tp.Any) -> _ST:
        decoded = interchange.load(val)
        fields = self.fields_by_var
        kwargs = {
            f: fields[f](v) for f, v in interchange.iteritems(decoded) if f in fields
        }
        return self.t(**kwargs)
