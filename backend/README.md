# SAPDO API Backend

This is the FastAPI backend for the SAPDO AI platform. It provides APIs for dataset management and chat functionality, with Supabase integration for data storage.

## Features

- **Dataset Management**: Upload, list, and manage datasets
- **CSV Processing**: Automatically convert CSV files to Supabase tables
- **Chat Interface**: Create and manage chat conversations with AI

## Setup

### Prerequisites

- Python 3.8+
- Supabase account and project

### Installation

1. Clone the repository
2. Navigate to the backend directory:
   ```
   cd backend
   ```
3. Create a virtual environment:
   ```
   python -m venv venv
   ```
4. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
5. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

### Configuration

Create a `.env` file in the backend directory with the following variables:

```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
SECRET_KEY=your_secret_key_for_jwt
```

### Database Setup

In your Supabase project, create the following tables:

1. **datasets**:
   - id (int, primary key)
   - name (text)
   - description (text, nullable)
   - type (text)
   - table_name (text, nullable)
   - number_of_datapoints (int)
   - number_of_experiments (int)
   - number_of_optimizations (int)
   - derived_datasets (int)
   - owner_id (int)
   - created_at (timestamp)
   - updated_at (timestamp)

2. **chats**:
   - id (int, primary key)
   - title (text)
   - dataset_id (int, nullable)
   - owner_id (int)
   - created_at (timestamp)
   - updated_at (timestamp)

3. **messages**:
   - id (int, primary key)
   - content (text)
   - role (text)
   - timestamp (timestamp)
   - chat_id (int, foreign key to chats.id)

## Running the Server

Start the FastAPI server:

```
cd backend
python run.py
```

Alternatively, you can use uvicorn directly:

```
cd backend
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

## API Documentation

Once the server is running, you can access the API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## CSV to Supabase Table Conversion

When a CSV file is uploaded:

1. The file is parsed using pandas
2. Column names are cleaned (spaces replaced with underscores, special characters removed)
3. A new table is created in Supabase with appropriate column types
4. The data is inserted into the table
5. A reference to the table is stored in the datasets table

## Development

### Project Structure

- `main.py`: FastAPI application entry point
- `app/api/`: API routes and endpoints
- `app/schemas/`: Pydantic models for request/response validation
- `app/core/`: Core functionality and utilities
