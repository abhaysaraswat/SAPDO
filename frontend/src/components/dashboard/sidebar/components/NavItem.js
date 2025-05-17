'use client';

import { forwardRef } from 'react';
import Link from 'next/link';
import { 
  ListItemButton, 
  ListItemIcon, 
  ListItemText, 
  Tooltip, 
  alpha,
  Box
} from '@mui/material';

const NavItem = forwardRef(({ item, active, collapsed, ...other }, ref) => {
  const { title, path, icon, info, external } = item;

  const renderContent = (
    <ListItemButton
      component={external ? 'a' : Link}
      href={path}
      target={external ? '_blank' : ''}
      rel={external ? 'noopener noreferrer' : ''}
      ref={ref}
      selected={active}
      sx={{
        minHeight: 36,
        borderRadius: 1,
        typography: 'body2',
        color: 'text.secondary',
        textTransform: 'capitalize',
        fontWeight: 'medium',
        transition: 'all 0.2s ease-in-out',
        '&.Mui-selected': {
          color: 'primary.main',
          bgcolor: (theme) => alpha(theme.palette.primary.main, 0.08),
          '&:hover': {
            bgcolor: (theme) => alpha(theme.palette.primary.main, 0.12),
          },
        },
        ...(collapsed && {
          justifyContent: 'center',
        }),
      }}
      {...other}
    >
      {icon && (
        <ListItemIcon
          sx={{
            width: 24,
            height: 24,
            color: 'inherit',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            ...(collapsed && {
              minWidth: 0,
              mr: 0,
            }),
          }}
        >
          {icon}
        </ListItemIcon>
      )}

      {!collapsed && (
        <>
          <ListItemText
            primary={title}
            primaryTypographyProps={{
              noWrap: true,
              component: 'span',
              variant: 'body2',
              textTransform: 'capitalize',
              fontWeight: active ? 600 : 500,
            }}
          />

          {info && info}
        </>
      )}
    </ListItemButton>
  );

  // Render with tooltip if collapsed
  if (collapsed) {
    return (
      <Tooltip title={title} placement="right" arrow>
        {renderContent}
      </Tooltip>
    );
  }

  return renderContent;
});

NavItem.displayName = 'NavItem';

export default NavItem;
