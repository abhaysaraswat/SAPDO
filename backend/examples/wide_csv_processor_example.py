"""
Example script demonstrating how to use the wide CSV processor.

This script shows how to:
1. Process a wide CSV file
2. Query the resulting dataset
3. Get column recommendations
4. Delete the dataset

Usage:
    python wide_csv_processor_example.py
"""
import os
import sys
import time
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.wide_csv_processor import WideCsvProcessor

def main():
    """Main function demonstrating the wide CSV processor."""
    print("Wide CSV Processor Example")
    print("=========================")
    
    # Initialize the processor
    processor = WideCsvProcessor()
    print("Initialized WideCsvProcessor")
    
    # Check if the example CSV file exists
    csv_path = Path("../data/modified.csv")
    if not csv_path.exists():
        print(f"Error: Example CSV file not found at {csv_path.absolute()}")
        print("Please place a wide CSV file at this location or update the path in this script.")
        return
    
    # Read the CSV file
    print(f"Reading CSV file: {csv_path}")
    with open(csv_path, "rb") as f:
        file_content = f.read()
    
    # Process the CSV file
    print("Processing CSV file...")
    start_time = time.time()
    result = processor.process_csv_file(
        file_content=file_content,
        dataset_name="Example Wide Dataset",
        description="Example dataset processed by wide_csv_processor_example.py"
    )
    end_time = time.time()
    
    # Print the result
    print(f"CSV file processed in {end_time - start_time:.2f} seconds")
    print(f"Dataset ID: {result['id']}")
    print(f"Table name: {result['table_name']}")
    print(f"Column count: {result['column_count']}")
    print(f"Row count: {result['row_count']}")
    
    # Store the dataset ID for later use
    dataset_id = result["id"]
    table_name = result["table_name"]
    
    # Get dataset information
    print("\nGetting dataset information...")
    dataset = processor.get_dataset(dataset_id)
    print(f"Dataset name: {dataset['name']}")
    print(f"Dataset description: {dataset['description']}")
    print(f"Dataset created at: {dataset['created_at']}")
    
    # Get column groups if available
    if "column_groups" in dataset:
        print(f"\nColumn groups: {len(dataset['column_groups'])}")
        for i, group in enumerate(dataset['column_groups'][:3]):  # Show first 3 groups
            print(f"  Group {i+1}: {group['name']} - {group['description']}")
    
    # Query the dataset
    print("\nQuerying the dataset...")
    query_result = processor.query_dataset(
        dataset_id=dataset_id,
        query_text=f"SELECT * FROM {table_name} LIMIT 5"
    )
    print(f"Query type: {query_result['type']}")
    print(f"Query results: {len(query_result['results'])} rows")
    
    # Get column recommendations
    print("\nGetting column recommendations...")
    recommendations = processor.get_column_recommendations(
        query_text="Find columns related to the first column"
    )
    print(f"Found {len(recommendations)} column recommendations")
    for i, rec in enumerate(recommendations[:3]):  # Show top 3 recommendations
        print(f"  Recommendation {i+1}: {rec['column_name']} (Score: {rec['score']:.4f})")
    
    # Ask if the user wants to delete the dataset
    delete_dataset = input("\nDelete the dataset? (y/n): ").lower() == "y"
    if delete_dataset:
        print(f"Deleting dataset {dataset_id}...")
        success = processor.delete_dataset(dataset_id)
        if success:
            print("Dataset deleted successfully")
        else:
            print("Failed to delete dataset")
    else:
        print(f"Dataset {dataset_id} was not deleted")
        print(f"You can query it using the table name: {table_name}")

if __name__ == "__main__":
    main()
