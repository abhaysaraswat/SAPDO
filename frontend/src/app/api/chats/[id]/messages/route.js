import { NextResponse } from 'next/server';

/**
 * API route for creating a new message in a chat
 */
export async function POST(request, { params }) {
  try {
    const chatId = params.id;
    const body = await request.json();
    
    // Call the backend API
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
    const response = await fetch(`${backendUrl}/api/chats/${chatId}/messages`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to create message: ${errorText}`);
    }
    
    const data = await response.json();
    
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error in chat messages API route:', error);
    return NextResponse.json(
      { error: 'Failed to create message', details: error.message },
      { status: 500 }
    );
  }
}
