'use client';

import { Box, Avatar, Typography } from '@mui/material';

export default function ChatMessage({ message, isUser }) {
  return (
    <Box 
      sx={{ 
        display: 'flex', 
        justifyContent: isUser ? 'flex-end' : 'flex-start',
        mb: 3,
        maxWidth: '100%'
      }}
    >
      {!isUser && (
        <Avatar 
          sx={{ 
            bgcolor: '#6366F1',
            width: 36,
            height: 36,
            mr: 1.5,
            mt: 0.5,
            fontSize: '0.9rem',
            fontWeight: 'bold'
          }}
        >
          AI
        </Avatar>
      )}
      
      <Box 
        sx={{ 
          maxWidth: '75%',
          p: 2,
          borderRadius: 2,
          ...(isUser 
            ? { 
                bgcolor: '#6366F1', 
                color: 'white',
                borderTopRightRadius: 0
              } 
            : { 
                bgcolor: 'white', 
                color: 'text.primary',
                borderTopLeftRadius: 0,
                boxShadow: '0 1px 2px rgba(0,0,0,0.05)'
              }
          )
        }}
      >
        <Typography 
          variant="body1" 
          sx={{ 
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-word',
            lineHeight: 1.5
          }}
        >
          {message.content}
        </Typography>
        
        {message.timestamp && (
          <Typography 
            variant="caption" 
            sx={{ 
              display: 'block',
              mt: 1,
              color: isUser ? 'rgba(255,255,255,0.7)' : 'text.secondary',
              fontSize: '0.75rem'
            }}
          >
            {new Date(message.timestamp).toLocaleTimeString([], { 
              hour: '2-digit', 
              minute: '2-digit' 
            })}
          </Typography>
        )}
      </Box>
      
      {isUser && (
        <Avatar 
          sx={{ 
            bgcolor: '#E0E7FF',
            color: '#6366F1',
            width: 36,
            height: 36,
            ml: 1.5,
            mt: 0.5,
            fontSize: '0.9rem',
            fontWeight: 'bold'
          }}
        >
          U
        </Avatar>
      )}
    </Box>
  );
}
