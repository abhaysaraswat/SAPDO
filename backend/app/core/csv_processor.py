import pandas as pd
import io
import uuid
from typing import List, Dict, Any, Tuple, Optional
from uuid import UUID
from .supabase import get_supabase_client
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os
load_dotenv()

SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL")


def process_csv_file(file_content: bytes, dataset_name: str, database_info_id: Optional[UUID] = None) -> Tuple[str, int]:
    """
    Process a CSV file and create a new table in Supabase with its contents.
    
    Args:
        file_content: The content of the CSV file as bytes
        dataset_name: The name of the dataset (will be used as table name prefix)
        database_info_id: Optional UUID of the database_info record to link to
        
    Returns:
        Tuple containing the table name and number of rows inserted
    """
    # Read CSV into pandas DataFrame
    df = pd.read_csv(io.BytesIO(file_content))

    
    # Clean column names (replace spaces with underscores, remove special chars)
    df.columns = [clean_column_name(col) for col in df.columns]
    
    # Generate a unique table name
    table_name = f"dataset_{dataset_name.lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}"

    
    # If database_info_id is provided, get the database info record
    if database_info_id:
        supabase = get_supabase_client()
        try:
            db_info_response = supabase.table("database_info").select("*").eq("id", str(database_info_id)).execute()
            if db_info_response.data:
                # Use the database_info name for the table name if available
                db_info_name = db_info_response.data[0]['name']
                table_name = f"dataset_{db_info_name.lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}"
        except Exception as e:
            print(f"Error retrieving database info: {str(e)}")
    
    # Convert DataFrame to list of dictionaries for Supabase
    records = df.to_dict(orient='records')
    
    # Create table in Supabase
    supabase = get_supabase_client()
    
    # First, create the table with the appropriate columns
    create_table_in_supabase(table_name, df.dtypes.to_dict(), database_info_id)
    
    # Then insert the data
    response = supabase.table(table_name).insert(records).execute()

    
    return table_name, len(records)


def clean_column_name(name: str) -> str:
    """
    Clean a column name to make it suitable for a database table.
    
    Args:
        name: The original column name
        
    Returns:
        A cleaned column name
    """
    # Replace spaces and special characters
    cleaned = name.lower().replace(' ', '_')
    cleaned = ''.join(c if c.isalnum() or c == '_' else '_' for c in cleaned)
    
    # Ensure it doesn't start with a number
    if cleaned[0].isdigit():
        cleaned = 'col_' + cleaned
        
    return cleaned


def create_table_in_supabase(table_name: str, column_types: Dict[str, Any], database_info_id: Optional[UUID] = None) -> None:
    supabase = get_supabase_client()
    pg_type_mapping = {
        'int64': 'integer',
        'float64': 'double precision',
        'bool': 'boolean',
        'datetime64[ns]': 'timestamp',
        'object': 'text',
    }

    columns = {}
    for col_name, dtype in column_types.items():
        pg_type = pg_type_mapping.get(str(dtype), 'text')
        columns[col_name] = pg_type


    # Connect to Supabase DB using psycopg2

    print(columns)

    
    try:
        response = supabase.rpc("create_dynamic_table", {
            "table_name": table_name,
            "columns": columns
        }).execute()

        update_res = supabase.table("database_info").update({
                "table_name": table_name
            }).eq("id", str(database_info_id)).execute()

        print(update_res)

        return response

    except Exception as e:
        print("❌ Error:", e)