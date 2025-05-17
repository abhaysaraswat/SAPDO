'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { 
  Box, 
  Typography, 
  Button, 
  TextField, 
  InputAdornment,
  Paper,
  Tabs,
  Tab,
  Card,
  CardContent,
  Chip,
  CircularProgress
} from '@mui/material';
import { 
  Search as SearchIcon,
  Add as AddIcon,
  Description as DescriptionIcon,
  Person as PersonIcon,
  Public as PublicIcon,
  Storage as StorageIcon
} from '@mui/icons-material';
import DatasetUploadDialog from '@/components/dataset/DatasetUploadDialog';

export default function DatasetPage() {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState('');
  const [tabValue, setTabValue] = useState(0);
  const [addDatasetOpen, setAddDatasetOpen] = useState(false);
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
  }, [searchQuery]);
  
  // Datasets are already filtered by the API
  const filteredDatasets = datasets;
  
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };
  
  const handleDatasetClick = (dataset) => {
    // Navigate to chat page with dataset information using the new URL format
    router.push(`/dashboard/chat/${dataset.id}?name=${encodeURIComponent(dataset.name)}&table=${encodeURIComponent(dataset.table_name)}`);
  };
  
  return (
    <Box sx={{ 
      height: '100%', 
      display: 'flex', 
      flexDirection: 'column',
      bgcolor: 'white',
      p: 0
    }}>
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        mb: 3,
        px: 3,
        pt: 3
      }}>
        <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
          Datasets
        </Typography>
        <Button
          variant="contained"
          color="primary"
          onClick={() => setAddDatasetOpen(true)}
          startIcon={<AddIcon />}
          sx={{ 
            borderRadius: '8px',
            textTransform: 'none',
            fontWeight: 'bold',
            bgcolor: '#6366F1',
            '&:hover': {
              bgcolor: '#4F46E5',
            }
          }}
        >
          Add Dataset
        </Button>
      </Box>
      
      <Tabs 
        value={tabValue} 
        onChange={handleTabChange}
        sx={{ 
          mb: 3,
          px: 3,
          '& .MuiTabs-indicator': {
            backgroundColor: '#6366F1',
            height: 3
          },
          '& .MuiTab-root': {
            textTransform: 'none',
            fontWeight: 500,
            fontSize: '0.9rem',
            minWidth: 0,
            mr: 2,
            p: 0,
            pb: 1,
            '&.Mui-selected': {
              color: '#6366F1',
              fontWeight: 600
            }
          }
        }}
      >
        <Tab 
          label="My datasets" 
        />
        <Tab 
          label="Shared with me" 
        />
        <Tab 
          label="Public datasets" 
        />
      </Tabs>
      
      <Box sx={{ px: 3 }}>
        <TextField
          size="small"
          placeholder="Search..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          sx={{ 
            mb: 3,
            maxWidth: '300px',
            '& .MuiOutlinedInput-root': {
              borderRadius: '8px',
            }
          }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon fontSize="small" />
              </InputAdornment>
            ),
          }}
        />
      </Box>
      
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, px: 3 }}>
        {loading ? (
          <Box sx={{ width: '100%', display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress size={32} />
          </Box>
        ) : error ? (
          <Box sx={{ width: '100%', textAlign: 'center', py: 4 }}>
            <Typography variant="body1" color="error">
              Error: {error}
            </Typography>
          </Box>
        ) : filteredDatasets.length === 0 ? (
          <Box sx={{ width: '100%', textAlign: 'center', py: 4 }}>
            <Typography variant="body1" color="text.secondary">
              No datasets found. Try a different search or create a new dataset.
            </Typography>
          </Box>
        ) : (
          filteredDatasets.map((dataset) => (
            <Card 
              key={dataset.id}
              onClick={() => handleDatasetClick(dataset)}
              sx={{ 
                width: '100%',
                maxWidth: '500px',
                borderRadius: 2,
                boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                transition: 'transform 0.2s ease, box-shadow 0.2s ease',
                cursor: 'pointer',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
                }
              }}
            >
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: 1 }}>
                    <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                      {dataset.name}
                    </Typography>
                    {dataset.database_info && (
                      <Chip 
                        icon={<StorageIcon fontSize="small" />}
                        label={dataset.database_info.name}
                        size="small"
                        sx={{ 
                          bgcolor: '#F0F9FF',
                          color: '#0284C7',
                          fontWeight: 500,
                          fontSize: '0.7rem',
                          height: '22px'
                        }}
                      />
                    )}
                  </Box>
                  <Chip 
                    label={dataset.type} 
                    size="small" 
                    sx={{ 
                      bgcolor: '#E0F2FE',
                      color: '#0369A1',
                      fontWeight: 500,
                      fontSize: '0.7rem',
                      height: '22px'
                    }} 
                  />
                </Box>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                  {dataset.number_of_datapoints} datapoints
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {dataset.description || 'No description provided'}
                </Typography>
              </CardContent>
            </Card>
          ))
        )}
      </Box>
      
      {/* Dataset Upload Dialog */}
      <DatasetUploadDialog 
        open={addDatasetOpen} 
        onClose={() => setAddDatasetOpen(false)} 
      />
    </Box>
  );
}
