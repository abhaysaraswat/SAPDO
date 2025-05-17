'use server';

import { NextResponse } from 'next/server';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function GET(request) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const id = searchParams.get('id');
    const limit = searchParams.get('limit') || 10;
    
    if (!id) {
      return NextResponse.json(
        { error: 'Dataset ID is required' },
        { status: 400 }
      );
    }
    
    const response = await fetch(`${API_BASE_URL}/api/datasets/${id}/preview?limit=${limit}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`Error fetching dataset preview: ${response.statusText}`);
    }
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error in dataset preview GET route:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to fetch dataset preview' },
      { status: 500 }
    );
  }
}
