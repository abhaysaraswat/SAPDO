'use server';

import { NextResponse } from 'next/server';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function GET(request) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const id = searchParams.get('id');
    const skip = searchParams.get('skip') || 0;
    const limit = searchParams.get('limit') || 100;
    const search = searchParams.get('search');
    const database_info_id = searchParams.get('database_info_id');
    
    let url;
    if (id) {
      url = `${API_BASE_URL}/api/datasets/${id}`;
    } else {
      url = `${API_BASE_URL}/api/datasets?skip=${skip}&limit=${limit}`;
      if (search) {
        url += `&search=${encodeURIComponent(search)}`;
      }
      if (database_info_id) {
        url += `&database_info_id=${encodeURIComponent(database_info_id)}`;
      }
    }
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`Error fetching datasets: ${response.statusText}`);
    }
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error in datasets GET route:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to fetch datasets' },
      { status: 500 }
    );
  }
}

export async function POST(request) {
  try {
    const body = await request.json();
    
    const response = await fetch(`${API_BASE_URL}/api/datasets`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });
    
    if (!response.ok) {
      throw new Error(`Error creating dataset: ${response.statusText}`);
    }
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error in datasets POST route:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to create dataset' },
      { status: 500 }
    );
  }
}

export async function DELETE(request) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const id = searchParams.get('id');
    
    if (!id) {
      return NextResponse.json(
        { error: 'ID is required for DELETE operation' },
        { status: 400 }
      );
    }
    
    const response = await fetch(`${API_BASE_URL}/api/datasets/${id}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`Error deleting dataset: ${response.statusText}`);
    }
    
    return NextResponse.json({ message: 'Dataset deleted successfully' });
  } catch (error) {
    console.error('Error in datasets DELETE route:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to delete dataset' },
      { status: 500 }
    );
  }
}
