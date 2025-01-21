from pyspark.errors import AnalysisException


def delta_table_exists(spark, path: str) -> bool:
    try:
        _ = spark.read.format("delta").load(path).schema
    except AnalysisException as e:
        return False
    return True