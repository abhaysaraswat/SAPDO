'use client';

import { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  List, 
  ListItem, 
  ListItemText, 
  ListItemIcon,
  ListItemButton,
  Checkbox,
  TextField,
  InputAdornment,
  Button,
  Divider,
  Chip,
  CircularProgress
} from '@mui/material';
import {
  Search as SearchIcon,
  ContentCopy as CloneIcon,
  Check as CheckIcon,
  Storage as StorageIcon
} from '@mui/icons-material';

export default function ExistingDatasetSelector({ onSelect, databaseInfoId }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDatasets, setSelectedDatasets] = useState([]);
  const [datasets, setDatasets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    const fetchDatasets = async () => {
      try {
        setLoading(true);
        let url = '/api/datasets?limit=100';
        
        if (searchQuery) {
          url += `&search=${encodeURIComponent(searchQuery)}`;
        }
        
        if (databaseInfoId) {
          url += `&database_info_id=${encodeURIComponent(databaseInfoId)}`;
        }
        
        const response = await fetch(url);
        
        if (!response.ok) {
          throw new Error('Failed to fetch datasets');
        }
        
        const data = await response.json();
        setDatasets(data.datasets || []);
      } catch (err) {
        console.error('Error fetching datasets:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    
    fetchDatasets();
  }, [searchQuery, databaseInfoId]);
  
  // Filter datasets based on search query (already handled by API, but keep for client-side filtering)
  const filteredDatasets = datasets;
  
  const handleToggle = (datasetId) => {
    const currentIndex = selectedDatasets.indexOf(datasetId);
    const newSelected = [...selectedDatasets];
    
    if (currentIndex === -1) {
      newSelected.push(datasetId);
    } else {
      newSelected.splice(currentIndex, 1);
    }
    
    setSelectedDatasets(newSelected);
  };
  
  const handleSelectDatasets = () => {
    if (selectedDatasets.length === 0) {
      return;
    }
    
    const selectedItems = datasets.filter(dataset => 
      selectedDatasets.includes(dataset.id)
    );
    
    if (onSelect) {
      onSelect(selectedItems);
    }
  };
  
  // Helper function to navigate to chat with a dataset using the new URL format
  const navigateToChatWithDataset = (dataset) => {
    // Use the new URL format: /dashboard/chat/{datasetId}?name={datasetName}&table={tableName}
    window.location.href = `/dashboard/chat/${dataset.id}?name=${encodeURIComponent(dataset.name)}&table=${encodeURIComponent(dataset.table_name)}`;
  };
  
  return (
    <Box sx={{ width: '100%' }}>
      <TextField
        fullWidth
        size="small"
        placeholder="Search datasets"
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        sx={{ mb: 2 }}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <SearchIcon fontSize="small" />
            </InputAdornment>
          ),
        }}
      />
      
      <Paper variant="outlined" sx={{ maxHeight: 400, overflow: 'auto' }}>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', p: 4 }}>
            <CircularProgress size={24} />
            <Typography variant="body2" color="text.secondary" sx={{ ml: 2 }}>
              Loading datasets...
            </Typography>
          </Box>
        ) : error ? (
          <Box sx={{ p: 2 }}>
            <Typography variant="body2" color="error">
              Error: {error}
            </Typography>
          </Box>
        ) : (
          <List dense sx={{ width: '100%', bgcolor: 'background.paper' }}>
            {filteredDatasets.length === 0 ? (
              <ListItem>
                <ListItemText 
                  primary="No datasets found" 
                  secondary="Try a different search term" 
                />
              </ListItem>
            ) : (
              filteredDatasets.map((dataset) => {
                const labelId = `checkbox-list-label-${dataset.id}`;
                const isSelected = selectedDatasets.includes(dataset.id);
                const datapoints = dataset.number_of_datapoints || 0;
                const databaseInfo = dataset.database_info;
                
                return (
                  <ListItem
                    key={dataset.id}
                    disablePadding
                    secondaryAction={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Chip 
                          label={`${datapoints} datapoints`} 
                          size="small" 
                          variant="outlined"
                        />
                        <Button
                          size="small"
                          variant="outlined"
                          onClick={(e) => {
                            e.stopPropagation(); // Prevent triggering the ListItemButton click
                            navigateToChatWithDataset(dataset);
                          }}
                          sx={{ 
                            minWidth: 0, 
                            px: 1,
                            textTransform: 'none',
                            fontSize: '0.75rem'
                          }}
                        >
                          Chat
                        </Button>
                      </Box>
                    }
                  >
                    <ListItemButton 
                      role={undefined} 
                      onClick={() => handleToggle(dataset.id)}
                      dense
                      selected={isSelected}
                    >
                      <ListItemIcon>
                        <Checkbox
                          edge="start"
                          checked={isSelected}
                          tabIndex={-1}
                          disableRipple
                          inputProps={{ 'aria-labelledby': labelId }}
                          color="primary"
                        />
                      </ListItemIcon>
                      <ListItemText
                        id={labelId}
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <Typography variant="body1">{dataset.name}</Typography>
                            {databaseInfo && (
                              <Chip 
                                icon={<StorageIcon fontSize="small" />}
                                label={databaseInfo.name}
                                size="small"
                                sx={{ ml: 1, height: 20, fontSize: '0.7rem' }}
                              />
                            )}
                          </Box>
                        }
                        secondary={`Type: ${dataset.type}`}
                      />
                    </ListItemButton>
                  </ListItem>
                );
              })
            )}
          </List>
        )}
      </Paper>
      
      <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="body2" color="textSecondary">
          {selectedDatasets.length} dataset{selectedDatasets.length !== 1 ? 's' : ''} selected
        </Typography>
        
        <Button
          variant="contained"
          color="primary"
          startIcon={<CloneIcon />}
          disabled={selectedDatasets.length === 0}
          onClick={handleSelectDatasets}
        >
          Add Selected
        </Button>
      </Box>
    </Box>
  );
}
