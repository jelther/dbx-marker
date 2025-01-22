from datetime import datetime
from unittest.mock import patch

import pytest
from freezegun import freeze_time

from dbx_marker import DbxMarker
from dbx_marker.exceptions import MarkerInvalidTypeError, MarkerUpdateError
from dbx_marker.sqls import UPDATE_MARKER_SQL


@freeze_time("2023-01-01 00:00:00")
@patch("dbx_marker.manager.delta_table_exists", return_value=False)
def test_update_marker_valid_integer(mock_delta_table_exists, mock_spark, caplog):
    manager = DbxMarker(delta_table_path="mock_path", spark=mock_spark)
    expected_sql_statement = UPDATE_MARKER_SQL.format(
        delta_table_path="mock_path",
        pipeline_name="test_pipeline",
        value="1",
        marker_type="int",
        now="2023-01-01 00:00:00",
    )

    manager.update_marker("test_pipeline", 1, "int")
    mock_spark.sql.assert_called_with(expected_sql_statement)

    assert "Updated marker for pipeline 'test_pipeline' to '1' (int)." in caplog.text


@freeze_time("2023-01-01 00:00:00")
@patch("dbx_marker.manager.delta_table_exists", return_value=False)
def test_update_marker_valid_float(mock_delta_table_exists, mock_spark, caplog):
    manager = DbxMarker(delta_table_path="mock_path", spark=mock_spark)
    expected_sql_statement = UPDATE_MARKER_SQL.format(
        delta_table_path="mock_path",
        pipeline_name="test_pipeline",
        value="1.123",
        marker_type="float",
        now="2023-01-01 00:00:00",
    )
    manager.update_marker("test_pipeline", 1.123, "float")
    mock_spark.sql.assert_called_with(expected_sql_statement)
    assert (
        "Updated marker for pipeline 'test_pipeline' to '1.123' (float)." in caplog.text
    )


@freeze_time("2023-01-01 00:00:00")
@patch("dbx_marker.manager.delta_table_exists", return_value=False)
def test_update_marker_valid_datetime(mock_delta_table_exists, mock_spark, caplog):
    manager = DbxMarker(delta_table_path="mock_path", spark=mock_spark)
    expected_sql_statement = UPDATE_MARKER_SQL.format(
        delta_table_path="mock_path",
        pipeline_name="test_pipeline",
        value="1990-01-01 00:00:00",
        marker_type="datetime",
        now="2023-01-01 00:00:00",
    )

    manager.update_marker(
        "test_pipeline",
        datetime(year=1990, month=1, day=1, hour=0, minute=0, second=0),
        "datetime",
    )
    mock_spark.sql.assert_called_with(expected_sql_statement)
    assert (
        "Updated marker for pipeline 'test_pipeline' to '1990-01-01 00:00:00' (datetime)."
        in caplog.text
    )


@freeze_time("2023-01-01 00:00:00")
@patch("dbx_marker.manager.delta_table_exists", return_value=True)
def test_update_marker_invalid_marker_type(mock_delta_table_exists, mock_spark, caplog):
    manager = DbxMarker(delta_table_path="mock_path", spark=mock_spark)
    with pytest.raises(MarkerInvalidTypeError):
        manager.update_marker("test_pipeline", 1, "invalid_type")


@freeze_time("2023-01-01 00:00:00")
@patch("dbx_marker.manager.delta_table_exists", return_value=True)
def test_update_marker_invalid_marker_type_datetime(
    mock_delta_table_exists, mock_spark, caplog
):
    manager = DbxMarker(delta_table_path="mock_path", spark=mock_spark)
    with pytest.raises(TypeError):
        manager.update_marker("test_pipeline", 1, "datetime")


@freeze_time("2023-01-01 00:00:00")
@patch("dbx_marker.manager.delta_table_exists", return_value=True)
def test_update_marker_invalid_marker_type_int_or_float(
    mock_delta_table_exists, mock_spark, caplog
):
    manager = DbxMarker(delta_table_path="mock_path", spark=mock_spark)
    with pytest.raises(TypeError):
        manager.update_marker("test_pipeline", "random", "int")


@freeze_time("2023-01-01 00:00:00")
@patch("dbx_marker.manager.delta_table_exists", return_value=True)
def test_update_marker_exception(mock_delta_table_exists, mock_spark, caplog):
    manager = DbxMarker(delta_table_path="mock_path", spark=mock_spark)
    mock_spark.sql.side_effect = Exception("Test exception")
    with pytest.raises(MarkerUpdateError):
        manager.update_marker("test_pipeline", 1, "int")
    assert (
        "Failed to update marker for pipeline 'test_pipeline': Test exception"
        in caplog.text
    )
