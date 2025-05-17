'use client';

import { useState } from 'react';
import { usePathname } from 'next/navigation';
import { 
  List, 
  ListSubheader, 
  Collapse, 
  Box, 
  Typography,
  alpha
} from '@mui/material';
import { 
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon
} from '@mui/icons-material';
import NavItem from './NavItem';

export default function NavSection({ section, collapsed, pathname }) {
  const { title, items = [] } = section;
  const [open, setOpen] = useState(true);
  
  const handleToggle = () => {
    setOpen(!open);
  };
  
  // If no title, render items directly
  if (!title) {
    return (
      <List disablePadding sx={{ px: 0 }}>
        {items.map((item) => (
          <NavItem 
            key={item.title} 
            item={item} 
            active={item.path === pathname} 
            collapsed={collapsed} 
          />
        ))}
      </List>
    );
  }
  
  // With title, render collapsible section
  return (
    <List
      disablePadding
      subheader={
        !collapsed && (
          <ListSubheader
            onClick={handleToggle}
            sx={{
              position: 'relative',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              fontWeight: 600,
              fontSize: '0.75rem',
              textTransform: 'uppercase',
              color: 'text.secondary',
              lineHeight: '30px',
              py: 1,
              px: 2,
              bgcolor: 'transparent',
              cursor: 'pointer',
              '&:hover': {
                color: 'text.primary',
              },
              transition: 'all 0.2s ease',
            }}
            disableSticky
          >
            <Typography variant="overline" sx={{ fontWeight: 600, letterSpacing: '0.05em' }}>
              {title}
            </Typography>
            {open ? <ExpandLessIcon fontSize="small" /> : <ExpandMoreIcon fontSize="small" />}
          </ListSubheader>
        )
      }
      sx={{
        mb: 1,
        '& .MuiListItemButton-root': {
          borderRadius: 1,
          mb: 0.25,
          py: 0.75,
          '&.Mui-selected': {
            bgcolor: (theme) => alpha(theme.palette.primary.main, 0.1),
            '&:hover': {
              bgcolor: (theme) => alpha(theme.palette.primary.main, 0.15),
            },
          },
        },
      }}
    >
      {!collapsed && (
        <Collapse in={open} timeout="auto" unmountOnExit>
          {items.map((item) => (
            <NavItem 
              key={item.title} 
              item={item} 
              active={item.path === pathname} 
              collapsed={collapsed} 
            />
          ))}
        </Collapse>
      )}
      
      {collapsed && (
        <Box sx={{ px: 1 }}>
          {items.map((item) => (
            <NavItem 
              key={item.title} 
              item={item} 
              active={item.path === pathname} 
              collapsed={collapsed} 
            />
          ))}
        </Box>
      )}
    </List>
  );
}
