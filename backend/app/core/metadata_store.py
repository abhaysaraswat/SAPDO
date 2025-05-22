"""
SQLite-based metadata store for datasets and columns.
"""
import sqlite3
import json
import os
import uuid
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

class MetadataStore:
    def __init__(self, storage_path="./data", batch_size=500):
        """
        Initialize the metadata store.
        
        Args:
            storage_path: Path to store SQLite database
            batch_size: Number of columns to process at a time
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self.db_path = self.storage_path / "metadata.sqlite"
        self.conn = sqlite3.connect(str(self.db_path))
        self.batch_size = batch_size
        self._initialize_db()
        
    def _initialize_db(self):
        """Create tables if they don't exist"""
        cursor = self.conn.cursor()
        
        # Datasets table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS datasets (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            table_name TEXT NOT NULL,
            created_at TEXT NOT NULL,
            column_count INTEGER NOT NULL,
            row_count INTEGER NOT NULL,
            file_size INTEGER,
            storage_format TEXT DEFAULT 'parquet',
            tags TEXT
        )
        ''')
        
        # Columns table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS columns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dataset_id TEXT NOT NULL,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            description TEXT,
            stats TEXT,
            embedding_id TEXT,
            FOREIGN KEY (dataset_id) REFERENCES datasets(id)
        )
        ''')
        
        # Create indexes for faster queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_columns_dataset_id ON columns(dataset_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_columns_name ON columns(name)')
        
        # Column groups table (for semantic grouping)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS column_groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dataset_id TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            columns TEXT NOT NULL,  -- JSON array of column names
            FOREIGN KEY (dataset_id) REFERENCES datasets(id)
        )
        ''')
        
        self.conn.commit()
        
    def store_dataset_metadata(self, 
                              dataset_id: str, 
                              name: str, 
                              description: str, 
                              table_name: str, 
                              column_metadata: Dict[str, Any], 
                              row_count: int,
                              file_size: Optional[int] = None,
                              tags: Optional[List[str]] = None) -> str:
        """
        Store dataset and column metadata in batches.
        
        Args:
            dataset_id: Unique ID for the dataset
            name: Name of the dataset
            description: Description of the dataset
            table_name: Name of the table in DuckDB
            column_metadata: Metadata about the columns
            row_count: Number of rows in the dataset
            file_size: Size of the file in bytes
            tags: List of tags for the dataset
            
        Returns:
            The dataset ID
        """
        cursor = self.conn.cursor()
        
        # Store dataset info
        cursor.execute(
            "INSERT INTO datasets VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                dataset_id, 
                name, 
                description, 
                table_name, 
                datetime.now().isoformat(), 
                len(column_metadata["columns"]), 
                row_count,
                file_size,
                'parquet',
                json.dumps(tags) if tags else None
            )
        )
        
        # Store column info in batches
        columns = column_metadata["columns"]
        print(f"Storing metadata for {len(columns)} columns in batches of {self.batch_size}")
        
        for i in range(0, len(columns), self.batch_size):
            batch_columns = columns[i:i+self.batch_size]
            
            # Use executemany for batch insertion
            cursor.executemany(
                "INSERT INTO columns (dataset_id, name, type) VALUES (?, ?, ?)",
                [(dataset_id, col["name"], col["type"]) for col in batch_columns]
            )
            
            # Commit each batch
            self.conn.commit()
            print(f"Stored metadata for {i + len(batch_columns)}/{len(columns)} columns...")
            
        # Create automatic column groups for very wide datasets
        if len(columns) > 1000:
            self._create_automatic_column_groups(dataset_id, columns)
            
        return dataset_id
        
    def _create_automatic_column_groups(self, dataset_id: str, columns: List[Dict[str, Any]]):
        """
        Create automatic column groups for very wide datasets.
        
        Args:
            dataset_id: Dataset ID
            columns: List of column metadata
        """
        cursor = self.conn.cursor()
        
        # Group by type
        type_groups = {}
        for col in columns:
            col_type = col["type"]
            if col_type not in type_groups:
                type_groups[col_type] = []
            type_groups[col_type].append(col["name"])
        
        # Create groups
        for col_type, col_names in type_groups.items():
            cursor.execute(
                "INSERT INTO column_groups (dataset_id, name, description, columns) VALUES (?, ?, ?, ?)",
                (
                    dataset_id,
                    f"Type: {col_type}",
                    f"Columns with type {col_type}",
                    json.dumps(col_names)
                )
            )
        
        # Group by prefix (if columns follow a naming pattern)
        prefix_groups = {}
        for col in columns:
            # Try to extract prefix (e.g., "user_" from "user_id", "user_name", etc.)
            parts = col["name"].split('_')
            if len(parts) > 1:
                prefix = parts[0]
                if prefix not in prefix_groups:
                    prefix_groups[prefix] = []
                prefix_groups[prefix].append(col["name"])
        
        # Create groups for prefixes with at least 5 columns
        for prefix, col_names in prefix_groups.items():
            if len(col_names) >= 5:
                cursor.execute(
                    "INSERT INTO column_groups (dataset_id, name, description, columns) VALUES (?, ?, ?, ?)",
                    (
                        dataset_id,
                        f"Prefix: {prefix}",
                        f"Columns starting with {prefix}_",
                        json.dumps(col_names)
                    )
                )
        
        # Create sequential groups for very wide datasets (e.g., columns 1-500, 501-1000, etc.)
        group_size = 500
        for i in range(0, len(columns), group_size):
            end_idx = min(i + group_size, len(columns))
            group_columns = [col["name"] for col in columns[i:end_idx]]
            
            cursor.execute(
                "INSERT INTO column_groups (dataset_id, name, description, columns) VALUES (?, ?, ?, ?)",
                (
                    dataset_id,
                    f"Columns {i+1}-{end_idx}",
                    f"Sequential group of columns from {i+1} to {end_idx}",
                    json.dumps(group_columns)
                )
            )
        
        self.conn.commit()
        
    def get_dataset(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        """
        Get dataset metadata.
        
        Args:
            dataset_id: Dataset ID
            
        Returns:
            Dictionary containing dataset metadata, or None if not found
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM datasets WHERE id = ?", (dataset_id,))
        dataset = cursor.fetchone()
        
        if not dataset:
            return None
            
        # Get columns (with pagination for wide datasets)
        columns = []
        cursor.execute("SELECT COUNT(*) FROM columns WHERE dataset_id = ?", (dataset_id,))
        column_count = cursor.fetchone()[0]
        
        # If there are too many columns, just return the count
        if column_count > 1000:
            # Get column groups instead
            cursor.execute("SELECT id, name, description FROM column_groups WHERE dataset_id = ?", (dataset_id,))
            groups = [{"id": row[0], "name": row[1], "description": row[2]} for row in cursor.fetchall()]
            
            return {
                "id": dataset[0],
                "name": dataset[1],
                "description": dataset[2],
                "table_name": dataset[3],
                "created_at": dataset[4],
                "column_count": dataset[5],
                "row_count": dataset[6],
                "file_size": dataset[7],
                "storage_format": dataset[8],
                "tags": json.loads(dataset[9]) if dataset[9] else [],
                "column_groups": groups,
                "columns_truncated": True,
                "columns_sample": self._get_columns_sample(dataset_id, 10)
            }
        else:
            # Get all columns
            cursor.execute("SELECT name, type, description FROM columns WHERE dataset_id = ?", (dataset_id,))
            columns = [{"name": row[0], "type": row[1], "description": row[2]} for row in cursor.fetchall()]
            
            return {
                "id": dataset[0],
                "name": dataset[1],
                "description": dataset[2],
                "table_name": dataset[3],
                "created_at": dataset[4],
                "column_count": dataset[5],
                "row_count": dataset[6],
                "file_size": dataset[7],
                "storage_format": dataset[8],
                "tags": json.loads(dataset[9]) if dataset[9] else [],
                "columns": columns
            }
            
    def _get_columns_sample(self, dataset_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get a sample of columns for a dataset.
        
        Args:
            dataset_id: Dataset ID
            limit: Maximum number of columns to return
            
        Returns:
            List of column metadata
        """
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT name, type, description FROM columns WHERE dataset_id = ? LIMIT ?", 
            (dataset_id, limit)
        )
        return [{"name": row[0], "type": row[1], "description": row[2]} for row in cursor.fetchall()]
        
    def get_dataset_columns(self, dataset_id: str, offset: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get columns for a dataset with pagination.
        
        Args:
            dataset_id: Dataset ID
            offset: Offset for pagination
            limit: Maximum number of columns to return
            
        Returns:
            List of column metadata
        """
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT name, type, description FROM columns WHERE dataset_id = ? LIMIT ? OFFSET ?", 
            (dataset_id, limit, offset)
        )
        return [{"name": row[0], "type": row[1], "description": row[2]} for row in cursor.fetchall()]
        
    def get_column_group(self, group_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a column group.
        
        Args:
            group_id: Group ID
            
        Returns:
            Dictionary containing group metadata, or None if not found
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT dataset_id, name, description, columns FROM column_groups WHERE id = ?", (group_id,))
        group = cursor.fetchone()
        
        if not group:
            return None
            
        return {
            "id": group_id,
            "dataset_id": group[0],
            "name": group[1],
            "description": group[2],
            "columns": json.loads(group[3])
        }
        
    def list_datasets(self, offset: int = 0, limit: int = 100, search: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all datasets with pagination and optional search.
        
        Args:
            offset: Offset for pagination
            limit: Maximum number of datasets to return
            search: Optional search term
            
        Returns:
            List of dataset metadata
        """
        cursor = self.conn.cursor()
        
        if search:
            cursor.execute(
                """
                SELECT id, name, description, table_name, created_at, column_count, row_count, file_size, storage_format, tags 
                FROM datasets 
                WHERE name LIKE ? OR description LIKE ? 
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
                """,
                (f"%{search}%", f"%{search}%", limit, offset)
            )
        else:
            cursor.execute(
                """
                SELECT id, name, description, table_name, created_at, column_count, row_count, file_size, storage_format, tags 
                FROM datasets 
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
                """,
                (limit, offset)
            )
            
        return [
            {
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "table_name": row[3],
                "created_at": row[4],
                "column_count": row[5],
                "row_count": row[6],
                "file_size": row[7],
                "storage_format": row[8],
                "tags": json.loads(row[9]) if row[9] else []
            }
            for row in cursor.fetchall()
        ]
        
    def update_column_description(self, dataset_id: str, column_name: str, description: str) -> bool:
        """
        Update the description for a column.
        
        Args:
            dataset_id: Dataset ID
            column_name: Column name
            description: New description
            
        Returns:
            True if successful, False otherwise
        """
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE columns SET description = ? WHERE dataset_id = ? AND name = ?",
            (description, dataset_id, column_name)
        )
        self.conn.commit()
        return cursor.rowcount > 0
        
    def delete_dataset(self, dataset_id: str) -> bool:
        """
        Delete a dataset and all its metadata.
        
        Args:
            dataset_id: Dataset ID
            
        Returns:
            True if successful, False otherwise
        """
        cursor = self.conn.cursor()
        
        # Delete columns
        cursor.execute("DELETE FROM columns WHERE dataset_id = ?", (dataset_id,))
        
        # Delete column groups
        cursor.execute("DELETE FROM column_groups WHERE dataset_id = ?", (dataset_id,))
        
        # Delete dataset
        cursor.execute("DELETE FROM datasets WHERE id = ?", (dataset_id,))
        
        self.conn.commit()
        return cursor.rowcount > 0
