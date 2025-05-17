'use client';

import { useState, useRef, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  CircularProgress, 
  Button, 
  ToggleButtonGroup, 
  ToggleButton,
  Chip,
  IconButton,
  Tooltip
} from '@mui/material';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import { 
  Add as AddIcon,
  BarChart as BarChartIcon,
  Settings as SettingsIcon
} from '@mui/icons-material';

// Initial welcome message
const initialMessages = [
  {
    id: 1,
    role: 'assistant',
    content: 'Hello! I\'m your AI assistant. How can I help you today?',
    timestamp: new Date().toISOString(),
  },
];

export default function ChatInterface({ dataset }) {
  const [messages, setMessages] = useState(initialMessages);
  const [isLoading, setIsLoading] = useState(false);
  const [mode, setMode] = useState('general');
  const [selectedDataset, setSelectedDataset] = useState(null);
  const messagesEndRef = useRef(null);
  
  // Set the selected dataset when the dataset prop changes
  useEffect(() => {
    if (dataset) {
      setSelectedDataset(dataset);
    }
  }, [dataset]);
  
  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  const handleSendMessage = async (content) => {
    // Add user message
    const userMessage = {
      id: messages.length + 1,
      role: 'user',
      content,
      timestamp: new Date().toISOString(),
    };
    
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    
    try {
      // Get all previous messages to include in the payload
      const previousMessages = messages
        .filter(msg => msg.role === 'user' || msg.role === 'assistant')
        .map(msg => ({
          role: msg.role,
          content: msg.content
        }));
      
      // Add the current message
      previousMessages.push({
        role: 'user',
        content: content
      });
      
      // Always use the /api/chats endpoint
      const createChatResponse = await fetch('/api/chats', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          dataset_id: selectedDataset?.id,
          table_name: selectedDataset?.table_name,
          messages: previousMessages
        }),
      });
      
      if (!createChatResponse.ok) {
        throw new Error('Failed to create chat');
      }
      
      // Get the response data
      const chatData = await createChatResponse.json();
      
      // Check if the response is a direct message response
      let aiResponseData = null;
      
      // If the response has content and role fields directly, use it as the AI response
      if (chatData.content && chatData.role === 'assistant') {
        aiResponseData = chatData;
      } 
      // Otherwise, try to find the assistant message in the messages array
      else if (chatData.messages && chatData.messages.length > 0) {
        // Find the last assistant message
        const assistantMessages = chatData.messages.filter(msg => msg.role === 'assistant');
        if (assistantMessages.length > 0) {
          aiResponseData = assistantMessages[assistantMessages.length - 1];
        }
      }
      
      // If we still don't have an AI response, log the response for debugging
      if (!aiResponseData) {
        console.error('Could not find assistant response in:', chatData);
        throw new Error('No assistant response found in chat data');
      }
      
      // Add AI response to messages
      const aiMessage = {
        id: messages.length + 2,
        role: 'assistant',
        content: aiResponseData.content,
        timestamp: aiResponseData.timestamp || new Date().toISOString(),
      };
      
      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      
      // Add error message
      const errorMessage = {
        id: messages.length + 2,
        role: 'assistant',
        content: 'Sorry, there was an error processing your request. Please try again.',
        timestamp: new Date().toISOString(),
        isError: true,
      };
      
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };
  

  const handleModeChange = (event, newMode) => {
    if (newMode !== null) {
      setMode(newMode);
    }
  };
  
  return (
    <Box sx={{ 
      height: '100%', 
      display: 'flex', 
      flexDirection: 'column',
      bgcolor: 'white',
      borderRadius: 2,
      overflow: 'hidden'
    }}>
      {/* Header section with dataset info */}
      <Box sx={{ 
        p: 2, 
        borderBottom: '1px solid',
        borderColor: 'divider',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <Box>
          <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 0.5 }}>
            {selectedDataset ? selectedDataset.name : 'AI Chat'}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Analyze with files, quickly gain insights.
          </Typography>
        </Box>
        <Tooltip title="View analytics">
          <IconButton>
            <BarChartIcon />
          </IconButton>
        </Tooltip>
      </Box>
      
      {/* Chat messages area */}
      <Box 
        sx={{ 
          flexGrow: 1, 
          overflow: 'auto',
          p: 3,
          backgroundColor: '#f9fafb',
        }}
      >
        {messages.map((message) => (
          <ChatMessage 
            key={message.id} 
            message={message} 
            isUser={message.role === 'user'} 
          />
        ))}
        
        {isLoading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}>
            <CircularProgress size={24} />
          </Box>
        )}
        
        <div ref={messagesEndRef} />
      </Box>
      
      {/* Input area with mode selection */}
      <Box sx={{ 
        p: 2, 
        backgroundColor: 'white',
        borderTop: '1px solid',
        borderColor: 'divider'
      }}>
        <Box sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between',
          mb: 2
        }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Button 
              variant="outlined" 
              startIcon={<AddIcon />}
              size="small"
              sx={{ 
                borderRadius: '20px',
                textTransform: 'none',
                px: 2
              }}
            >
              Add files
            </Button>
            
            {selectedDataset && (
              <Chip 
                label={`Table: ${selectedDataset.table_name || 'Unknown'}`}
                size="small"
                sx={{ borderRadius: '20px' }}
              />
            )}
          </Box>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <ToggleButtonGroup
              value={mode}
              exclusive
              onChange={handleModeChange}
              aria-label="chat mode"
              size="small"
              sx={{ 
                '& .MuiToggleButton-root': {
                  textTransform: 'none',
                  px: 2,
                  py: 0.5,
                  borderRadius: '20px',
                  border: '1px solid #e0e0e0',
                  '&.Mui-selected': {
                    bgcolor: '#f0f0f0',
                    color: 'text.primary',
                    '&:hover': {
                      bgcolor: '#e0e0e0',
                    }
                  }
                }
              }}
            >
              <ToggleButton value="general" aria-label="general mode">
                General mode
              </ToggleButton>
              <ToggleButton value="advanced" aria-label="advanced mode">
                Advanced mode
              </ToggleButton>
            </ToggleButtonGroup>
            
            <Button 
              variant="contained" 
              color="primary"
              sx={{ 
                borderRadius: '20px',
                textTransform: 'none',
                px: 2,
                bgcolor: '#6366F1',
                '&:hover': {
                  bgcolor: '#4F46E5',
                }
              }}
            >
              Start a new chat
            </Button>
          </Box>
        </Box>
        
        <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />
      </Box>
    </Box>
  );
}
