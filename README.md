# python-typelib: Python's Typing Toolkit

_Sensible, non-invasive, production-ready tooling for leveraging Python type 
annotations at runtime._

[![Version][version]][version]
[![License: MIT][license]][license]
[![Python Versions][python]][python]
[![Code Size][code-size]][repo]
[![CI][ci-badge]][ci]
[![Coverage][cov-badge]][coverage]
[![Code Style][style-badge]][style-repo]

<!-- TOC -->
* [python-typelib: Python's Typing Toolkit](#python-typelib-pythons-typing-toolkit)
  * [Introduction](#introduction)
    * [What is `typelib`?](#what-is-typelib)
    * [Why `typelib`?](#why-typelib)
  * [Quickstart](#quickstart)
    * [Installation](#installation)
    * [The InterchangeProtocol: A Gentle Introduction](#the-interchangeprotocol-a-gentle-introduction)
<!-- TOC -->

## Introduction

### What is `typelib`?

1. `typelib` is a library devoted to runtime analysis, validation, and (un)marshalling 
of types as described by [PEP 484][pep-484].
2. `typelib` utilizes a graph-based resolver for analyzing python type annotations at 
runtime via the standard library.
3. `typelib` strives to stay up-to-date with the latest typing PEPs, as listed in the
[Typing PEPs][typing-peps] index. 
   - It also fully supports [PEP 563][pep-563] and the 
   `annotations` future, enabling developers to make full use of new-style unions and 
   builtin generics, without requiring a new version of Python.

### Why `typelib`?

There are many libraries that afford a similar set of features. To name a few:
- Pydantic
- mashumaro
- cattrs
- dataclasses-json
- dacite

What separates this library from the pack? A few things:

1. A graph-based type resolver.
   - Every type description is a graph - we resolve types into a graph structure, then
     use the builtin `graphlib` to provide a stable sort of nodes in the graph.
   - We can _proactively detect_ cyclic and recursive types and prevent common 
     pitfalls by leveraging `ForwardRefs` to defer evaluation of the cycle without 
     paying a penalty in performance.
2. We don't require you inherit custom base classes or mixins. 
   - `typelib` works _with_ the standard library, not in _parallel_.
3. _No code-gen_.
   - The libraries you use should be _easy to reason about_ and _easy to inspect_. 
   - Nobody wants to be paged at 3 AM because a third-party library explodes and it 
     can't be debugged.

In summary, this library is _easy to debug_, leverages a _sensible data structure_, and
can work at the _edges of your code_ instead of you integrate a novel type-system.

## Quickstart

### Installation

```shell
poetry add python-typelib -E json
```

### The InterchangeProtocol: A Gentle Introduction

`typelib` is meant to be a general-purpose toolk

Given a model like so:

```python
# src/app/models.py
from __future__ import annotations

import uuid

import datetime
import dataclasses


@dataclasses.dataclass(slots=True, weakref_slot=True, kw_only=True)
class BusinessModel:
    important: str
    data: str
    internal: str
    id: uuid.UUID | None = None
    created_at: datetime.datetime | None = None

```

We can easily define an interface to (a) receive inputs, (b) store inputs, (c) 
return outputs:

```python
from __future__ import annotations
import dataclasses
import datetime
import uuid

from typing import TypedDict

from typelib import interchange, compat

from app import models


class ClientRPC:
    
    def __init__(self):
        self.business_repr = interchange.protocol(models.BusinessModel)
        self.client_repr = interchange.protocol(ClientRepresentation)
        self.db = {}


    def create(self, inp: InputT) -> ClientRepresentation:
        stored = self._store(self._receive(inp))
        return self._send(stored)
    
    def get(self, id: uuid.UUID) -> ClientRepresentation | None:
        stored = self.db.get(id)
        if not stored:
            return 
        return self._send(stored)

    def _receive(self, inp: InputT) -> models.BusinessModel:
        instance = self.business_repr.unmarshal(inp)
        return instance
    
    
    def _store(self, instance: models.BusinessModel) -> models.BusinessModel:
        stored =  dataclasses.replace(
            instance, 
            id=uuid.uuid4(), 
            created_at=datetime.datetime.now(tz=datetime.timezone.utc)
        )
        self.db[stored.uuid] = stored
        return stored
    
    
    def _send(self, instance: models.BusinessModel) -> ClientRepresentation:
        marshalled = self.client_repr.marshal(instance)
        return marshalled

    

    
class ClientRepresentation(TypedDict):
    id: uuid.UUID
    important: str
    data: str
    created_at: datetime.datetime



# py 3.12+: type InputT = str | bytes | dict[str, str]
InputT = compat.TypeAliasType("InputT", "str | bytes | dict[str, str]")

```

Let's take a pause and break down what we just saw:
1. We defined a dataclass called `BusinessModel` which is our core data model for 
   our app.
   - Note: we could use any class here, so long as type annotations are present in 
     either the class signature or class body.
2. We defined a `ClientRepresentation` which describes a dictionary structure that 
   _does not include internal-only fields (e.g., `BusinessModel.internal`)_.
   - Note: we used a `TypedDict` here - no need for a dataclass, and `typelib` 
     handles it just fine.
3. We defined `ClientRPC` class which contains the logic for:
   1. _receiving an input_
   2. _storing an input_
   3. _sending a response_
4. Take special note of how we translate between representations of our internal 
   business model and the client representation:
   - We instantiated an `InterchangeProtocol` using the `typelib.format` module.
   - To unmarshal an input (JSON-encoded or Python primitive), we pass it to the 
     defined protocol for the business model.
   - To translate the saved model, we pass it _directly to the client format protocol._

> **:bulb: Note**
> 
> typelib can translate between any structured object or container, without any 
> special configuration! We have robust support for translating between most any type.

[pypi]: https://pypi.org/project/python-typelib/
[version]: https://img.shields.io/pypi/v/python-typelib.svg
[license]: https://img.shields.io/pypi/v/python-typelib.svg
[python]: https://img.shields.io/pypi/pyversions/python-typelib.svg
[repo]: https://github.com/seandstewart/python-typelib
[code-size]: https://img.shields.io/github/languages/code-size/seandstewart/python-typelib.svg?style=flat
[ci-badge]: https://github.com/seandstewart/python-typelib/actions/workflows/validate.yml/badge.svg
[ci]: https://github.com/seandstewart/python-typelib/actions/workflows/validate.ym
[cov-badge]: https://codecov.io/gh/seandstewart/python-typelib/graph/badge.svg?token=TAM7VCTBHD
[coverage]: https://codecov.io/gh/seandstewart/python-typelib
[style-badge]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
[style-repo]: https://github.com/astral-sh/ruff
[pep-484]: https://www.python.org/dev/peps/pep-0484/
[pep-563]: https://www.python.org/dev/peps/pep-0563/
[typing-peps]: https://peps.python.org/topic/typing/