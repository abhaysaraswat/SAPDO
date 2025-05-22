# Wide CSV Processor

This document provides detailed information about the Wide CSV Processor, which enables SAPDO to handle CSV files with thousands of columns.

## Overview

The Wide CSV Processor is designed to overcome the column limit of PostgreSQL/Supabase (1,600 columns) by using DuckDB, a high-performance analytical database that can efficiently handle wide tables. It processes CSV files in chunks to avoid memory issues, converts the data to Parquet format for efficient storage, and provides semantic search capabilities for columns.

## Architecture

The Wide CSV Processor consists of four main components:

1. **DuckDB Processor**: Handles the processing of CSV files and conversion to Parquet format.
2. **Metadata Store**: Stores metadata about datasets and columns in SQLite.
3. **Vector Store**: Provides semantic search capabilities for columns.
4. **Wide CSV Processor**: Integrates the above components and provides a unified API.

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      Wide CSV Processor                          │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────┬─────────────────────────────┬─────────────────┐
│  DuckDB         │      Metadata Store         │  Vector         │
│  Processor      │      (SQLite)               │  Store          │
└─────────────────┴─────────────────────────────┴─────────────────┘
        │                      │                        │
        ▼                      ▼                        ▼
┌─────────────────┐ ┌─────────────────────────┐ ┌─────────────────┐
│  Parquet Files  │ │  SQLite Database        │ │  Vector         │
│                 │ │                         │ │  Embeddings     │
└─────────────────┘ └─────────────────────────┘ └─────────────────┘
```

## Data Flow

1. **CSV Upload**:
   - User uploads a CSV file
   - System checks the number of columns
   - If > 1,600 columns, the Wide CSV Processor is used

2. **Processing**:
   - CSV file is read in chunks to avoid memory issues
   - Each chunk is processed and converted to Parquet format
   - Metadata about the dataset and columns is stored in SQLite
   - Column embeddings are generated for semantic search

3. **Querying**:
   - User can query the dataset using SQL or natural language
   - SQL queries are executed directly against DuckDB
   - Natural language queries use the vector store to find relevant columns

## Components

### DuckDB Processor

The DuckDB Processor (`DuckDBProcessor` class) is responsible for:

- Processing CSV files in chunks
- Converting data to Parquet format
- Creating DuckDB views for querying
- Executing SQL queries against the data

Key methods:
- `process_csv_file`: Process a CSV file and store it as Parquet
- `query_table`: Execute a SQL query against a table
- `get_table_columns`: Get column information for a table
- `get_table_sample`: Get a sample of data from a table

### Metadata Store

The Metadata Store (`MetadataStore` class) is responsible for:

- Storing metadata about datasets and columns in SQLite
- Creating automatic column groups for wide datasets
- Providing pagination for column access

Key methods:
- `store_dataset_metadata`: Store dataset and column metadata
- `get_dataset`: Get dataset metadata
- `get_dataset_columns`: Get columns for a dataset with pagination
- `get_column_group`: Get a column group
- `list_datasets`: List all datasets with pagination and search

### Vector Store

The Wide CSV Processor supports multiple vector store implementations:

### Local Vector Store

The Local Vector Store (`VectorStore` class) is responsible for:

- Generating embeddings for columns using Sentence Transformers
- Providing semantic search capabilities
- Storing and loading embeddings to/from disk

Key methods:
- `index_columns`: Index column metadata for semantic search
- `search_columns`: Search for columns semantically related to a query
- `save`: Save the vector store to disk
- `load`: Load the vector store from disk

### Pinecone Vector Store

The Pinecone Vector Store (`PineconeVectorStore` class) is responsible for:

- Generating embeddings for columns using OpenAI's embedding models
- Storing embeddings in Pinecone
- Providing semantic search capabilities via Pinecone

Key methods:
- `index_columns`: Index column metadata for semantic search
- `search_columns`: Search for columns semantically related to a query
- `delete_dataset`: Delete all vectors for a dataset

### Qdrant Vector Store

The Qdrant Vector Store (`QdrantVectorStore` class) is responsible for:

- Generating embeddings for columns using Sentence Transformers
- Storing embeddings in Qdrant
- Providing semantic search capabilities via Qdrant

Key methods:
- `index_columns`: Index column metadata for semantic search
- `search_columns`: Search for columns semantically related to a query

### Wide CSV Processor

The Wide CSV Processor (`WideCsvProcessor` class) integrates the above components and provides a unified API for:

- Processing CSV files
- Querying datasets
- Getting column recommendations
- Managing datasets

Key methods:
- `process_csv_file`: Process a wide CSV file
- `query_dataset`: Query a dataset
- `get_column_recommendations`: Get column recommendations based on a query
- `list_datasets`: List all datasets
- `get_dataset`: Get dataset information
- `get_dataset_columns`: Get columns for a dataset with pagination
- `delete_dataset`: Delete a dataset

## Performance Considerations

The Wide CSV Processor is designed to handle large CSV files with thousands of columns efficiently. Here are some performance considerations:

- **Memory Usage**: The processor uses chunked processing to avoid loading the entire CSV file into memory at once. This allows it to handle files that would otherwise cause out-of-memory errors.

- **Storage Efficiency**: Parquet format provides efficient columnar storage, which can reduce storage requirements by 3-5x compared to CSV files.

- **Query Performance**: DuckDB is optimized for analytical queries and can efficiently query specific columns without loading the entire dataset into memory.

- **Batch Processing**: Column metadata and embeddings are processed in batches to avoid memory issues.

## Usage Examples

### Processing a CSV File

```python
from app.core.wide_csv_processor import WideCsvProcessor

