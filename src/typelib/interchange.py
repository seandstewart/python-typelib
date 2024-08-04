"""Interface for marshalling, unmarshalling, encoding, and decoding data to and from a bound type.

Examples: Typical Usage
    >>> import dataclasses
    >>> from typelib import interchange
    >>>
    >>> @dataclasses.dataclass
    ... class Class:
    ...     attr: str
    ...
    >>> proto = interchange.protocol(Class)
    >>> proto.unmarshal({"attr": "value"})
    Class(attr="value")
    >>> proto.codec.decode(b'{"attr": "value"}')
    Class(attr="value")
    >>> proto.codec.encode(Class(attr="value"))
    b'{"attr":"value"}'
"""

from __future__ import annotations

import dataclasses
import typing as tp

from typelib import codec as mcodec
from typelib import marshal as mmarshal
from typelib import unmarshal as munmarshal
from typelib.py import classes, compat, inspection

__all__ = ("protocol", "InterchangeProtocol")


@compat.cache
def protocol(
    t: type[T],
    *,
    codec: mcodec.AbstractCodec[T] | None = None,
    marshaller: mmarshal.AbstractMarshaller[T] | None = None,
    unmarshaller: munmarshal.AbstractUnmarshaller[T] | None = None,
    encoder: mcodec.EncoderT = compat.json.dumps,
    decoder: mcodec.DecoderT = compat.json.loads,
) -> InterchangeProtocol[T]:
    """Factory function for creating an [`InterchangeProtocol`][typelib.interchange.InterchangeProtocol] instance.

    Note:
        In the simplest case, all that needs be provided is `t`. We will
        generate a marshaller, unmarshaller and codec. In most cases, you probably
        don't need to override the default marshaller and unmarshaller behavior.

        If no `codec` is passed, we create a [`Codec`][typelib.codec.Codec]
        instance with `marshaller`, `unmarshaller`, `encoder`
        and `decoder`. This codec instance combines your marshalling protocol
        and your wire protocol, allowing you to pass instances of `t` directly
        to [`Codec.encode`][typelib.codec.Codec.encode] and receive instances of `t`
        directly from [`Codec.decode`][typelib.codec.Codec.decode].

        The `encoder` and `decoder` default to JSON, using either
        stdlib [`json`][] or [`orjson`](https://github.com/ijl/orjson) if available.

        You can customize your wire protocol in two ways:
            1. Pass in a custom [`AbstractCodec`][typelib.codec.AbstractCodec] instance.
               * This will override the behavior described above. Useful when you have
                 your own optimized path for your wire protocol and don't desire our
                 marshalling capabilities.
            2. Pass in custom `encoder` and `decoder` values.
               * This will follow the behavior described above. Useful when you use a
                 wire protocol other than JSON.

    Args:
        t: The type to create the interchange protocol for.
        codec: The codec for encoding and decoding data for over-the-wire (optional).
        marshaller: The marshaller used to marshal inputs into the associated type. (optional)
        unmarshaller: The unmarshaller used to unmarshal inputs into the associated type. (optional)
        encoder: The encoder for encoding data for over-the-wire (defaults to JSON).
        decoder: The decoder for decoding data from over-the-wire (defaults to JSON).


    See Also:
        * [`typelib.codec`][]
    """
    marshal = marshaller or mmarshal.marshaller(typ=t)
    unmarshal = unmarshaller or munmarshal.unmarshaller(typ=t)
    if inspection.isbytestype(t) and codec is None:
        codec = mcodec.Codec(
            marshaller=marshal,
            unmarshaller=unmarshal,
            encoder=lambda v: v,  # type: ignore[arg-type,return-value]
            decoder=lambda v: v,  # type: ignore[arg-type,return-value]
        )
    codec = codec or mcodec.Codec(
        marshaller=marshal,
        unmarshaller=unmarshal,
        encoder=encoder,
        decoder=decoder,
    )
    proto = InterchangeProtocol(t=t, marshal=marshal, unmarshal=unmarshal, codec=codec)
    return proto


T = tp.TypeVar("T")


@classes.slotted(dict=False, weakref=True)
@dataclasses.dataclass
class InterchangeProtocol(tp.Generic[T]):
    """The protocol for marshalling, unmarshalling, encoding and decoding data (interchange)."""

    t: type[T]
    """The bound type definition for this protocol."""
    marshal: mmarshal.AbstractMarshaller[T]
    """Callable which will marshal `T` instances into primitive types for serialization."""
    unmarshal: munmarshal.AbstractUnmarshaller[T]
    """Callable which will unmarshal primitive types into `T` instances."""
    codec: mcodec.AbstractCodec[T]
    """The wire protocol for encoding and decoding binary data."""
