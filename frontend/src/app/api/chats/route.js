import { NextResponse } from 'next/server';

/**
 * API route for creating a new chat
 */
export async function POST(request) {
  try {
    const body = await request.json();
    
    // Call the backend API
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
    const response = await fetch(`${backendUrl}/api/chat/messages`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to create chat: ${errorText}`);
    }
    
    const data = await response.json();
    
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error in chats API route:', error);
    return NextResponse.json(
      { error: 'Failed to create chat', details: error.message },
      { status: 500 }
    );
  }
}

/**
 * API route for getting all chats
 */
export async function GET(request) {
  try {
    const { searchParams } = new URL(request.url);
    const skip = searchParams.get('skip') || 0;
    const limit = searchParams.get('limit') || 100;
    const datasetId = searchParams.get('dataset_id');
    
    // Build query string
    let queryString = `?skip=${skip}&limit=${limit}`;
    if (datasetId) {
      queryString += `&dataset_id=${datasetId}`;
    }
    
    // Call the backend API
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
    const response = await fetch(`${backendUrl}/api/chats${queryString}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to get chats: ${errorText}`);
    }
    
    const data = await response.json();
    
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error in chats API route:', error);
    return NextResponse.json(
      { error: 'Failed to get chats', details: error.message },
      { status: 500 }
    );
  }
}
