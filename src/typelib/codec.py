"""Interfaces for managing type-enforced wire protocols (codecs).

Tip:
    It shouldn't be necessary to create your own [`Codec`][] instances, you can instead
    rely upon the higher-level API provided by [`interchange.protocol`][typelib.interchange.protocol].

    Use this module for type annotations, if you need.

See Also:
    - [`interchange.protocol`][typelib.interchange.protocol]
"""

from __future__ import annotations

import abc
import dataclasses
import typing as t

from typelib import marshal, serdes, unmarshal

__all__ = ("AbstractCodec", "Codec")

from typelib.py import classes

T = t.TypeVar("T")


class AbstractCodec(abc.ABC, t.Generic[T]):
    """The abstract interface for defining a wire protocol (codec).

    Developers may define custom codecs with this interface which are compatible with
    [`typelib.interchange.protocol`][].

    See Also:
        * [`typelib.interchange.protocol`][]
    """

    def encode(self, value: T) -> bytes: ...

    def decode(self, value: bytes) -> T: ...


@classes.slotted(dict=False, weakref=False)
@dataclasses.dataclass(frozen=True)
class Codec(AbstractCodec[T], t.Generic[T]):
    """A standard wire protocol (codec).

    This codec wraps the encoding and decoding of data to/from bytes with marshalling
    and unmarshaling capabilities, allowing you to serialize and deserialize data directly
    to/from your in-memory data models.

    See Also:
         * :[`typelib.interchange.protocol`][]
    """

    marshaller: marshal.AbstractMarshaller[T]
    """The marshaller used to convert an instance of `T` to a serializable object."""
    unmarshaller: unmarshal.AbstractUnmarshaller[T]
    """The unmarshaller used to convert a deserialized object into an instance of `T`."""
    encoder: EncoderT
    """The encoder used to serialize a marshalled `T` into bytes."""
    decoder: DecoderT
    """The decoder used to deserialize a bytes-like object into a Python data structure for marshalling into `T`."""

    def encode(self, value: T) -> bytes:
        """Encode an instance of `T` to bytes.

        We will first marshal the given instance using the
        [`marshaller`][typelib.codec.Codec.marshaller], then encode the marshalled data
        into bytes using the [`encoder`][typelib.codec.Codec.encoder].

        Args:
            value: The instance to encode.
        """
        marshalled = self.marshaller(value)
        encoded = self.encoder(marshalled)
        return encoded

    def decode(self, value: bytes) -> T:
        """Decode an instance of `T` from bytes.

        We will first decode the data from bytes using the
        [`decoder`][typelib.codec.Codec.decoder], then unmarshal the data into an
        instance of `T` using [`unmarshaller`][typelib.codec.Codec.unmarshaller].

        Args:
            value: The bytes to decode.
        """
        decoded = self.decoder(value)
        unmarshalled = self.unmarshaller(decoded)
        return unmarshalled


EncoderT: t.TypeAlias = t.Callable[[serdes.MarshalledValueT], bytes]
"""Protocol for a wire serializer."""
DecoderT: t.TypeAlias = t.Callable[[bytes], serdes.MarshalledValueT]
"""Protocol for a wire deserializer."""
