from __future__ import annotations

import datetime
import time
import typing as t

import pendulum

from typelib import compat


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
        >>> interchange.isoformat(datetime.timedelta())
        'P0Y0M0DT0H0M0.000000S'
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
    period = (
        f"P{d.years}Y{d.months}M{d.remaining_days}D"
        f"T{d.hours}H{d.minutes}M{d.remaining_seconds}.{d.microseconds:06}S"
    )
    return period


_T = t.TypeVar("_T")


def unixtime(t: datetime.date | datetime.time) -> float:
    """Convert a date/time object to a unix timestamp.

    Args:
        t: The object to be converted.
    """
    if isinstance(t, datetime.time):
        t = datetime.datetime.now(tz=t.tzinfo).replace(
            hour=t.hour,
            minute=t.minute,
            second=t.second,
            microsecond=t.microsecond,
        )

    return time.mktime(t.timetuple())


DateTimeT = t.TypeVar("DateTimeT", datetime.date, datetime.time, datetime.timedelta)


@compat.lru_cache(maxsize=100_000)
def dateparse(val: str, t: type[DateTimeT]) -> DateTimeT:
    """Parse a date string into a datetime object.

    Args:
        val: The date string to parse.
        t: The target datetime type.

    Returns:
        The parsed datetime object.
    """
    try:
        parsed: pendulum.DateTime | pendulum.Duration = pendulum.parse(val)  # type: ignore[assignment]
        if isinstance(parsed, pendulum.DateTime):
            if issubclass(t, datetime.time):
                return parsed.time().replace(tzinfo=parsed.tzinfo)
            if issubclass(t, datetime.datetime):
                return parsed
            if issubclass(t, datetime.date):
                return parsed.date()
        if not isinstance(parsed, t):
            raise ValueError(f"Cannot parse {val!r} as {t.__qualname__!r}")
        return parsed
    except ValueError:
        if val.isdigit() or val.isdecimal():
            numval = float(val)
            # Assume the number value is seconds - same logic as time-since-epoch
            if issubclass(t, datetime.timedelta):
                return datetime.timedelta(seconds=numval)
            # Parse a datetime from the time-since-epoch as indicated by the value.
            dt = datetime.datetime.fromtimestamp(numval, tz=datetime.timezone.utc)
            # Return the datetime if the target type is a datetime
            if issubclass(t, datetime.datetime):
                return dt
            # If the target type is a time object, just return the time.
            if issubclass(t, datetime.time):
                return dt.time().replace(tzinfo=dt.tzinfo)
            # If the target type is a date object, just return the date.
            return dt.date()

        raise
