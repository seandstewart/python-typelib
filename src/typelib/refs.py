from __future__ import annotations

import functools
import inspect
import sys
import typing

from typelib import frames, future

__all__ = ("ForwardRef", "evaluate", "forwardref")

ForwardRef: typing.TypeAlias = typing.ForwardRef


def forwardref(
    ref: str,
    *,
    is_argument: bool = False,
    module: typing.Any | None = None,
    is_class: bool = True,
) -> ForwardRef:
    module = _resolve_module_name(ref, module)
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
            if type(ref) is not ForwardRef:
                return ref
            if ref.__forward_evaluated__:
                return ref.__forward_value__

            recursive_guard = recursive_guard or set()
            return ref._evaluate(globalns, localns, recursive_guard)

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
            globalns = {**globals(), **(globalns or {})}
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
    module = ref.rsplit(".", maxsplit=1)[0]
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