# Initialize the processor
processor = WideCsvProcessor()

# Process a CSV file
with open('path/to/file.csv', 'rb') as f:
    file_content = f.read()
    result = processor.process_csv_file(
        file_content=file_content,
        dataset_name='My Dataset',
        description='A dataset with many columns'
    )

# Print the result
print(f"Dataset ID: {result['id']}")
print(f"Table name: {result['table_name']}")
print(f"Column count: {result['column_count']}")
print(f"Row count: {result['row_count']}")
```

### Querying a Dataset

```python
# Query a dataset using SQL
query_result = processor.query_dataset(
    dataset_id='123e4567-e89b-12d3-a456-426614174000',
    query_text='SELECT * FROM dataset_table LIMIT 10'
)

# Query a dataset using natural language
query_result = processor.query_dataset(
    dataset_id='123e4567-e89b-12d3-a456-426614174000',
    query_text='Show me the first 10 rows'
)

# Print the results
print(f"Query type: {query_result['type']}")
print(f"Results: {query_result['results']}")
```

### Getting Column Recommendations

```python
# Get column recommendations
recommendations = processor.get_column_recommendations(
    query_text='Find columns related to temperature'
)

# Print the recommendations
for rec in recommendations:
    print(f"Column: {rec['column_name']}, Score: {rec['score']}")
```

## Integration with Function Calling

The Wide CSV Processor is integrated with the function calling system to allow the AI to interact with wide datasets. The following functions are available:

- `check_dataset_storage`: Check if a dataset is stored in Supabase or DuckDB
- `get_column_recommendations`: Get column recommendations based on a query
- `query_duckdb_dataset`: Run a SQL query against a DuckDB dataset

Example usage:

```python
from app.core.function_calling import (
    check_dataset_storage,
    get_column_recommendations,
    query_duckdb_dataset
)

# Check if a dataset is stored in DuckDB
storage_result = check_dataset_storage({"dataset_id": "123e4567-e89b-12d3-a456-426614174000"})
storage_info = json.loads(storage_result)
print(f"Storage type: {storage_info['storage_type']}")

# Get column recommendations
recommendations_result = get_column_recommendations({"query_text": "Find columns related to temperature"})
recommendations = json.loads(recommendations_result)
for rec in recommendations:
    print(f"Column: {rec['column_name']}, Score: {rec['score']}")

# Query a DuckDB dataset
query_result_json = query_duckdb_dataset({
    "dataset_id": "123e4567-e89b-12d3-a456-426614174000",
    "query_text": "SELECT * FROM dataset_table LIMIT 10"
})
query_result = json.loads(query_result_json)
print(f"Results: {query_result['results']}")
```

## API Endpoints

The Wide CSV Processor is integrated with the SAPDO API through the following endpoints:

- `POST /datasets/upload`: Upload a CSV file
- `GET /datasets/{dataset_id}/preview`: Get a preview of a dataset
- `GET /datasets/{dataset_id}`: Get dataset information
- `GET /datasets`: List all datasets
- `DELETE /datasets/{dataset_id}`: Delete a dataset

These endpoints automatically detect if a dataset is stored in Supabase or DuckDB and use the appropriate processor.

## Configuration

The vector store implementation can be configured using environment variables:

```
# Vector store configuration
VECTOR_STORE_TYPE=pinecone  # Options: local, qdrant, pinecone

