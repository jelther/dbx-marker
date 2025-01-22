# dbx-marker

Easily manage incremental progress using watermarks in your Databricks data pipelines.

## Overview

dbx-marker is a Python library that helps you manage watermarks in your Databricks data pipelines using Delta tables.

It provides a simple interface to track and manage pipeline progress, making it easier to implement incremental processing and resume operations.

## Features

- Simple API for managing pipeline watermarks
- Persistent storage using Delta tables
- Thread-safe operations
- Comprehensive error handling
- Built for Databricks environments

## Installation

Install using pip:

```bash
pip install dbx-marker
```

## Quick Start

```python
from dbx_marker import DbxMarker
from pyspark.sql import SparkSession

# Initialize SparkSession
spark = SparkSession.builder.getOrCreate()

# Create a marker instance
marker = DbxMarker(
    delta_table_path="/path/to/markers",
    spark=spark,
    datetime_format="%Y-%m-%d %H:%M:%S"  # Optional: defaults to "%Y-%m-%d %H:%M:%S"
)

# Update markers with different types
from datetime import datetime

# Integer marker
marker.update_marker("pipeline_int", 42, "int")

# Float marker
marker.update_marker("pipeline_float", 42.5, "float")

# Datetime marker
marker.update_marker("pipeline_date", datetime.now(), "datetime")

# Get the current marker (returns the appropriate type)
current_marker = marker.get_marker("pipeline_name")

# Delete a marker when needed
marker.delete_marker("pipeline_name")
```

## Usage

### Initialization

Create a `DbxMarker` instance by specifying the Delta table path where markers will be stored:

```python
from dbx_marker import DbxMarker
from pyspark.sql import SparkSession

# Initialize SparkSession
spark = SparkSession.builder.getOrCreate()

marker = DbxMarker(
    delta_table_path="/path/to/markers",
    spark=spark,  # Optional: will create new session if not provided
    datetime_format="%Y-%m-%d %H:%M:%S"  # Optional: customize datetime format
)
```

### Managing Markers

#### Update a Marker
```python
# Supported types: int, float, datetime
marker.update_marker("pipeline_name", value, marker_type)
```

#### Get Current Marker
```python
# Returns int, float, or datetime based on the marker's type
current_value = marker.get_marker("pipeline_name")
```

#### Delete a Marker
```python
marker.delete_marker("pipeline_name")
```

### Marker Types

The library supports three types of markers:
- `int`: Integer values
- `float`: Floating point values
- `datetime`: Datetime values

When updating a marker, you must specify both the value and its type. The type must match the value:
- For `int`: Use integer values
- For `float`: Use float values
- For `datetime`: Use datetime objects

### Error Handling

The library provides specific exceptions for different scenarios:

- `MarkerInitializationError`: When table creation fails
- `MarkerNotFoundError`: When a requested marker doesn't exist
- `MarkerUpdateError`: When marker update fails
- `MarkerDeleteError`: When marker deletion fails
- `MarkerParsingError`: When marker value cannot be parsed
- `MarkerInvalidTypeError`: When an invalid marker type is specified

## Requirements

- Databricks
- Python >= 3.13
- Loguru >= 0.7.3

## Development

1. Clone the repository
2. Install development dependencies:
```bash
pdm install -G dev
```

3. Run tests:
```bash
pdm run test
```

4. Run all checks:
```bash
pdm run all-checks
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

