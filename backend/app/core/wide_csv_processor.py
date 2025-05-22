"""
Processor for wide CSV files with many columns.

This module integrates DuckDB, SQLite metadata store, and vector search
to efficiently process and query CSV files with thousands of columns.
"""
import os
import uuid
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, BinaryIO
from datetime import datetime
from dotenv import load_dotenv

from .duckdb_processor import DuckDBProcessor
from .metadata_store import MetadataStore
from .vector_store import VectorStore, QdrantVectorStore, PineconeVectorStore, VECTOR_STORE_TYPE

# Load environment variables
load_dotenv()

class WideCsvProcessor:
    def __init__(self, storage_path="./data", chunk_size=1000, batch_size=500):
        """
        Initialize the wide CSV processor.
        
        Args:
            storage_path: Path to store data files
            chunk_size: Number of rows to process at a time
            batch_size: Number of columns to process at a time for vector indexing
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        # Initialize DuckDB and metadata store
        self.duckdb_processor = DuckDBProcessor(storage_path, chunk_size)
        self.metadata_store = MetadataStore(storage_path, batch_size)
        
        # Create vector store directory
        self.vector_store_path = self.storage_path / "vector_store"
        self.vector_store_path.mkdir(exist_ok=True)
        
        # Initialize vector store based on configuration
        self.vector_store_type = VECTOR_STORE_TYPE
        print(f"Using vector store type: {self.vector_store_type}")
        
        if self.vector_store_type == "pinecone":
            # Use Pinecone with OpenAI embeddings
            self.vector_store = PineconeVectorStore(batch_size=batch_size)
            print("Initialized Pinecone vector store with OpenAI embeddings")
        elif self.vector_store_type == "qdrant":
            # Use Qdrant with Sentence Transformers
            self.vector_store = QdrantVectorStore(batch_size=batch_size)
            print("Initialized Qdrant vector store with Sentence Transformers")
        else:
            # Use local vector store with Sentence Transformers
            self.vector_store = VectorStore(batch_size=batch_size)
            print("Initialized local vector store with Sentence Transformers")
    
    def process_csv_file(self, file_content: bytes, dataset_name: str, description: str = None) -> Dict[str, Any]:
        """
        Process a wide CSV file.
        
        Args:
            file_content: The content of the CSV file as bytes
            dataset_name: Name of the dataset
            description: Optional description of the dataset
            
        Returns:
            Dictionary containing dataset information
        """
        print(f"Starting to process wide CSV file: {dataset_name}")
        
        # Generate a unique ID for this dataset
        dataset_id = str(uuid.uuid4())
        
        try:
            # Step 1: Process the CSV file with DuckDB
            print("Step 1: Processing CSV with DuckDB...")
            table_name, row_count, column_metadata = self.duckdb_processor.process_csv_file(
                file_content, dataset_name
            )

            print(column_metadata)
            
            # Step 2: Store metadata
            print("Step 2: Storing metadata...")
            file_size = len(file_content)
            self.metadata_store.store_dataset_metadata(
                dataset_id=dataset_id,
                name=dataset_name,
                description=description or f"Dataset uploaded on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                table_name=table_name,
                column_metadata=column_metadata,
                row_count=row_count,
                file_size=file_size
            )
            
            # Step 3: Index columns for vector search
            print("Step 3: Indexing columns for vector search...")
            self.vector_store.index_columns(dataset_id, column_metadata["columns"])
            
            # Step 4: Save vector store (only for local vector store)
            if self.vector_store_type == "local":
                print("Step 4: Saving local vector store...")
                vector_store_file = self.vector_store_path / f"{dataset_id}.json"
                self.vector_store.save(str(vector_store_file))
            else:
                print("Step 4: Vector store data saved to external service")
            
            print(f"Successfully processed CSV file: {dataset_name}")
            
            # Return dataset information
            return {
                "id": dataset_id,
                "name": dataset_name,
                "description": description,
                "table_name": table_name,
                "column_count": len(column_metadata["columns"]),
                "row_count": row_count,
                "file_size": file_size
            }
            
        except Exception as e:
            print(f"Error processing CSV file: {str(e)}")
            raise ValueError(f"Failed to process CSV file: {str(e)}")
    
    def query_dataset(self, dataset_id: str, query_text: str, limit: int = 1000) -> Dict[str, Any]:
        """
        Query a dataset.
        
        Args:
            dataset_id: Dataset ID
            query_text: Query text (SQL or natural language)
            limit: Maximum number of rows to return
            
        Returns:
            Dictionary containing query results
        """
        # Get dataset information
        dataset = self.metadata_store.get_dataset(dataset_id)
        if not dataset:
            raise ValueError(f"Dataset not found: {dataset_id}")
        
        # Check if this is a SQL query
        if query_text.strip().upper().startswith("SELECT"):
            # Execute SQL query directly
            return {
                "type": "sql_query",
                "query": query_text,
                "results": self.duckdb_processor.query_table(dataset["table_name"], query_text, limit)
            }
        
        # For natural language queries, try to find relevant columns first
        relevant_columns = self.vector_store.search_columns(query_text, limit=5)
        
        # If we found relevant columns, construct a SQL query
        if relevant_columns:
            # Get the most relevant column
            top_column = relevant_columns[0]["column_name"]
            
            # Construct a simple SQL query
            if "count" in query_text.lower() or "how many" in query_text.lower():
                sql_query = f"SELECT COUNT(*) AS count FROM {dataset['table_name']}"
            elif "average" in query_text.lower() or "mean" in query_text.lower():
                sql_query = f"SELECT AVG({top_column}) AS average FROM {dataset['table_name']}"
            elif "maximum" in query_text.lower() or "max" in query_text.lower():
                sql_query = f"SELECT MAX({top_column}) AS maximum FROM {dataset['table_name']}"
            elif "minimum" in query_text.lower() or "min" in query_text.lower():
                sql_query = f"SELECT MIN({top_column}) AS minimum FROM {dataset['table_name']}"
            else:
                # Default to showing top rows with the relevant column
                sql_query = f"SELECT {top_column} FROM {dataset['table_name']} LIMIT {limit}"
            
            # Execute the SQL query
            results = self.duckdb_processor.query_table(dataset["table_name"], sql_query, limit)
            
            return {
                "type": "nl_query",
                "query": query_text,
                "sql_query": sql_query,
                "relevant_columns": relevant_columns,
                "results": results
            }
        
        # If we couldn't find relevant columns, return a sample of the data
        return {
            "type": "sample",
            "query": query_text,
            "message": "Could not determine relevant columns for your query. Here's a sample of the data:",
            "results": self.duckdb_processor.get_table_sample(dataset["table_name"], 5)
        }
    
    def get_column_recommendations(self, query_text: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get column recommendations based on a query.
        
        Args:
            query_text: Query text
            limit: Maximum number of recommendations to return
            
        Returns:
            List of column recommendations
        """
        return self.vector_store.search_columns(query_text, limit)
    
    def list_datasets(self, offset: int = 0, limit: int = 100, search: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all datasets.
        
        Args:
            offset: Offset for pagination
            limit: Maximum number of datasets to return
            search: Optional search term
            
        Returns:
            List of dataset information
        """
        return self.metadata_store.list_datasets(offset, limit, search)
    
    def get_dataset(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        """
        Get dataset information.
        
        Args:
            dataset_id: Dataset ID
            
        Returns:
            Dictionary containing dataset information, or None if not found
        """
        return self.metadata_store.get_dataset(dataset_id)
    
    def get_dataset_columns(self, dataset_id: str, offset: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get columns for a dataset with pagination.
        
        Args:
            dataset_id: Dataset ID
            offset: Offset for pagination
            limit: Maximum number of columns to return
            
        Returns:
            List of column information
        """
        return self.metadata_store.get_dataset_columns(dataset_id, offset, limit)
    
    def get_column_group(self, group_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a column group.
        
        Args:
            group_id: Group ID
            
        Returns:
            Dictionary containing group information, or None if not found
        """
        return self.metadata_store.get_column_group(group_id)
    
    def delete_dataset(self, dataset_id: str) -> bool:
        """
        Delete a dataset.
        
        Args:
            dataset_id: Dataset ID
            
        Returns:
            True if successful, False otherwise
        """
        # Get dataset information
        dataset = self.metadata_store.get_dataset(dataset_id)
        if not dataset:
            return False
        
        # Delete from metadata store
        self.metadata_store.delete_dataset(dataset_id)
        
        # Delete vector store data
        if self.vector_store_type == "local":
            # Delete local vector store file
            vector_store_file = self.vector_store_path / f"{dataset_id}.json"
            if vector_store_file.exists():
                vector_store_file.unlink()
        elif self.vector_store_type == "pinecone" and hasattr(self.vector_store, 'delete_dataset'):
            # Delete vectors from Pinecone
            self.vector_store.delete_dataset(dataset_id)
        
        # Delete Parquet file
        parquet_file = self.storage_path / f"{dataset['table_name']}.parquet"
        if parquet_file.exists():
            parquet_file.unlink()
        
        return True
