from datetime import datetime
from typing import Optional, Union

from loguru import logger
from pyspark.sql import SparkSession

from dbx_marker.config import config
from dbx_marker.exceptions import (
    MarkerDeleteError,
    MarkerInitializationError,
    MarkerInvalidTypeError,
    MarkerNotFoundError,
    MarkerUpdateError,
)
from dbx_marker.sqls import (
    DELETE_MARKER_SQL,
    GET_MARKER_SQL,
    INITIALIZE_TABLE_SQL,
    UPDATE_MARKER_SQL,
)
from dbx_marker.utils import delta_table_exists, parse_marker_from_type


class DbxMarker:
    def __init__(
        self,
        delta_table_path: str,
        spark: Optional[SparkSession] = None,
        datetime_format: str = config.DATETIME_FORMAT,
    ):
        """
        Initialize the manager with the path to the Delta table that stores markers.

        :param delta_table_path: Delta table location for tracking metadata.
        :param spark: Optional SparkSession instance, will create new one if not provided
        """
        self.delta_table_path = delta_table_path
        self.datetime_format = datetime_format
        self.spark = spark or SparkSession.builder.getOrCreate()
        self._initialize_table()

    def _initialize_table(self):
        """
        Ensure the Delta table for markers exists.
        """
        logger.debug("Checking if Delta table for markers exists.")
        try:

            if not delta_table_exists(self.spark, self.delta_table_path):
                logger.info("Delta table does not exist. Creating it now.")

                self.spark.sql(
                    INITIALIZE_TABLE_SQL.format(delta_table_path=self.delta_table_path)
                )
                logger.info("Delta table initialized successfully.")
            else:
                logger.debug("Delta table already exists.")
        except Exception as e:
            logger.error(f"Failed to initialize Delta table: {e}")
            raise MarkerInitializationError(
                f"Could not initialize the Delta table: {e}"
            ) from e

    def get_marker(self, pipeline_name: str) -> Union[int, float, datetime]:
        """
        Get the current marker value for a given pipeline.

        :param pipeline_name: Unique identifier for the pipeline.
        :return: The current marker value, or None if no marker is found.
        """
        sql_statement: str = GET_MARKER_SQL.format(
            delta_table_path=self.delta_table_path, pipeline_name=pipeline_name
        )
        try:
            df = self.spark.sql(sql_statement)
            row = df.first()
            if row is None:
                raise MarkerNotFoundError(
                    f"No marker found for pipeline '{pipeline_name}'."
                )
            return parse_marker_from_type(
                row["value"], row["marker_type"], self.datetime_format
            )
        except MarkerNotFoundError as mnfe:
            logger.error(mnfe)
            raise mnfe
        except Exception as e:
            logger.error(f"Failed to retrieve marker for pipeline {pipeline_name}: {e}")
            raise MarkerNotFoundError(
                f"An error occurred while retrieving marker for pipeline '{pipeline_name}': {e}"
            ) from e

    def update_marker(
        self, pipeline_name: str, value: Union[int, float, datetime], marker_type: str
    ) -> None:
        """
        Update or insert the marker for a pipeline.

        :param pipeline_name: Unique identifier for the pipeline.
        :param value: New marker value.
        :param marker_type: Type of the marker value (int, float, datetime).
        """
        now: datetime = datetime.now()

        # Ensure the marker type is valid
        if marker_type not in config.ALLOWED_MARKER_TYPES:
            raise MarkerInvalidTypeError(
                f"Invalid marker type: {marker_type}. Allowed marker types: {config.ALLOWED_MARKER_TYPES}"
            )

        if marker_type == "datetime":
            if not isinstance(value, datetime):
                raise TypeError(
                    f"Expected `value` to be a datetime when `marker_type` is `datetime`, got {type(value).__name__}"
                )
            value_parsed = value.strftime(self.datetime_format)
        else:
            if not isinstance(value, (int, float)):
                raise TypeError(
                    f"Expected `value` to be int or float when `marker_type` is `{marker_type}`, got {type(value).__name__}"
                )
            value_parsed = str(value)

        sql_statement: str = UPDATE_MARKER_SQL.format(
            delta_table_path=self.delta_table_path,
            pipeline_name=pipeline_name,
            value=value_parsed,
            marker_type=marker_type,
            now=now,
        )

        try:
            self.spark.sql(sql_statement)
            logger.info(
                f"Updated marker for pipeline '{pipeline_name}' to '{value}' ({marker_type})."
            )
        except Exception as e:
            logger.error(f"Failed to update marker for pipeline '{pipeline_name}': {e}")
            raise MarkerUpdateError(
                f"Failed to update marker for pipeline '{pipeline_name}': {e}"
            ) from e

    def delete_marker(self, pipeline_name: str) -> None:
        """
        Delete a marker entry for a pipeline.

        :param pipeline_name: Unique identifier for the pipeline.
        """
        try:
            self.get_marker(pipeline_name)
        except MarkerNotFoundError:
            raise MarkerNotFoundError(
                f"Cannot delete marker: Marker for pipeline '{pipeline_name}' does not exist."
            )

        sql_statement: str = DELETE_MARKER_SQL.format(
            delta_table_path=self.delta_table_path, pipeline_name=pipeline_name
        )

        try:
            self.spark.sql(sql_statement)
            logger.debug(f"Deleted marker for pipeline '{pipeline_name}'.")
        except Exception as e:
            logger.error(f"Failed to delete marker for pipeline '{pipeline_name}': {e}")
            raise MarkerDeleteError(
                f"Failed to delete marker for pipeline '{pipeline_name}': {e}"
            ) from e
