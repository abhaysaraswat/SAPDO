# Data Directory

This directory is used to store data files for the SAPDO application, including:

- DuckDB database files
- Parquet files for wide CSV datasets
- SQLite metadata store
- Vector store files

## Wide CSV Processor

The SAPDO application now includes support for processing CSV files with thousands of columns, which exceeds the column limit of PostgreSQL/Supabase (1,600 columns). The wide CSV processor uses:

- **DuckDB**: A high-performance analytical database that can efficiently handle wide tables
- **Parquet**: A columnar storage format that provides efficient storage and retrieval
- **SQLite**: For storing metadata about datasets and columns
- **Vector Store**: For semantic search of columns

### How It Works

1. When a CSV file is uploaded, the system checks the number of columns:
   - If the file has fewer than 1,600 columns, it uses the standard Supabase processing
   - If the file has more than 1,600 columns, it uses the wide CSV processor

2. The wide CSV processor:
   - Processes the CSV file in chunks to avoid memory issues
   - Converts the data to Parquet format for efficient storage
   - Stores metadata about the dataset and columns in SQLite
   - Creates embeddings for columns to enable semantic search

3. The data can then be queried using:
   - SQL queries via DuckDB
   - Natural language queries via the vector store

### Example Dataset

The `large.csv` file in this directory is an example dataset with 10,174 columns and 47,341 data rows. This file is used to test the wide CSV processor.

### Directory Structure

After processing wide CSV files, the following files will be created in this directory:

- `sapdo.duckdb`: The DuckDB database file
- `metadata.sqlite`: The SQLite metadata store
- `vector_store/`: Directory containing vector store files
- `*.parquet`: Parquet files for each dataset

## Usage

The wide CSV processor is automatically used when a CSV file with more than 1,600 columns is uploaded through the SAPDO interface. No special configuration is required.

For programmatic access, you can use the `WideCsvProcessor` class:

```python
from app.core.wide_csv_processor import WideCsvProcessor

# Initialize the processor
processor = WideCsvProcessor()

# Process a CSV file
with open('path/to/file.csv', 'rb') as f:
    file_content = f.read()
    result = processor.process_csv_file(file_content, 'Dataset Name')

# Query a dataset
query_result = processor.query_dataset(dataset_id, 'SELECT * FROM table_name LIMIT 10')

# Get column recommendations
recommendations = processor.get_column_recommendations('Find columns related to temperature')
