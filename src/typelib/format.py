from __future__ import annotations

import dataclasses
import typing as tp

from typelib import classes, compat
from typelib import codec as mcodec
from typelib import marshal as mmarshal
from typelib import unmarshal as munmarshal

__all__ = ("protocol", "InterchangeProtocol")


@compat.cache
def protocol(
    t: type[T],
    *,
    marshaller: mmarshal.AbstractMarshaller[T] | None = None,
    unmarshaller: munmarshal.AbstractUnmarshaller[T] | None = None,
    codec: mcodec.AbstractCodec[T] | None = None,
) -> InterchangeProtocol[T]:
    marshal = marshaller or mmarshal.marshaller(typ=t)
    unmarshal = unmarshaller or munmarshal.unmarshaller(typ=t)
    codec = codec or mcodec.Codec(
        marshaller=marshal,
        unmarshaller=unmarshal,
        encoder=compat.json.dumps,
        decoder=compat.json.loads,
    )
    proto = InterchangeProtocol(t=t, marshal=marshal, unmarshal=unmarshal, codec=codec)
    return proto


T = tp.TypeVar("T")


@classes.slotted(dict=False, weakref=True)
@dataclasses.dataclass
class InterchangeProtocol(tp.Generic[T]):
    t: type[T]
    marshal: mmarshal.AbstractMarshaller[T]
    unmarshal: munmarshal.AbstractUnmarshaller[T]
    codec: mcodec.AbstractCodec[T]
