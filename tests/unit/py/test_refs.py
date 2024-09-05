from unittest import mock

import pytest

from typelib.py import refs


def evaluated_ref(t: str) -> refs.ForwardRef:
    _ref = refs.ForwardRef("str")
    _ref._evaluate(None, None, recursive_guard=frozenset())
    return _ref


@pytest.mark.suite(
    not_ref=dict(given_ref=str, expected_type=str),
    ref=dict(given_ref=refs.ForwardRef("str"), expected_type=str),
    evaluated_ref=dict(given_ref=evaluated_ref("str"), expected_type=str),
)
def test_evaluate(given_ref, expected_type):
    # When
    evaluated = refs.evaluate(given_ref)
    # Then
    assert evaluated == expected_type


class RefClass: ...


@pytest.mark.suite(
    no_module_provided=dict(
        given_ref_name="str",
        given_module_name=None,
        expected_ref=refs.ForwardRef("str", module=mock.ANY),
    ),
    module_provided=dict(
        given_ref_name="str",
        given_module_name="builtins",
        expected_ref=refs.ForwardRef("str", module="builtins"),
    ),
    module_in_name=dict(
        given_ref_name="builtins.str",
        given_module_name=None,
        expected_ref=refs.ForwardRef("str", module="builtins"),
    ),
    module_from_frame=dict(
        given_ref_name="RefClass",
        given_module_name=None,
        expected_ref=refs.ForwardRef("RefClass", module=__name__),
    ),
    module_from_caller=dict(
        given_ref_name="UnknownClass",
        given_module_name=None,
        expected_ref=refs.ForwardRef("UnknownClass", module=mock.ANY),
    ),
)
def test_forwardref(given_ref_name, given_module_name, expected_ref):
    # When
    created_ref = refs.forwardref(given_ref_name, module=given_module_name)
    # Then
    assert created_ref == expected_ref
