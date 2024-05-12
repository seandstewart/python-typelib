from __future__ import annotations

import types
from unittest import mock

import pytest


@pytest.fixture()
def mock_frame():
    return mock.create_autospec(types.FrameType, instance=True, spec_set=True)


@pytest.fixture()
def mock_module():
    return mock.create_autospec(types.ModuleType, instance=True)


@pytest.fixture()
def mock_getmodule(mock_module):
    with mock.patch("inspect.getmodule") as m:
        m.return_value = mock_module
        yield m
