'use client';

import { useState } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Button,
  Container,
  Alert,
  Snackbar
} from '@mui/material';
import { 
  ArrowBack as BackIcon,
  ContentCopy as CloneIcon
} from '@mui/icons-material';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import ExistingDatasetSelector from '@/components/dataset/ExistingDatasetSelector';

export default function ExistingDatasetPage() {
  const router = useRouter();
  const [selectedDatasets, setSelectedDatasets] = useState([]);
  const [showSuccess, setShowSuccess] = useState(false);
  
  const handleSelectDatasets = (datasets) => {
    setSelectedDatasets(datasets);
    setShowSuccess(true);
    
    // In a real app, we would make an API call to clone the datasets
    // For demo purposes, we'll just show a success message and redirect after a delay
    setTimeout(() => {
      router.push('/dashboard/dataset');
    }, 2000);
  };
  
  return (
    <Container maxWidth="lg">
      <Box sx={{ mb: 4 }}>
        <Button
          component={Link}
          href="/dashboard/dataset"
          startIcon={<BackIcon />}
          sx={{ mb: 2 }}
        >
          Back to Datasets
        </Button>
        
        <Typography variant="h4" gutterBottom>
          Add from Existing Datasets
        </Typography>
        <Typography variant="body1" color="textSecondary">
          Select one or more existing datasets to add to your workspace
        </Typography>
      </Box>
      
      <Paper sx={{ p: 3 }}>
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Available Datasets
          </Typography>
          <Typography variant="body2" color="textSecondary">
            Select the datasets you want to add to your workspace. You can select multiple datasets.
          </Typography>
        </Box>
        
        <ExistingDatasetSelector onSelect={handleSelectDatasets} />
        
        <Box sx={{ mt: 4 }}>
          <Alert severity="info">
            In a real application, this would allow you to:
            <ul>
              <li>Clone datasets from other projects or workspaces</li>
              <li>Import shared datasets from team members</li>
              <li>Create new datasets based on existing ones</li>
            </ul>
          </Alert>
        </Box>
      </Paper>
      
      <Snackbar
        open={showSuccess}
        autoHideDuration={6000}
        onClose={() => setShowSuccess(false)}
        message={`Added ${selectedDatasets.length} dataset(s) successfully`}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      />
    </Container>
  );
}
