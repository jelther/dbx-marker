from dbx_marker import DbxMarker, MarkerNotFoundError
import pytest

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
