import types
from unittest import mock

import pytest

from typelib.py import frames

GLOBAL: str = "FOO"
_LOCAL: str = "BAR"


@pytest.mark.suite(
    global_var=dict(given_name="GLOBAL", expected_value=GLOBAL),
    local_var=dict(given_name="local", expected_value=_LOCAL),
    unknown_var=dict(given_name="_frob", expected_value=None),
)
def test_extract(given_name, expected_value):
    # Given
    local: str = _LOCAL  # noqa: F841
    # When
    extracted = frames.extract(given_name)
    # Then
    assert extracted == expected_value


def test_getcaller_no_fback(mock_frame):
    # Given
    given_frame = mock_frame
    given_frame.f_back = None
    expected_frame = given_frame
    # When
    caller = frames.getcaller(given_frame)
    # Then
    assert caller == expected_frame


def test_getcaller_module_in_package(mock_frame, mock_module, mock_getmodule):
    # Given
    given_frame = mock_frame
    given_next_frame = mock.create_autospec(
        types.FrameType, spec_set=True, instance=True
    )
    given_final_frame = mock.create_autospec(
        types.FrameType, spec_set=True, instance=True
    )
    given_final_frame.f_back = None
    given_next_frame.f_back = given_final_frame
    given_frame.f_back = given_next_frame
    given_module_name = frames.PKG_NAME
    mock_module.__name__ = given_module_name
    expected_frame = given_final_frame
    # When
    caller = frames.getcaller(given_frame)
    # Then
    assert caller == expected_frame


def test_getcaller_co_qualname_in_package(mock_frame, mock_module, mock_getmodule):
    # Given
    given_frame = mock_frame
    given_next_frame = mock.create_autospec(
        types.FrameType, spec_set=True, instance=True
    )
    given_final_frame = mock.create_autospec(
        types.FrameType, spec_set=True, instance=True
    )
    given_final_frame.f_back = None
    given_next_frame.f_back = given_final_frame
    given_frame.f_back = given_next_frame
    mock_getmodule.return_value = None
    given_next_frame.f_code.co_qualname = frames.PKG_NAME
    expected_frame = given_final_frame
    # When
    caller = frames.getcaller(given_frame)
    # Then
    assert caller == expected_frame


def test_getcaller_co_filename_in_package(mock_frame, mock_module, mock_getmodule):
    # Given
    given_frame = mock_frame
    given_next_frame = mock.create_autospec(
        types.FrameType, spec_set=True, instance=True
    )
    given_final_frame = mock.create_autospec(
        types.FrameType, spec_set=True, instance=True
    )
    given_final_frame.f_back = None
    given_next_frame.f_back = given_final_frame
    given_frame.f_back = given_next_frame
    mock_getmodule.return_value = None
    given_next_frame.f_code.co_filename = frames.PKG_NAME
    expected_frame = given_final_frame
    # When
    caller = frames.getcaller(given_frame)
    # Then
    assert caller == expected_frame


def test_getcaller_not_in_package(mock_frame, mock_module, mock_getmodule):
    # Given
    given_frame = mock_frame
    given_next_frame = mock.create_autospec(
        types.FrameType, spec_set=True, instance=True
    )
    given_final_frame = mock.create_autospec(
        types.FrameType, spec_set=True, instance=True
    )
    given_final_frame.f_back = None
    given_next_frame.f_back = given_final_frame
    given_frame.f_back = given_next_frame
    mock_getmodule.return_value = None
    given_next_frame.f_code.co_filename = "file"
    given_next_frame.f_code.co_qualname = "qual"
    expected_frame = given_next_frame
    # When
    caller = frames.getcaller(given_frame)
    # Then
    assert caller == expected_frame
