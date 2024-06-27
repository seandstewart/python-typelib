from __future__ import annotations

import dataclasses
import typing as tp

from typelib import classes, compat
from typelib import marshal as mmarshal
from typelib import unmarshal as munmarshal

__all__ = ("protocol", "InterchangeProtocol")


@compat.cache
def protocol(
    t: type[T],
    *,
    marshal: mmarshal.AbstractMarshaller[T] | None = None,
    unmarshal: munmarshal.AbstractUnmarshaller[T] | None = None,
) -> InterchangeProtocol[T]:
    marshal = marshal or mmarshal.marshaller(typ=t)
    unmarshal = unmarshal or munmarshal.unmarshaller(typ=t)
    proto = InterchangeProtocol(t=t, marshal=marshal, unmarshal=unmarshal)
    return proto


T = tp.TypeVar("T")


@classes.slotted(dict=False, weakref=True)
@dataclasses.dataclass
class InterchangeProtocol(tp.Generic[T]):
    t: type[T]
    marshal: mmarshal.AbstractMarshaller[T]
    unmarshal: munmarshal.AbstractUnmarshaller[T]
