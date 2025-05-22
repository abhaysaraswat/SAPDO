"""
Example script demonstrating how to use the Pinecone vector store with OpenAI embeddings.

This script shows how to:
1. Initialize the Pinecone vector store with OpenAI embeddings
2. Index column metadata for semantic search
3. Search for columns semantically related to a query
4. Delete vectors for a dataset

Usage:
    python pinecone_openai_example.py
"""
import os
import sys
import time
import json
from pathlib import Path
from dotenv import load_dotenv

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables
load_dotenv()

# Check if required environment variables are set
required_vars = ["OPENAI_API_KEY", "PINECONE_API_KEY", "PINECONE_ENVIRONMENT"]
missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
    print("Please set these variables in your .env file")
    sys.exit(1)

# Import the PineconeVectorStore class
from app.core.vector_store import PineconeVectorStore

# Import SentenceTransformer for the local vector store example
try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("Warning: sentence-transformers not installed. Only Pinecone example will work.")

def main():
    """Main function demonstrating the Pinecone vector store with OpenAI embeddings."""
    print("Pinecone Vector Store with OpenAI Embeddings Example")
    print("===================================================")
    
    # Initialize the vector store
    print("\nInitializing Pinecone vector store...")
    
    # Override environment variables for testing
    os.environ["PINECONE_ENVIRONMENT"] = "us-east-1-aws"  # Use a valid AWS region
    
    vector_store = PineconeVectorStore(
        index_name="column-metadata-test",
        namespace="example",
        embedding_model="text-embedding-3-small",
        batch_size=10
    )
    
    # Create sample column metadata
    print("\nCreating sample column metadata...")
    dataset_id = "example-dataset-123"
    columns = [
        {"name": "temperature_celsius", "type": "float64", "description": "Temperature in Celsius"},
        {"name": "humidity_percent", "type": "float64", "description": "Relative humidity in percent"},
        {"name": "pressure_hpa", "type": "float64", "description": "Atmospheric pressure in hectopascals"},
        {"name": "wind_speed_kmh", "type": "float64", "description": "Wind speed in kilometers per hour"},
        {"name": "wind_direction_degrees", "type": "float64", "description": "Wind direction in degrees"},
        {"name": "precipitation_mm", "type": "float64", "description": "Precipitation in millimeters"},
        {"name": "cloud_cover_percent", "type": "float64", "description": "Cloud cover in percent"},
        {"name": "visibility_km", "type": "float64", "description": "Visibility in kilometers"},
        {"name": "uv_index", "type": "float64", "description": "UV index"},
        {"name": "air_quality_index", "type": "float64", "description": "Air quality index"},
    ]
    
    # Index the columns
    print("\nIndexing columns...")
    start_time = time.time()
    num_indexed = vector_store.index_columns(dataset_id, columns)
    end_time = time.time()
    print(f"Indexed {num_indexed} columns in {end_time - start_time:.2f} seconds")
    
    # Wait a moment for Pinecone to process the vectors
    print("\nWaiting for Pinecone to process the vectors...")
    time.sleep(2)
    
    # Search for columns
    print("\nSearching for columns...")
    search_queries = [
        "temperature",
        "wind",
        "air quality",
        "precipitation",
        "weather conditions"
    ]
    
    for query in search_queries:
        print(f"\nQuery: {query}")
        results = vector_store.search_columns(query, limit=3)
        print(f"Found {len(results)} results:")
        for i, result in enumerate(results):
            print(f"  {i+1}. {result['column_name']} (Score: {result['score']:.4f})")
            print(f"     Type: {result['column_type']}")
            print(f"     Description: {result['description']}")
    
    # Ask if the user wants to delete the vectors
    delete_vectors = input("\nDelete vectors for this dataset? (y/n): ").lower() == "y"
    if delete_vectors:
        print(f"\nDeleting vectors for dataset {dataset_id}...")
        vector_store.delete_dataset(dataset_id)
        print("Vectors deleted")
    else:
        print("\nVectors not deleted")
    
    print("\nExample complete!")

if __name__ == "__main__":
    main()
