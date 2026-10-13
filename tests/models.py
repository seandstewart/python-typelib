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


IntVar = typing.TypeVar("IntVar", bound=int)
StrVar = typing.TypeVar("StrVar", bound=str)


@dataclasses.dataclass
class DataGeneric[StrVarT: str, IntVarT: int]:
    field: StrVarT
    value: IntVarT


@dataclasses.dataclass
class LegacyDataGeneric(typing.Generic[StrVar, IntVar]):  # noqa: UP046
    field: StrVar
    value: IntVar


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


type ListAlias = list[int]


@dataclasses.dataclass
class NestedTypeAliasType:
    alias: ListAlias


type ValueAlias = int
type RecursiveAlias = dict[str, RecursiveAlias | ValueAlias]
StringRecursiveAlias = typing.TypeAliasType(  # noqa: UP040
    "StringRecursiveAlias", "dict[str, StringRecursiveAlias | ValueAlias]"
)

# String-valued aliases cover the string `__value__` path.
ScalarValue = typing.TypeAliasType(  # noqa: UP040
    "ScalarValue", "int | float | str | bool | None"
)
Record = typing.TypeAliasType(  # noqa: UP040
    "Record", "dict[str, list[Record] | list[ScalarValue] | Record | ScalarValue]"
)


TVar = typing.TypeVar("TVar", bound=int)


@dataclasses.dataclass
class SimpleGeneric[TVarT: int]:
    field: TVarT


@dataclasses.dataclass
class NestedGeneric[TVarT: int]:
    gen: SimpleGeneric[TVarT]


@dataclasses.dataclass
class LegacySimpleGeneric(typing.Generic[TVar]):  # noqa: UP046
    field: TVar


@dataclasses.dataclass
class LegacyNestedGeneric(typing.Generic[TVar]):  # noqa: UP046
    gen: LegacySimpleGeneric[TVar]


type Box[T] = list[T]
type Swap[A, B] = dict[B, A]


@dataclasses.dataclass
class Leaf[T]:
    value: T


@dataclasses.dataclass
class Node[T]:
    value: T
    children: list[Node[T]]


type Tree[T] = dict[str, Tree[T] | T]
type Forest[T] = list[Node[T]]
type MutualList = list[MutualMap | int]
type MutualMap = dict[str, MutualList]
type JSON = dict[str, JSON] | list[JSON] | str | int | float | bool | None
