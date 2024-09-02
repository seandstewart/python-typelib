"""Support for marshalling Python data structures into primitive equivalents.

Notes:
    "Marshalling" your data structure prepares it to be serialized into binary and sent
    over the wire, but *does not* serialize it. We keep these stages isolated to ensure
    maximum flexibility and simplicity.

    We ensure that your marshalled data is compatible with Python's built-in
    [`json`][] module. This provides maximum compatibility with most serialization
    protocols by limiting the output to simple Python builtin types:

    - [`bool`][]
    - [`int`][]
    - [`float`][]
    - [`str`][]
    - [`None`][]
    - [`list`][]
    - [`dict`][]

Tip:
    You may use this package directly, but we encourage you to work with our
    high-level API provided by the top-level [`typelib`][] module.

Examples: Typical Usage
    >>> import dataclasses
    >>> import decimal
    >>> from typelib import marshals
    >>>
    >>> @dataclasses.dataclass(slots=True, weakref_slot=True, kw_only=True)
    ... class Struct:
    ...     key: str
    ...     number: decimal.Decimal
    ...
    >>>
    >>> data = Struct(key="some-key", number=decimal.Decimal("1.0"))
    >>> marshals.marshal(data)
    {'key': 'some-key', 'number': '1.0'}
    >>> marshaller = marshals.marshaller(Struct)
    >>> marshaller(data)
    {'key': 'some-key', 'number': '1.0'}

See Also:
    * [`marshal`][typelib.marshals.marshal]
    * [`marshaller`][typelib.marshals.marshaller]
    * [`typelib.codec`][]
"""

from typelib.marshals.api import *
from typelib.marshals.routines import *
