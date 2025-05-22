"""
Function calling utilities for OpenAI API integration.
"""
from ..core.supabase import get_supabase_client
from ..core.llama_index_utils import query_database
import json
import os
from pathlib import Path

# Try to import the wide CSV processor
try:
    from ..core.wide_csv_processor import WideCsvProcessor
    WIDE_CSV_PROCESSOR_AVAILABLE = True
except ImportError:
    WIDE_CSV_PROCESSOR_AVAILABLE = False

# Initialize the wide CSV processor if available
wide_csv_processor = None
if WIDE_CSV_PROCESSOR_AVAILABLE:
    try:
        wide_csv_processor = WideCsvProcessor()
    except Exception as e:
        print(f"Error initializing WideCsvProcessor: {str(e)}")

# Function schemas
FUNCTION_SCHEMAS = [
    # Add a function to check if a dataset is stored in DuckDB
    {
        "type": "function",
        "name": "check_dataset_storage",
        "description": "Check if a dataset is stored in Supabase or DuckDB",
        "parameters": {
            "type": "object",
            "properties": {
                "dataset_id": {
                    "type": "string",
                    "description": "ID of the dataset to check"
                }
            },
            "required": ["dataset_id"],
            "additionalProperties": False
        },
        "strict": True
    },
    # Add a function to get column recommendations based on a query
    {
        "type": "function",
        "name": "get_column_recommendations",
        "description": "Get column recommendations based on a query",
        "parameters": {
            "type": "object",
            "properties": {
                "query_text": {
                    "type": "string",
                    "description": "Query text to find relevant columns"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of recommendations to return"
                }
            },
            "required": ["query_text"],
            "additionalProperties": False
        },
        "strict": True
    },
    # Add a function to query a DuckDB dataset
    {
        "type": "function",
        "name": "query_duckdb_dataset",
        "description": "Run a SQL query against a DuckDB dataset",
        "parameters": {
            "type": "object",
            "properties": {
                "dataset_id": {
                    "type": "string",
                    "description": "ID of the dataset to query"
                },
                "query_text": {
                    "type": "string",
                    "description": "SQL query or natural language query"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of rows to return"
                }
            },
            "required": ["dataset_id", "query_text"],
            "additionalProperties": False
        },
        "strict": True
    },
    {
        "type": "function",
        "name": "get_filtered_count",
        "description": "Get the count of records in a table with optional filtering",
        "parameters": {
            "type": "object",
            "properties": {
                "table_name": {
                    "type": "string",
                    "description": "Name of the table to count records from"
                },
                "column_name": {
                    "type": "string",
                    "description": "Name of the column to count (usually '*' or a specific column)"
                },
                "filter_condition": {
                    "type": ["string", "null"],
                    "description": "Optional SQL WHERE condition to filter the records (without the 'WHERE' keyword)"
                }
            },
            "required": ["table_name", "column_name", "filter_condition"],
            "additionalProperties": False
        },
        "strict": True
    },
    {
        "type": "function",
        "name": "get_table_columns",
        "description": "Get column information for a specified database table",
        "parameters": {
            "type": "object",
            "properties": {
                "table_name": {
                    "type": "string",
                    "description": "Name of the table to get columns from"
                }
            },
            "required": ["table_name"],
            "additionalProperties": False
        },
        "strict": True
    },
    {
    "type": "function",
    "name": "query_table_data",
    "description": "Run a query against a database table to retrieve data",
    "parameters": {
        "type": "object",
        "properties": {
            "table_name": {
                "type": "string",
                "description": "Name of the table to query"
            },
            "query": {
                "type": "string",
                "description": "Natural language description of the data to retrieve"
            },
            "filters": {
                "type": ["object", "null"],
                "description": "Optional filters to apply to the query",
                "properties": {
                    "field": {
                        "type": ["string", "null"],
                        "description": "Field name to filter on"
                    },
                    "value": {
                        "type": ["string", "number", "boolean", "null"],
                        "description": "Value to filter by"
                    },
                    "operator": {
                        "type": ["string", "null"],
                        "description": "Comparison operator (e.g., 'equals', 'greater_than', 'less_than')"
                    }
                },
                "required": ["field", "value", "operator"], 
                "additionalProperties": False
            }
        },
        "required": ["table_name", "query", "filters"],
        "additionalProperties": False
    },
    "strict": True
}
]



