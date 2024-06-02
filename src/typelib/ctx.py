from __future__ import annotations

from typelib import inspection, refs


class TypeContext(dict):
    def __missing__(self, key: type | refs.ForwardRef):
        if isinstance(key, refs.ForwardRef):
            raise KeyError(key)
        ref = refs.forwardref(
            inspection.get_qualname(key), module=getattr(key, "__module__", None)
        )
        return self[ref]
