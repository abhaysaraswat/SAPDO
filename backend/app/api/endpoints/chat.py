from fastapi import APIRouter, HTTPException, status, Body, Query
from typing import List, Optional
from datetime import datetime
import os
import json

from ...schemas.chat import Chat, ChatCreate, ChatList, Message, MessageBase
from ...core.supabase import get_supabase_client
from ...core.llama_index_utils import query_database
from ...core.function_calling import FUNCTION_SCHEMAS, FUNCTION_MAP

router = APIRouter()


@router.get("/", response_model=ChatList)
async def get_chats(
    skip: int = 0,
    limit: int = 100,
    dataset_id: Optional[int] = None
):
    """
    Get all chats with optional pagination and filtering by dataset.
    """
    supabase = get_supabase_client()
    
    # Start query
    query = supabase.table("chats")
    
    # Filter by dataset if provided
    if dataset_id is not None:
        query = query.eq("dataset_id", dataset_id)
    
    # Get total count
    count_response = query.select("id", count="exact").execute()
    total = count_response.count
    
    # Get paginated results
    response = query.select("*").range(skip, skip + limit - 1).order("updated_at", desc=True).execute()
    
    return {
        "chats": response.data,
        "total": total
    }


@router.post("/", response_model=Chat, status_code=status.HTTP_201_CREATED)
async def create_chat(chat: ChatCreate):
    """
    Create a new chat.
    """
    supabase = get_supabase_client()
    
    # Set default title if not provided
    title = chat.title
    if not title and chat.dataset_id:
        # Try to get dataset name
        dataset_response = supabase.table("datasets").select("name").eq("id", chat.dataset_id).execute()
        if dataset_response.data:
            title = f"Chat about {dataset_response.data[0]['name']}"
        else:
            title = "New Chat"
    
    # Insert chat
    now = datetime.utcnow().isoformat()
    response = supabase.table("chats").insert({
        "title": title,
        "dataset_id": chat.dataset_id,
        "table_name": chat.table_name,
        "created_at": now,
        "updated_at": now,
        "owner_id": 1  # Hardcoded for now, would come from auth in real app
    }).execute()
    
    if not response.data:
        raise HTTPException(status_code=500, detail="Failed to create chat")
    
    chat_id = response.data[0]["id"]
    messages_data = []
    
    # Add initial user message if provided
    if chat.messages and len(chat.messages) > 0:
        for msg in chat.messages:
            user_message = {
                "content": msg.content,
                "role": msg.role,
                "timestamp": now,
                "chat_id": chat_id,
                "table_name": msg.table_name or chat.table_name
            }
            
            user_msg_response = supabase.table("messages").insert(user_message).execute()
            
            if user_msg_response.data:
                messages_data.append(user_msg_response.data[0])
                
                # If this is a user message, generate an AI response
                if msg.role == "user":
                    # Generate AI response using function calling
                    ai_response_text = generate_ai_response(msg.content, chat.table_name)
                    
                    # Insert AI response
                    ai_message = {
                        "content": ai_response_text,
                        "role": "assistant",
                        "timestamp": datetime.utcnow().isoformat(),
                        "chat_id": chat_id
                    }
                    
                    ai_msg_response = supabase.table("messages").insert(ai_message).execute()
                    
                    if ai_msg_response.data:
                        messages_data.append(ai_msg_response.data[0])
    else:
        # Add initial assistant message if no messages provided
        initial_message = {
            "content": "Hello! I'm your AI assistant. How can I help you today?",
            "role": "assistant",
            "timestamp": now,
            "chat_id": chat_id
        }
        
        message_response = supabase.table("messages").insert(initial_message).execute()
        
        if message_response.data:
            messages_data.append(message_response.data[0])
    
    # Return the chat with all messages
    chat_data = response.data[0]
    chat_data["messages"] = messages_data
    
    return chat_data


@router.get("/{chat_id}", response_model=Chat)
async def get_chat(chat_id: int):
    """
    Get a specific chat by ID, including its messages.
    """
    supabase = get_supabase_client()
    
    # Get the chat
    chat_response = supabase.table("chats").select("*").eq("id", chat_id).execute()
    
    if not chat_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    
    chat = chat_response.data[0]
    
    # Get the messages for this chat
    messages_response = supabase.table("messages").select("*").eq("chat_id", chat_id).order("timestamp").execute()
    
    chat["messages"] = messages_response.data
    
    return chat

@router.post("/messages",response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_message(
    message: MessageBase
):
    """
    Add a new message to a chat and get an AI response.
    """
    supabase = get_supabase_client()
    
    # Check if chat exists
    
    table_name = message.table_name
    
    # Insert user message
    now = datetime.utcnow().isoformat()
    
    formatted_messages = []
    for msg in message.messages:
        # Check if content is a list (has attachments)
        if isinstance(msg.content, list):
            # For messages with file attachments, format according to OpenAI's requirements
            content_items = []
            
            formatted_messages.append({
                "role": msg.role,
                "content": content_items
            })
        else:
            # For simple text messages
            formatted_messages.append({
                "role": msg.role,
                "content": msg.content
            })

    print(formatted_messages)
    # Generate AI response using function calling
    ai_response_text = generate_ai_response(formatted_messages, table_name)
    
    
    if not ai_response_text:
        raise HTTPException(status_code=500, detail="Failed to create AI response")
        
    # Return the AI message
    return {
        "content": ai_response_text,
        "role": "assistant",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/messages", response_model=dict, status_code=status.HTTP_200_OK)
async def create_direct_message(
    message: MessageBase
):
    """
    Process a message directly without storing it in a chat.
    This is useful for one-off queries or when a chat hasn't been created yet.
    """
    # Generate AI response using function calling
    ai_response_text = generate_ai_response(message.content, message.table_name)
    
    # Return the response as a simple object
    return {
        "content": ai_response_text,
        "role": "assistant",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat(chat_id: int):
    """
    Delete a chat and all its messages.
    """
    supabase = get_supabase_client()
    
    # Check if chat exists
    chat_response = supabase.table("chats").select("*").eq("id", chat_id).execute()
    
    if not chat_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    
    # Delete all messages for this chat
    supabase.table("messages").delete().eq("chat_id", chat_id).execute()
    
    # Delete the chat
    supabase.table("chats").delete().eq("id", chat_id).execute()
    
    return None


def generate_ai_response(messages: str, table_name: Optional[str] = None) -> str:
    """
    Generate an AI response based on the user's message using OpenAI function calling.
    
    Args:
        user_message: The message from the user
        table_name: Optional table name to query directly
        
    Returns:
        The AI response text
    """
    try:
        from openai import OpenAI
        
        client = OpenAI()
        
        # Initial message to the model
        
        # If table_name is provided, add it to the system message
        if table_name:
            messages.insert(0, {
                "role": "system", 
                "content": f"You are an AI assistant that helps users query data from the '{table_name}' table. Use the provided functions to get information about the table structure and to query data."
            })
        
        # First, call the model to see if it wants to use a function
        response = client.responses.create(
            model="gpt-4.1",
            input=messages,
            tools=FUNCTION_SCHEMAS
        )
        
        # Check if the model wants to call a function
        if response.output and any(item.type == "function_call" for item in response.output):
            # Process each function call
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
            
            # Return the final text response
            return final_response.output_text
        else:
            # If no function was called, return the original response
            return response.output_text
    except Exception as e:
        # Fallback response in case of error
        print(f"Error generating AI response: {str(e)}")
        return f"I'm sorry, I encountered an error while processing your request. Please try again or ask a different question."
