"""Utilities for translating between various types."""

from __future__ import annotations

import ast
import contextlib
import dataclasses
import datetime
import functools
import operator
import typing as t

import pendulum
from more_itertools import peekable

from typelib import compat, inspection


@t.overload
def decode(val: bytes | bytearray | memoryview, *, encoding: str = "utf8") -> str: ...  # type: ignore[overload-overlap]


@t.overload
def decode(val: _T) -> _T: ...  # type: ignore[overload-overlap]


def decode(val: t.Any, *, encoding: str = "utf8") -> t.Any:
    """Decode a bytes-like object into a str.

    Notes:
        If a non-bytes-like object is passed, it will be returned unchanged.

    Args:
        val: The object to be decoded.
        encoding: The encoding to use when decoding the object (defaults "utf8").
    """
    val = val.tobytes() if isinstance(val, memoryview) else val
    if isinstance(val, (bytes, bytearray)):
        decoded = val.decode(encoding)
        return decoded
    return val


@compat.lru_cache(maxsize=100_000)
def isoformat(t: datetime.date | datetime.time | datetime.timedelta) -> str:
    """Format any date/time object into an ISO-8601 string.

    Notes:
        While the standard library includes `isoformat()` methods for
        :py:class:`datetime.date`, :py:class:`datetime.time`, &
        :py:class:`datetime.datetime`, they do not include a method for serializing
        :py:class:`datetime.timedelta`, even though durations are included in the
        ISO 8601 specification. This function fills that gap.

    Examples:
        >>> import datetime
        >>> from typelib import interchange
        >>> interchange.isoformat(datetime.date(1970, 1, 1))
        '1970-01-01'
        >>> interchange.isoformat(datetime.time())
        '00:00:00'
        >>> interchange.isoformat(datetime.datetime(1970, 1, 1))
        '1970-01-01T00:00:00'
        >>> interchange.isoformat(datetime.timedelta(hours=1))
        'PT1H'
    """
    if isinstance(t, (datetime.date, datetime.time)):
        return t.isoformat()
    d: pendulum.Duration = (
        t
        if isinstance(t, pendulum.Duration)
        else pendulum.duration(
            days=t.days,
            seconds=t.seconds,
            microseconds=t.microseconds,
        )
    )
    datepart = "".join(
        f"{p}{s}"
        for p, s in ((d.years, "Y"), (d.months, "M"), (d.remaining_days, "D"))
        if p
    )
    timepart = "".join(
        f"{p}{s}"
        for p, s in (
            (d.hours, "H"),
            (d.minutes, "M"),
            (
                f"{d.remaining_seconds}.{d.microseconds:06}"
                if d.microseconds
                else d.remaining_seconds,
                "S",
            ),
        )
        if p
    )
    period = f"P{datepart}T{timepart}"
    return period


_T = t.TypeVar("_T")


def unixtime(t: datetime.date | datetime.time | datetime.timedelta) -> float:
    """Convert a date/time object to a unix timestamp.

    Notes:
        Time is messy. Here is how we've decided to make this work:

        - `datetime.datetime` instances will preserve the current tzinfo (even if naive).
        - `datetime.time` instances will default to today, preserving the tzinfo (even if naive).
        - `datetime.date` instances will assume UTC.
        - `datetime.timedelta` instances be reflected as total seconds since epoch (January 1, 1970).

        If you find yourself in a situation where this does not work for you, your best
        bet is to stop using tz-naive date/time objects. *It's always best to keep your time
        explicit!*

    Args:
        t: The object to be converted.

    Examples:
        >>> import datetime
        >>> from typelib import interchange
        >>>
        >>> interchange.unixtime(datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc))
        0.0
        >>> interchange.unixtime(datetime.date(1970, 1, 1))
        0.0
    """
    if isinstance(t, datetime.timedelta):
        return t.total_seconds()

    if isinstance(t, datetime.time):
        t = datetime.datetime.now(tz=t.tzinfo).replace(
            hour=t.hour,
            minute=t.minute,
            second=t.second,
            microsecond=t.microsecond,
        )
    if isinstance(t, datetime.date) and not isinstance(t, datetime.datetime):
        t = datetime.datetime(
            year=t.year,
            month=t.month,
            day=t.day,
            tzinfo=datetime.timezone.utc,
        )

    return t.timestamp()


DateTimeT = t.TypeVar("DateTimeT", datetime.date, datetime.time, datetime.timedelta)


@compat.lru_cache(maxsize=100_000)
def dateparse(val: str, td: type[DateTimeT]) -> DateTimeT:
    """Parse a date string into a datetime object.

    Args:
        val: The date string to parse.
        td: The target datetime type.

    Returns:
        The parsed datetime object.

    Raises:
        ValueError: If `val` is not a date string or does not resolve to an instance of
                    the target datetime type.
    """
    try:
        # When `exact=False`, the only two possibilities are DateTime and Duration.
        parsed: pendulum.DateTime | pendulum.Duration = pendulum.parse(val)  # type: ignore[assignment]
        normalized = _nomalize_dt(val=val, parsed=parsed, td=td)
        return normalized
    except ValueError:
        if val.isdigit() or val.isdecimal():
            return _normalize_number(numval=float(val), td=td)
        raise


def _nomalize_dt(
    *, val: str, parsed: pendulum.DateTime | pendulum.Duration, td: type[DateTimeT]
) -> DateTimeT:
    if isinstance(parsed, pendulum.DateTime):
        if issubclass(td, datetime.time):
            return parsed.time().replace(tzinfo=parsed.tzinfo)
        if issubclass(td, datetime.datetime):
            return parsed
        if issubclass(td, datetime.date):
            return parsed.date()
    if not isinstance(parsed, td):
        raise ValueError(f"Cannot parse {val!r} as {td.__qualname__!r}")
    return parsed


