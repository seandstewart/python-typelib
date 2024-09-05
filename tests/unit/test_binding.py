from __future__ import annotations

import collections
import inspect
from unittest import mock

import pytest

from typelib import binding


@pytest.fixture(
    params=[
        inspect.Parameter.POSITIONAL_ONLY,
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
        inspect.Parameter.KEYWORD_ONLY,
        inspect.Parameter.VAR_KEYWORD,
    ]
)
def one(request) -> inspect.Parameter:
    return inspect.Parameter(
        "one",
        request.param,
        annotation=int,
    )


@pytest.fixture(
    params=[
        inspect.Parameter.POSITIONAL_ONLY,
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
        inspect.Parameter.VAR_POSITIONAL,
        inspect.Parameter.KEYWORD_ONLY,
    ]
)
def two(request) -> inspect.Parameter:
    return inspect.Parameter(
        "two",
        request.param,
        annotation=int,
    )


@pytest.fixture(
    params=[
        inspect.Parameter.POSITIONAL_ONLY,
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
        inspect.Parameter.KEYWORD_ONLY,
    ]
)
def three(request) -> inspect.Parameter:
    return inspect.Parameter(
        "three",
        request.param,
        annotation=int,
    )


@pytest.fixture(
    params=[
        inspect.Parameter.POSITIONAL_ONLY,
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
        inspect.Parameter.KEYWORD_ONLY,
    ]
)
def four(request) -> inspect.Parameter:
    return inspect.Parameter(
        "four",
        request.param,
        annotation=int,
    )


@pytest.fixture(
    params=[
        inspect.Parameter.POSITIONAL_ONLY,
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
        inspect.Parameter.KEYWORD_ONLY,
    ]
)
def five(request) -> inspect.Parameter:
    return inspect.Parameter(
        "five",
        request.param,
        annotation=int,
    )


@pytest.fixture()
def given_signature(one, two, three, four, five):
    params = sorted([one, two, three, four, five], key=lambda p: p.kind)
    counts = collections.Counter(p.kind for p in params)
    if (
        counts[inspect.Parameter.VAR_KEYWORD] > 1
        or counts[inspect.Parameter.VAR_POSITIONAL] > 1
    ):
        pytest.skip("Impossible param combination.")

    return inspect.Signature(params)


@pytest.fixture()
def given_input(one, two, three, four, five):
    inp = []
    kw_inp = {}
    params = sorted([one, two, three, four, five], key=lambda p: p.kind)
    for p in params:
        if p.kind == inspect.Parameter.POSITIONAL_ONLY:
            inp.append("1")
        elif p.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
            inp.append("2")
        elif p.kind == inspect.Parameter.VAR_POSITIONAL:
            inp.append("3")
        elif p.kind == inspect.Parameter.KEYWORD_ONLY:
            kw_inp.update({p.name: "4"})
        elif p.kind == inspect.Parameter.VAR_KEYWORD:
            kw_inp.update({p.name: "5"})
    return tuple(inp), kw_inp


@pytest.fixture()
def expected_output(one, two, three, four, five):
    params = sorted([one, two, three, four, five], key=lambda p: p.kind)
    out = []
    kw_out = {}
    for p in params:
        if p.kind == inspect.Parameter.POSITIONAL_ONLY:
            out.append(1)
        elif p.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
            out.append(2)
        elif p.kind == inspect.Parameter.VAR_POSITIONAL:
            out.append(3)
        elif p.kind == inspect.Parameter.KEYWORD_ONLY:
            kw_out.update({p.name: 4})
        elif p.kind == inspect.Parameter.VAR_KEYWORD:
            kw_out.update({p.name: 5})

    return tuple(out), kw_out


def test_bind(given_signature, given_input, expected_output):
    # Given
    given_callable = mock.Mock(
        __signature__=given_signature, side_effect=lambda *a, **kw: (a, kw)
    )
    given_binding = binding.bind(given_callable)
    given_args, given_kwargs = given_input
    # When
    output = given_binding(*given_args, **given_kwargs)
    # Then
    assert output == expected_output


def test_bind_kwargs_only():
    # Given
    def given_callable(**kwargs: int):
        return kwargs

    given_binding = binding.bind(given_callable)
    given_kwargs = {"a": "1", "b": "2"}
    expected_output = {"a": 1, "b": 2}
    # When
    output = given_binding(**given_kwargs)
    # Then
    assert output == expected_output


def test_bind_args_only():
    # Given
    def given_callable(*args: int):
        return args

    given_binding = binding.bind(given_callable)
    given_args = ("1", "2")
    expected_output = (1, 2)
    # When
    output = given_binding(*given_args)
    # Then
    assert output == expected_output


def test_wrap(given_signature, given_input, expected_output):
    # Given
    given_callable = mock.Mock(
        __signature__=given_signature, side_effect=lambda *a, **kw: (a, kw)
    )
    given_binding = binding.wrap(given_callable)
    given_args, given_kwargs = given_input
    # When
    output = given_binding(*given_args, **given_kwargs)
    # Then
    assert output == expected_output


def test_wrap_class():
    # Given
    @binding.wrap
    class GivenClass:
        def __init__(self, attr: int):
            self.attr = attr

    given_attr = "1"
    expected_attr = 1

    # When
    instance = GivenClass(given_attr)
    # Then
    assert instance.attr == expected_attr
