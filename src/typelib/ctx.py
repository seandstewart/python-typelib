"""A simple hashmap for working with types in a contextual manner."""

from __future__ import annotations

import typing as tp
import typing_extensions as te

from typelib.py import refs

ValueT = tp.TypeVar("ValueT")
KeyT = te.TypeAliasType("KeyT", "type | refs.ForwardRef")


class TypeContext(dict[KeyT, ValueT], tp.Generic[ValueT]):
    """A key-value mapping which can map between forward references and real types."""

    def __missing__(self, key: type | refs.ForwardRef):
        """Hook to handle missing type references.

        Allows for sharing lookup results between forward references and real types.

        Args:
            key: The type or reference.
        """
        # If we missed a ForwardRef, we've already tried this, bail out.
        if isinstance(key, refs.ForwardRef):
            raise KeyError(key)

        ref = refs.forwardref(key)
        return self[ref]
