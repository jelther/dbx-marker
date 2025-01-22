from datetime import datetime
from unittest.mock import patch

import pytest

from dbx_marker.config import config
from dbx_marker.exceptions import MarkerInvalidTypeError, MarkerParsingError
from dbx_marker.utils import parse_marker_from_type


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


def test_parse_marker_from_type_raises_exception_int():
    with patch("dbx_marker.utils.int") as mock_int:
        mock_int.side_effect = ValueError("test exception")
        with pytest.raises(MarkerParsingError):
            parse_marker_from_type("1", "int", config.DATETIME_FORMAT)


def test_parse_marker_from_type_raises_exception_float():
    with patch("dbx_marker.utils.float") as mock_float:
        mock_float.side_effect = ValueError("test exception")
        with pytest.raises(MarkerParsingError):
            parse_marker_from_type("1.0", "float", config.DATETIME_FORMAT)


def test_parse_marker_from_type_raises_exception_datetime():
    with patch("dbx_marker.utils.datetime") as mock_datetime:
        mock_datetime.strptime.side_effect = ValueError("test exception")
        with pytest.raises(MarkerParsingError):
            parse_marker_from_type(
                "2023-10-01 00:00:00", "datetime", config.DATETIME_FORMAT
            )
