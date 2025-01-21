from datetime import datetime
from typing import Optional

from loguru import logger
from pyspark.sql import SparkSession

from dbx_marker.exceptions import (
    MarkerExistsError,
    MarkerNotFoundError,
    MarkerUpdateError,
    MarkerDeleteError,
)
from dbx_marker.sqls import (
    INITIALIZE_TABLE_SQL,
    GET_MARKER_SQL,
    UPDATE_MARKER_SQL,
    DELETE_MARKER_SQL,
)
from dbx_marker.utils import delta_table_exists


class DbxMarkerManager:
    def __init__(self, delta_table_path: str, spark: Optional[SparkSession] = None):
        """
        Initialize the manager with the path to the Delta table that stores markers or checkpoints.

        :param delta_table_path: Delta table location for tracking metadata.
        :param spark: Optional SparkSession instance, will create new one if not provided
        """
        self.delta_table_path = delta_table_path
        self.spark = spark or SparkSession.builder.getOrCreate()
        self._initialize_table()

    def _initialize_table(self):
        """
        Ensure the Delta table for markers exists.
        """
        logger.debug("Initializing Delta table for markers/checkpoints.")
        try:

            if not delta_table_exists(self.spark, self.delta_table_path):
                logger.debug("Delta table does not exist. Creating it now.")

            self.spark.sql(
                INITIALIZE_TABLE_SQL.format(delta_table_path=self.delta_table_path)
            )
            logger.debug("Delta table initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Delta table: {e}")
            raise MarkerUpdateError(f"Could not initialize the Delta table: {e}") from e

    def get_marker(self, pipeline_name: str) -> Optional[str]:
        """
        Get the current marker or checkpoint value for a given pipeline.

        :param pipeline_name: Unique identifier for the pipeline.
        :return: The current marker value, or None if no marker is found.
        """
        sql_statement: str = GET_MARKER_SQL.format(
            delta_table_path=self.delta_table_path, pipeline_name=pipeline_name
        )
        try:
            df = self.spark.sql(sql_statement)
            if df.count() == 0:
                logger.debug(f"No marker found for pipeline {pipeline_name}.")
                raise MarkerNotFoundError(
                    f"No marker found for pipeline '{pipeline_name}'."
                )
        except MarkerNotFoundError as mnfe:
            logger.error(mnfe)
            raise mnfe
        except Exception as e:
            logger.error(f"Failed to retrieve marker for pipeline {pipeline_name}: {e}")
            raise MarkerNotFoundError(
                f"An error occurred while retrieving marker for pipeline '{pipeline_name}': {e}"
            ) from e

        return df.first()["value"]

    def update_marker(self, pipeline_name: str, value: str) -> None:
        """
        Update or insert the marker for a pipeline.

        :param pipeline_name: Unique identifier for the pipeline.
        :param value: New marker or checkpoint value.
        """
        try:
            existing_marker = self.get_marker(pipeline_name)
            if existing_marker:
                raise MarkerExistsError(
                    f"Marker for pipeline '{pipeline_name}' already exists: {existing_marker}. Cannot insert a duplicate."
                )
        except MarkerNotFoundError:
            pass

        now: datetime = datetime.now()
        sql_statement: str = UPDATE_MARKER_SQL.format(
            delta_table_path=self.delta_table_path,
            pipeline_name=pipeline_name,
            value=value,
            now=now,
        )
        try:
            self.spark.sql(sql_statement)
            logger.debug(f"Updated marker for pipeline '{pipeline_name}' to '{value}'.")
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
