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
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import ExistingDatasetSelector from '../dataset/ExistingDatasetSelector';
import { 
  Add as AddIcon,
  BarChart as BarChartIcon,
  Settings as SettingsIcon,
  Storage as StorageIcon
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
  const [datasetDialogOpen, setDatasetDialogOpen] = useState(false);
  const [isThinking, setIsThinking] = useState(false);
  const [streamingText, setStreamingText] = useState('');
  const [streamingComplete, setStreamingComplete] = useState(true);
  const messagesEndRef = useRef(null);
  
  // Set the selected dataset when the dataset prop changes
  useEffect(() => {
    if (dataset) {
      setSelectedDataset(dataset);
    } else {
      // If no dataset is provided, open the dataset selection dialog automatically
      setDatasetDialogOpen(true);
    }
  }, [dataset]);
  
  // Handle opening the dataset selection dialog
  const handleOpenDatasetDialog = () => {
    setDatasetDialogOpen(true);
  };
  
  // Handle closing the dataset selection dialog
  const handleCloseDatasetDialog = () => {
    // Only allow closing the dialog if a dataset is selected
    if (selectedDataset) {
      setDatasetDialogOpen(false);
    }
  };
  
  // Handle dataset selection
  const handleDatasetSelect = (datasets) => {
    if (datasets && datasets.length > 0) {
      setSelectedDataset(datasets[0]);
    }
    setDatasetDialogOpen(false);
  };
  
  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  // Simulate text streaming effect
  const simulateTextStreaming = (text) => {
    setStreamingComplete(false);
    setStreamingText('');
    
    let i = 0;
    const speed = 10; // milliseconds per character
    
    const streamInterval = setInterval(() => {
      if (i < text.length) {
        setStreamingText(prev => prev + text.charAt(i));
        i++;
      } else {
        clearInterval(streamInterval);
        setStreamingComplete(true);
      }
    }, speed);
    
    return () => clearInterval(streamInterval);
  };
  
  const handleSendMessage = async (content) => {
    if (!selectedDataset) {
      // If no dataset is selected, open the dataset selection dialog
      setDatasetDialogOpen(true);
      return;
    }
    
    // Add user message
    const userMessage = {
      id: messages.length + 1,
      role: 'user',
      content,
      timestamp: new Date().toISOString(),
    };
    
    setMessages((prev) => [...prev, userMessage]);
    
    // Add a temporary "Thinking..." message
    const thinkingMessageId = messages.length + 2;
    setIsThinking(true);
    setMessages((prev) => [...prev, {
      id: thinkingMessageId,
      role: 'assistant',
      content: 'Thinking...',
      timestamp: new Date().toISOString(),
      isThinking: true,
    }]);
    
    try {
      // Get all previous messages to include in the payload
      const previousMessages = messages
        .filter(msg => msg.role === 'user' || msg.role === 'assistant')
        .filter(msg => !msg.isThinking) // Filter out thinking messages
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
      
      // Remove the thinking message
      setMessages((prev) => prev.filter(msg => msg.id !== thinkingMessageId));
      setIsThinking(false);
      
      // Start streaming the response
      const responseContent = aiResponseData.content;
      
      // Add AI response to messages with empty content initially
      const aiMessage = {
        id: thinkingMessageId, // Reuse the ID to replace the thinking message
        role: 'assistant',
        content: '',
        timestamp: aiResponseData.timestamp || new Date().toISOString(),
        isStreaming: true,
      };
      
      setMessages((prev) => [...prev, aiMessage]);
      
      // Simulate streaming effect
      const cleanupStreaming = simulateTextStreaming(responseContent);
      
      // Update the message content as the streaming text changes
      const streamingInterval = setInterval(() => {
        setMessages((prev) => 
          prev.map(msg => 
            msg.id === thinkingMessageId 
              ? { ...msg, content: streamingText, isStreaming: !streamingComplete } 
              : msg
          )
        );
        
        // If streaming is complete, clear the interval
        if (streamingComplete) {
          clearInterval(streamingInterval);
          
          // Final update with the complete content
          setMessages((prev) => 
            prev.map(msg => 
              msg.id === thinkingMessageId 
                ? { ...msg, content: responseContent, isStreaming: false } 
                : msg
            )
          );
        }
      }, 50);
      
      // Cleanup function
      return () => {
        cleanupStreaming();
        clearInterval(streamingInterval);
      };
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
              startIcon={<StorageIcon />}
              size="small"
              onClick={handleOpenDatasetDialog}
              sx={{ 
                borderRadius: '20px',
                textTransform: 'none',
                px: 2
              }}
            >
              {selectedDataset ? 'Change Dataset' : 'Select Dataset'}
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
        
        {selectedDataset ? (
          <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />
        ) : (
          <Box sx={{ 
            p: 2, 
            backgroundColor: '#f5f5f5', 
            borderRadius: 2, 
            textAlign: 'center',
            border: '1px dashed #ccc'
          }}>
            <Typography variant="body1" color="text.secondary">
              Please select a dataset to start chatting
            </Typography>
            <Button
              variant="contained"
              color="primary"
              startIcon={<StorageIcon />}
              onClick={handleOpenDatasetDialog}
              sx={{ mt: 2 }}
            >
              Select Dataset
            </Button>
          </Box>
        )}
      </Box>
      
      {/* Dataset Selection Dialog */}
      <Dialog
        open={datasetDialogOpen}
        onClose={handleCloseDatasetDialog}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Select a Dataset
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Select a dataset to use for this chat. The AI will be able to query and analyze the data from the selected dataset.
          </Typography>
          <ExistingDatasetSelector onSelect={handleDatasetSelect} />
        </DialogContent>
        <DialogActions>
          {selectedDataset && (
            <Button onClick={handleCloseDatasetDialog}>Cancel</Button>
          )}
          {!selectedDataset && (
            <Typography variant="caption" color="text.secondary">
              You must select a dataset to continue
            </Typography>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  );
}
