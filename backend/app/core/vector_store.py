"""
Vector store for semantic search of columns.
"""
import uuid
import json
import os
import time
import re
import string
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
VECTOR_STORE_TYPE = os.getenv("VECTOR_STORE_TYPE", "local")  # Default to local if not specified

class VectorStore:
    """
    A simple vector store implementation for semantic search.
    
    This implementation uses Sentence Transformers for embedding generation
    and stores the embeddings in memory. In a production environment, you would
    use a dedicated vector database like Qdrant, Chroma, or Pinecone.
    """
    
    def __init__(self, model_name="all-MiniLM-L6-v2", batch_size=32):
        """
        Initialize the vector store.
        
        Args:
            model_name: Name of the Sentence Transformers model to use
            batch_size: Batch size for embedding generation
        """
        self.model = SentenceTransformer(model_name)
        self.batch_size = batch_size
        self.embeddings = {}  # id -> embedding
        self.metadata = {}    # id -> metadata
        
    def index_columns(self, dataset_id: str, columns: List[Dict[str, Any]]) -> int:
        """
        Index column metadata for semantic search.
        
        Args:
            dataset_id: Dataset ID
            columns: List of column metadata
            
        Returns:
            Number of columns indexed
        """
        # Process columns in batches
        total_indexed = 0
        
        for i in range(0, len(columns), self.batch_size):
            batch_columns = columns[i:i+self.batch_size]
            
            # Create text descriptions for each column
            texts = []
            ids = []
            
            for column in batch_columns:
                # Create a descriptive text for the column
                column_desc = f"Column {column['name']}"
                if column.get('description'):
                    column_desc += f": {column['description']}"
                else:
                    # Try to make a more descriptive text based on the column name
                    words = column['name'].replace('_', ' ').replace('-', ' ').split()
                    if len(words) > 1:
                        column_desc += f": {' '.join(words)}"
                
                # Add type information
                column_desc += f" (Type: {column['type']})"
                
                # Generate a unique ID
                column_id = str(uuid.uuid4())
                
                texts.append(column_desc)
                ids.append(column_id)
                
                # Store metadata
                self.metadata[column_id] = {
                    "dataset_id": dataset_id,
                    "column_name": column["name"],
                    "column_type": column["type"],
                    "description": column.get("description", "")
                }
            
            # Generate embeddings
            print(f"Generating embeddings for {len(texts)} columns...")
            embeddings = self.model.encode(texts, batch_size=self.batch_size, show_progress_bar=True)
            
            # Store embeddings
            for i, column_id in enumerate(ids):
                self.embeddings[column_id] = embeddings[i]
            
            total_indexed += len(batch_columns)
            print(f"Indexed {total_indexed}/{len(columns)} columns...")
        
        return total_indexed
    
    def search_columns(self, query_text: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for columns semantically related to the query.
        
        Args:
            query_text: Query text
            limit: Maximum number of results to return
            
        Returns:
            List of dictionaries containing column information and similarity scores
        """
        if not self.embeddings:
            return []
        
        # Generate query embedding
        query_embedding = self.model.encode(query_text)
        
        # Calculate similarities
        similarities = []
        for column_id, embedding in self.embeddings.items():
            # Calculate cosine similarity
            similarity = self._cosine_similarity(query_embedding, embedding)
            similarities.append((column_id, similarity))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return top results
        results = []
        for column_id, score in similarities[:limit]:
            metadata = self.metadata[column_id]
            results.append({
                "dataset_id": metadata["dataset_id"],
                "column_name": metadata["column_name"],
                "column_type": metadata["column_type"],
                "description": metadata["description"],
                "score": float(score)  # Convert to float for JSON serialization
            })
        
        return results
    
    def _cosine_similarity(self, a, b) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            a: First vector
            b: Second vector
            
        Returns:
            Cosine similarity
        """
        import numpy as np
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    def save(self, path: str) -> None:
        """
        Save the vector store to disk.
        
        Args:
            path: Path to save to
        """
        import numpy as np
        
        # Convert embeddings to list for JSON serialization
        serializable_embeddings = {k: v.tolist() for k, v in self.embeddings.items()}
        
        # Save to disk
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            json.dump({
                'embeddings': serializable_embeddings,
                'metadata': self.metadata
            }, f)
    
    def load(self, path: str) -> None:
        """
        Load the vector store from disk.
        
        Args:
            path: Path to load from
        """
        import numpy as np
        
        # Load from disk
        with open(path, 'r') as f:
            data = json.load(f)
        
        # Convert embeddings back to numpy arrays
        self.embeddings = {k: np.array(v) for k, v in data['embeddings'].items()}
        self.metadata = data['metadata']


class PineconeVectorStore:
    """
    Pinecone-based vector store for semantic search.
    
    This implementation uses OpenAI for embedding generation
    and Pinecone for vector storage and search.
    """
    
    @staticmethod
    def _sanitize_id(text: str, max_length: int = 30) -> str:
        """
        Sanitize text to be used as a Pinecone vector ID.
        
        Args:
            text: Text to sanitize
            max_length: Maximum length of the sanitized text
            
        Returns:
            Sanitized text (ASCII only, no special characters)
        """
        if not text:
            return "unknown"
        
        # Remove non-ASCII characters
        ascii_text = ''.join(c for c in text if c in string.printable)
        
        # Replace spaces and special characters with underscores
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', ascii_text)
        
        # Truncate to max_length
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        # Ensure it's not empty
        if not sanitized:
            sanitized = "column"
        
        return sanitized
    
    def __init__(self, index_name="column-metadata", namespace="default", 
                 embedding_model="text-embedding-3-small", batch_size=100):
        """
        Initialize the Pinecone vector store.
        
        Args:
            index_name: Name of the Pinecone index
            namespace: Namespace within the index
            embedding_model: Name of the OpenAI embedding model to use
            batch_size: Batch size for embedding generation
        """
        try:
            from pinecone import Pinecone, ServerlessSpec
            from openai import OpenAI
        except ImportError:
            raise ImportError("Required packages not installed. Install with 'pip install pinecone-client openai'")
        
        if not PINECONE_API_KEY:
            raise ValueError("PINECONE_API_KEY environment variable not set")
        if not PINECONE_ENVIRONMENT:
            raise ValueError("PINECONE_ENVIRONMENT environment variable not set")
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        # Initialize Pinecone
        self.pc = Pinecone(api_key=PINECONE_API_KEY)
        
        # Initialize OpenAI client
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
        
        self.index_name = index_name
        self.namespace = namespace
        self.embedding_model = embedding_model
        self.batch_size = batch_size
        
        # Determine embedding dimensions based on model
        self.embedding_dimensions = 1536  # Default for text-embedding-3-small
        if embedding_model == "text-embedding-3-large":
            self.embedding_dimensions = 3072
        
        # Ensure index exists
        self._ensure_index_exists()
        
        # Get index
        self.index = self.pc.Index(self.index_name)
    
    def _ensure_index_exists(self):
        """Create Pinecone index if it doesn't exist"""
        from pinecone import ServerlessSpec
        
        # Check if index exists
        existing_indexes = self.pc.list_indexes()
        if self.index_name not in existing_indexes.names():
            print(f"Creating Pinecone index: {self.index_name} with dimension {self.embedding_dimensions}")
            
            # Parse region from environment
            # Expected format: "us-east1-aws" or similar
            # For AWS, valid regions are: us-east-1, us-west-2, eu-west-1, ap-southeast-1
            # For GCP, valid regions are: us-central1, us-east1, us-east4, us-west1, us-west4, northamerica-northeast1, 
            #                             southamerica-east1, eu-west1, eu-west2, eu-west3, eu-west4, eu-central1, 
            #                             eu-north1, asia-northeast1, asia-east1, asia-southeast1, australia-southeast1
            
            # Default to aws us-east-1 if can't parse
            cloud = "aws"
            region = "us-east-1"
            
            # Try to parse the environment string
            if PINECONE_ENVIRONMENT:
                env_parts = PINECONE_ENVIRONMENT.split('-')
                if len(env_parts) >= 2 and env_parts[-1] in ["aws", "gcp", "azure"]:
                    cloud = env_parts[-1]
                    # For AWS, use standard region format
                    if cloud == "aws":
                        # Convert us-east1-aws to us-east-1
                        if len(env_parts) >= 3:
                            region_parts = env_parts[:-1]  # Remove the cloud part
                            # Handle the numeric part (e.g., east1 -> east-1)
                            last_part = region_parts[-1]
                            if any(c.isdigit() for c in last_part):
                                # Split the last part into alpha and numeric
                                alpha = ''.join(c for c in last_part if not c.isdigit())
                                numeric = ''.join(c for c in last_part if c.isdigit())
                                region_parts[-1] = f"{alpha}-{numeric}"
                            region = '-'.join(region_parts)
                    else:
                        # For GCP and Azure, use the format as is
                        region = '-'.join(env_parts[:-1])
                
            print(f"Using cloud: {cloud}, region: {region}")
            
            # Create index
            self.pc.create_index(
                name=self.index_name,
                dimension=self.embedding_dimensions,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud=cloud,
                    region=region
                )
            )
            
            # Wait for index to be ready
            print("Waiting for index to be ready...")
            time.sleep(10)  # Give it some time to initialize
            
            # Check if index exists now
            retries = 0
            while retries < 5:
                if self.index_name in self.pc.list_indexes().names():
                    break
                print("Index not ready yet, waiting...")
                time.sleep(5)
                retries += 1
                
            print(f"Created Pinecone index: {self.index_name}")
    
    def _generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings using OpenAI.
        
        Args:
            texts: List of texts to generate embeddings for
            
        Returns:
            List of embeddings
        """
        embeddings = []
        
        # Process in batches to avoid rate limits
        for i in range(0, len(texts), self.batch_size):
            batch_texts = texts[i:i+self.batch_size]
            
            # Generate embeddings
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=batch_texts
            )
            
            # Extract embeddings
            batch_embeddings = [item.embedding for item in response.data]
            embeddings.extend(batch_embeddings)
            
            # Sleep to avoid rate limits if there are more batches
            if i + self.batch_size < len(texts):
                time.sleep(0.5)
        
        return embeddings
    
    def index_columns(self, dataset_id: str, columns: List[Dict[str, Any]]) -> int:
        """
        Index column metadata for semantic search.
        
        Args:
            dataset_id: Dataset ID
            columns: List of column metadata
            
        Returns:
            Number of columns indexed
        """
        # Process columns in batches
        total_indexed = 0
        
        for i in range(0, len(columns), self.batch_size):
            batch_columns = columns[i:i+self.batch_size]
            
            # Create text descriptions for each column
            texts = []
            metadatas = []
            ids = []
            
            for column in batch_columns:
                # Create a descriptive text for the column
                column_desc = f"Column {column['name']}"
                if column.get('description'):
                    column_desc += f": {column['description']}"
                else:
                    # Try to make a more descriptive text based on the column name
                    words = column['name'].replace('_', ' ').replace('-', ' ').split()
                    if len(words) > 1:
                        column_desc += f": {' '.join(words)}"
                
                # Add type information
                column_desc += f" (Type: {column['type']})"
                
                # Generate a unique ID with sanitized dataset_id and column name to ensure it's ASCII-compatible
                sanitized_dataset_id = self._sanitize_id(dataset_id)
                sanitized_name = self._sanitize_id(column['name'])
                column_id = f"{sanitized_dataset_id}_{sanitized_name}_{str(uuid.uuid4())[:8]}"
                
                texts.append(column_desc)
                metadatas.append({
                    "dataset_id": dataset_id,
                    "column_name": column["name"],
                    "column_type": column["type"],
                    "description": column.get("description", ""),
                    "text": column_desc  # Include the full text for reference
                })
                ids.append(column_id)
            
            # Generate embeddings
            print(f"Generating embeddings for {len(texts)} columns using OpenAI {self.embedding_model}...")
            embeddings = self._generate_embeddings(texts)
            
            # Prepare vectors for Pinecone
            vectors = [
                (ids[i], embeddings[i], metadatas[i])
                for i in range(len(ids))
            ]
            
            # Upsert to Pinecone in smaller batches to avoid exceeding the 2MB request size limit
            print(f"Upserting {len(vectors)} vectors to Pinecone in smaller batches...")
            # Use a smaller batch size for upsert to avoid exceeding the 2MB limit
            upsert_batch_size = 50  # Adjust this value based on your vector dimensions and metadata size
            
            for j in range(0, len(vectors), upsert_batch_size):
                batch_vectors = vectors[j:j+upsert_batch_size]
                try:
                    self.index.upsert(vectors=batch_vectors, namespace=self.namespace)
                    print(f"  Upserted batch {j//upsert_batch_size + 1}/{(len(vectors)-1)//upsert_batch_size + 1} ({len(batch_vectors)} vectors)")
                    # Small delay between batches to avoid rate limits
                    time.sleep(0.5)
                except Exception as e:
                    print(f"Error upserting batch: {str(e)}")
                    # If the batch is still too large, try with an even smaller batch
                    if "exceeds the maximum supported size" in str(e) and upsert_batch_size > 10:
                        print("Batch too large, retrying with smaller batch size...")
                        smaller_batch_size = upsert_batch_size // 2
                        for k in range(j, min(j+upsert_batch_size, len(vectors)), smaller_batch_size):
                            smaller_batch = vectors[k:k+smaller_batch_size]
                            try:
                                self.index.upsert(vectors=smaller_batch, namespace=self.namespace)
                                print(f"  Upserted smaller batch ({len(smaller_batch)} vectors)")
                                time.sleep(0.5)
                            except Exception as e2:
                                print(f"Error upserting smaller batch: {str(e2)}")
                                # If still failing, try one by one
                                for vector in smaller_batch:
                                    try:
                                        self.index.upsert(vectors=[vector], namespace=self.namespace)
                                        print(f"  Upserted single vector")
                                        time.sleep(0.2)
                                    except Exception as e3:
                                        print(f"Error upserting single vector: {str(e3)}")
                                        # Skip this vector and continue
                                        continue
            
            total_indexed += len(batch_columns)
            print(f"Indexed {total_indexed}/{len(columns)} columns...")
        
        return total_indexed
    
    def search_columns(self, query_text: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for columns semantically related to the query.
        
        Args:
            query_text: Query text
            limit: Maximum number of results to return
            
        Returns:
            List of dictionaries containing column information and similarity scores
        """
        # Generate query embedding
        print(f"Generating embedding for query: {query_text}")
        query_embedding = self._generate_embeddings([query_text])[0]
        
        # Search in Pinecone
        print(f"Searching Pinecone index: {self.index_name}")
        results = self.index.query(
            vector=query_embedding,
            top_k=limit,
            include_metadata=True,
            namespace=self.namespace
        )
        
        # Format results
        formatted_results = []
        for match in results.matches:
            metadata = match.metadata
            formatted_results.append({
                "dataset_id": metadata["dataset_id"],
                "column_name": metadata["column_name"],
                "column_type": metadata["column_type"],
                "description": metadata["description"],
                "score": float(match.score)
            })
        
        return formatted_results
    
    def delete_dataset(self, dataset_id: str) -> bool:
        """
        Delete all vectors for a dataset.
        
        Args:
            dataset_id: Dataset ID
            
        Returns:
            True if successful
        """
        # Delete by metadata filter
        self.index.delete(
            filter={"dataset_id": {"$eq": dataset_id}},
            namespace=self.namespace
        )
        return True


