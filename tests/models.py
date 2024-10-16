from __future__ import annotations

import dataclasses
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
