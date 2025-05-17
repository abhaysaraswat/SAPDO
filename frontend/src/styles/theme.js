'use client';

import { createTheme, alpha } from '@mui/material/styles';

// Define our color palette
const colors = {
  primary: {
    main: '#6366F1', // Indigo
    light: '#818CF8',
    dark: '#4F46E5',
    contrastText: '#FFFFFF',
  },
  secondary: {
    main: '#EC4899', // Pink
    light: '#F472B6',
    dark: '#DB2777',
    contrastText: '#FFFFFF',
  },
  success: {
    main: '#10B981', // Emerald
    light: '#34D399',
    dark: '#059669',
    contrastText: '#FFFFFF',
  },
  error: {
    main: '#EF4444', // Red
    light: '#F87171',
    dark: '#DC2626',
    contrastText: '#FFFFFF',
  },
  warning: {
    main: '#F59E0B', // Amber
    light: '#FBBF24',
    dark: '#D97706',
    contrastText: '#FFFFFF',
  },
  info: {
    main: '#3B82F6', // Blue
    light: '#60A5FA',
    dark: '#2563EB',
    contrastText: '#FFFFFF',
  },
  grey: {
    50: '#F9FAFB',
    100: '#F3F4F6',
    200: '#E5E7EB',
    300: '#D1D5DB',
    400: '#9CA3AF',
    500: '#6B7280',
    600: '#4B5563',
    700: '#374151',
    800: '#1F2937',
    900: '#111827',
  },
  text: {
    primary: '#111827',
    secondary: '#4B5563',
    disabled: '#9CA3AF',
  },
  background: {
    default: '#F9FAFB',
    paper: '#FFFFFF',
    dark: '#111827',
  },
  divider: '#E5E7EB',
};

// Define shadows
const shadows = [
  'none',
  '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
  '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
  '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
  '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
  '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
  '0 35px 60px -15px rgba(0, 0, 0, 0.3)',
  ...Array(16).fill('none'),
];

// Create a base theme with our design tokens
const baseTheme = createTheme({
  palette: {
    primary: colors.primary,
    secondary: colors.secondary,
    success: colors.success,
    error: colors.error,
    warning: colors.warning,
    info: colors.info,
    grey: colors.grey,
    text: colors.text,
    background: colors.background,
    divider: colors.divider,
  },
  shadows,
  shape: {
    borderRadius: 12,
  },
  typography: {
    fontFamily: 'var(--font-geist-sans), sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 700,
      lineHeight: 1.2,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 700,
      lineHeight: 1.2,
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 600,
      lineHeight: 1.2,
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 600,
      lineHeight: 1.2,
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 600,
      lineHeight: 1.2,
    },
    h6: {
      fontSize: '1rem',
      fontWeight: 600,
      lineHeight: 1.2,
    },
    subtitle1: {
      fontSize: '1rem',
      fontWeight: 500,
      lineHeight: 1.5,
    },
    subtitle2: {
      fontSize: '0.875rem',
      fontWeight: 500,
      lineHeight: 1.5,
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.5,
    },
    body2: {
      fontSize: '0.875rem',
      lineHeight: 1.5,
    },
    button: {
      fontSize: '0.875rem',
      fontWeight: 600,
      textTransform: 'none',
    },
    caption: {
      fontSize: '0.75rem',
      lineHeight: 1.5,
    },
    overline: {
      fontSize: '0.75rem',
      fontWeight: 600,
      textTransform: 'uppercase',
      letterSpacing: '0.08em',
    },
  },
});

