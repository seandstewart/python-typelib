"""A simple hashmap type for working with types in a contextual manner."""

from __future__ import annotations

import dataclasses

from typelib import graph, inspection, refs


class TypeContext(dict):
    """A key-value mapping which can map between forward references and real types."""

    def __missing__(self, key: graph.TypeNode | type | refs.ForwardRef):
        if not isinstance(key, graph.TypeNode):
            key = graph.TypeNode(type=key)
            return self[key]

        type = key.type
        if isinstance(type, refs.ForwardRef):
            raise KeyError(key)
        ref = (
            key.type
            if isinstance(type, refs.ForwardRef)
            else refs.forwardref(
                inspection.get_qualname(type), module=getattr(type, "__module__", None)
            )
        )
        node = dataclasses.replace(key, type=ref)
        return self[node]
