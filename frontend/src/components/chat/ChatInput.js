'use client';

import { useState } from 'react';
import { 
  Box,
  Paper, 
  InputBase, 
  IconButton, 
  Tooltip,
  CircularProgress
} from '@mui/material';
import { 
  Send as SendIcon,
  AttachFile as AttachFileIcon
} from '@mui/icons-material';

export default function ChatInput({ onSendMessage, isLoading }) {
  const [message, setMessage] = useState('');
  
  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() && !isLoading) {
      onSendMessage(message);
      setMessage('');
    }
  };
  
  return (
    <Paper
      component="form"
      onSubmit={handleSubmit}
      elevation={0}
      sx={{ 
        p: '8px 16px', 
        display: 'flex', 
        alignItems: 'center',
        borderRadius: '12px',
        border: '1px solid',
        borderColor: 'divider',
        bgcolor: '#f9fafb'
      }}
    >
      <InputBase
        sx={{ 
          flex: 1,
          fontSize: '0.95rem',
          '&::placeholder': {
            color: 'text.secondary',
            opacity: 0.7
          }
        }}
        placeholder="Type your message..."
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={(e) => {
          // Submit on Enter key press (without Shift key)
          if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
          }
        }}
        multiline
        maxRows={4}
        disabled={isLoading}
      />
      
      <Box sx={{ display: 'flex', alignItems: 'center' }}>
        <Tooltip title="Send message">
          <IconButton 
            color="primary" 
            sx={{ 
              p: '8px',
              bgcolor: '#6366F1',
              color: 'white',
              '&:hover': {
                bgcolor: '#4F46E5',
              },
              '&.Mui-disabled': {
                bgcolor: '#E0E7FF',
                color: '#6366F1',
              }
            }} 
            aria-label="send message"
            type="submit"
            disabled={!message.trim() || isLoading}
          >
            {isLoading ? <CircularProgress size={20} color="inherit" /> : <SendIcon fontSize="small" />}
          </IconButton>
        </Tooltip>
      </Box>
    </Paper>
  );
}
