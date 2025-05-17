from typing import List
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends
from ...schemas.database_info import DatabaseInfo, DatabaseInfoCreate, DatabaseInfoList
from ...core.supabase import get_supabase_client

router = APIRouter()


@router.post("/", response_model=DatabaseInfo)
async def create_database_info(database_info: DatabaseInfoCreate):
    """
    Create a new database_info record.
    """
    supabase = get_supabase_client()
    
    try:
        # Insert the new database_info record
        response = supabase.table("database_info").insert({
            "name": database_info.name,
            "description": database_info.description
        }).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create database info")
        
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating database info: {str(e)}")


@router.get("/{database_info_id}", response_model=DatabaseInfo)
async def get_database_info(database_info_id: UUID):
    """
    Get a specific database_info record by ID.
    """
    supabase = get_supabase_client()
    
    try:
        response = supabase.table("database_info").select("*").eq("id", str(database_info_id)).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Database info not found")
        
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving database info: {str(e)}")


@router.get("/", response_model=DatabaseInfoList)
async def list_database_info():
    """
    List all database_info records.
    """
    supabase = get_supabase_client()
    
    try:
        response = supabase.table("database_info").select("*").order("created_at", desc=True).execute()
        
        return {
            "items": response.data,
            "total": len(response.data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing database info: {str(e)}")


@router.delete("/{database_info_id}")
async def delete_database_info(database_info_id: UUID):
    """
    Delete a database_info record.
    """
    supabase = get_supabase_client()
    
    try:
        response = supabase.table("database_info").delete().eq("id", str(database_info_id)).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Database info not found")
        
        return {"message": "Database info deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting database info: {str(e)}")
