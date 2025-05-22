#!/bin/bash
# Setup script for the Wide CSV Processor
# This script installs the required dependencies for the Wide CSV Processor

# Exit on error
set -e

# Print commands
set -x

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "pip3 is not installed. Please install pip3 and try again."
    exit 1
fi

# Create data directory if it doesn't exist
mkdir -p data
mkdir -p data/vector_store

# Install required packages
echo "Installing required packages..."

# Install DuckDB with special handling
echo "Installing DuckDB..."
pip3 install duckdb==0.8.1

# Install other dependencies
echo "Installing other dependencies..."
pip3 install pyarrow==14.0.1 sentence-transformers==2.2.2

# Optional: Install vector store clients
echo "Installing vector store clients..."
echo "1. Local vector store (already installed with sentence-transformers)"
echo "2. Qdrant vector store"
echo "3. Pinecone vector store with OpenAI embeddings"
echo "4. All of the above"
echo "5. None"
read -p "Which vector store(s) would you like to install? (1-5): " -n 1 -r
echo

case $REPLY in
    1)
        echo "Using local vector store only (already installed)"
        ;;
    2)
        echo "Installing Qdrant client..."
        pip3 install qdrant-client
        ;;
    3)
        echo "Installing Pinecone client and OpenAI..."
        pip3 install pinecone>=3.0.0 openai
        ;;
    4)
        echo "Installing all vector store clients..."
        pip3 install qdrant-client pinecone>=3.0.0 openai
        ;;
    *)
        echo "No additional vector store clients installed"
        ;;
esac

# Create a test CSV file with many columns
echo "Creating a test CSV file with many columns..."
python3 - <<EOF
import pandas as pd
import numpy as np

# Create a DataFrame with 2000 columns and 100 rows
columns = [f"col_{i}" for i in range(2000)]
df = pd.DataFrame(np.random.rand(100, 2000), columns=columns)

# Save to CSV
df.to_csv("data/test_wide.csv", index=False)
print(f"Created test CSV file with {len(df.columns)} columns and {len(df)} rows")
EOF

# Run the example script
echo "Running the example script..."
cd "$(dirname "$0")/.."
python3 examples/wide_csv_processor_example.py

echo "Setup complete!"
echo "You can now use the Wide CSV Processor to process CSV files with thousands of columns."
echo "See the documentation in docs/wide_csv_processor.md for more information."

# Configure vector store type
echo
echo "Vector Store Configuration"
echo "=========================="
echo "1. Local vector store (uses Sentence Transformers, stores locally)"
echo "2. Qdrant vector store (uses Sentence Transformers, requires Qdrant server)"
echo "3. Pinecone vector store (uses OpenAI embeddings, requires Pinecone account)"
read -p "Which vector store would you like to use? (1-3): " -n 1 -r
echo

# Check if .env file exists
if [ ! -f "../.env" ]; then
    echo "Creating .env file..."
    touch "../.env"
fi

case $REPLY in
    2)
        echo "Setting vector store type to Qdrant..."
        if grep -q "VECTOR_STORE_TYPE" "../.env"; then
            sed -i '' 's/VECTOR_STORE_TYPE=.*/VECTOR_STORE_TYPE="qdrant"/' "../.env"
        else
            echo 'VECTOR_STORE_TYPE="qdrant"' >> "../.env"
        fi
        echo "Please make sure you have a Qdrant server running."
        ;;
    3)
        echo "Setting vector store type to Pinecone..."
        if grep -q "VECTOR_STORE_TYPE" "../.env"; then
            sed -i '' 's/VECTOR_STORE_TYPE=.*/VECTOR_STORE_TYPE="pinecone"/' "../.env"
        else
            echo 'VECTOR_STORE_TYPE="pinecone"' >> "../.env"
        fi
        
        # Ask for Pinecone API key and environment
        read -p "Enter your Pinecone API key: " pinecone_api_key
        read -p "Enter your Pinecone environment (e.g., us-east1-aws): " pinecone_env
        
        # Update .env file
        if grep -q "PINECONE_API_KEY" "../.env"; then
            sed -i '' "s/PINECONE_API_KEY=.*/PINECONE_API_KEY=\"$pinecone_api_key\"/" "../.env"
        else
            echo "PINECONE_API_KEY=\"$pinecone_api_key\"" >> "../.env"
        fi
        
        if grep -q "PINECONE_ENVIRONMENT" "../.env"; then
            sed -i '' "s/PINECONE_ENVIRONMENT=.*/PINECONE_ENVIRONMENT=\"$pinecone_env\"/" "../.env"
        else
            echo "PINECONE_ENVIRONMENT=\"$pinecone_env\"" >> "../.env"
        fi
        
        # Check if OpenAI API key is set
        if ! grep -q "OPENAI_API_KEY" "../.env"; then
            read -p "Enter your OpenAI API key: " openai_api_key
            echo "OPENAI_API_KEY=\"$openai_api_key\"" >> "../.env"
        fi
        ;;
    *)
        echo "Setting vector store type to local..."
        if grep -q "VECTOR_STORE_TYPE" "../.env"; then
            sed -i '' 's/VECTOR_STORE_TYPE=.*/VECTOR_STORE_TYPE="local"/' "../.env"
        else
            echo 'VECTOR_STORE_TYPE="local"' >> "../.env"
        fi
        ;;
esac

echo
echo "Vector store configuration complete!"
echo "You can change the vector store type by editing the VECTOR_STORE_TYPE variable in the .env file."
