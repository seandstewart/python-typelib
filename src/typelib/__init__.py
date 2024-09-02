"""The top-level API for typelib.

Examples: Typical Usage
    >>> import dataclasses
    >>> import typelib
    >>>
    >>> @dataclasses.dataclass
    ... class Data:
    ...     attr: int
    ...     key: str
    ...
    >>>
    >>> typelib.unmarshal(Data, '{"key":"string","attr":"1"}')
    Data(attr=1, key='string')
    >>> typelib.marshal(Data(attr=1, key='string'))
    {'attr': 1, 'key': 'string'}
    >>> codec = typelib.codec(Data)
    >>> codec.encode(Data(attr=1, key='string'))
    b'{"attr":1,"key":"string"}'
    >>> codec.decode(b'{"key":"string","attr":1}')
    Data(attr=1, key='string')
"""

from __future__ import annotations

import importlib.metadata

from typelib.api import *

__metadata__ = importlib.metadata.metadata("typelib")
__version__ = __metadata__.get("version")
__authors__ = __metadata__.get("authors")
__license__ = __metadata__.get("license")
