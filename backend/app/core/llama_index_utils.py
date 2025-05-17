"""
LlamaIndex utilities for database querying and vector search.
"""
import os
from typing import List, Optional, Dict, Any

from llama_index.core import VectorStoreIndex, SQLDatabase, ServiceContext
from llama_index.core.objects import ObjectIndex
from llama_index.readers.database import DatabaseReader
from llama_index.llms.openai import OpenAI
from ..core.supabase import get_supabase_client
from .config import get_settings

# Cache for query engines to avoid recreating them for each request
_query_engines_cache = {}


def get_connection_string() -> str:
    """
    Get the database connection string from environment variables.
    """
    settings = get_settings()
    return settings.SUPABASE_DB_URL


def get_query_engine(table_name: str) -> Any:
    """
    Get or create a query engine for the specified tables.
    
    Args:
        table_names: List of table names to include in the index
        dataset_id: Optional dataset ID to use as a cache key
        
    Returns:
        A query engine that can be used to query the database
    """
    # Create a cache key based on the table names and dataset_id
    # cache_key = f"{'-'.join(sorted(table_name))}
    
    # Check if we already have a query engine for this combination
    # if cache_key in _query_engines_cache:
    #     return _query_engines_cache[cache_key]
    
    # Create a new query engine
    connection_string = get_connection_string()

    print(connection_string)
    
    # Initialize SQLDatabase
    # sql_database = SQLDatabase.from_uri(connection_string)

    # print(sql_database)
    
    # Create a reader to ingest table data
    supabase = get_supabase_client()
    db_reader = supabase.rpc("get_columns", {
        "p_table_name": table_name
    }).execute()
    print(db_reader)
    
    # Load table documents
    documents = db_reader.load_data(table_names=table_name)
    
    # Setup LLM
    llm = OpenAI(model="gpt-3.5-turbo")
    
    # Build service context and vector index
    service_context = ServiceContext.from_defaults(llm=llm)
    vector_index = VectorStoreIndex.from_documents(documents, service_context=service_context)
    
    # Create object index for SQL + vector queries
    obj_index = ObjectIndex.from_objects(
        [db_reader],
        [vector_index],
        service_context=service_context
    )
    
    # Create query engine
    query_engine = obj_index.as_query_engine(similarity_top_k=3)
    
    # Cache the query engine
    _query_engines_cache[cache_key] = query_engine
    
    return query_engine


def query_database(query_text: str, table_name: str) -> str:
    """
    Query the database using LlamaIndex.
    
    Args:
        query_text: The natural language query text
        table_names: List of table names to include in the index
        dataset_id: Optional dataset ID to use as a cache key
        
    Returns:
        The response text from the query engine
    """
    query_engine = get_query_engine(table_name)
    response = query_engine.query(query_text)
    return str(response)
