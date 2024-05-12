from __future__ import annotations

import abc
import struct
from typing import Any, Generic, Mapping, TypeVar

T = TypeVar("T")


def deserializer(t: type[T]) -> AbstractDeserializer[T]:
    # nodes = graph.static_order(t)
    # context = {}
    ...


class AbstractDeserializer(abc.ABC, Generic[T]):
    t: type[T]
    context: Mapping[type, AbstractDeserializer]

    __slots__ = ("t", "context")

    def __init__(self, t: type[T], context: Mapping[type, AbstractDeserializer]):
        self.t = t
        self.context = context

    @abc.abstractmethod
    def __call__(self, val: Any) -> T: ...


StrT = TypeVar("StrT", bound=str)


class StringDeserializer(AbstractDeserializer[StrT], Generic[StrT]):
    def __call__(self, val: Any) -> StrT:
        if isinstance(val, (bytes, bytearray)):
            return self.t(val.decode("utf8"))
        if isinstance(val, memoryview):
            return self.t(val.tobytes().decode("utf8"))
        return self.t(val)


BytesT = TypeVar("BytesT", bound=bytes)


class BytesDeserializer(AbstractDeserializer[BytesT], Generic[BytesT]):
    def __call__(self, val: Any) -> BytesT:
        if isinstance(val, str):
            return self.t(val.encode("utf8"))
        if isinstance(val, int):
            return self.t(val.to_bytes())
        if isinstance(val, float):
            return self.t(struct.pack("!f", val))
        return self.t(val)
