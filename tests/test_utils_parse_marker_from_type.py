from datetime import datetime
from unittest.mock import MagicMock

import pytest
from pyspark.errors import AnalysisException

from dbx_marker.config import config
from dbx_marker.exceptions import MarkerInvalidTypeError
from dbx_marker.utils import delta_table_exists, parse_marker_from_type


@pytest.mark.parametrize(
    "marker, marker_type, expected",
    [
        ("2023-10-01 00:00:00", "datetime", datetime(2023, 10, 1)),
        ("1", "int", 1),
        ("1.0", "float", 1.0),
    ],
)
def test_parse_marker_from_type_valid(marker, marker_type, expected):
    assert (
        parse_marker_from_type(marker, marker_type, config.DATETIME_FORMAT) == expected
    )


def test_parse_marker_from_type_invalid():
    with pytest.raises(MarkerInvalidTypeError):
        parse_marker_from_type("invalid", "invalid", config.DATETIME_FORMAT)