def _normalize_number(*, numval: float, td: type[DateTimeT]) -> DateTimeT:
    # Assume the number value is seconds - same logic as time-since-epoch
    if issubclass(td, datetime.timedelta):
        return datetime.timedelta(seconds=numval)
    # Parse a datetime from the time-since-epoch as indicated by the value.
    dt = datetime.datetime.fromtimestamp(numval, tz=datetime.timezone.utc)
    # Return the datetime if the target type is a datetime
    if issubclass(td, datetime.datetime):
        return dt
    # If the target type is a time object, just return the time.
    if issubclass(td, datetime.time):
        return dt.time().replace(tzinfo=dt.tzinfo)
    # If the target type is a date object, just return the date.
    return dt.date()


def iteritems(val: t.Any) -> t.Iterable[tuple[t.Any, t.Any]]:
    """Iterate over (field, value) pairs for any object.

    Notes:
        If the given item is detected to be an iterable of pairs (e.g., `[('a', 1), ('b', 2)]`),
        we will iterate directly over that.

        Otherwise, we will create an iterator over (field, value) pairs with the following
        strategy:
            - For mappings -> `((key, value), ...)`
            - For structured objects (user-defined classes) -> `((field, value), ...)`
            - For all other iterables -> `((index, value), ...)`.

    Args:
        val: The object to iterate over.
    """
    if _is_iterable_of_pairs(val):
        return iter(val)

    iterate = get_items_iter(val.__class__)
    return iterate(val)


def _is_iterable_of_pairs(val: t.Any) -> bool:
    if not inspection.isiterabletype(val.__class__) or inspection.ismappingtype(
        val.__class__
    ):
        return False
    peek = peekable(val).peek()
    return inspection.iscollectiontype(peek.__class__) and len(peek) == 2


def itervalues(val: t.Any) -> t.Iterator[t.Any]:
    iterate = get_items_iter(val.__class__)
    return (v for k, v in iterate(val))


@functools.cache
def get_items_iter(tp: type) -> t.Callable[[t.Any], t.Iterable[tuple[t.Any, t.Any]]]:
    """Given a type, return a callable which will produce an iterator over (field, value) pairs."""
    ismapping, isnamedtuple, isiterable = (
        inspection.ismappingtype(tp),
        inspection.isnamedtuple(tp),
        inspection.isiterabletype(tp),
    )
    if ismapping:
        return _itemscaller
    if isnamedtuple:
        return _namedtupleitems
    if isiterable:
        return enumerate
    return _make_fields_iterator(tp)


def _namedtupleitems(val: t.NamedTuple) -> t.Iterable[tuple[str, t.Any]]:
    return zip(val._fields, val)


def _make_fields_iterator(
    tp: type,
) -> t.Callable[[t.Any], t.Iterator[tuple[t.Any, t.Any]]]:
    # If we have a dataclass, use the defined public fields.
    if dataclasses.is_dataclass(tp):
        public_attribs = [
            f.name for f in dataclasses.fields(tp) if not f.name.startswith("_")
        ]
    # Otherwise, try using the public type-hints.
    else:
        attribs = inspection.get_type_hints(tp)
        public_attribs = [k for k in attribs if not k.startswith("_")]
    # If that didn't work, look for `__slots__`.
    if not public_attribs and hasattr(tp, "__slots__"):
        public_attribs = [s for s in tp.__slots__ if not s.startswith("_")]
    # If we located all public attributes, create a factory function for iterating over
    #   these fields and fetching the value from an instance.
    if public_attribs:

        def _iterfields(val: t.Any) -> t.Iterator[tuple[str, t.Any]]:
            return ((a, getattr(val, a)) for a in public_attribs)

        return _iterfields

    # Finally, if all else fails, just use `vars` on the instance.
    def _itervars(val: t.Any) -> t.Iterator[tuple[str, t.Any]]:
        return ((k, v) for k, v in vars(val).items() if not k.startswith("_"))

    return _itervars


def load(val: _T) -> PythonValueT | _T:
    """Attempt to decode :py:param:`val` if it is a text-like object.

    Args:
        val: The value to decode.
    """
    return strload(val) if inspection.istexttype(val.__class__) else val  # type: ignore[arg-type]


@compat.lru_cache(maxsize=100_000)
def strload(val: str | bytes | bytearray | memoryview) -> PythonValueT:
    """Attempt to decode a string-like input into a Python value.

    Args:
        val: The string-like input to be decoded.
    """
    with contextlib.suppress(ValueError):
        return compat.json.loads(val)

    decoded = decode(val)
    with contextlib.suppress(ValueError, TypeError, SyntaxError):
        return ast.literal_eval(decoded)

    return decoded


PythonPrimitiveT: t.TypeAlias = "bool | int | float | str | None"
PythonValueT: t.TypeAlias = (
    "PythonPrimitiveT | "
    "dict[PythonPrimitiveT, PythonValueT] | "
    "list[PythonValueT] | "
    "tuple[PythonValueT, ...] | "
    "set[PythonValueT]"
)
MarshalledValueT: t.TypeAlias = "PythonPrimitiveT | dict[PythonPrimitiveT, MarshalledValueT] | list[MarshalledValueT]"


_itemscaller = operator.methodcaller("items")
_valuescaller = operator.methodcaller("values")
