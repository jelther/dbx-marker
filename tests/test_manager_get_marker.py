from unittest.mock import patch

import pytest
from pyspark import Row

from dbx_marker import DbxMarker, MarkerNotFoundError
from dbx_marker.config import config


@patch("dbx_marker.manager.delta_table_exists", return_value=True)
def test_get_marker_that_exists(mock_table_exists, mock_spark):
    with patch(
        "dbx_marker.manager.parse_marker_from_type", return_value=1
    ) as mock_parse_marker_from_type:
        manager = DbxMarker(delta_table_path="mock_path", spark=mock_spark)
        mock_spark.sql.return_value.first.return_value = Row(
            value="1", marker_type="int"
        )
        value = manager.get_marker("test_pipeline")
        assert value == 1
        mock_parse_marker_from_type.assert_called_with(
            "1", "int", config.DATETIME_FORMAT
        )


@patch("dbx_marker.manager.delta_table_exists", return_value=True)
def test_get_marker_not_found(mock_table_exists, mock_spark):
    with patch("dbx_marker.manager.parse_marker_from_type", return_value=1) as _:
        manager = DbxMarker(delta_table_path="mock_path", spark=mock_spark)
        mock_spark.sql.return_value.first.return_value = None
        with pytest.raises(MarkerNotFoundError):
            manager.get_marker("non_existent_pipeline")


@patch("dbx_marker.manager.delta_table_exists", return_value=True)
def test_get_marker_raises_exception(mock_table_exists, mock_spark):
    manager = DbxMarker(delta_table_path="mock_path", spark=mock_spark)
    mock_spark.sql.side_effect = Exception("Test exception")
    with pytest.raises(MarkerNotFoundError):
        manager.get_marker("test_pipeline")
