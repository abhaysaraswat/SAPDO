"""
Example script demonstrating how to use function calling with DuckDB datasets.

This script shows how to:
1. Check if a dataset is stored in DuckDB or Supabase
2. Get column recommendations for a DuckDB dataset
3. Query a DuckDB dataset using function calling

Usage:
    python duckdb_function_calling_example.py <dataset_id>
"""
import os
import sys
import json
import argparse
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.function_calling import (
    check_dataset_storage,
    get_column_recommendations,
    query_duckdb_dataset
)

def main():
    """Main function demonstrating DuckDB function calling."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test DuckDB function calling")
    parser.add_argument("dataset_id", help="ID of the dataset to query")
    args = parser.parse_args()
    
    dataset_id = args.dataset_id
    
    print("DuckDB Function Calling Example")
    print("==============================")
    
    # Check if the dataset is stored in DuckDB or Supabase
    print(f"\nChecking storage type for dataset {dataset_id}...")
    storage_result = check_dataset_storage({"dataset_id": dataset_id})
    storage_info = json.loads(storage_result)
    
    if "error" in storage_info:
        print(f"Error: {storage_info['error']}")
        return
    
    print(f"Storage type: {storage_info['storage_type']}")
    
    if storage_info['storage_type'] != "duckdb":
        print("This example requires a DuckDB dataset. Please provide a dataset ID for a dataset stored in DuckDB.")
        return
    
    print(f"Table name: {storage_info['table_name']}")
    print(f"Column count: {storage_info['column_count']}")
    print(f"Row count: {storage_info['row_count']}")
    
    # Get column recommendations
    print("\nGetting column recommendations...")
    recommendation_queries = [
        "Find columns related to the first column",
        "Find numeric columns",
        "Find columns with dates or timestamps"
    ]
    
    for query in recommendation_queries:
        print(f"\nQuery: {query}")
        recommendations_result = get_column_recommendations({"query_text": query})
        recommendations = json.loads(recommendations_result)
        
        if isinstance(recommendations, dict) and "error" in recommendations:
            print(f"Error: {recommendations['error']}")
            continue
        
        print(f"Found {len(recommendations)} column recommendations")
        for i, rec in enumerate(recommendations[:3]):  # Show top 3 recommendations
            print(f"  Recommendation {i+1}: {rec['column_name']} (Score: {rec['score']:.4f})")
    
    # Query the dataset
    print("\nQuerying the dataset...")
    query_examples = [
        f"SELECT * FROM {storage_info['table_name']} LIMIT 5",
        "Show me the first 3 rows",
        "Count the total number of rows"
    ]
    
    for query in query_examples:
        print(f"\nQuery: {query}")
        query_result_json = query_duckdb_dataset({
            "dataset_id": dataset_id,
            "query_text": query,
            "limit": 5
        })
        query_result = json.loads(query_result_json)
        
        if isinstance(query_result, dict) and "error" in query_result:
            print(f"Error: {query_result['error']}")
            continue
        
        print(f"Query type: {query_result['type']}")
        
        if query_result['type'] == "sql_query":
            print(f"SQL query: {query_result['query']}")
        elif query_result['type'] == "nl_query":
            print(f"Natural language query: {query_result['query']}")
            print(f"Translated to SQL: {query_result['sql_query']}")
            print("Relevant columns:")
            for i, col in enumerate(query_result.get('relevant_columns', [])[:3]):
                print(f"  Column {i+1}: {col['column_name']} (Score: {col['score']:.4f})")
        
        results = query_result.get('results', [])
        if isinstance(results, dict) and 'data' in results:
            results = results['data']
        
        print(f"Results: {len(results)} rows")
        if results:
            # Print the first result as a sample
            print("Sample result:")
            first_result = results[0]
            if isinstance(first_result, dict):
                for key, value in list(first_result.items())[:5]:  # Show first 5 key-value pairs
                    print(f"  {key}: {value}")
            else:
                print(f"  {first_result}")

if __name__ == "__main__":
    main()
