import pytest

from dbx_marker import DbxMarker, MarkerNotFoundError


def test_delete_marker(mock_spark):
    manager = DbxMarker(delta_table_path="mock_path", spark=mock_spark)
    mock_spark.sql.return_value.first.return_value = {"value" : "test_value"}
    manager.delete_marker("test_pipeline")

def test_delete_marker_not_found(mock_spark):
    manager = DbxMarker(delta_table_path="mock_path", spark=mock_spark)
    mock_spark.sql.return_value.first.return_value = None
    with pytest.raises(MarkerNotFoundError):
        manager.delete_marker("non_existent_pipeline")
