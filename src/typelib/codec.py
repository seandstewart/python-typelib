"""Interfaces for managing type-enforced wire protocols (codecs)."""

from __future__ import annotations

import abc
import typing as t

from typelib import marshal, serdes, unmarshal

__all__ = ("AbstractCodec", "Codec")

T = t.TypeVar("T")


class AbstractCodec(abc.ABC, t.Generic[T]):
    """The abstract interface for defining a wire protocol (codec).

    Developers may define custom codecs with this interface which are compatible with
    :py:func:`typelib.interchange.protocol`.

    See Also:
        * :py:func:`typelib.interchange.protocol`
    """

    def encode(self, value: T) -> bytes: ...

    def decode(self, value: bytes) -> T: ...


class Codec(AbstractCodec[T], t.Generic[T]):
    """A standard wire protocol (codec).

    This codec wraps the encoding and decoding of data to/from bytes with marshalling
    and unmarshaling capabilities, allowing you to serialize and deserialize data directly
    to/from your in-memory data models.

    See Also:
         * :py:func:`typelib.interchange.protocol`
    """

    __slots__ = ("marshaller", "unmarshaller", "encoder", "decoder")

    def __init__(
        self,
        *,
        marshaller: marshal.AbstractMarshaller[T],
        unmarshaller: unmarshal.AbstractUnmarshaller[T],
        encoder: EncoderT,
        decoder: DecoderT,
    ):
        self.marshaller = marshaller
        self.unmarshaller = unmarshaller
        self.encoder = encoder
        self.decoder = decoder

    def encode(self, value: T) -> bytes:
        """Encode an instance of `T` to bytes.

        We will first marshal the given instance using :py:attr:`marshaller`, then
        encode the marshalled data into bytes using :py:attr:`encoder`.

        Args:
            value: The instance to encode.
        """
        marshalled = self.marshaller(value)
        encoded = self.encoder(marshalled)
        return encoded

    def decode(self, value: bytes) -> T:
        """Decode an instance of `T` from bytes.

        We will first decode the data from bytes using :py:attr:`decoder`, then
        unmarshal the data into an instance of `T` using :py:attr:`unmarshaller`.

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
