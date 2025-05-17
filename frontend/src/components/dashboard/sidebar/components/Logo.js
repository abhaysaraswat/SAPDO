'use client';

import Link from 'next/link';
import { Box, Typography, useTheme } from '@mui/material';
import { Star as StarIcon } from '@mui/icons-material';

export default function Logo({ collapsed = false }) {
  const theme = useTheme();
  
  return (
    <Link href="/" style={{ textDecoration: 'none' }}>
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: collapsed ? 'center' : 'flex-start',
          transition: 'all 0.2s ease-in-out',
        }}
      >
        <Box
          sx={{
            width: 40,
            height: 40,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            borderRadius: '12px',
            background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.primary.dark} 100%)`,
            boxShadow: `0 2px 8px ${theme.palette.primary.main}40`,
            color: 'white',
            mr: collapsed ? 0 : 1.5,
            transition: 'all 0.3s ease',
            '&:hover': {
              transform: 'translateY(-2px)',
              boxShadow: `0 4px 12px ${theme.palette.primary.main}60`,
            },
          }}
          className="animate-pulse"
        >
          <StarIcon fontSize="medium" />
        </Box>
        
        {!collapsed && (
          <Box sx={{ display: 'flex', flexDirection: 'column' }}>
            <Typography
              variant="h6"
              component="div"
              sx={{
                fontWeight: 700,
                lineHeight: 1.2,
                color: 'text.primary',
                letterSpacing: '0.02em',
                textTransform: 'uppercase',
              }}
              className="text-gradient-primary"
            >
              Sapdo
            </Typography>
            
            <Typography
              variant="caption"
              sx={{
                fontWeight: 500,
                lineHeight: 1,
                color: 'text.secondary',
                letterSpacing: '0.05em',
                textTransform: 'uppercase',
              }}
            >
              BETA
            </Typography>
          </Box>
        )}
      </Box>
    </Link>
  );
}
