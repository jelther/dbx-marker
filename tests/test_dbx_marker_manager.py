import pytest
from dbx_marker.manager import DbxMarkerManager
from dbx_marker.exceptions import MarkerNotFoundError, MarkerExistsError



def test_initialize_table(mock_spark):
    manager = DbxMarkerManager(delta_table_path="mock_path", spark=mock_spark)
    assert manager.delta_table_path == "mock_path"

def test_get_marker_existing(mock_spark):
    manager = DbxMarkerManager(delta_table_path="mock_path", spark=mock_spark)
    mock_spark.sql.return_value.count.return_value = 1
    mock_spark.sql.return_value.first.return_value = {"value": "test_value"}
    value = manager.get_marker("test_pipeline")
    assert value == "test_value"

def test_get_marker_not_found(mock_spark):
    manager = DbxMarkerManager(delta_table_path="mock_path", spark=mock_spark)
    mock_spark.sql.return_value.count.return_value = 0
    with pytest.raises(MarkerNotFoundError):
        manager.get_marker("non_existent_pipeline")

def test_update_marker(mock_spark):
    manager = DbxMarkerManager(delta_table_path="mock_path", spark=mock_spark)
    mock_spark.sql.return_value.count.return_value = 0
    manager.update_marker("test_pipeline", "new_value")

def test_update_marker_exists(mock_spark):
    manager = DbxMarkerManager(delta_table_path="mock_path", spark=mock_spark)
    mock_spark.sql.return_value.count.return_value = 1
    with pytest.raises(MarkerExistsError):
        manager.update_marker("test_pipeline", "new_value")

def test_delete_marker(mock_spark):
    manager = DbxMarkerManager(delta_table_path="mock_path", spark=mock_spark)
    mock_spark.sql.return_value.count.return_value = 1
    manager.delete_marker("test_pipeline")

def test_delete_marker_not_found(mock_spark):
    manager = DbxMarkerManager(delta_table_path="mock_path", spark=mock_spark)
    mock_spark.sql.return_value.count.return_value = 0
    with pytest.raises(MarkerNotFoundError):
        manager.delete_marker("non_existent_pipeline")
