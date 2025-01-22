from dbx_marker import DbxMarker


def test_update_marker(mock_spark):
    manager = DbxMarker(delta_table_path="mock_path", spark=mock_spark)
    mock_spark.sql.return_value.first.return_value = {"value" : "test_value"}
    manager.update_marker("test_pipeline", "new_value")
