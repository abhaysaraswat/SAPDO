# SAPDO - AI-Powered Data Analysis Platform

SAPDO is a modern data analysis platform that combines the power of AI with database management to provide intuitive data exploration and analysis capabilities. It allows users to upload datasets, chat with an AI assistant about their data, and get insights through natural language queries.

![SAPDO Platform]([https://via.placeholder.com/800x400?text=SAPDO+Platform](https://x.com/abhayysaraswat/status/1923756345972457703))

## Features

### 📊 Dataset Management
- **Upload CSV Files**: Easily upload CSV files that are automatically converted to database tables
- **Wide CSV Support**: Process CSV files with thousands of columns using DuckDB and Parquet
- **Dataset Organization**: Browse, search, and manage your datasets
- **Metadata Tracking**: Track dataset information including number of datapoints and descriptions

### 💬 AI Chat Interface
- **Natural Language Queries**: Ask questions about your data in plain English
- **Interactive Conversations**: Have back-and-forth conversations with the AI about your data
- **Context Awareness**: The AI remembers previous messages in the conversation for better context

### 🔍 Function Calling
- **Database Querying**: The AI can directly query your database tables to retrieve information
- **Column Information**: Get information about table structure and column types
- **Data Filtering**: Filter data using various operators (equals, greater than, less than, etc.)
- **Type-Safe Queries**: Properly formatted queries based on data types

### 🛠️ Technical Features
- **Supabase Integration**: Seamless integration with Supabase for database management
- **DuckDB & Parquet**: Support for wide datasets with thousands of columns
- **Vector Search**: Semantic search for columns in large datasets
- **OpenAI Integration**: Leverages OpenAI's function calling capabilities for intelligent queries
- **Modern UI**: Clean, responsive interface built with Next.js and Material UI
- **API-First Design**: Well-structured API endpoints for all functionality

## Architecture

SAPDO is built with a modern stack:

- **Frontend**: Next.js with Material UI
- **Backend**: FastAPI (Python)
- **Databases**:
  - Supabase (PostgreSQL) for regular datasets
  - DuckDB with Parquet for wide datasets (10,000+ columns)
  - SQLite for metadata storage
- **AI**: OpenAI API with function calling
- **Vector Store**: Sentence Transformers for semantic column search

The application is structured as follows:

```
sapdo/
├── backend/           # FastAPI backend
│   ├── app/           # Application code
│   │   ├── api/       # API endpoints
│   │   ├── core/      # Core functionality
│   │   └── schemas/   # Data models
│   └── docs/          # Documentation
└── frontend/          # Next.js frontend
    ├── public/        # Static assets
    └── src/           # Source code
        ├── app/       # Next.js app router
        ├── components/# React components
        └── styles/    # CSS styles
```

## Getting Started

### Prerequisites

- Node.js 18+ for the frontend
- Python 3.8+ for the backend
- Supabase account and project
- OpenAI API key

### Installation

#### Backend Setup

1. Clone the repository
2. Navigate to the backend directory:
   ```bash
   cd backend
   ```
3. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
4. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
5. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
6. Create a `.env` file with the following variables:
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   SECRET_KEY=your_secret_key_for_jwt
   OPENAI_API_KEY=your_openai_api_key
   ```
7. Start the backend server:
   ```bash
   python run.py
   ```

#### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Create a `.env.local` file with:
   ```
   NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
   ```
4. Start the development server:
   ```bash
   npm run dev
   ```
5. Open [http://localhost:3000](http://localhost:3000) in your browser

### Database Setup

In your Supabase project, create the following tables:

1. **datasets**:
   - id (int, primary key)
   - name (text)
   - description (text, nullable)
   - type (text)
   - table_name (text, nullable)
   - number_of_datapoints (int)
   - owner_id (int)
   - created_at (timestamp)
   - updated_at (timestamp)

2. **chats**:
   - id (int, primary key)
   - title (text)
   - dataset_id (int, nullable)
   - table_name (text, nullable)
   - owner_id (int)
   - created_at (timestamp)
   - updated_at (timestamp)

3. **messages**:
   - id (int, primary key)
   - content (text)
   - role (text)
   - timestamp (timestamp)
   - chat_id (int, foreign key to chats.id)

## Usage

### Uploading a Dataset

1. Navigate to the Datasets page
2. Click "Add Dataset"
3. Upload a CSV file
4. Provide a name and description for your dataset
5. Click "Upload"

### Chatting with Your Data

1. Navigate to the Datasets page
2. Click on a dataset to open the chat interface
3. Ask questions about your data, such as:
   - "What columns are in this table?"
   - "Show me the top 5 records by age"
   - "Find users where age is greater than 30"
4. The AI will use function calling to retrieve the appropriate data and provide a natural language response

### Function Calling Examples

The AI can perform various database operations through function calling:

```python
# Get columns from a table
get_table_columns({"table_name": "users"})

# Query data with filters
query_table_data({
    "table_name": "users",
    "query": "Find users where age is greater than 30",
    "filters": {
        "field": "age",
        "value": 30,
        "operator": "greater_than"
    }
})

# Check dataset storage type
check_dataset_storage({"dataset_id": "123e4567-e89b-12d3-a456-426614174000"})

# Get column recommendations for wide datasets
get_column_recommendations({"query_text": "Find columns related to temperature"})

# Query a DuckDB dataset
query_duckdb_dataset({
    "dataset_id": "123e4567-e89b-12d3-a456-426614174000",
    "query_text": "SELECT * FROM dataset_table LIMIT 10"
})
```

## Wide CSV Processing

SAPDO now supports processing CSV files with thousands of columns, which exceeds the column limit of PostgreSQL/Supabase (1,600 columns). The wide CSV processor uses:

- **DuckDB**: A high-performance analytical database that can efficiently handle wide tables
- **Parquet**: A columnar storage format that provides efficient storage and retrieval
- **SQLite**: For storing metadata about datasets and columns
- **Vector Store**: For semantic search of columns

### How It Works

1. When a CSV file is uploaded, the system checks the number of columns:
   - If the file has fewer than 1,600 columns, it uses the standard Supabase processing
   - If the file has more than 1,600 columns, it uses the wide CSV processor

2. The wide CSV processor:
   - Processes the CSV file in chunks to avoid memory issues
   - Converts the data to Parquet format for efficient storage
   - Stores metadata about the dataset and columns in SQLite
   - Creates embeddings for columns to enable semantic search

3. The data can then be queried using:
   - SQL queries via DuckDB
   - Natural language queries via the vector store

For more details, see the [data/README.md](data/README.md) file.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
