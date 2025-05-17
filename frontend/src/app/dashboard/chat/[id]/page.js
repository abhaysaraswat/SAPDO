'use client';

import { useState, useEffect } from 'react';
import { useSearchParams, useParams } from 'next/navigation';
import { Box } from '@mui/material';
import ChatInterface from '@/components/chat/ChatInterface';

export default function ChatWithIdPage() {
  const searchParams = useSearchParams();
  const params = useParams();
  const [dataset, setDataset] = useState(null);
  
  useEffect(() => {
    // Get dataset from URL parameters
    const datasetId = params.id;
    const datasetName = searchParams.get('name');
    const tableName = searchParams.get('table');
    
    if (datasetId && datasetName && tableName) {
      setDataset({
        id: datasetId,
        name: datasetName,
        table_name: tableName
      });
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
