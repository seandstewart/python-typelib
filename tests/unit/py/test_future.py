import pytest

from typelib.py import future


@pytest.mark.suite(
    no_transform=dict(given_annotation="str", expected_annotation="str"),
    no_transform_union=dict(
        given_annotation="typing.Union[str, int]",
        expected_annotation="typing.Union[str, int]",
    ),
    transform_union=dict(
        given_annotation="str | int | None",
        expected_annotation="typing.Union[str, int, None]",
    ),
    transform_generic=dict(
        given_annotation="dict[str, int]",
        expected_annotation="typing.Dict[str, int]",
    ),
    transform_nested_union=dict(
        given_annotation="dict[str, int | float]",
        expected_annotation="typing.Dict[str, typing.Union[int, float]]",
    ),
    transform_nested_generic=dict(
        given_annotation="str | dict[str, int | float]",
        expected_annotation="typing.Union[str, typing.Dict[str, typing.Union[int, float]]]",
    ),
    unsupported_op=dict(
        given_annotation="1 + 2",
        expected_annotation="1 + 2",
    ),
)
def test_transform(given_annotation, expected_annotation):
    # When
    transformed = future.transform(given_annotation)
    # Then
    assert transformed == expected_annotation
