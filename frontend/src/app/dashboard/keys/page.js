'use client';

import { useState } from 'react';
import { 
  Box, 
  Card, 
  Typography, 
  TextField, 
  InputAdornment, 
  IconButton,
  Tooltip,
  Stack,
  LinearProgress
} from '@mui/material';
import { ContentCopy as CopyIcon } from '@mui/icons-material';

// Mock API keys data
const mockKeysData = {
  apiKey: 'sapdo_sk_12345678901234567890',
  secretKey: 'sapdo_sk_abcdefghijklmnopqrst'
};

export default function KeysPage() {
  const [showTooltip, setShowTooltip] = useState({
    apiKey: false,
    secretKey: false,
  });
  
  // Simulate loading state
  const [isLoading, setIsLoading] = useState(false);
  
  const handleCopy = (text, field) => {
    navigator.clipboard.writeText(text);
    // Show tooltip
    setShowTooltip({ ...showTooltip, [field]: true });
    // Hide tooltip after 2 seconds
    setTimeout(() => {
      setShowTooltip({ ...showTooltip, [field]: false });
    }, 2000);
  };
  
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">API Keys</h1>
      </div>
      
      <Card sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Keys
        </Typography>
        
        {isLoading ? (
          <LinearProgress sx={{ my: 4 }} />
        ) : (
          <Stack sx={{ width: 400, mt: 2 }} spacing={2}>
            <TextField
              label="API Key"
              variant="outlined"
              type="password"
              disabled
              value="••••••••••••••••••••••"
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <Tooltip title="Copied!" open={showTooltip.apiKey} arrow>
                      <IconButton
                        onClick={() => handleCopy(mockKeysData.apiKey, 'apiKey')}
                        edge="end"
                      >
                        <CopyIcon />
                      </IconButton>
                    </Tooltip>
                  </InputAdornment>
                ),
              }}
            />
            
            <TextField
              label="Secret Key"
              variant="outlined"
              type="password"
              disabled
              value="••••••••••••••••••••••"
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <Tooltip title="Copied!" open={showTooltip.secretKey} arrow>
                      <IconButton
                        onClick={() => handleCopy(mockKeysData.secretKey, 'secretKey')}
                        edge="end"
                      >
                        <CopyIcon />
                      </IconButton>
                    </Tooltip>
                  </InputAdornment>
                ),
              }}
            />
          </Stack>
        )}
        
        <Box mt={4}>
          <Typography variant="body2" color="textSecondary">
            These keys allow you to authenticate API requests. Keep them secure and do not share them publicly.
          </Typography>
        </Box>
      </Card>
      
      <Card sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Usage
        </Typography>
        
        <Box mt={2}>
          <Typography variant="body1" gutterBottom>
            Example API request:
          </Typography>
          
          <Box 
            sx={{ 
              backgroundColor: 'grey.100', 
              p: 2, 
              borderRadius: 1,
              fontFamily: 'monospace',
              fontSize: '0.875rem',
              overflowX: 'auto'
            }}
          >
            {`curl -X POST https://api.sapdo.com/v1/prompt \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "model": "gpt-4",
    "messages": [
      {"role": "user", "content": "Hello, how can you help me?"}
    ]
  }'`}
          </Box>
        </Box>
      </Card>
    </div>
  );
}
