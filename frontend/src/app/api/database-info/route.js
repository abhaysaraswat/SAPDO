'use server';

import { NextResponse } from 'next/server';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function GET(request) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const id = searchParams.get('id');
    
    let url = `${API_BASE_URL}/api/database-info`;
    if (id) {
      url = `${API_BASE_URL}/api/database-info/${id}`;
    }
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`Error fetching database info: ${response.statusText}`);
    }
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error in database-info GET route:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to fetch database info' },
      { status: 500 }
    );
  }
}

export async function POST(request) {
  try {
    const body = await request.json();
    
    const response = await fetch(`${API_BASE_URL}/api/database-info`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });
    
    if (!response.ok) {
      throw new Error(`Error creating database info: ${response.statusText}`);
    }
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error in database-info POST route:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to create database info' },
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
    
    const response = await fetch(`${API_BASE_URL}/api/database-info/${id}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`Error deleting database info: ${response.statusText}`);
    }
    
    return NextResponse.json({ message: 'Database info deleted successfully' });
  } catch (error) {
    console.error('Error in database-info DELETE route:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to delete database info' },
      { status: 500 }
    );
  }
}
