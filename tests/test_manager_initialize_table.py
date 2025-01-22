import logging
from unittest.mock import patch

import pytest

from dbx_marker import DbxMarker
from dbx_marker.exceptions import MarkerInitializationError
from dbx_marker.sqls import INITIALIZE_TABLE_SQL


@patch("dbx_marker.manager.delta_table_exists", return_value=False)
def test_initialize_table_doesnt_exist(mock_table_exists, mock_spark, caplog):
    manager = DbxMarker(delta_table_path="mock_path", spark=mock_spark)
    assert manager.delta_table_path == "mock_path"
    assert mock_spark.sql.call_count == 1
    mock_spark.sql.assert_called_with(
        INITIALIZE_TABLE_SQL.format(delta_table_path="mock_path")
    )

    # Verify log messages
    assert len(caplog.records) == 3
    assert caplog.records[0].message == "Checking if Delta table for markers exists."
    assert caplog.records[0].levelno == logging.DEBUG
    assert caplog.records[1].message == "Delta table does not exist. Creating it now."
    assert caplog.records[1].levelno == logging.INFO
    assert caplog.records[2].message == "Delta table initialized successfully."
    assert caplog.records[2].levelno == logging.INFO


@patch("dbx_marker.manager.delta_table_exists", return_value=True)
def test_initialize_table_that_exists(mock_table_exists, mock_spark, caplog):
    manager = DbxMarker(delta_table_path="mock_path", spark=mock_spark)
    assert manager.delta_table_path == "mock_path"
    assert mock_spark.sql.call_count == 0

    # Verify log messages
    assert len(caplog.records) == 2
    assert caplog.records[0].message == "Checking if Delta table for markers exists."
    assert caplog.records[0].levelno == logging.DEBUG
    assert caplog.records[1].message == "Delta table already exists."
    assert caplog.records[1].levelno == logging.DEBUG


@patch("dbx_marker.manager.delta_table_exists", return_value=False)
def test_initialize_table_raises_exception(mock_table_exists, mock_spark, caplog):
    manager = DbxMarker(delta_table_path="mock_path", spark=mock_spark)
    mock_spark.sql.side_effect = Exception("Test exception")
    with pytest.raises(MarkerInitializationError):
        manager._initialize_table()
    assert "Failed to initialize Delta table: Test exception" in caplog.text
