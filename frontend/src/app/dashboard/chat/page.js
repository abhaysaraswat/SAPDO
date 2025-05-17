'use client';

import { useState, useEffect } from 'react';
import { useSearchParams, useParams } from 'next/navigation';
import { Box } from '@mui/material';
import ChatInterface from '@/components/chat/ChatInterface';

export default function ChatPage() {
  const searchParams = useSearchParams();
  const params = useParams();
  const [dataset, setDataset] = useState(null);
  
  useEffect(() => {
    // Try to get dataset from URL parameters in the new format
    const datasetId = params.id;
    const datasetName = searchParams.get('name');
    const tableName = searchParams.get('table');
    
    if (datasetId && datasetName && tableName) {
      setDataset({
        id: datasetId,
        name: datasetName,
        table_name: tableName
      });
      return;
    }
    
    // Fallback to the old format for backward compatibility
    const datasetParam = searchParams.get('dataset');
    if (datasetParam) {
      try {
        const parsedDataset = JSON.parse(decodeURIComponent(datasetParam));
        setDataset(parsedDataset);
      } catch (error) {
        console.error('Error parsing dataset parameter:', error);
      }
    }
  }, [searchParams, params]);
  
  return (
    <Box sx={{ 
      height: '100%', 
      display: 'flex', 
      flexDirection: 'column',
      p: 0
    }}>
      <ChatInterface dataset={dataset} />
    </Box>
  );
}
