'use client';

import { useState, useEffect } from 'react';
import { usePathname } from 'next/navigation';
import { 
  Box, 
  Drawer, 
  List, 
  Divider, 
  IconButton, 
  useMediaQuery, 
  useTheme,
  Collapse,
  Tooltip
} from '@mui/material';
import { 
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon
} from '@mui/icons-material';
import { navConfig } from './config';
import Logo from './components/Logo';
import NavSection from './components/NavSection';

export default function Sidebar({ open, onToggle }) {
  const pathname = usePathname();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  // Drawer content
  const renderContent = (
    <Box
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        bgcolor: 'background.paper',
        boxShadow: 'none',
        transition: 'all 0.3s ease',
        overflow: 'hidden',
        borderRight: '1px solid',
        borderColor: 'divider',
      }}
    >
      {/* Logo */}
      <Box
        sx={{
          py: 3,
          px: 2.5,
          display: 'flex',
          alignItems: 'center',
          justifyContent: open ? 'space-between' : 'center',
        }}
      >
        <Logo collapsed={!open} />
        
        {open && !isMobile && (
          <IconButton onClick={onToggle} className="hover-scale">
            <ChevronLeftIcon />
          </IconButton>
        )}
      </Box>

      <Divider sx={{ borderStyle: 'dashed' }} />

      {/* Nav Sections */}
      <Box sx={{ flexGrow: 1, overflow: 'auto', px: 2, py: 2, display: 'flex', flexDirection: 'column', height: '100%' }}>
        {navConfig.map((section, index) => (
          <NavSection
            key={section.title || `section-${index}`}
            section={section}
            collapsed={!open}
            pathname={pathname}
          />
        ))}
      </Box>

      <Divider sx={{ borderStyle: 'dashed' }} />

      {/* Collapse button for mobile */}
      {isMobile && open && (
        <Box sx={{ p: 2, textAlign: 'center' }}>
          <IconButton 
            onClick={onToggle}
            sx={{ 
              bgcolor: 'background.default',
              '&:hover': { bgcolor: 'action.hover' },
              boxShadow: theme.shadows[2],
              borderRadius: '50%',
              width: 40,
              height: 40,
            }}
            className="hover-scale"
          >
            <ChevronLeftIcon />
          </IconButton>
        </Box>
      )}
    </Box>
  );

  // Mobile drawer
  if (isMobile) {
    return (
      <>
        <Drawer
          open={open}
          onClose={onToggle}
          ModalProps={{ keepMounted: true }}
          PaperProps={{
            sx: {
              width: 256,
              bgcolor: 'background.paper',
              transition: 'all 0.3s ease',
            },
          }}
        >
          {renderContent}
        </Drawer>

        {/* Toggle button when sidebar is closed */}
        {!open && (
          <Box
            sx={{
              position: 'fixed',
              top: 16,
              left: 16,
              zIndex: 1000,
            }}
          >
            <Tooltip title="Open menu">
              <IconButton
                onClick={onToggle}
                sx={{
                  bgcolor: 'background.paper',
                  boxShadow: theme.shadows[3],
                  '&:hover': { bgcolor: 'background.paper' },
                  width: 40,
                  height: 40,
                }}
                className="hover-scale"
              >
                <ChevronRightIcon />
              </IconButton>
            </Tooltip>
          </Box>
        )}
      </>
    );
  }

  // Desktop drawer
  return (
    <Box
      component="nav"
      sx={{
        flexShrink: 0,
        width: open ? 256 : 80,
        transition: 'width 0.3s ease',
      }}
    >
      <Box
        sx={{
          height: '100%',
          position: 'fixed',
          width: open ? 256 : 80,
          transition: 'width 0.3s ease',
          bgcolor: 'background.paper',
          zIndex: 10,
        }}
      >
        {renderContent}
        
        {/* Toggle button when sidebar is collapsed */}
        {!open && (
          <Box
            sx={{
              position: 'absolute',
              top: 16,
              right: -16,
              zIndex: 1000,
            }}
          >
            <Tooltip title="Expand menu">
              <IconButton
                onClick={onToggle}
                sx={{
                  bgcolor: 'background.paper',
                  boxShadow: theme.shadows[3],
                  '&:hover': { bgcolor: 'background.paper' },
                  width: 32,
                  height: 32,
                }}
                className="hover-scale"
              >
                <ChevronRightIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Box>
        )}
      </Box>
    </Box>
  );
}
