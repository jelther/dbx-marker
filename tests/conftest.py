from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_spark():
    mock = MagicMock()
    mock.sql = MagicMock()
    # delta_table_exists return False by default
    with patch('dbx_marker.utils.delta_table_exists', return_value=False):
        yield mock