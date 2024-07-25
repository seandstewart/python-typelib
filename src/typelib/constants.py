"""Constants used throughout the library."""

import typing as t


class empty:
    """A singleton for signalling no input."""


DEFAULT_ENCODING: t.Final[str] = "utf-8"
PKG_NAME: t.Final[str] = __name__.split(".", maxsplit=1)[0]
