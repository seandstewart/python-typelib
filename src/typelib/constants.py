import inspect


class empty:
    """A singleton for signalling no input."""


DEFAULT_ENCODING = "utf-8"
POSITIONAL_ONLY = inspect.Parameter.POSITIONAL_ONLY
POSITIONAL_OR_KEYWORD = inspect.Parameter.POSITIONAL_OR_KEYWORD
KEYWORD_ONLY = inspect.Parameter.KEYWORD_ONLY
SELF_NAME = "self"
TOO_MANY_POS = "too many positional arguments"
VAR_POSITIONAL = inspect.Parameter.VAR_POSITIONAL
VAR_KEYWORD = inspect.Parameter.VAR_KEYWORD
KWD_KINDS = (VAR_KEYWORD, KEYWORD_ONLY)
POS_KINDS = (VAR_POSITIONAL, POSITIONAL_ONLY)
NULLABLES = (None, Ellipsis, type(None), type(Ellipsis))
PKG_NAME = __name__.split(".", maxsplit=1)[0]
