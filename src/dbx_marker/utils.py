from datetime import datetime
from typing import Union

from loguru import logger
from pyspark.errors import AnalysisException

from dbx_marker.exceptions import MarkerInvalidTypeError, MarkerParsingError


def delta_table_exists(spark, path: str) -> bool:
    """
    Check if a Delta table exists at the given path.

    :param spark: SparkSession instance
    :param path: Path to check for Delta table
    :return: True if table exists, False otherwise
    """
    try:
        _ = spark.read.format("delta").load(path).schema
        return True
    except AnalysisException:
        return False


def parse_marker_from_type(
    marker: str, marker_type: str, datetime_format: str = "%Y-%m-%d %H:%M:%S"
) -> Union[int, float, datetime]:

    parsed_marker: Union[int, float, datetime]

    try:
        if marker_type == "int":
            parsed_marker = int(marker)
        elif marker_type == "float":
            parsed_marker = float(marker)
        elif marker_type == "datetime":
            parsed_marker = datetime.strptime(marker, datetime_format)
        else:
            raise MarkerInvalidTypeError(f"Invalid marker type: {marker_type}")
    except MarkerInvalidTypeError as mite:
        logger.error(mite)
        raise mite
    except Exception as e:
        logger.error(f"Failed to parse marker: {e}")
        raise MarkerParsingError(f"Failed to parse marker: {e}") from e

    return parsed_marker
