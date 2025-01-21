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

# Create a marker manager
manager = DbxMarker(
    delta_table_path="/path/to/markers",
    spark=spark
)

# Update a marker (will upsert if it doesn't exist)
manager.update_marker("my_pipeline", "2024-01-21")

# Get the current marker
current_marker = manager.get_marker("my_pipeline")

# Delete a marker when needed
manager.delete_marker("my_pipeline")
```

## Usage

### Initialization

Create a `DbxMarkerManager` instance by specifying the Delta table path where markers will be stored:

```python
from dbx_marker import DbxMarker
from pyspark.sql import SparkSession

# Initialize SparkSession
spark = SparkSession.builder.getOrCreate()

manager = DbxMarker(
    delta_table_path="/path/to/markers",
    spark=spark  # Optional: will create new session if not provided
)
```

### Managing Markers

#### Update a Marker
```python
manager.update_marker("pipeline_name", "marker_value")
```

#### Get Current Marker
```python
current_value = manager.get_marker("pipeline_name")
```

#### Delete a Marker
```python
manager.delete_marker("pipeline_name")
```

### Error Handling

The library provides specific exceptions for different scenarios:

- `MarkerExistsError`: When trying to create a duplicate marker
- `MarkerNotFoundError`: When a requested marker doesn't exist
- `MarkerUpdateError`: When marker update fails
- `MarkerDeleteError`: When marker deletion fails

## Requirements

- Python >= 3.13
- PySpark >= 3.5.4
- Delta-Spark >= 3.3.0
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

