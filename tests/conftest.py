from unittest.mock import MagicMock

import pytest
from loguru import logger


@pytest.fixture
def mock_spark():
    mock = MagicMock()
    mock.sql = MagicMock()
    yield mock


@pytest.fixture
def caplog(caplog):
    handler_id = logger.add(caplog.handler, format="{message}")
    yield caplog
    logger.remove(handler_id)
