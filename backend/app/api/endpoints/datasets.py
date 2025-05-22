from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from typing import List, Optional
import pandas as pd
import io

from ...schemas.dataset import Dataset, DatasetCreate, DatasetList
from ...core.supabase import get_supabase_client
from ...core.csv_processor import process_csv_file

router = APIRouter()


@router.get("/")
async def get_datasets(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    database_info_id: Optional[str] = None
):
    """
    Get all datasets with optional pagination, search, and database_info filtering.
    
    Includes datasets from both Supabase and DuckDB.
    """
    all_datasets = []
    
    # First, get datasets from DuckDB
    try:
        from ...core.wide_csv_processor import WideCsvProcessor
        processor = WideCsvProcessor()
        duckdb_datasets = processor.list_datasets(offset=skip, limit=limit, search=search)
        
        # Convert DuckDB datasets to the expected format
        for item in duckdb_datasets:
            # Add storage type
            item["storage_type"] = "duckdb"
            
            # Ensure all required fields are present
            if "updated_at" not in item or item["updated_at"] is None:
                item["updated_at"] = item.get("created_at")
                
            if "owner_id" not in item or item["owner_id"] is None:
                item["owner_id"] = 1  # Default owner ID
                
            all_datasets.append(item)
    except Exception as e:
        # Log the error but continue to get Supabase datasets
        print(f"Error getting DuckDB datasets: {str(e)}")
    
    # Then, get datasets from Supabase
    supabase = get_supabase_client()
    
    # Start query
    query = supabase.table("database_info")
    
    # Add search if provided
    if search:
        query = query.ilike("name", f"%{search}%")
    
    # Filter by database_info_id if provided
    if database_info_id:
        query = query.eq("database_info_id", database_info_id)
    
    # Get results
    response = query.select("*").execute()
    
    # Process Supabase datasets
    for item in response.data:
        # Convert string ID to integer if needed
        try:
            item_id = int(item.get("id")) if isinstance(item.get("id"), str) and item.get("id").isdigit() else item.get("id")
        except (ValueError, TypeError):
            # If conversion fails, use the original ID
            item_id = item.get("id")
            
        # Ensure updated_at is present
        if "updated_at" not in item or item["updated_at"] is None:
            item["updated_at"] = item.get("created_at")
            
        # Ensure owner_id is present
        if "owner_id" not in item or item["owner_id"] is None:
            item["owner_id"] = 1  # Default owner ID
            
        # Add storage type
        item["storage_type"] = "supabase"
            
        # Update the item with the processed values
        item["id"] = item_id
        all_datasets.append(item)
    
    # Sort combined datasets by created_at (newest first)
    all_datasets.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    # Apply pagination to the combined results
    paginated_datasets = all_datasets[skip:skip+limit]
    
    return {
        "datasets": paginated_datasets,
        "total": len(all_datasets)
    }


@router.post("/", response_model=Dataset, status_code=status.HTTP_201_CREATED)
async def create_dataset(dataset: DatasetCreate):
    """
    Create a new dataset (metadata only, no file upload).
    """
    supabase = get_supabase_client()
    
    # Insert dataset metadata
    response = supabase.table("datasets").insert({
        "name": dataset.name,
        "description": dataset.description,
        "type": dataset.type,
        "number_of_datapoints": 0,
        "number_of_experiments": 0,
        "number_of_optimizations": 0,
        "derived_datasets": 0,
        "owner_id": 1  # Hardcoded for now, would come from auth in real app
    }).execute()
    
    if not response.data:
        raise HTTPException(status_code=500, detail="Failed to create dataset")
    
    return response.data[0]


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_dataset(
    file: UploadFile = File(...),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    database_info_id: Optional[str] = Form(None)
):
    """
    Upload a CSV file and create a new dataset with its contents.
    
    For CSV files with fewer than 1600 columns, this will use Supabase.
    For CSV files with more columns, this will use DuckDB and Parquet.
    """
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are supported"
        )
    
    # Read file content
    file_content = await file.read()
    
    try:
        # Process CSV and create table
        database_info_uuid = None
        if database_info_id:
            from uuid import UUID
            database_info_uuid = UUID(database_info_id)
            
        result = process_csv_file(file_content, name, database_info_uuid)
        
        # Check the return type to determine if we're using Supabase or DuckDB
        if isinstance(result, tuple):
            # Regular Supabase processing
            table_name, row_count = result
            
            if not table_name:
                raise HTTPException(status_code=500, detail="Failed to create dataset metadata")
            
            return {"table_name": table_name, "storage_type": "supabase"}
        else:
            # Wide CSV processing with DuckDB
            return {
                "table_name": result["table_name"],
                "storage_type": "duckdb",
                "column_count": result["column_count"],
                "row_count": result["row_count"],
                "id": result["id"]
            }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing CSV file: {str(e)}"
        )


