"""
Function calling utilities for OpenAI API integration.
"""
from ..core.supabase import get_supabase_client
from ..core.llama_index_utils import query_database
import json

# Function schemas
FUNCTION_SCHEMAS = [
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

# Function dispatcher
FUNCTION_MAP = {
    "get_table_columns": get_table_columns,
    "query_table_data": query_table_data,
    "get_filtered_count": get_filtered_count
}
