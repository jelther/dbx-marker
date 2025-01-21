import pytest

from dbx_marker.exceptions import MarkerNotFoundError
from dbx_marker.manager import DbxMarker


def test_initialize_table(mock_spark):
    manager = DbxMarker(delta_table_path="mock_path", spark=mock_spark)
    assert manager.delta_table_path == "mock_path"

def test_get_marker_existing(mock_spark):
    manager = DbxMarker(delta_table_path="mock_path", spark=mock_spark)
    mock_spark.sql.return_value.first.return_value = {"value": "test_value"}
    value = manager.get_marker("test_pipeline")
    assert value == "test_value"

def test_get_marker_not_found(mock_spark):
    manager = DbxMarker(delta_table_path="mock_path", spark=mock_spark)
    mock_spark.sql.return_value.first.return_value = None
    with pytest.raises(MarkerNotFoundError):
        manager.get_marker("non_existent_pipeline")

def test_update_marker(mock_spark):
    manager = DbxMarker(delta_table_path="mock_path", spark=mock_spark)
    mock_spark.sql.return_value.first.return_value = {"value" : "test_value"}
    manager.update_marker("test_pipeline", "new_value")

def test_delete_marker(mock_spark):
    manager = DbxMarker(delta_table_path="mock_path", spark=mock_spark)
    mock_spark.sql.return_value.first.return_value = {"value" : "test_value"}
    manager.delete_marker("test_pipeline")

def test_delete_marker_not_found(mock_spark):
    manager = DbxMarker(delta_table_path="mock_path", spark=mock_spark)
    mock_spark.sql.return_value.first.return_value = None
    with pytest.raises(MarkerNotFoundError):
        manager.delete_marker("non_existent_pipeline")
