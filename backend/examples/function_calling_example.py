"""
Example script demonstrating the OpenAI function calling feature.

This script shows how to use the function calling feature to:
1. Get columns from a database table
2. Query data from a database table
3. Query data with filters

Usage:
    python function_calling_example.py

Requirements:
    - OpenAI API key set in environment variables
    - Supabase credentials set in environment variables
"""
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
import sys
import time

# Add the parent directory to the path so we can import from the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our function calling utilities
from app.core.function_calling import FUNCTION_SCHEMAS, FUNCTION_MAP

# Load environment variables
load_dotenv()

def run_example():
    """Run the function calling example."""
    # Initialize the OpenAI client
    client = OpenAI()
    
    # Example 1: Get columns from a table
    print("\n=== Example 1: Get columns from a table ===\n")
    
    # User query that should trigger the get_table_columns function
    user_message = "What columns are in the 'dataset_abhay_8492056c' table?"
    
    # System message to provide context
    system_message = "You are an AI assistant that helps users query database tables. Use the provided functions to get information about table structure and to query data."
    
    # Initial messages
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message}
    ]
    
    # Call the model
    print(f"User: {user_message}")
    print("Calling OpenAI API...")
    
    response = client.responses.create(
        model="gpt-4.1",
        input=messages,
        tools=FUNCTION_SCHEMAS
    )

    print(response)
    
    # Process the response
    if response.output and any(item.type == "function_call" for item in response.output):
        for tool_call in response.output:
            if tool_call.type != "function_call":
                continue
                
            # Get function details
            function_name = tool_call.name
            function_args = json.loads(tool_call.arguments)
            
            print(f"\nModel decided to call function: {function_name}")
            print(f"With arguments: {json.dumps(function_args, indent=2)}")
            
            # Execute the function
            if function_name in FUNCTION_MAP:
                print(f"\nExecuting {function_name}...")
                function_result = FUNCTION_MAP[function_name](function_args)
                print(f"Function result: {function_result}")
                
                # Add the function call and result to the conversation
                messages.append(tool_call)
                messages.append({
                    "type": "function_call_output",
                    "call_id": tool_call.call_id,
                    "output": str(function_result)
                })
        
        # Call the model again with the function results
        print("\nCalling OpenAI API with function results...")
        final_response = client.responses.create(
            model="gpt-4.1",
            input=messages,
            tools=FUNCTION_SCHEMAS
        )
        
        print(f"\nFinal response: {final_response.output_text}")
    else:
        print(f"\nModel response without function call: {response.output_text}")
    
    # Example 2: Query data from a table
    print("\n\n=== Example 2: Query data from a table ===\n")
    
    # User query that should trigger the query_table_data function
    user_message = "tell me highest billing amount and its details"
    
    # Initial messages
    messages.append(
        {"role": "system", "content": system_message}
    )
    messages.append(
        {"role": "user", "content": user_message}
    )

    print(messages)
    
    # Call the model
    print(f"User: {user_message}")
    print("Calling OpenAI API...")
    
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
            
            print(f"\nModel decided to call function: {function_name}")
            print(f"With arguments: {json.dumps(function_args, indent=2)}")
            
            # Execute the function
            if function_name in FUNCTION_MAP:
                print(f"\nExecuting {function_name}...")
                function_result = FUNCTION_MAP[function_name](function_args)
                # print(f"Function result: {function_result}")
                
                # Add the function call and result to the conversation
                messages.append(tool_call)
                messages.append({
                    "type": "function_call_output",
                    "call_id": tool_call.call_id,
                    "output": str(function_result)
                })
        
        # Call the model again with the function results
        print("\nCalling OpenAI API with function results...")
        final_response = client.responses.create(
            model="gpt-4.1",
            input=messages,
            tools=FUNCTION_SCHEMAS
        )
        
        print(f"\nFinal response: {final_response.output_text}")
    else:
        print(f"\nModel response without function call: {response.output_text}")
        
    # Example 3: Query data with filters using Supabase's query builder
    # print("\n\n=== Example 3: Query data with filters using Supabase's query builder ===\n")
    
    # User query that should trigger the query_table_data function with filters
    # user_message = "Find users where age is greater than 30"
    
    # # Initial messages
    # messages = [
    #     {"role": "system", "content": system_message},
    #     {"role": "user", "content": user_message}
    # ]
    
    # # Call the model
    # print(f"User: {user_message}")
    # print("Calling OpenAI API...")
    
    # response = client.responses.create(
    #     model="gpt-4.1",
    #     input=messages,
    #     tools=FUNCTION_SCHEMAS
    # )
    
    # # Process the response
    # if response.output and any(item.type == "function_call" for item in response.output):
    #     for tool_call in response.output:
    #         if tool_call.type != "function_call":
    #             continue
                
    #         # Get function details
    #         function_name = tool_call.name
    #         function_args = json.loads(tool_call.arguments)
            
    #         print(f"\nModel decided to call function: {function_name}")
    #         print(f"With arguments: {json.dumps(function_args, indent=2)}")
            
    #         # Execute the function
    #         if function_name in FUNCTION_MAP:
    #             print(f"\nExecuting {function_name}...")
    #             function_result = FUNCTION_MAP[function_name](function_args)
    #             print(f"Function result: {function_result}")
                
    #             # Add the function call and result to the conversation
    #             messages.append(tool_call)
    #             messages.append({
    #                 "type": "function_call_output",
    #                 "call_id": tool_call.call_id,
    #                 "output": str(function_result)
    #             })
        
    #     # Call the model again with the function results
    #     print("\nCalling OpenAI API with function results...")
    #     final_response = client.responses.create(
    #         model="gpt-4.1",
    #         input=messages,
    #         tools=FUNCTION_SCHEMAS
    #     )
        
    #     print(f"\nFinal response: {final_response.output_text}")
    # else:
    #     print(f"\nModel response without function call: {response.output_text}")

if __name__ == "__main__":
    run_example()
