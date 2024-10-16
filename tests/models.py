from __future__ import annotations

import dataclasses
import datetime
import enum
import typing


@dataclasses.dataclass
class RecursiveType:
    cycle: RecursiveType | None = None


@dataclasses.dataclass
class IndirectCycleType:
    indirect: CycleType


@dataclasses.dataclass
class CycleType:
    cycle: IndirectCycleType | None = None


@dataclasses.dataclass
class Data:
    field: str
    value: int


class Vanilla:
    def __init__(self, field: str, value: int):
        self.field = field
        self.value = value

    def __eq__(self, other):
        return self.field == getattr(other, "field", ...) and self.value == getattr(
            other, "value", ...
        )


class VanillaWithHints(Vanilla):
    field: str
    value: int


class NTuple(typing.NamedTuple):
    field: str
    value: int


class TDict(typing.TypedDict):
    field: str
    value: int


class GivenEnum(enum.Enum):
    one = "one"


@dataclasses.dataclass
class UnionSTDLib:
    timestamp: datetime.datetime | None = None
    date_time: datetime.datetime | None = None
    intstr: int | str = 0


@dataclasses.dataclass
class Parent:
    intersection: ParentIntersect
    child: Child


@dataclasses.dataclass
class Child:
    intersection: ChildIntersect


@dataclasses.dataclass
class ParentIntersect:
    a: int


@dataclasses.dataclass
class ChildIntersect:
    b: int
