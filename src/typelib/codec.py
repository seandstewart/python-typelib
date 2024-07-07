from __future__ import annotations

import abc
import typing as t

from typelib import marshal, serdes, unmarshal

__all__ = ("AbstractCodec", "Codec")

T = t.TypeVar("T")


class AbstractCodec(abc.ABC, t.Generic[T]):
    def encode(self, value: T) -> bytes: ...

    def decode(self, value: bytes) -> T: ...


class Codec(AbstractCodec[T], t.Generic[T]):
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
        marshalled = self.marshaller(value)
        encoded = self.encoder(marshalled)
        return encoded

    def decode(self, value: bytes) -> T:
        decoded = self.decoder(value)
        unmarshalled = self.unmarshaller(decoded)
        return unmarshalled


EncoderT: t.TypeAlias = t.Callable[[serdes.MarshalledValueT], bytes]
DecoderT: t.TypeAlias = t.Callable[[bytes], serdes.MarshalledValueT]
