from unittest.mock import patch

import pytest
from freezegun import freeze_time

from dbx_marker import DbxMarker, MarkerDeleteError, MarkerNotFoundError
from dbx_marker.sqls import DELETE_MARKER_SQL


@freeze_time("2023-01-01 00:00:00")
@patch("dbx_marker.manager.delta_table_exists", return_value=False)
def test_delete_marker_valid(mock_table_exists, mock_spark):
    manager = DbxMarker(delta_table_path="mock_path", spark=mock_spark)
    with patch(
        "dbx_marker.manager.parse_marker_from_type", return_value=1
    ) as mock_parse_marker_from_type:
        mock_parse_marker_from_type.return_value = 1
        expected_sql_statement = DELETE_MARKER_SQL.format(
            delta_table_path="mock_path", pipeline_name="test_pipeline"
        )
        manager.delete_marker("test_pipeline")
        mock_spark.sql.assert_called_with(expected_sql_statement)


@patch("dbx_marker.manager.delta_table_exists", return_value=False)
def test_delete_marker_not_found(mock_table_exists, mock_spark):
    manager = DbxMarker(delta_table_path="mock_path", spark=mock_spark)

    with patch(
        "dbx_marker.manager.DbxMarker.get_marker", return_value=None
    ) as mock_get_marker:
        mock_get_marker.side_effect = MarkerNotFoundError("Marker not found")
        with pytest.raises(MarkerNotFoundError):
            manager.delete_marker("non_existent_pipeline")


@patch("dbx_marker.manager.delta_table_exists", return_value=False)
def test_delete_marker_raises_exception(mock_table_exists, mock_spark):
    manager = DbxMarker(delta_table_path="mock_path", spark=mock_spark)
    with patch("dbx_marker.manager.DbxMarker.get_marker", return_value=1):
        mock_spark.sql.side_effect = Exception("Test exception")
        with pytest.raises(MarkerDeleteError):
            manager.delete_marker("test_pipeline")