// Create the final theme with component overrides
const theme = createTheme(baseTheme, {
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        '*': {
          boxSizing: 'border-box',
        },
        html: {
          margin: 0,
          padding: 0,
          width: '100%',
          height: '100%',
          WebkitOverflowScrolling: 'touch',
        },
        body: {
          margin: 0,
          padding: 0,
          width: '100%',
          height: '100%',
        },
        '#root': {
          width: '100%',
          height: '100%',
        },
        input: {
          '&[type=number]': {
            MozAppearance: 'textfield',
            '&::-webkit-outer-spin-button': {
              margin: 0,
              WebkitAppearance: 'none',
            },
            '&::-webkit-inner-spin-button': {
              margin: 0,
              WebkitAppearance: 'none',
            },
          },
        },
        img: {
          display: 'block',
          maxWidth: '100%',
        },
        a: {
          textDecoration: 'none',
          color: 'inherit',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          boxShadow: 'none',
          fontWeight: 600,
          textTransform: 'none',
          padding: '10px 16px',
          transition: 'all 0.2s ease-in-out',
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: baseTheme.shadows[2],
          },
        },
        contained: {
          boxShadow: baseTheme.shadows[1],
          '&:hover': {
            boxShadow: baseTheme.shadows[3],
          },
        },
        containedPrimary: {
          background: `linear-gradient(135deg, ${colors.primary.main} 0%, ${colors.primary.dark} 100%)`,
        },
        containedSecondary: {
          background: `linear-gradient(135deg, ${colors.secondary.main} 0%, ${colors.secondary.dark} 100%)`,
        },
        outlined: {
          borderWidth: 2,
          '&:hover': {
            borderWidth: 2,
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          boxShadow: baseTheme.shadows[2],
          transition: 'transform 0.3s ease, box-shadow 0.3s ease',
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: baseTheme.shadows[4],
          },
        },
      },
    },
    MuiCardContent: {
      styleOverrides: {
        root: {
          padding: 24,
        },
      },
    },
    MuiCardHeader: {
      styleOverrides: {
        root: {
          padding: '24px 24px 0',
        },
      },
    },
    MuiCardActions: {
      styleOverrides: {
        root: {
          padding: '0 24px 24px',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          borderRadius: 16,
          transition: 'box-shadow 0.3s ease',
        },
        elevation1: {
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
        },
        elevation2: {
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        },
        elevation3: {
          boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
        },
        elevation4: {
          boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 8,
            transition: 'box-shadow 0.3s ease',
            '&:hover': {
              boxShadow: '0 0 0 4px rgba(99, 102, 241, 0.1)',
            },
            '&.Mui-focused': {
              boxShadow: '0 0 0 4px rgba(99, 102, 241, 0.2)',
            },
          },
        },
      },
    },
    MuiInputBase: {
      styleOverrides: {
        root: {
          borderRadius: 8,
        },
      },
    },
    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          borderRadius: 8,
        },
        input: {
          padding: '14px 16px',
        },
      },
    },
    MuiDialog: {
      styleOverrides: {
        paper: {
          borderRadius: 16,
          boxShadow: baseTheme.shadows[5],
        },
      },
    },
    MuiDialogTitle: {
      styleOverrides: {
        root: {
          padding: 24,
        },
      },
    },
    MuiDialogContent: {
      styleOverrides: {
        root: {
          padding: 24,
        },
      },
    },
    MuiDialogActions: {
      styleOverrides: {
        root: {
          padding: 24,
        },
      },
    },
    MuiListItem: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          '&.Mui-selected': {
            backgroundColor: alpha(colors.primary.main, 0.1),
          },
        },
      },
    },
    MuiListItemButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          '&:hover': {
            backgroundColor: alpha(colors.primary.main, 0.05),
          },
          '&.Mui-selected': {
            backgroundColor: alpha(colors.primary.main, 0.1),
            '&:hover': {
              backgroundColor: alpha(colors.primary.main, 0.15),
            },
          },
        },
      },
    },
    MuiListItemIcon: {
      styleOverrides: {
        root: {
          minWidth: 40,
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          fontWeight: 500,
        },
      },
    },
    MuiAvatar: {
      styleOverrides: {
        root: {
          backgroundColor: colors.primary.main,
          color: colors.primary.contrastText,
        },
      },
    },
    MuiTooltip: {
      styleOverrides: {
        tooltip: {
          backgroundColor: colors.grey[800],
          borderRadius: 6,
          padding: '8px 12px',
          fontSize: '0.75rem',
        },
        arrow: {
          color: colors.grey[800],
        },
      },
    },
    MuiLinearProgress: {
      styleOverrides: {
        root: {
          borderRadius: 4,
          overflow: 'hidden',
        },
      },
    },
    MuiAlert: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          boxShadow: baseTheme.shadows[1],
        },
        standardSuccess: {
          backgroundColor: alpha(colors.success.main, 0.1),
          color: colors.success.dark,
        },
        standardError: {
          backgroundColor: alpha(colors.error.main, 0.1),
          color: colors.error.dark,
        },
        standardWarning: {
          backgroundColor: alpha(colors.warning.main, 0.1),
          color: colors.warning.dark,
        },
        standardInfo: {
          backgroundColor: alpha(colors.info.main, 0.1),
          color: colors.info.dark,
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        root: {
          padding: '16px 24px',
        },
        head: {
          fontWeight: 600,
          backgroundColor: colors.grey[50],
        },
      },
    },
    MuiTableRow: {
      styleOverrides: {
        root: {
          '&:last-child td': {
            borderBottom: 0,
          },
          '&:hover': {
            backgroundColor: alpha(colors.primary.main, 0.04),
          },
        },
      },
    },
    MuiStepLabel: {
      styleOverrides: {
        label: {
          '&.Mui-active': {
            fontWeight: 600,
            color: colors.primary.main,
          },
          '&.Mui-completed': {
            fontWeight: 600,
            color: colors.success.main,
          },
        },
      },
    },
    MuiStepIcon: {
      styleOverrides: {
        root: {
          '&.Mui-active': {
            color: colors.primary.main,
          },
          '&.Mui-completed': {
            color: colors.success.main,
          },
        },
      },
    },
  },
});

export default theme;

// CSS variables for use in Tailwind CSS
export const cssVariables = {
  '--color-primary': colors.primary.main,
  '--color-primary-light': colors.primary.light,
  '--color-primary-dark': colors.primary.dark,
  '--color-secondary': colors.secondary.main,
  '--color-success': colors.success.main,
  '--color-error': colors.error.main,
  '--color-warning': colors.warning.main,
  '--color-info': colors.info.main,
  '--color-background': colors.background.default,
  '--color-paper': colors.background.paper,
  '--color-text-primary': colors.text.primary,
  '--color-text-secondary': colors.text.secondary,
  '--color-divider': colors.divider,
  '--border-radius-sm': '4px',
  '--border-radius-md': '8px',
  '--border-radius-lg': '16px',
  '--shadow-sm': shadows[1],
  '--shadow-md': shadows[2],
  '--shadow-lg': shadows[4],
  '--shadow-xl': shadows[5],
};
