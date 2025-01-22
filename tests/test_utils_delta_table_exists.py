from unittest.mock import MagicMock
from pyspark.errors import AnalysisException
from dbx_marker.utils import delta_table_exists


def test_delta_table_exists(mock_spark):
    mock_format = MagicMock()
    mock_spark.read.format.return_value = mock_format
    
    mock_format.load.side_effect = AnalysisException("Table not found")
    assert not delta_table_exists(mock_spark, "mock_path")
    
    mock_df = MagicMock()
    mock_format.load.side_effect = None
    mock_format.load.return_value = mock_df
    mock_df.schema = ["some_schema"]  # Mocking non-empty schema
    assert delta_table_exists(mock_spark, "mock_path")
    
    mock_spark.read.format.assert_called_with("delta")