def get_table_columns(args):
    """
    Get column information for a specified database table.
    
    Args:
        args: Dictionary containing function arguments
            - table_name: Name of the table to get columns from
            
    Returns:
        JSON string containing column information
    """
    table_name = args.get("table_name")
    supabase = get_supabase_client()
    
    try:
        result = supabase.rpc("get_columns", {
            "p_table_name": table_name
        }).execute()
        
        # Process the result to extract column information
        columns = result.data if result.data else []
        return json.dumps(columns)
    except Exception as e:
        return json.dumps({"error": str(e)})

def get_filtered_count(args):
    """
    Get the count of records in a table with optional filtering.
    
    Args:
        args: Dictionary containing function arguments
            - table_name: Name of the table to count records from
            - column_name: Name of the column to count
            - filter_condition: Optional SQL WHERE condition to filter the records
            
    Returns:
        JSON string containing the count result
    """
    table_name = args.get("table_name")
    column_name = args.get("column_name")
    filter_condition = args.get("filter_condition")
    
    # Handle null or empty filter_condition
    if not filter_condition:
        filter_condition = None
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.rpc("get_filtered_count", {
            "p_table_name": table_name,
            "p_column_name": column_name,
            "p_filter_condition": filter_condition
        }).execute()
        
        # Process the result to extract the count
        count = result.data if result.data else 0
        return json.dumps({"count": count})
    except Exception as e:
        return json.dumps({"error": str(e)})

def query_table_data(args):
    """
    Run a query against a database table to retrieve data using Supabase's query builder.
    
    Args:
        args: Dictionary containing function arguments
            - table_name: Name of the table to query
            - query: Natural language description of the data to retrieve (used for context)
            - filters: Optional filters to apply to the query
                - field: Field name to filter on
                - value: Value to filter by
                - operator: Comparison operator
            
    Returns:
        String containing the query results
    """
    table_name = args.get("table_name")
    query_text = args.get("query")  # Used for context/logging
    filters = args.get("filters", {})
    
    try:
        # Get Supabase client
        supabase = get_supabase_client()
        
        # Start building the query
        query = supabase.table("dataset_abhay_8492056c").select("*")
        
        # Apply filters if provided
        if filters and filters.get("field") and filters.get("value") is not None:
            field = filters.get("field")
            value = filters.get("value")
            operator = filters.get("operator", "equals").lower()
            
            # Map operator to Supabase method
            if operator in ["equals", "equal", "="]:
                query = query.eq(field, value)
            elif operator in ["greater_than", "greater", ">"]:
                query = query.gt(field, value)
            elif operator in ["less_than", "less", "<"]:
                query = query.lt(field, value)
            elif operator in ["greater_than_or_equal", "greater_or_equal", ">="]:
                query = query.gte(field, value)
            elif operator in ["less_than_or_equal", "less_or_equal", "<="]:
                query = query.lte(field, value)
            elif operator in ["not_equal", "not_equals", "!="]:
                query = query.neq(field, value)
            elif operator in ["like", "contains"]:
                # For LIKE/contains, we need to format the value with wildcards
                if isinstance(value, str):
                    query = query.like(field, f"%{value}%")
                else:
                    query = query.eq(field, value)  # Fallback to equals for non-string values
            else:
                # Default to equals for unknown operators
                query = query.eq(field, value)
                
            print(f"Applied filter: {field} {operator} {value}")
        
        # Execute the query
        response = query.execute()
        
        # Process the results
        if response.data:
            return json.dumps(response.data)
        else:
            return json.dumps([])
            
    except Exception as e:
        error_msg = f"Error executing query: {str(e)}"
        print(error_msg)
        return json.dumps({"error": error_msg})

