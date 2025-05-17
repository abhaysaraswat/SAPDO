'use client';

import { useState, useRef } from 'react';
import { 
  Box, 
  Button, 
  Typography, 
  Paper, 
  LinearProgress,
  Alert,
  Chip,
  Stack,
  IconButton
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Delete as DeleteIcon,
  FilePresent as FileIcon,
  Description as CsvIcon,
  TableChart as ExcelIcon
} from '@mui/icons-material';

export default function FileUpload({ onFileUpload }) {
  const [file, setFile] = useState(null);
  const [error, setError] = useState('');
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const fileInputRef = useRef(null);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    
    if (!selectedFile) {
      return;
    }
    
    // Check file type
    const fileType = selectedFile.name.split('.').pop().toLowerCase();
    if (!['csv', 'xlsx', 'xls'].includes(fileType)) {
      setError('Please upload a CSV or Excel file');
      setFile(null);
      return;
    }
    
    // Check file size (limit to 10MB)
    if (selectedFile.size > 10 * 1024 * 1024) {
      setError('File size should be less than 10MB');
      setFile(null);
      return;
    }
    
    setError('');
    setFile(selectedFile);
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file to upload');
      return;
    }
    
    setUploading(true);
    setUploadProgress(0);
    
    // Simulate upload progress
    const interval = setInterval(() => {
      setUploadProgress((prevProgress) => {
        const newProgress = prevProgress + 10;
        if (newProgress >= 100) {
          clearInterval(interval);
          return 100;
        }
        return newProgress;
      });
    }, 500);
    
    // Simulate API call
    setTimeout(() => {
      clearInterval(interval);
      setUploading(false);
      setUploadProgress(100);
      
      // Call the callback with the file
      if (onFileUpload) {
        onFileUpload(file);
      }
      
      // Reset after 1 second
      setTimeout(() => {
        setFile(null);
        setUploadProgress(0);
      }, 1000);
    }, 5000);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    
    if (event.dataTransfer.files && event.dataTransfer.files.length > 0) {
      const droppedFile = event.dataTransfer.files[0];
      
      // Check file type
      const fileType = droppedFile.name.split('.').pop().toLowerCase();
      if (!['csv', 'xlsx', 'xls'].includes(fileType)) {
        setError('Please upload a CSV or Excel file');
        return;
      }
      
      // Check file size (limit to 10MB)
      if (droppedFile.size > 10 * 1024 * 1024) {
        setError('File size should be less than 10MB');
        return;
      }
      
      setError('');
      setFile(droppedFile);
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
  };

  const getFileIcon = () => {
    if (!file) return null;
    
    const fileType = file.name.split('.').pop().toLowerCase();
    if (fileType === 'csv') {
      return <CsvIcon fontSize="large" color="primary" />;
    } else if (['xlsx', 'xls'].includes(fileType)) {
      return <ExcelIcon fontSize="large" color="success" />;
    }
    
    return <FileIcon fontSize="large" />;
  };

  return (
    <Box sx={{ width: '100%' }}>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      <Paper
        variant="outlined"
        sx={{
          p: 3,
          textAlign: 'center',
          borderStyle: 'dashed',
          borderWidth: 2,
          borderColor: 'divider',
          bgcolor: 'background.default',
          cursor: 'pointer',
          '&:hover': {
            borderColor: 'primary.main',
            bgcolor: 'action.hover',
          },
        }}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          accept=".csv,.xlsx,.xls"
          style={{ display: 'none' }}
        />
        
        {!file && !uploading && (
          <>
            <UploadIcon fontSize="large" color="primary" sx={{ mb: 1 }} />
            <Typography variant="h6" gutterBottom>
              Drag and drop your file here
            </Typography>
            <Typography variant="body2" color="textSecondary" gutterBottom>
              or click to browse
            </Typography>
            <Stack direction="row" spacing={1} justifyContent="center" sx={{ mt: 1 }}>
              <Chip label="CSV" size="small" icon={<CsvIcon />} />
              <Chip label="Excel" size="small" icon={<ExcelIcon />} />
            </Stack>
          </>
        )}
        
        {file && !uploading && (
          <Box sx={{ textAlign: 'center' }}>
            {getFileIcon()}
            <Typography variant="subtitle1" gutterBottom>
              {file.name}
            </Typography>
            <Typography variant="body2" color="textSecondary" gutterBottom>
              {(file.size / 1024).toFixed(2)} KB
            </Typography>
            
            <Stack direction="row" spacing={2} justifyContent="center" sx={{ mt: 2 }}>
              <Button
                variant="contained"
                color="primary"
                startIcon={<UploadIcon />}
                onClick={(e) => {
                  e.stopPropagation();
                  handleUpload();
                }}
              >
                Upload
              </Button>
              <Button
                variant="outlined"
                color="error"
                startIcon={<DeleteIcon />}
                onClick={(e) => {
                  e.stopPropagation();
                  setFile(null);
                }}
              >
                Remove
              </Button>
            </Stack>
          </Box>
        )}
        
        {uploading && (
          <Box sx={{ width: '100%', textAlign: 'center' }}>
            <Typography variant="subtitle1" gutterBottom>
              Uploading {file.name}...
            </Typography>
            <LinearProgress 
              variant="determinate" 
              value={uploadProgress} 
              sx={{ height: 10, borderRadius: 5, my: 2 }} 
            />
            <Typography variant="body2" color="textSecondary">
              {uploadProgress}% Complete
            </Typography>
          </Box>
        )}
      </Paper>
      
      <Typography variant="caption" color="textSecondary" sx={{ mt: 1, display: 'block' }}>
        Supported formats: CSV, Excel (XLSX, XLS) • Max file size: 10MB
      </Typography>
    </Box>
  );
}
