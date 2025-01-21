from pyspark.errors import AnalysisException


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
