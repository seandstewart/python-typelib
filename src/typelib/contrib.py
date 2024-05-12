from __future__ import annotations

import typing

__all__ = (
    "SQLAMetaData",
    "sqla_registry",
)


if typing.TYPE_CHECKING:

    class SQLAMetaData: ...

    class sqla_registry: ...


else:
    try:
        from sqlalchemy import MetaData as SQLAMetaData
    except (ImportError, ModuleNotFoundError):

        class SQLAMetaData: ...

    try:
        from sqlalchemy.orm import registry as sqla_registry
    except (ImportError, ModuleNotFoundError):

        class sqla_registry: ...
