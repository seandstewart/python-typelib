from __future__ import annotations

import abc
import datetime
import decimal
import fractions
import numbers
import typing as tp

from typelib import inspection, interchange

T = tp.TypeVar("T")


class AbstractUnmarshaller(abc.ABC, tp.Generic[T]):
    context: tp.Mapping[type, AbstractUnmarshaller]
    t: type[T]

    __slots__ = ("t", "context")

    def __init__(self, t: type[T], context: tp.Mapping[type, AbstractUnmarshaller]):
        self.t = t
        self.context = context

    @abc.abstractmethod
    def __call__(self, val: tp.Any) -> T: ...


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