# Pinecone configuration (required if VECTOR_STORE_TYPE=pinecone)
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=us-east-1-aws  # Format: region-cloud (e.g., us-east-1-aws, us-west1-gcp)
OPENAI_API_KEY=your_openai_api_key
```

## Comparison of Vector Store Implementations

| Feature | Local Vector Store | Pinecone Vector Store | Qdrant Vector Store |
|---------|-------------------|----------------------|---------------------|
| Embedding Model | Sentence Transformers | OpenAI | Sentence Transformers |
| Storage | Local JSON files | Pinecone cloud service | Qdrant service |
| Scalability | Low (memory-bound) | High | Medium-High |
| Setup Complexity | Low | Medium | Medium |
| Cost | Free | Pay-as-you-go | Free (self-hosted) or pay-as-you-go |
| Performance | Good for small datasets | Excellent for large datasets | Good for medium datasets |
| Persistence | Manual save/load | Automatic | Automatic |

## Example Usage

### Using Pinecone with OpenAI

```python
# Initialize the vector store
vector_store = PineconeVectorStore(
    index_name="column-metadata",
    namespace="default",
    embedding_model="text-embedding-3-small",
    batch_size=100
)

# Index columns
vector_store.index_columns(dataset_id, columns)

# Search for columns
results = vector_store.search_columns("temperature data", limit=5)
```

Note: The implementation uses the latest Pinecone Python client (v3.0+) which has a different API than previous versions. The key differences are:

1. Initialization:
   ```python
   # Old API (v2.x)
   import pinecone
   pinecone.init(api_key="your-api-key", environment="your-environment")
   index = pinecone.Index("your-index")
   
   # New API (v3.x)
   from pinecone import Pinecone, ServerlessSpec
   pc = Pinecone(api_key="your-api-key")
   index = pc.Index("your-index")
   ```

2. Index creation:
   ```python
   # Old API (v2.x)
   pinecone.create_index(name="your-index", dimension=1536, metric="cosine")
   
   # New API (v3.x)
   pc.create_index(
       name="your-index",
       dimension=1536,
       metric="cosine",
       spec=ServerlessSpec(cloud="aws", region="us-east-1")
   )
   ```

The implementation handles these differences transparently.

### Important Notes on Pinecone Integration

#### Pinecone Environment Format

When using Pinecone, the `PINECONE_ENVIRONMENT` variable should follow this format:

- For AWS: `region-aws` (e.g., `us-east-1-aws`, `us-west-2-aws`, `eu-west-1-aws`)
- For GCP: `region-gcp` (e.g., `us-west1-gcp`, `us-east1-gcp`, `eu-west1-gcp`)

Valid AWS regions include:
- us-east-1
- us-west-2
- eu-west-1
- ap-southeast-1

Valid GCP regions include:
- us-central1
- us-east1
- us-east4
- us-west1
- us-west4
- northamerica-northeast1
- southamerica-east1
- eu-west1
- eu-west2
- eu-west3
- eu-west4
- eu-central1
- eu-north1
- asia-northeast1
- asia-east1
- asia-southeast1
- australia-southeast1

The implementation will attempt to parse the environment string and convert it to the correct format for Pinecone's ServerlessSpec.

#### Pinecone Vector IDs

Pinecone requires vector IDs to be ASCII-compatible. The implementation automatically sanitizes column names and dataset IDs to ensure they are compatible with Pinecone's requirements:

- Non-ASCII characters are removed
- Special characters are replaced with underscores
- Long names are truncated to a reasonable length
- Empty names are replaced with default values

This ensures that even when working with datasets that have column names containing special characters (like ®, ™, etc.) or very long names (like survey questions), the system will still work correctly with Pinecone.

See the `backend/examples/pinecone_openai_example.py` file for a complete example.

## Future Improvements

Potential future improvements to the Wide CSV Processor include:

- **Distributed Processing**: Support for distributed processing of very large CSV files
- **Incremental Updates**: Support for incremental updates to datasets
- **Advanced Querying**: Support for more advanced querying capabilities, such as joins and aggregations
- **Visualization**: Integration with visualization tools to visualize wide datasets
- **Export**: Support for exporting datasets to various formats
- **Caching**: Caching of query results for improved performance
- **Security**: Fine-grained access control for datasets and columns
- **Additional Vector Stores**: Support for more vector stores like Weaviate, Milvus, etc.
- **Custom Embedding Models**: Support for custom embedding models

## Conclusion

The Wide CSV Processor enables SAPDO to handle CSV files with thousands of columns, which would otherwise be impossible with PostgreSQL/Supabase alone. It provides efficient storage, querying, and semantic search capabilities for wide datasets, making it a powerful tool for data analysis.