@router.get("/{dataset_id}")
async def get_dataset(dataset_id: str):
    """
    Get a specific dataset by ID.
    
    Works with both Supabase and DuckDB datasets.
    """
    # First, check if this is a DuckDB dataset
    try:
        from ...core.wide_csv_processor import WideCsvProcessor
        processor = WideCsvProcessor()
        duckdb_dataset = processor.get_dataset(dataset_id)
        
        if duckdb_dataset:
            # Add storage type
            duckdb_dataset["storage_type"] = "duckdb"
            return duckdb_dataset
    except Exception as e:
        # Log the error but continue to try Supabase
        print(f"Error checking DuckDB dataset: {str(e)}")
    
    # If we get here, try Supabase
    supabase = get_supabase_client()
    response = supabase.table("datasets").select("*").eq("id", dataset_id).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    # Add storage type
    dataset = response.data[0]
    dataset["storage_type"] = "supabase"
    
    return dataset


@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dataset(dataset_id: str):
    """
    Delete a dataset by ID.
    
    Works with both Supabase and DuckDB datasets.
    """
    # First, check if this is a DuckDB dataset
    try:
        from ...core.wide_csv_processor import WideCsvProcessor
        processor = WideCsvProcessor()
        duckdb_dataset = processor.get_dataset(dataset_id)
        
        if duckdb_dataset:
            # This is a DuckDB dataset, delete it
            success = processor.delete_dataset(dataset_id)
            if success:
                return None
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to delete DuckDB dataset"
                )
    except Exception as e:
        # Log the error but continue to try Supabase
        print(f"Error checking/deleting DuckDB dataset: {str(e)}")
    
    # If we get here, try Supabase
    supabase = get_supabase_client()
    
    # First get the dataset to check if it exists and get the table name
    response = supabase.table("datasets").select("*").eq("id", dataset_id).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    # Get the table name
    table_name = response.data[0].get("table_name")
    
    # Delete the dataset metadata
    supabase.table("datasets").delete().eq("id", dataset_id).execute()
    
    # If there's a table associated with this dataset, drop it
    if table_name:
        try:
            supabase.table(table_name).execute_sql(f'DROP TABLE IF EXISTS "{table_name}"')
        except Exception as e:
            # Log the error but don't fail the request
            print(f"Error dropping table {table_name}: {str(e)}")
    
    return None


@router.get("/{dataset_id}/preview", response_model=dict)
async def preview_dataset(dataset_id: str, limit: int = 10):
    """
    Get a preview of the dataset's data (first few rows).
    
    Works with both Supabase and DuckDB datasets.
    """
    # First, check if this is a DuckDB dataset by looking in the metadata store
    try:
        from ...core.wide_csv_processor import WideCsvProcessor
        processor = WideCsvProcessor()
        duckdb_dataset = processor.get_dataset(dataset_id)
        
        if duckdb_dataset:
            # This is a DuckDB dataset
            table_name = duckdb_dataset["table_name"]
            
            # Get a sample of the data
            sample = processor.duckdb_processor.get_table_sample(table_name, limit)
            
            # Get column information
            if duckdb_dataset.get("columns_truncated", False):
                # For wide datasets, get a sample of columns
                columns = [col["name"] for col in duckdb_dataset.get("columns_sample", [])]
                column_count = duckdb_dataset["column_count"]
                truncated = True
            else:
                # For smaller datasets, get all columns
                columns = [col["name"] for col in duckdb_dataset.get("columns", [])]
                column_count = len(columns)
                truncated = False
            
            return {
                "columns": columns,
                "data": sample,
                "total_rows": duckdb_dataset["row_count"],
                "storage_type": "duckdb",
                "column_count": column_count,
                "columns_truncated": truncated
            }
    except Exception as e:
        # Log the error but continue to try Supabase
        print(f"Error checking DuckDB dataset: {str(e)}")
    
    # If we get here, try Supabase
    supabase = get_supabase_client()
    
    # Get the dataset metadata
    response = supabase.table("datasets").select("*").eq("id", dataset_id).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    dataset = response.data[0]
    table_name = dataset.get("table_name")
    
    if not table_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dataset has no associated table"
        )
    
    # Get the data preview
    data_response = supabase.table(table_name).select("*").limit(limit).execute()
    
    # Get the column names
    columns_response = supabase.table(table_name).select("*").limit(1).execute()
    columns = list(columns_response.data[0].keys()) if columns_response.data else []
    
    return {
        "columns": columns,
        "data": data_response.data,
        "total_rows": dataset.get("number_of_datapoints", 0),
        "storage_type": "supabase"
    }
