from __future__ import annotations

import inspect
import types
from typing import Any, Final

__all__ = (
    "extract",
    "getcaller",
    "PKG_NAME",
)


def extract(name: str, *, frame: types.FrameType = None) -> Any | None:
    """Extract `name` from the stacktrace of `frame`.

    If `frame` is not provided, this function will use the current frame.


    """
    frame = frame or inspect.currentframe()
    seen: set[types.FrameType] = set()
    add = seen.add
    while frame and frame not in seen:
        if name in frame.f_globals:
            return frame.f_globals[name]
        if name in frame.f_locals:
            return frame.f_locals[name]
        add(frame)
        frame = frame.f_back

    return None


def getcaller(frame: types.FrameType = None) -> types.FrameType:
    """Get the caller of the current scope, excluding this library.

    If `frame` is not provided, this function will use the current frame.
    """

    frame = frame or inspect.currentframe()
    while frame.f_back:
        frame = frame.f_back
        module = inspect.getmodule(frame)
        if module and module.__name__.startswith(PKG_NAME):
            continue

        code = frame.f_code
        if getattr(code, "co_qualname", "").startswith(PKG_NAME):
            continue
        if PKG_NAME in code.co_filename:
            continue
        return frame

    return frame


PKG_NAME: Final[str] = __name__.split(".", maxsplit=1)[0]