def check_dataset_storage(args):
    """
    Check if a dataset is stored in Supabase or DuckDB.
    
    Args:
        args: Dictionary containing function arguments
            - dataset_id: ID of the dataset to check
            
    Returns:
        JSON string containing storage information
    """
    dataset_id = args.get("dataset_id")
    
    # Check if the dataset is in DuckDB
    if WIDE_CSV_PROCESSOR_AVAILABLE and wide_csv_processor:
        try:
            duckdb_dataset = wide_csv_processor.get_dataset(dataset_id)
            if duckdb_dataset:
                return json.dumps({
                    "storage_type": "duckdb",
                    "dataset_id": dataset_id,
                    "table_name": duckdb_dataset.get("table_name"),
                    "column_count": duckdb_dataset.get("column_count", 0),
                    "row_count": duckdb_dataset.get("row_count", 0)
                })
        except Exception as e:
            print(f"Error checking DuckDB dataset: {str(e)}")
    
    # Check if the dataset is in Supabase
    supabase = get_supabase_client()
    try:
        response = supabase.table("datasets").select("*").eq("id", dataset_id).execute()
        if response.data:
            dataset = response.data[0]
            return json.dumps({
                "storage_type": "supabase",
                "dataset_id": dataset_id,
                "table_name": dataset.get("table_name"),
                "number_of_datapoints": dataset.get("number_of_datapoints", 0)
            })
    except Exception as e:
        print(f"Error checking Supabase dataset: {str(e)}")
    
    # Dataset not found
    return json.dumps({
        "error": f"Dataset not found: {dataset_id}"
    })

def get_column_recommendations(args):
    """
    Get column recommendations based on a query.
    
    Args:
        args: Dictionary containing function arguments
            - query_text: Query text to find relevant columns
            - limit: Maximum number of recommendations to return
            
    Returns:
        JSON string containing column recommendations
    """
    query_text = args.get("query_text")
    limit = args.get("limit", 5)
    
    if not WIDE_CSV_PROCESSOR_AVAILABLE or not wide_csv_processor:
        return json.dumps({
            "error": "Wide CSV processor not available"
        })
    
    try:
        recommendations = wide_csv_processor.get_column_recommendations(query_text, limit)
        return json.dumps(recommendations)
    except Exception as e:
        return json.dumps({
            "error": f"Error getting column recommendations: {str(e)}"
        })

def query_duckdb_dataset(args):
    """
    Run a SQL query against a DuckDB dataset.
    
    Args:
        args: Dictionary containing function arguments
            - dataset_id: ID of the dataset to query
            - query_text: SQL query or natural language query
            - limit: Maximum number of rows to return
            
    Returns:
        JSON string containing query results
    """
    dataset_id = args.get("dataset_id")
    query_text = args.get("query_text")
    limit = args.get("limit", 1000)
    
    if not WIDE_CSV_PROCESSOR_AVAILABLE or not wide_csv_processor:
        return json.dumps({
            "error": "Wide CSV processor not available"
        })
    
    try:
        # Get the dataset
        dataset = wide_csv_processor.get_dataset(dataset_id)
        if not dataset:
            return json.dumps({
                "error": f"Dataset not found: {dataset_id}"
            })
        
        # Query the dataset
        result = wide_csv_processor.query_dataset(dataset_id, query_text, limit)
        return json.dumps(result)
    except Exception as e:
        return json.dumps({
            "error": f"Error querying DuckDB dataset: {str(e)}"
        })

# Function dispatcher
FUNCTION_MAP = {
    "get_table_columns": get_table_columns,
    "query_table_data": query_table_data,
    "get_filtered_count": get_filtered_count,
    "check_dataset_storage": check_dataset_storage,
    "get_column_recommendations": get_column_recommendations,
    "query_duckdb_dataset": query_duckdb_dataset
}
