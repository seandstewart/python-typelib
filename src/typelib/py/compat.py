from __future__ import annotations

import sys
from typing import TYPE_CHECKING

__all__ = ("TypeIs", "json")

if sys.version_info >= (3, 13):
    from typing import TypeIs
else:
    from typing_extensions import TypeIs

if TYPE_CHECKING:
    import orjson as json
else:
    try:
        import orjson as json
    except ImportError:
        import json
