'use client';

import { useState } from 'react';
import { 
  Drawer,
  IconButton,
  Typography,
  Box,
  Stepper,
  Step,
  StepLabel,
  TextField,
  Button,
  Paper,
  Divider
} from '@mui/material';
import { 
  Close as CloseIcon,
  CloudUpload as UploadIcon,
  ArrowForward as ArrowForwardIcon
} from '@mui/icons-material';
import FileUpload from './FileUpload';

const steps = ['Setup', 'Upload'];

export default function DatasetUploadDialog({ open, onClose }) {
  const [activeStep, setActiveStep] = useState(0);
  const [datasetName, setDatasetName] = useState('');
  const [datasetDescription, setDatasetDescription] = useState('');
  const [nameError, setNameError] = useState('');
  const [file, setFile] = useState(null);
  const [databaseInfoId, setDatabaseInfoId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleNext = async () => {
    if (activeStep === 0) {
      // Validate dataset name
      if (!datasetName.trim()) {
        setNameError('Name is required');
        return;
      }
      setNameError('');
      
      // Create database_info record
      setIsLoading(true);
      setError('');
      
      try {
        const response = await fetch('/api/database-info', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            name: datasetName,
            description: datasetDescription || undefined,
          }),
        });
        
        if (!response.ok) {
          throw new Error('Failed to create database info');
        }
        
        const data = await response.json();
        setDatabaseInfoId(data.id);
        setActiveStep((prevStep) => prevStep + 1);
      } catch (err) {
        setError('Failed to create database record. Please try again.');
        console.error('Error creating database info:', err);
      } finally {
        setIsLoading(false);
      }
    } else {
      setActiveStep((prevStep) => prevStep + 1);
    }
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };

  const handleFileUpload = async (uploadedFile) => {
    setFile(uploadedFile);
    setIsLoading(true);
    setError('');
    
    try {
      // Create form data with file and metadata
      const formData = new FormData();
      formData.append('file', uploadedFile);
      formData.append('name', datasetName);
      
      if (datasetDescription) {
        formData.append('description', datasetDescription);
      }
      
      if (databaseInfoId) {
        formData.append('database_info_id', databaseInfoId);
      }
      
      // Upload file to backend
      const response = await fetch('/api/datasets/upload', {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error('Failed to upload file');
      }
      
      // Close dialog on success
      onClose();
    } catch (err) {
      setError('Failed to upload file. Please try again.');
      console.error('Error uploading file:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClose = () => {
    // Reset state
    setActiveStep(0);
    setDatasetName('');
    setDatasetDescription('');
    setNameError('');
    setFile(null);
    onClose();
  };

  return (
    <Drawer 
      anchor="right"
      open={open} 
      onClose={handleClose}
      SlideProps={{
        direction: 'left' // Makes it slide from right to left
      }}
      PaperProps={{
        sx: {
          width: 500,
          boxShadow: '0 10px 40px rgba(0,0,0,0.1)',
          borderRadius: 0 // Make corners sharp
        }
      }}
    >
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        p: 3,
        pb: 2
      }}>
        <Typography variant="h6" fontWeight="bold">Create dataset</Typography>
        <IconButton onClick={handleClose} size="small" disabled={isLoading}>
          <CloseIcon />
        </IconButton>
      </Box>

      <Divider />

      <Box sx={{ p: 0, height: '100%' }}>
        <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
          {/* Steps indicator */}
          <Box sx={{ 
            p: 3,
            pb: 0
          }}>
            <Stepper 
              activeStep={activeStep} 
              sx={{
                '& .MuiStepLabel-label': {
                  fontWeight: 500,
                },
                '& .MuiStepLabel-label.Mui-active': {
                  fontWeight: 600,
                  color: 'primary.main'
                },
                '& .MuiStepConnector-line': {
                  minWidth: '10px', // Make the connector line even smaller
                  borderTopWidth: 1, // Make the line thinner
                },
                '& .MuiStep-root': {
                  padding: 0, // Remove padding from steps
                },
                '& .MuiStepConnector-root': {
                  margin: '0 4px', // Reduce margin around connector
                }
              }}
              connector={<span style={{ width: 10, borderTop: '1px solid #bdbdbd', margin: '0 4px' }} />} // Custom minimal connector
            >
              {steps.map((label) => (
                <Step key={label}>
                  <StepLabel>{label}</StepLabel>
                </Step>
              ))}
            </Stepper>
          </Box>

          {/* Main content area */}
          <Box sx={{ flexGrow: 1, p: 4 }}>
            {error && (
              <Box sx={{ mb: 3, p: 2, bgcolor: '#FFEBEE', color: '#D32F2F', borderRadius: 0 }}>
                <Typography variant="body2">{error}</Typography>
              </Box>
            )}
            {activeStep === 0 ? (
              // Setup step
              <Box>
                <Typography variant="h6" fontWeight="bold" sx={{ mb: 3 }}>
                  Configure dataset
                </Typography>

                <TextField
                  label="Name *"
                  fullWidth
                  value={datasetName}
                  onChange={(e) => setDatasetName(e.target.value)}
                  error={!!nameError}
                  helperText={nameError || "For example: My favorite books"}
                  sx={{ mb: 3 }}
                />

                <TextField
                  label="Description"
                  fullWidth
                  multiline
                  rows={4}
                  value={datasetDescription}
                  onChange={(e) => setDatasetDescription(e.target.value)}
                  helperText="For example: The books that I've read multiple times"
                />

                <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
                  <Button 
                    onClick={handleClose}
                    disabled={isLoading}
                    sx={{ borderRadius: 0 }}
                  >
                    Cancel
                  </Button>
                  <Button 
                    variant="contained" 
                    onClick={handleNext}
                    endIcon={<ArrowForwardIcon />}
                    disabled={isLoading}
                    sx={{ borderRadius: 0 }}
                  >
                    {isLoading ? 'Creating...' : 'Continue'}
                  </Button>
                </Box>
              </Box>
            ) : (
              // Upload step
              <Box>
                <Typography variant="h6" fontWeight="bold" sx={{ mb: 3 }}>
                  Upload
                </Typography>

                <Paper
                  variant="outlined"
                  sx={{
                    p: 4,
                    textAlign: 'center',
                    borderStyle: 'dashed',
                    borderWidth: 2,
                    borderColor: 'divider',
                    bgcolor: 'background.default',
                    borderRadius: 0, // Make corners sharp
                    mb: 3
                  }}
                >
                  <UploadIcon fontSize="large" color="primary" sx={{ mb: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    Drag and drop your files here
                  </Typography>
                  <Typography variant="body2" color="textSecondary" gutterBottom sx={{ mb: 2 }}>
                    or
                  </Typography>
                  <Button
                    variant="contained"
                    component="label"
                    disabled={isLoading}
                    sx={{ 
                      textTransform: 'none',
                      borderRadius: 0 // Make corners sharp
                    }}
                  >
                    {isLoading ? 'Uploading...' : 'Attach file'}
                    <input
                      type="file"
                      hidden
                      accept=".csv,.xlsx,.xls"
                      onChange={(e) => {
                        if (e.target.files && e.target.files[0]) {
                          handleFileUpload(e.target.files[0]);
                        }
                      }}
                    />
                  </Button>
                </Paper>

                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Button 
                    onClick={handleBack}
                    disabled={isLoading}
                    sx={{ borderRadius: 0 }}
                  >
                    Back
                  </Button>
                </Box>
              </Box>
            )}
          </Box>
        </Box>
      </Box>
    </Drawer>
  );
}
