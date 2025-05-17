'use server';

import { NextResponse } from 'next/server';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function POST(request) {
  try {
    // Get the form data from the request
    const formData = await request.formData();
    
    // Forward the request to the backend
    const response = await fetch(`${API_BASE_URL}/api/datasets/upload`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      throw new Error(`Error uploading dataset: ${response.statusText}`);
    }
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error in datasets upload POST route:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to upload dataset' },
      { status: 500 }
    );
  }
}
