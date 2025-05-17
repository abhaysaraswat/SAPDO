'use client';

import { useState } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Stepper, 
  Step, 
  StepLabel, 
  Button,
  Container,
  Grid,
  Card,
  CardContent,
  Divider,
  Alert
} from '@mui/material';
import { 
  ArrowBack as BackIcon,
  CloudUpload as UploadIcon,
  Settings as ConfigureIcon,
  Check as ConfirmIcon
} from '@mui/icons-material';
import Link from 'next/link';
import FileUpload from '@/components/dataset/FileUpload';

const steps = ['Upload File', 'Configure Dataset', 'Confirm'];

export default function UploadDatasetPage() {
  const [activeStep, setActiveStep] = useState(0);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [datasetName, setDatasetName] = useState('');
  
  const handleNext = () => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };
  
  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };
  
  const handleFileUpload = (file) => {
    setUploadedFile(file);
    setDatasetName(file.name.split('.')[0]); // Set default dataset name from filename
    handleNext();
  };
  
  const getStepContent = (step) => {
    switch (step) {
      case 0:
        return (
          <Box sx={{ mt: 4 }}>
            <Typography variant="h6" gutterBottom>
              Upload a CSV or Excel File
            </Typography>
            <Typography variant="body2" color="textSecondary" paragraph>
              Upload your dataset file. We support CSV and Excel formats.
            </Typography>
            <FileUpload onFileUpload={handleFileUpload} />
          </Box>
        );
      case 1:
        return (
          <Box sx={{ mt: 4 }}>
            <Typography variant="h6" gutterBottom>
              Configure Dataset
            </Typography>
            <Typography variant="body2" color="textSecondary" paragraph>
              Configure your dataset settings. This step would include options for:
            </Typography>
            
            <Grid container spacing={3} sx={{ mt: 2 }}>
              <Grid item xs={12}>
                <Alert severity="info">
                  This is a demo interface. In a real application, this step would include:
                  <ul>
                    <li>Column mapping</li>
                    <li>Data type selection</li>
                    <li>Preview of parsed data</li>
                    <li>Advanced configuration options</li>
                  </ul>
                </Alert>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      File Information
                    </Typography>
                    <Divider sx={{ my: 1 }} />
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="body2">
                        <strong>Filename:</strong> {uploadedFile?.name}
                      </Typography>
                      <Typography variant="body2">
                        <strong>Size:</strong> {uploadedFile ? (uploadedFile.size / 1024).toFixed(2) + ' KB' : ''}
                      </Typography>
                      <Typography variant="body2">
                        <strong>Type:</strong> {uploadedFile?.type || uploadedFile?.name.split('.').pop().toUpperCase()}
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
            
            <Box sx={{ mt: 4, display: 'flex', justifyContent: 'flex-end' }}>
              <Button onClick={handleBack} sx={{ mr: 1 }}>
                Back
              </Button>
              <Button
                variant="contained"
                color="primary"
                onClick={handleNext}
              >
                Continue
              </Button>
            </Box>
          </Box>
        );
      case 2:
        return (
          <Box sx={{ mt: 4 }}>
            <Typography variant="h6" gutterBottom>
              Confirm Dataset Creation
            </Typography>
            <Typography variant="body2" color="textSecondary" paragraph>
              Review your dataset details before creating it.
            </Typography>
            
            <Alert severity="success" sx={{ mt: 2 }}>
              Your dataset is ready to be created. In a real application, this would show a summary of the dataset configuration.
            </Alert>
            
            <Box sx={{ mt: 4, display: 'flex', justifyContent: 'flex-end' }}>
              <Button onClick={handleBack} sx={{ mr: 1 }}>
                Back
              </Button>
              <Button
                variant="contained"
                color="primary"
                component={Link}
                href="/dashboard/dataset"
              >
                Create Dataset
              </Button>
            </Box>
          </Box>
        );
      default:
        return 'Unknown step';
    }
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
          Upload Dataset
        </Typography>
        <Typography variant="body1" color="textSecondary">
          Create a new dataset by uploading a CSV or Excel file
        </Typography>
      </Box>
      
      <Paper sx={{ p: 3 }}>
        <Stepper activeStep={activeStep} alternativeLabel>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
        
        {getStepContent(activeStep)}
      </Paper>
    </Container>
  );
}
