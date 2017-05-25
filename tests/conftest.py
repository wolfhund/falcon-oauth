import os
import pytest

from webtest import TestApp
from .app import api


@pytest.fixture
def webtest_app():
    return TestApp(api)
