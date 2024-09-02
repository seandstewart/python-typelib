"""Support for unmarshalling unstructured data into Python data structures.

Notes:
    "Unmarshalling" refers to the process of taking a "primitive" form of data, such
    as a basic dictionary or JSON string, and coercing it into a higher-order structured
    data type.

Tip:
    You may use this package directly, but we encourage you to work with the
    higher-level API provided by the [`typelib`][] module.

Examples: Typical Usage
    >>> import dataclasses
    >>> import decimal
    >>> from typelib import unmarshals
    >>>
    >>> @dataclasses.dataclass(slots=True, weakref_slot=True, kw_only=True)
    ... class Struct:
    ...     key: str
    ...     number: decimal.Decimal
    ...
    >>>
    >>> data = {"key": "some-key", "number": "3.14"}
    >>> unmarshals.unmarshal(Struct, data)
    Struct(key='some-key', number=decimal.Decimal('3.14'))
    >>> unmarshaller = unmarshals.unmarshaller(Struct)
    >>> unmarshaller(data)
    Struct(key='some-key', number=decimal.Decimal('3.14'))

See Also:
    * [`unmarshals`][typelib.unmarshals.unmarshal]
    * [`unmarshaller`][typelib.unmarshals.unmarshaller]
    * [`typelib.codec`][]
"""

from typelib.unmarshals.api import *
from typelib.unmarshals.routines import *
