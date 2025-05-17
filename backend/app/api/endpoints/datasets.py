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
    """
    supabase = get_supabase_client()
    
    # Start query
    query = supabase.table("database_info")
    
    # Add search if provided
    if search:
        query = query.ilike("name", f"%{search}%")
    
    # Filter by database_info_id if provided
    if database_info_id:
        query = query.eq("database_info_id", database_info_id)
    
    # Add pagination
    # query = query.range(skip, skip + limit - 1)
    
    # # Get total count
    # count_response = query.select("id", count="exact").execute()
    # total = count_response.count
    
    # Get paginated results
    response = query.select("*").execute()
    
    # Ensure all required fields are present
    datasets = []
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
            
        # Update the item with the processed values
        item["id"] = item_id
        datasets.append(item)
    
    return {
        "datasets": datasets,
        # "total": total
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
        # Process CSV and create table in Supabase
        database_info_uuid = None
        if database_info_id:
            from uuid import UUID
            database_info_uuid = UUID(database_info_id)
            
        table_name, row_count = process_csv_file(file_content, name, database_info_uuid)

        print(table_name)
        

        if not table_name:
            raise HTTPException(status_code=500, detail="Failed to create dataset metadata")
        
        return {"table_name": table_name} 
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing CSV file: {str(e)}"
        )


@router.get("/{dataset_id}", response_model=Dataset)
async def get_dataset(dataset_id: str):
    """
    Get a specific dataset by ID.
    """
    supabase = get_supabase_client()
    response = supabase.table("datasets").select("*").eq("id", dataset_id).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    return response.data[0]


@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dataset(dataset_id: str):
    """
    Delete a dataset by ID.
    """
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
    """
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
        "total_rows": dataset.get("number_of_datapoints", 0)
    }
