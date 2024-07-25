# flake8: noqa
from __future__ import annotations

from typing import TYPE_CHECKING

import sys

__all__ = (
    "Final",
    "ParamSpec",
    "Self",
    "TypeAliasType",
    "TypeGuard",
    "TypeIs",
    "TypeVarTuple",
    "DATACLASS_KW_ONLY",
    "DATACLASS_MATCH_ARGS",
    "DATACLASS_NATIVE_SLOTS",
    "KW_ONLY",
    "lru_cache",
    "cache",
)

if TYPE_CHECKING:
    from typing import TypeVar, overload, Callable

    DATACLASS_KW_ONLY: Final[bool] = True
    DATACLASS_NATIVE_SLOTS: Final[bool] = True
    DATACLASS_MATCH_ARGS: Final[bool] = True
    KW_ONLY: Final[object] = object()

    from typing_extensions import (
        TypeIs,
        ParamSpec,
        Self,
        Final,
        TypeAlias,
        TypeAliasType,
        TypeVarTuple,
        TypeGuard,
    )

    import orjson as json

    F = TypeVar("F")

    @overload
    def lru_cache(*, maxsize: int | None = None) -> Callable[[F], F]: ...

    @overload
    def lru_cache(func: F, *, maxsize: int | None = None) -> F: ...

    def lru_cache(
        func: F | None = None, *, maxsize: int | None = None
    ) -> F | Callable[[F], F]: ...

    def cache(func: F) -> F: ...

    if sys.version_info >= (3, 11):
        TupleVarsT = TypeVarTuple("TupleVarsT")
        TupleT: TypeAlias = "tuple[*TupleVarsT]"  # type: ignore[valid-type]

    else:
        TupleVarsT = TypeVarTuple("TupleVarsT")
        TupleT: TypeAlias = tuple[TupleVarsT]

else:
    from functools import lru_cache, cache

    if sys.version_info >= (3, 13):
        from typing import TypeIs

    else:
        from typing_extensions import TypeIs

    if sys.version_info >= (3, 12):
        from typing import TypeAliasType

    else:
        from typing_extensions import TypeAliasType

    if sys.version_info >= (3, 11):
        from typing import ParamSpec, Self, Final, TypeVarTuple

        TupleVarsT = TypeVarTuple("TupleVarsT")
        TupleT: TypeAlias = "tuple[*TupleVarsT]"

    else:
        from typing_extensions import ParamSpec, Self, Final, TypeVarTuple

        TupleVarsT = TypeVarTuple("TupleVarsT")
        TupleT: TypeAlias = tuple[TupleVarsT]

    if sys.version_info >= (3, 10):
        from typing import TypeGuard

        from dataclasses import KW_ONLY

        DATACLASS_KW_ONLY = DATACLASS_MATCH_ARGS = DATACLASS_NATIVE_SLOTS = True

    else:
        from typing_extensions import TypeGuard

        DATACLASS_KW_ONLY = DATACLASS_MATCH_ARGS = DATACLASS_NATIVE_SLOTS = False
        KW_ONLY = object()

    try:
        import orjson as json
    except (ImportError, ModuleNotFoundError):
        import json