class QdrantVectorStore:
    """
    Qdrant-based vector store for semantic search.
    
    This implementation uses Sentence Transformers for embedding generation
    and Qdrant for vector storage and search. Qdrant must be running as a
    separate service (e.g., via Docker).
    """
    
    def __init__(self, host="localhost", port=6333, model_name="all-MiniLM-L6-v2", batch_size=32):
        """
        Initialize the Qdrant vector store.
        
        Args:
            host: Qdrant host
            port: Qdrant port
            model_name: Name of the Sentence Transformers model to use
            batch_size: Batch size for embedding generation
        """
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.http import models as qdrant_models
        except ImportError:
            raise ImportError("Qdrant client not installed. Install with 'pip install qdrant-client'")
        
        self.client = QdrantClient(host=host, port=port)
        self.model = SentenceTransformer(model_name)
        self.collection_name = "column_metadata"
        self.batch_size = batch_size
        self._ensure_collection()
    
    def _ensure_collection(self):
        """Create collection if it doesn't exist"""
        from qdrant_client.http import models as qdrant_models
        
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if self.collection_name not in collection_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=qdrant_models.VectorParams(
                    size=self.model.get_sentence_embedding_dimension(),
                    distance=qdrant_models.Distance.COSINE
                )
            )
    
    def index_columns(self, dataset_id: str, columns: List[Dict[str, Any]]) -> int:
        """
        Index column metadata for semantic search.
        
        Args:
            dataset_id: Dataset ID
            columns: List of column metadata
            
        Returns:
            Number of columns indexed
        """
        from qdrant_client.http import models as qdrant_models
        
        # Process columns in batches
        total_indexed = 0
        
        for i in range(0, len(columns), self.batch_size):
            batch_columns = columns[i:i+self.batch_size]
            
            # Create text descriptions for each column
            texts = []
            payloads = []
            ids = []
            
            for column in batch_columns:
                # Create a descriptive text for the column
                column_desc = f"Column {column['name']}"
                if column.get('description'):
                    column_desc += f": {column['description']}"
                else:
                    # Try to make a more descriptive text based on the column name
                    words = column['name'].replace('_', ' ').replace('-', ' ').split()
                    if len(words) > 1:
                        column_desc += f": {' '.join(words)}"
                
                # Add type information
                column_desc += f" (Type: {column['type']})"
                
                texts.append(column_desc)
                payloads.append({
                    "dataset_id": dataset_id,
                    "column_name": column["name"],
                    "column_type": column["type"],
                    "description": column.get("description", "")
                })
                ids.append(str(uuid.uuid4()))
            
            # Generate embeddings
            print(f"Generating embeddings for {len(texts)} columns...")
            embeddings = self.model.encode(texts, batch_size=self.batch_size, show_progress_bar=True)
            
            # Upload to Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=qdrant_models.Batch(
                    ids=ids,
                    vectors=embeddings.tolist(),
                    payloads=payloads
                )
            )
            
            total_indexed += len(batch_columns)
            print(f"Indexed {total_indexed}/{len(columns)} columns...")
        
        return total_indexed
    
    def search_columns(self, query_text: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for columns semantically related to the query.
        
        Args:
            query_text: Query text
            limit: Maximum number of results to return
            
        Returns:
            List of dictionaries containing column information and similarity scores
        """
        # Generate query embedding
        query_embedding = self.model.encode(query_text)
        
        # Search in Qdrant
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=limit
        )
        
        return [
            {
                "dataset_id": hit.payload["dataset_id"],
                "column_name": hit.payload["column_name"],
                "column_type": hit.payload["column_type"],
                "description": hit.payload["description"],
                "score": hit.score
            }
            for hit in results
        ]
