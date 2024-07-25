"""Support for unmarshalling unstructured data into Python data structures.

Notes:
    "Unmarshalling" refers to the process of taking a "primitive" form of data, such
    as a basic dictionary or JSON string, and coercing it into a higher-order structured
    data type.

Tip:
    You are safe to use this package directly, but we encourage you to work with the
    higher-level API provided by the [`interchange`][typelib.interchange] module.

Examples: Typical Usage
    >>> import dataclasses
    >>> import decimal
    >>> from typelib import unmarshal
    >>>
    >>> @dataclasses.dataclass(slots=True, weakref_slot=True, kw_only=True)
    ... class Struct:
    ...     key: str
    ...     number: decimal.Decimal
    ...
    >>>
    >>> data = {"key": "some-key", "number": "3.14"}
    >>> unmarshal.unmarshal(Struct, data)
    Struct(key='some-key', number=decimal.Decimal('3.14'))
    >>> unmarshaller = unmarshal.unmarshaller(Struct)
    >>> unmarshaller(data)
    Struct(key='some-key', number=decimal.Decimal('3.14'))

See Also:
    * [`unmarshal`][typelib.unmarshal.unmarshal]
    * [`unmarshaller`][typelib.unmarshal.unmarshaller]
    * [`interchange.protocol`][typelib.interchange.protocol]
"""

from typelib.unmarshal.api import *
from typelib.unmarshal.routines import *
