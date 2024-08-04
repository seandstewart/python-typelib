"""A simple hashmap for working with types in a contextual manner."""

from __future__ import annotations

import dataclasses

from typelib import graph
from typelib.py import inspection, refs


class TypeContext(dict):
    """A key-value mapping which can map between forward references and real types."""

    def __missing__(self, key: graph.TypeNode | type | refs.ForwardRef):
        """Hook to handle missing type references.

        Allows for sharing lookup results between forward references and real types.

        Args:
            key: The type or reference.
        """
        # Eager wrap in a TypeNode
        if not isinstance(key, graph.TypeNode):
            key = graph.TypeNode(type=key)
            return self[key]

        # If we missed a ForwardRef, we've already tried this, bail out.
        type = key.type
        if isinstance(type, refs.ForwardRef):
            raise KeyError(key)

        ref = refs.forwardref(
            inspection.qualname(type), module=getattr(type, "__module__", None)
        )
        node = dataclasses.replace(key, type=ref)
        return self[node]
