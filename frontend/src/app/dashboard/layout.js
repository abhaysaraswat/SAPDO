'use client';

import { useState, useEffect } from 'react';
import { Box, useMediaQuery, useTheme } from '@mui/material';
import Sidebar from '@/components/dashboard/sidebar/Sidebar';

export default function DashboardLayout({ children }) {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [sidebarOpen, setSidebarOpen] = useState(!isMobile);
  
  // Handle sidebar state based on screen size
  useEffect(() => {
    setSidebarOpen(!isMobile);
  }, [isMobile]);
  
  const handleToggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };
  
  return (
    <Box 
      sx={{ 
        display: 'flex', 
        height: '100vh', 
        overflow: 'hidden',
        bgcolor: 'background.default',
      }}
    >
      <Sidebar open={sidebarOpen} onToggle={handleToggleSidebar} />
      
      <Box 
        component="main" 
        sx={{ 
          flexGrow: 1, 
          overflow: 'auto',
          p: 0,
          transition: 'width 0.3s ease',
          width: { 
            xs: '100%', 
            md: `calc(100% - ${sidebarOpen ? '256px' : '80px'})` 
          },
          bgcolor: 'background.default',
          position: 'relative',
          zIndex: 1,
        }}
        className="animate-fade-in"
      >
        <Box 
          sx={{ 
            maxWidth: '1600px', 
            mx: 'auto',
            height: '100%',
          }}
        >
          {children}
        </Box>
      </Box>
    </Box>
  );
}
