"""
DuckDB processor for handling large CSV files with many columns.
"""
import duckdb
import pandas as pd
import io
import uuid
import os
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime

class DuckDBProcessor:
    def __init__(self, storage_path="./data", chunk_size=1000):
        """
        Initialize the DuckDB processor.
        
        Args:
            storage_path: Path to store DuckDB database and Parquet files
            chunk_size: Number of rows to process at a time
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self.db_path = self.storage_path / "sapdo.duckdb"
        self.conn = duckdb.connect(str(self.db_path))
        self.chunk_size = chunk_size
        
    def process_csv_file(self, file_content: bytes, dataset_name: str) -> Tuple[str, int, Dict[str, Any]]:
        """
        Process a wide CSV file in chunks and store it as Parquet.
        
        Args:
            file_content: The content of the CSV file as bytes
            dataset_name: The name of the dataset
            
        Returns:
            Tuple containing:
            - table_name: Name of the created table
            - row_count: Number of rows processed
            - column_metadata: Metadata about the columns
        """
        # Create a unique table name
        clean_name = ''.join(c if c.isalnum() else '_' for c in dataset_name.lower())
        table_name = f"dataset_{clean_name}_{uuid.uuid4().hex[:8]}"
        parquet_path = self.storage_path / f"{table_name}.parquet"
        
        # Process in chunks using pandas
        total_rows = 0
        column_metadata = None
        
        # Use TextFileReader to process in chunks
        csv_file = io.BytesIO(file_content)
        
        print(f"Starting to process CSV file for dataset: {dataset_name}")
        
        # First, read the header to get column names
        try:
            header_df = pd.read_csv(csv_file, nrows=1)
            column_names = header_df.columns.tolist()
            print(f"Found {len(column_names)} columns in the CSV file")
        except Exception as e:
            print(f"Error reading CSV header: {str(e)}")
            raise ValueError(f"Failed to read CSV header: {str(e)}")
        
        # Reset file pointer
        csv_file.seek(0)
        
        # Process in chunks
        try:
            chunks = pd.read_csv(
                csv_file, 
                chunksize=self.chunk_size,
                low_memory=True,
                dtype='object'  # Start with object type for all columns
            )
            
            # Process first chunk to determine column types
            first_chunk = next(chunks, None)
            if first_chunk is None:
                raise ValueError("CSV file appears to be empty")
                
            print(f"Processing first chunk with {len(first_chunk)} rows")
            
            # Infer better dtypes after seeing some data
            dtypes = {}
            for col in first_chunk.columns:
                # Try to convert to more efficient types
                try:
                    if pd.api.types.is_numeric_dtype(first_chunk[col]):
                        if first_chunk[col].apply(lambda x: pd.isna(x) or (x == int(x) if pd.notnull(x) else True)).all():
                            dtypes[col] = 'Int64'  # Nullable integer type
                        else:
                            dtypes[col] = 'float64'
                    else:
                        dtypes[col] = 'object'
                except:
                    # If conversion fails, keep as object
                    dtypes[col] = 'object'
            
            # Store column metadata
            column_metadata = {
                "table_name": table_name,
                "column_count": len(first_chunk.columns),
                "columns": [{"name": col, "type": str(dtype)} for col, dtype in dtypes.items()]
            }
            
            # Create a list to store all chunks
            all_chunks = [first_chunk]
            total_rows = len(first_chunk)
            
            print(f"Processed first chunk, total rows so far: {total_rows}")
            
            # Process remaining chunks
            chunk_count = 1
            for chunk in chunks:
                chunk_count += 1
                all_chunks.append(chunk)
                total_rows += len(chunk)
                
                # Update progress every 10 chunks
                if chunk_count % 10 == 0:
                    print(f"Processed {chunk_count} chunks, {total_rows} rows so far...")
            
            # Combine all chunks and write to parquet
            print(f"Combining {len(all_chunks)} chunks and writing to parquet...")
            combined_df = pd.concat(all_chunks, ignore_index=True)
            combined_df.to_parquet(parquet_path, engine='pyarrow', index=False)
            
            print(f"Finished processing CSV file. Total rows: {total_rows}")
            
            # Register in DuckDB
            self.conn.execute(f"CREATE OR REPLACE VIEW {table_name} AS SELECT * FROM '{parquet_path}'")
            print(f"Created DuckDB view: {table_name}")
            
            return table_name, total_rows, column_metadata
            
        except Exception as e:
            print(f"Error processing CSV file: {str(e)}")
            # Clean up any partial files
            if parquet_path.exists():
                parquet_path.unlink()
            raise ValueError(f"Failed to process CSV file: {str(e)}")
        
    def query_table(self, table_name: str, query_text: str, limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Execute a SQL query against the table.
        
        Args:
            table_name: Name of the table to query
            query_text: SQL query or natural language query
            limit: Maximum number of rows to return
            
        Returns:
            List of dictionaries containing the query results
        """
        try:
            # For simple queries, translate to SQL
            if "show me" in query_text.lower() and "first" in query_text.lower():
                # Extract number if present (e.g., "first 5 rows")
                import re
                match = re.search(r'first\s+(\d+)', query_text.lower())
                row_limit = int(match.group(1)) if match else 10
                
                # Use streaming for large result sets
                result = self.conn.execute(f"SELECT * FROM {table_name} LIMIT {row_limit}")
                column_names = [desc[0] for desc in result.description]
                rows = result.fetchall()
                
                # Convert to list of dicts
                return [dict(zip(column_names, row)) for row in rows]
            
            # Direct SQL execution (for when you have SQL already)
            if query_text.strip().upper().startswith("SELECT"):
                # Add limit if not present
                if "LIMIT" not in query_text.upper():
                    query_text = f"{query_text} LIMIT {limit}"
                    
                # Execute with streaming
                result = self.conn.execute(query_text)
                column_names = [desc[0] for desc in result.description]
                
                # For potentially large results, fetch in batches
                batch_size = 100
                all_results = []
                
                while True:
                    rows = result.fetchmany(batch_size)
                    if not rows:
                        break
                    all_results.extend([dict(zip(column_names, row)) for row in rows])
                    
                    # If we have too many results, truncate and warn
                    if len(all_results) > limit:
                        all_results = all_results[:limit]
                        return {
                            "warning": f"Result set truncated to {limit} rows",
                            "data": all_results
                        }
                
                return all_results
                
            return [{"error": "Could not parse query. Please use SQL or simple natural language."}]
        except Exception as e:
            return [{"error": f"Error executing query: {str(e)}"}]
            
    def get_table_columns(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Get column information for a table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            List of dictionaries containing column information
        """
        try:
            # Query DuckDB for column information
            result = self.conn.execute(f"PRAGMA table_info('{table_name}')")
            columns = result.fetchall()
            
            # Format the result
            column_info = []
            for col in columns:
                column_info.append({
                    "name": col[1],
                    "type": col[2],
                    "nullable": not col[3],
                    "default": col[4]
                })
                
            return column_info
        except Exception as e:
            print(f"Error getting column information: {str(e)}")
            return []
            
    def get_table_sample(self, table_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get a sample of data from a table.
        
        Args:
            table_name: Name of the table
            limit: Maximum number of rows to return
            
        Returns:
            List of dictionaries containing the sample data
        """
        return self.query_table(table_name, f"SELECT * FROM {table_name} LIMIT {limit}")
