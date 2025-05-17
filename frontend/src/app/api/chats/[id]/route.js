import { NextResponse } from 'next/server';

/**
 * API route for getting a specific chat
 */
export async function GET(request, { params }) {
  try {
    const chatId = params.id;
    
    // Call the backend API
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
    const response = await fetch(`${backendUrl}/api/chats/${chatId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to get chat: ${errorText}`);
    }
    
    const data = await response.json();
    
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error in chat API route:', error);
    return NextResponse.json(
      { error: 'Failed to get chat', details: error.message },
      { status: 500 }
    );
  }
}

/**
 * API route for deleting a chat
 */
export async function DELETE(request, { params }) {
  try {
    const chatId = params.id;
    
    // Call the backend API
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
    const response = await fetch(`${backendUrl}/api/chats/${chatId}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to delete chat: ${errorText}`);
    }
    
    return new NextResponse(null, { status: 204 });
  } catch (error) {
    console.error('Error in chat API route:', error);
    return NextResponse.json(
      { error: 'Failed to delete chat', details: error.message },
      { status: 500 }
    );
  }
}
