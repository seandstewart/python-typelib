"""Utilities for working with :py:class:`typing.ForwardRef`."""

from __future__ import annotations

import functools
import inspect
import sys
import typing

from typelib.py import frames, future

__all__ = ("ForwardRef", "evaluate", "forwardref")

ForwardRef: typing.TypeAlias = typing.ForwardRef


def forwardref(
    ref: str,
    *,
    is_argument: bool = False,
    module: typing.Any | None = None,
    is_class: bool = True,
) -> ForwardRef:
    """Create a :py:class:`typing.ForwardRef` instance from a :py:param:`ref` string.

    This wrapper function will attempt to determine the module name ahead of instantiation
    if not provided. This is important when resolving the reference to an actual type.

    Args:
        ref: The type reference string.
        is_argument: Whether the reference string was an argument to a function (default False).
        module: The python module in which the reference string is defined (optional)
        is_class: Whether the reference string is a class (default True).
    """
    module = _resolve_module_name(ref, module)
    if module is not None:
        ref = ref.replace(f"{module}.", "")
    return ForwardRef(
        ref,
        is_argument=is_argument,
        module=module,
        is_class=is_class,
    )


if typing.TYPE_CHECKING:

    def evaluate(
        ref: ForwardRef,
        *,
        globalns: typing.Mapping[str, typing.Any] | None = None,
        localns: typing.Mapping[str, typing.Any] | None = None,
        recursive_guard: set | None = None,
    ) -> typing.Any: ...


else:
    if sys.version_info >= (3, 10):

        def evaluate(
            ref: ForwardRef,
            *,
            globalns: typing.Mapping[str, typing.Any] | None = None,
            localns: typing.Mapping[str, typing.Any] | None = None,
            recursive_guard: set | None = None,
        ) -> typing.Any:
            """Evaluate the :py:class:`typing.ForwardRef` instance into a proper type.

            Notes:
                Most of the time you will not need to provide anything but :py:param:`ref`.

                In Python 3.9, we will automatically transform "new-style" type hints into
                runtime-compatible type hints:
                  - Union-operator (`str | int` -> `typing.Union[str, int]`)
                  - builtin generics (`dict[str, str]` -> `typing.Dict[str, str]`)

            Args:
                ref: The :py:class:`typing.ForwardRef` instance to evaluate.
                globalns: A mapping of global variable names to values (optional).
                localns: A mapping of local variable names to values (optional).
                recursive_guard: A set instance to prevent recursion during evaluation (optional).
            """
            if type(ref) is not ForwardRef:
                return ref
            if ref.__forward_evaluated__:
                return ref.__forward_value__

            recursive_guard = recursive_guard or set()
            return ref._evaluate(globalns, localns, recursive_guard=recursive_guard)

    else:

        def evaluate(
            ref: ForwardRef,
            *,
            globalns: typing.Mapping[str, typing.Any] | None = None,
            localns: typing.Mapping[str, typing.Any] | None = None,
            recursive_guard: set | None = None,
        ) -> typing.Any:
            if type(ref) is not ForwardRef:
                return ref
            if ref.__forward_evaluated__:
                return ref.__forward_value__

            arg = future.transform_annotation(ref.__forward_arg__)
            globalns = {
                **globals(),
                **(globalns or {}),
                **vars(typing),
                "typing": typing,
            }
            nref = forwardref(
                arg,
                is_argument=ref.__forward_is_argument__,
                module=ref.__forward_module__,
                is_class=ref.__forward_is_class__,
            )
            recursive_guard = recursive_guard or set()
            return nref._evaluate(globalns, localns, recursive_guard)


@functools.cache
def _resolve_module_name(ref: str, module: str | None) -> str | None:
    if module is not None:
        return module

    # Easy path, use the qualname if it's provided.
    module = ref.split(".", maxsplit=1)[0]
    if module != ref:
        return module
    # Harder path, find the actual object in the stack frame, if possible.
    obj = frames.extract(ref)
    module = getattr(obj, "__module__", None)
    if module:
        return module
    # Tricky path, get the caller and get the module name of the caller.
    caller = frames.getcaller()
    module = getattr(inspect.getmodule(caller), "__name__", None)
    return module
