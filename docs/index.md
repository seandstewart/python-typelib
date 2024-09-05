# Welcome to `typelib`

[![Version][version]][version]
[![License: MIT][license]][license]
[![Python Versions][python]][python]
[![Code Size][code-size]][repo]
[![CI][ci-badge]][ci]
[![Coverage][cov-badge]][coverage]
[![Code Style][style-badge]][style-repo]

## Python's Typing Toolkit

`typelib` provides a sensible, non-invasive, production-ready toolkit for leveraging 
Python type annotations at runtime. 

## Quickstart

### Installation

```shell
poetry add 'typelib[json]'
```

### Bring Your Own Models

We don't care how your data model is implemented - you can use [`dataclasses`][], 
[`TypedDict`][typing.TypedDict], [`NamedTuple`][typing.NamedTuple], a plain collection,
a custom class, or any other modeling library. As long as your type is valid at runtime, 
we'll support it.


### The How and the Where

#### How: The High-Level API

We have a simple high-level API which should handle most production use-cases:

```python
from __future__ import annotations

import dataclasses
import datetime
import decimal


import typelib

@dataclasses.dataclass(slots=True, weakref_slot=True, kw_only=True)
class BusinessModel:
    op: str
    value: decimal.Decimal
    id: int | None = None
    created_at: datetime.datetime | None = None
    

codec = typelib.codec(BusinessModel)
instance = codec.decode(b'{"op":"add","value":"1.0"}')
print(instance)
#> BusinessModel(op='add', value=decimal.Decimal('1.0'), id=None, created_at=None)
encoded = codec.encode(instance)
print(encoded)
#> b'{"op":"add","value":"1.0","id":null,"created_at":null}'
```

/// tip
Looking for more? Check out our [API Reference][typelib] for the high-level API.
///


#### Where: At the Edges of Your Code

You can integrate this library at the "edges" of your code - e.g., at the integration
points between your application and your client or you application and your data-store:

```python
from __future__ import annotations

import dataclasses
import datetime
import decimal
import operator
import random

import typelib


class ClientRPC:
    def __init__(self):
        self.codec = typelib.codec(BusinessModel)

    def call(self, inp: bytes) -> bytes:
        model = self.receive(inp)
        done = self.op(model)
        return self.send(done)

    @staticmethod
    def op(model: BusinessModel) -> BusinessModel:
        op = getattr(operator, model.op)
        return dataclasses.replace(
            model,
            value=op(model.value, model.value),
            id=random.getrandbits(64),
            created_at=datetime.datetime.now(tz=datetime.UTC)
        )

    def send(self, model: BusinessModel) -> bytes:
        return self.codec.encode(model)

    def receive(self, data: bytes) -> BusinessModel:
        return self.codec.decode(data)


@dataclasses.dataclass(slots=True, weakref_slot=True, kw_only=True)
class BusinessModel:
    op: str
    value: decimal.Decimal
    id: int | None = None
    created_at: datetime.datetime | None = None

```

#### Where: Between Layers in Your Code

You can integrate this library to ease the translation of one type to another:

```python
from __future__ import annotations

import dataclasses
import datetime
import decimal
import typing as t


import typelib

@dataclasses.dataclass(slots=True, weakref_slot=True, kw_only=True)
class BusinessModel:
    op: str
    value: decimal.Decimal
    id: int | None = None
    created_at: datetime.datetime | None = None
    

class ClientRepr(t.TypedDict):
    op: str
    value: str
    id: str | None
    created_at: datetime.datetime | None


business_codec = typelib.codec(BusinessModel)
client_codec = typelib.codec(ClientRepr)
# Initialize your business model directly from your input.
instance = business_codec.decode(
   b'{"op":"add","value":"1.0","id":"10","created_at":"1970-01-01T00:00:00+0000}'
)
print(instance)
#> BusinessModel(op='add', value=Decimal('1.0'), id=10, created_at=datetime.datetime(1970, 1, 1, 0, 0, fold=1, tzinfo=Timezone('UTC')))
# Encode your business model into the format defined by your ClientRepr.
encoded = client_codec.encode(instance)
print(encoded)
#> b'{"op":"add","value":"1.0","id":"10","created_at":"1970-01-01T00:00:00+00:00"}'

```

/// tip
There's no need to initialize your ClientRepr instance to leverage its codec, as long
as:

1. The instance you pass in has the same overlap of required fields.
2. The values in the overlapping fields can be translated to the target type.
///

## Why `typelib`

`typelib` provides a **simple, non-invasive API** to make everyday data wrangling in 
your production applications easy and reliable.

### We DO

1. Provide an API for marshalling and unmarshalling data based upon type annotations.
2. Provide an API for integrating our marshalling with over-the-wire serialization and 
   deserialization.
3. Provide fine-grained, high-performance, runtime introspection of Python types.
4. Provide future-proofing to allow for emerging type annotation syntax.

### We DON'T

1. Require you to inherit from a custom base class.
2. Require you to use custom class decorators.
3. Rely upon generated code.

## How It Works

`typelib`'s implementation is unique among runtime type analyzers - we use an iterative,
graph-based resolver to build a predictable, static ordering of the types represented by
an annotation. We have implemented our type-resolution algorithm in isolation from our 
logic for marshalling and unmarshalling as a simple iterative loop, making the logic 
simple to reason about.

/// tip
Read a detailed discussion [here](./graph.md).
///


[pypi]: https://pypi.org/project/typelib/
[version]: https://img.shields.io/pypi/v/typelib.svg
[license]: https://img.shields.io/pypi/l/typelib.svg
[python]: https://img.shields.io/pypi/pyversions/typelib.svg
[repo]: https://github.com/seandstewart/python-typelib
[code-size]: https://img.shields.io/github/languages/code-size/seandstewart/python-typelib.svg?style=flat
[ci-badge]: https://github.com/seandstewart/python-typelib/actions/workflows/validate.yml/badge.svg
[ci]: https://github.com/seandstewart/python-typelib/actions/workflows/validate.ym
[cov-badge]: https://codecov.io/gh/seandstewart/python-typelib/graph/badge.svg?token=TAM7VCTBHD
[coverage]: https://codecov.io/gh/seandstewart/python-typelib
[style-badge]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
[style-repo]: https://github.com/astral-sh/ruff
