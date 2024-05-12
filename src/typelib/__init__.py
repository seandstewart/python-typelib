import importlib.metadata

__metadata__ = importlib.metadata.metadata("typelib")
__version__ = __metadata__.get("version")
__authors__ = __metadata__.get("authors")
__license__ = __metadata__.get("license")
