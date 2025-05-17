'use client';

import { ModuleRegistry, AllCommunityModule } from 'ag-grid-community';

// Register AG Grid modules
ModuleRegistry.registerModules([AllCommunityModule]);

// AG Grid theme configuration
export const agGridTheme = {
  alpine: {
    // Header styling
    '--ag-header-height': '48px',
    '--ag-header-foreground-color': '#4B5563',
    '--ag-header-background-color': '#F9FAFB',
    '--ag-header-cell-hover-background-color': '#F3F4F6',
    '--ag-header-cell-moving-background-color': '#E5E7EB',
    
    // Font styling
    '--ag-font-size': '14px',
    '--ag-font-family': 'var(--font-geist-sans)',
    
    // Border styling
    '--ag-border-color': '#E5E7EB',
    '--ag-row-border-color': '#F3F4F6',
    '--ag-borders': 'none',
    '--ag-borders-critical': 'none',
    '--ag-borders-secondary': 'none',
    '--ag-row-border-style': 'solid',
    '--ag-row-border-width': '1px',
    
    // Row styling
    '--ag-row-hover-color': 'rgba(99, 102, 241, 0.04)',
    '--ag-selected-row-background-color': 'rgba(99, 102, 241, 0.08)',
    '--ag-odd-row-background-color': '#FFFFFF',
    '--ag-row-background-color': '#FFFFFF',
    '--ag-row-height': '48px',
    
    // Cell styling
    '--ag-cell-horizontal-padding': '16px',
    '--ag-range-selection-border-color': 'var(--color-primary)',
    '--ag-range-selection-background-color': 'rgba(99, 102, 241, 0.1)',
    
    // Other styling
    '--ag-checkbox-checked-color': 'var(--color-primary)',
    '--ag-checkbox-unchecked-color': '#9CA3AF',
    '--ag-checkbox-indeterminate-color': 'var(--color-primary)',
    '--ag-input-focus-border-color': 'var(--color-primary)',
    '--ag-input-focus-box-shadow': '0 0 0 2px rgba(99, 102, 241, 0.25)',
    '--ag-card-shadow': 'none',
    '--ag-card-radius': '8px',
    '--ag-invalid-color': 'var(--color-error)',
    '--ag-disabled-foreground-color': '#9CA3AF',
    
    // Animations
    '--ag-cell-horizontal-border': 'none',
    '--ag-selected-tab-underline-color': 'var(--color-primary)',
    '--ag-selected-tab-underline-width': '2px',
    '--ag-selected-tab-underline-transition-speed': '0.3s',
    '--ag-range-selection-border-style': 'solid',
    '--ag-range-selection-border-width': '2px',
  }
};

// Add custom styles to AG Grid
export const agGridCustomStyles = `
  .ag-header-cell-label {
    font-weight: 600;
    justify-content: flex-start;
  }
  
  .ag-header-cell:hover {
    background-color: rgba(99, 102, 241, 0.04);
  }
  
  .ag-row {
    transition: background-color 0.2s ease;
  }
  
  .ag-row:hover {
    background-color: rgba(99, 102, 241, 0.04);
  }
  
  .ag-row-selected {
    background-color: rgba(99, 102, 241, 0.08) !important;
  }
  
  .ag-cell {
    line-height: 48px;
  }
`;
