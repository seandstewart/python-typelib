"""Utilities for maintaining runtime compatibility with emerging type annotation operations.

Notes:
    This module's functionality is unnecessary for Python versions >= 3.10

Examples: Typical Usage
    >>> from typelib.py import future
    >>> future.transform_annotation("str | int")
    'typing.Union[str, int]'
    >>> future.transform_annotation("dict[str, int]")
    'typing.Dict[str, int]'
"""

from __future__ import annotations

import ast
import collections
import functools
import sys
import typing

__all__ = ("transform_annotation",)


@functools.cache
def transform(annotation: str, *, union: str = "typing.Union") -> str:
    """Transform a modern annotations into their [`typing`][] equivalent:

    - [`types.UnionType`][] into a [`typing.Union`][] (`str | int` -> `typing.Union[str, int]`)
    - builtin generics into typing generics (`dict[str, int]` -> `typing.Dict[str, int]`)

    Args:
        annotation: The annotation to transform, as a string.
        union: The name of the Union type to subscript (defaults `"typing.Union"`).

    Note:
        While this transformation requires your expression be valid Python syntax, it
        doesn't make sure the type annotation is valid.
    """
    parsed = ast.parse(annotation, mode="eval")
    transformed = TransformAnnotation(union=union).generic_visit(parsed)
    unparsed = ast.unparse(transformed).strip()
    return unparsed


class TransformAnnotation(ast.NodeTransformer):
    """A [`ast.NodeTransformer`][] that transforms [`typing.Union`][]."""

    def __init__(self, union: str = "typing.Union") -> None:
        self.union = union

    def visit_BinOp(self, node: ast.BinOp):
        """Transform a [`ast.BinOp`][] to [`typing.Union`][]."""
        # Ignore anything but a bitwise OR `|`
        if not isinstance(node.op, ast.BitOr):
            return node
        # Build a stack of args to the bitor
        args = collections.deque([node.right])
        left = node.left
        while isinstance(left, ast.BinOp):
            args.appendleft(left.right)
            left = left.left
        args.appendleft(left)
        # Visit each node in the stack
        elts = [self.visit(n) for n in args]
        # Write the old-style `Union`.
        union = ast.Subscript(
            value=ast.Name(id=self.union, ctx=ast.Load()),
            slice=ast.Index(value=ast.Tuple(elts=elts, ctx=ast.Load())),  # type: ignore[call-arg,arg-type]
            ctx=ast.Load(),
        )
        ast.copy_location(union, node)
        ast.fix_missing_locations(union)
        return union

    def visit_Name(self, node: ast.Name):
        """Transform a builtin [`ast.Name`][] to the `typing` equivalent."""
        # Re-write new-style builtin generics as old-style typing generics
        if node.id not in _GENERICS:
            return node

        new = ast.Name(id=_GENERICS[node.id], ctx=ast.Load())
        ast.copy_location(new, node)
        return new

    def visit_Subscript(self, node: ast.Subscript):
        """Transform all subscripts within a [`ast.Subscript`][]."""
        # Scan all subscripts to we transform nested new-style types.
        transformed = self.visit(node.slice)
        new = ast.Subscript(
            value=self.visit(node.value),
            slice=transformed,
            ctx=node.ctx,
        )
        ast.copy_location(new, node)
        ast.fix_missing_locations(new)
        return new

    def visit_Tuple(self, node: ast.Tuple):
        """Transform all values within a [`ast.Tuple`][]."""
        # Scan all tuples to ensure we transform nested new-style types.
        transformed = [self.visit(n) for n in node.elts]
        new = ast.Tuple(elts=transformed, ctx=node.ctx)
        ast.copy_location(new, node)
        ast.fix_missing_locations(new)
        return new


_GENERICS = {
    "dict": "typing.Dict",
    "list": "typing.List",
    "set": "typing.Set",
    "tuple": "typing.Tuple",
    "Pattern": "typing.Pattern",
}


if typing.TYPE_CHECKING:  # pragma: no cover

    def transform_annotation(annotation: str, *, union: str = "Union") -> str: ...

elif sys.version_info >= (3, 10):  # pragma: no cover

    def transform_annotation(annotation: str, *, union: str = "Union") -> str:
        return annotation

else:  # pragma: no cover
    transform_annotation = transform
