# Function Calling

This document explains how to use the function calling feature in the application. Function calling allows the AI model to fetch data and take actions based on user queries.

## Overview

Function calling provides a powerful and flexible way for OpenAI models to interface with your code or external services. In this application, we've implemented function calling to allow the AI to:

1. Retrieve column information from database tables
2. Run queries against database tables to retrieve data

## Implementation Details

The function calling feature is implemented in the following files:

- `backend/app/core/function_calling.py`: Defines the function schemas and implementations
- `backend/app/api/endpoints/chat.py`: Integrates function calling into the chat API
- `backend/examples/function_calling_example.py`: Provides examples of how to use the function calling feature

### Function Schemas

We've defined two function schemas:

1. `get_table_columns`: Retrieves column information for a specified database table
2. `query_table_data`: Runs a query against a database table to retrieve data

These schemas are defined in `backend/app/core/function_calling.py` and follow the OpenAI function calling schema format.

### Function Implementations

The actual function implementations are also defined in `backend/app/core/function_calling.py`. These functions:

1. Take a dictionary of arguments as input
2. Execute the appropriate logic (e.g., retrieving column information or querying data)
3. Return the results as a string

#### Supabase Query Builder

The `query_table_data` function uses Supabase's query builder API to directly query the database. This approach provides several advantages:

1. **Direct Database Access**: Uses Supabase's native query builder for efficient database access
2. **Flexible Filtering**: Supports various filter operators (equals, greater than, less than, etc.)
3. **Type-Safe Queries**: Properly formats values based on their types
4. **Error Handling**: Includes robust error handling and logging

### Integration with Chat API

The function calling feature is integrated into the chat API in `backend/app/api/endpoints/chat.py`. The `generate_ai_response` function:

1. Takes a user message and optional table name as input
2. Calls the OpenAI API with the function schemas
3. If the model decides to call a function, executes the function and returns the results
4. Calls the OpenAI API again with the function results to generate a final response
5. Returns the final response to the user

## Usage

### Basic Usage

When a user sends a message to the chat API, the model will automatically determine whether to call a function based on the message content. For example:

- "What columns are in the users table?" will trigger the `get_table_columns` function
- "Show me the top 5 users by age" will trigger the `query_table_data` function

### Example Code

Here's a simple example of how to use the function calling feature:

```python
from openai import OpenAI
import json
from app.core.function_calling import FUNCTION_SCHEMAS, FUNCTION_MAP

client = OpenAI()

# User message
user_message = "What columns are in the users table?"

# Initial messages
messages = [
    {"role": "system", "content": "You are an AI assistant that helps users query database tables."},
    {"role": "user", "content": user_message}
]

# Call the model
response = client.responses.create(
    model="gpt-4.1",
    input=messages,
    tools=FUNCTION_SCHEMAS
)

# Process the response
if response.output and any(item.type == "function_call" for item in response.output):
    for tool_call in response.output:
        if tool_call.type != "function_call":
            continue
            
        # Get function details
        function_name = tool_call.name
        function_args = json.loads(tool_call.arguments)
        
        # Execute the function
        if function_name in FUNCTION_MAP:
            function_result = FUNCTION_MAP[function_name](function_args)
            
            # Add the function call and result to the conversation
            messages.append(tool_call)
            messages.append({
                "type": "function_call_output",
                "call_id": tool_call.call_id,
                "output": str(function_result)
            })
    
    # Call the model again with the function results
    final_response = client.responses.create(
        model="gpt-4.1",
        input=messages,
        tools=FUNCTION_SCHEMAS
    )
    
    print(final_response.output_text)
else:
    print(response.output_text)
```

### Running the Example

You can run the provided example script to see the function calling feature in action:

```bash
cd backend
python examples/function_calling_example.py
```

This will run three examples:
1. Getting columns from a table
2. Querying data from a table
3. Querying data with filters using Supabase's query builder

## Extending the Feature

### Adding New Functions

To add a new function:

1. Define the function schema in `FUNCTION_SCHEMAS` in `backend/app/core/function_calling.py`
2. Implement the function in the same file
3. Add the function to the `FUNCTION_MAP` dictionary

For example, to add a function that retrieves table statistics:

```python
# Add to FUNCTION_SCHEMAS
{
    "type": "function",
    "name": "get_table_stats",
    "description": "Get statistics for a specified database table",
    "parameters": {
        "type": "object",
        "properties": {
            "table_name": {
                "type": "string",
                "description": "Name of the table to get statistics for"
            }
        },
        "required": ["table_name"],
        "additionalProperties": False
    },
    "strict": True
}

# Implement the function
def get_table_stats(args):
    """Get statistics for a specified database table."""
    table_name = args.get("table_name")
    supabase = get_supabase_client()
    
    try:
        # Implement your logic here
        # ...
        return json.dumps(stats)
    except Exception as e:
        return json.dumps({"error": str(e)})

# Add to FUNCTION_MAP
FUNCTION_MAP["get_table_stats"] = get_table_stats
```

## Best Practices

1. **Clear Function Descriptions**: Provide clear and detailed descriptions for your functions and parameters to help the model understand when to use them.
2. **Error Handling**: Always include error handling in your function implementations to gracefully handle unexpected inputs or errors.
3. **Strict Mode**: Use strict mode to ensure function calls adhere to the function schema.
4. **Testing**: Test your functions with a variety of inputs to ensure they work as expected.
5. **Logging**: Add logging to your functions to help debug issues.
6. **Use Native APIs**: When possible, use native APIs like Supabase's query builder for more efficient and reliable database access.
7. **Proper Value Formatting**: Format values based on their types and the operation being performed.

## Troubleshooting

### Common Issues

1. **Function Not Being Called**: If the model is not calling your function, check that the function description and parameter descriptions are clear and that the model understands when to use the function.
2. **Function Errors**: If your function is returning errors, check the function implementation and ensure it's handling all possible inputs correctly.
3. **Model Not Understanding Function Results**: If the model is not understanding the function results, ensure the results are formatted in a way that's easy for the model to parse and understand.

### Debugging

To debug function calling issues, you can:

1. Print the model's response to see if it's trying to call a function
2. Print the function arguments to see what the model is passing to the function
3. Print the function results to see what the function is returning
4. Print the final model response to see how it's incorporating the function results

## References

- [OpenAI Function Calling Documentation](https://platform.openai.com/docs/guides/function-calling)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
