import { NextResponse } from 'next/server';

/**
 * Redirect to /api/chats endpoint
 */
export async function POST(request) {
  try {
    const body = await request.json();
    const { content, table_name } = body;
    
    // Create a messages array with the user message
    const messages = [
      {
        role: 'user',
        content: content
      }
    ];
    
    // Call the /api/chats endpoint instead
    const response = await fetch(`${request.nextUrl.origin}/api/chats`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        table_name,
        messages
      }),
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to get response from chats endpoint: ${errorText}`);
    }
    
    const data = await response.json();
    
    // Find the assistant message in the response
    let assistantMessage = null;
    if (data.messages && data.messages.length > 0) {
      const assistantMessages = data.messages.filter(msg => msg.role === 'assistant');
      if (assistantMessages.length > 0) {
        assistantMessage = assistantMessages[assistantMessages.length - 1];
      }
    }
    
    if (!assistantMessage) {
      throw new Error('No assistant message found in response');
    }
    
    // Return just the assistant message
    return NextResponse.json({
      content: assistantMessage.content,
      role: assistantMessage.role,
      timestamp: assistantMessage.timestamp
    });
  } catch (error) {
    console.error('Error in chat API route:', error);
    return NextResponse.json(
      { error: 'Failed to process chat message', details: error.message },
      { status: 500 }
    );
  }
}
