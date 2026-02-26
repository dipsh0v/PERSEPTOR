/**
 * PERSEPTOR v2.0 - Premium Theme System
 * Cybersecurity-grade design with glassmorphism, premium typography, and fluid animations.
 */

import { createTheme, Theme, alpha } from '@mui/material/styles';

// ─── Design Tokens ──────────────────────────────────────────────────────────

const tokens = {
  // Brand colors
  primary: {
    main: '#6366f1',      // Indigo-500
    light: '#818cf8',     // Indigo-400
    dark: '#4f46e5',      // Indigo-600
    contrast: '#ffffff',
  },
  secondary: {
    main: '#ec4899',      // Pink-500
    light: '#f472b6',     // Pink-400
    dark: '#db2777',      // Pink-600
    contrast: '#ffffff',
  },
  accent: {
    cyan: '#06b6d4',
    emerald: '#10b981',
    amber: '#f59e0b',
    rose: '#f43f5e',
    violet: '#8b5cf6',
  },
  // Dark mode surfaces
  dark: {
    bg: '#0a0e1a',          // Deep navy
    surface: '#111827',      // Card surface
    surfaceLight: '#1f2937', // Elevated surface
    border: '#1e293b',       // Subtle border
    borderLight: '#334155',  // Hover border
  },
  // Light mode surfaces
  light: {
    bg: '#f8fafc',
    surface: '#ffffff',
    surfaceLight: '#f1f5f9',
    border: '#e2e8f0',
    borderLight: '#cbd5e1',
  },
  // Typography
  font: {
    primary: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    mono: '"JetBrains Mono", "Fira Code", "Cascadia Code", monospace',
  },
  // Radius
  radius: {
    sm: 8,
    md: 12,
    lg: 16,
    xl: 20,
    full: 9999,
  },
};

// ─── Shared Component Overrides ─────────────────────────────────────────────

const getComponents = (mode: 'dark' | 'light') => {
  const isDark = mode === 'dark';
  const surface = isDark ? tokens.dark : tokens.light;

  return {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          scrollbarWidth: 'thin' as const,
          scrollbarColor: `${alpha(tokens.primary.main, 0.3)} transparent`,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: tokens.radius.lg,
          backgroundImage: 'none',
          backgroundColor: isDark ? alpha(surface.surface, 0.7) : surface.surface,
          backdropFilter: 'blur(20px)',
          border: `1px solid ${alpha(surface.border, isDark ? 0.5 : 1)}`,
          boxShadow: isDark
            ? `0 4px 24px ${alpha('#000', 0.3)}, 0 0 0 1px ${alpha(surface.border, 0.5)}`
            : `0 4px 24px ${alpha('#000', 0.06)}, 0 0 0 1px ${alpha(surface.border, 0.5)}`,
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            borderColor: alpha(tokens.primary.main, 0.3),
            boxShadow: isDark
              ? `0 8px 40px ${alpha('#000', 0.4)}, 0 0 0 1px ${alpha(tokens.primary.main, 0.2)}`
              : `0 8px 40px ${alpha('#000', 0.1)}, 0 0 0 1px ${alpha(tokens.primary.main, 0.15)}`,
            transform: 'translateY(-2px)',
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: tokens.radius.lg,
          backgroundImage: 'none',
          backgroundColor: isDark ? alpha(surface.surface, 0.6) : surface.surface,
          backdropFilter: 'blur(16px)',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: tokens.radius.md,
          textTransform: 'none' as const,
          fontWeight: 600,
          fontSize: '0.875rem',
          letterSpacing: '0.025em',
          padding: '10px 24px',
          transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
        },
        contained: {
          boxShadow: `0 2px 8px ${alpha(tokens.primary.main, 0.3)}`,
          '&:hover': {
            boxShadow: `0 4px 16px ${alpha(tokens.primary.main, 0.4)}`,
            transform: 'translateY(-1px)',
          },
          '&:active': {
            transform: 'translateY(0)',
          },
        },
        outlined: {
          borderWidth: '1.5px',
          '&:hover': {
            borderWidth: '1.5px',
            backgroundColor: alpha(tokens.primary.main, 0.08),
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: tokens.radius.md,
            transition: 'all 0.2s ease',
            '&:hover .MuiOutlinedInput-notchedOutline': {
              borderColor: alpha(tokens.primary.main, 0.5),
            },
            '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
              borderWidth: '2px',
              boxShadow: `0 0 0 3px ${alpha(tokens.primary.main, 0.12)}`,
            },
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: tokens.radius.sm,
          fontWeight: 500,
          fontSize: '0.75rem',
          letterSpacing: '0.02em',
        },
      },
    },
    MuiAccordion: {
      styleOverrides: {
        root: {
          borderRadius: `${tokens.radius.md}px !important`,
          '&:before': { display: 'none' },
          backgroundImage: 'none',
          backgroundColor: isDark ? alpha(surface.surface, 0.4) : alpha(surface.surfaceLight, 0.5),
          border: `1px solid ${alpha(surface.border, isDark ? 0.3 : 0.5)}`,
          transition: 'all 0.2s ease',
          '&:hover': {
            borderColor: alpha(tokens.primary.main, 0.2),
          },
        },
      },
    },
    MuiTab: {
      styleOverrides: {
        root: {
          textTransform: 'none' as const,
          fontWeight: 600,
          fontSize: '0.875rem',
          letterSpacing: '0.01em',
          minHeight: 48,
          borderRadius: `${tokens.radius.sm}px ${tokens.radius.sm}px 0 0`,
        },
      },
    },
    MuiTabs: {
      styleOverrides: {
        indicator: {
          height: 3,
          borderRadius: '3px 3px 0 0',
          background: `linear-gradient(90deg, ${tokens.primary.main}, ${tokens.secondary.main})`,
        },
      },
    },
    MuiDialog: {
      styleOverrides: {
        paper: {
          borderRadius: tokens.radius.xl,
          backgroundImage: 'none',
          backgroundColor: isDark ? surface.surface : surface.surface,
          border: `1px solid ${alpha(surface.border, 0.5)}`,
          boxShadow: `0 24px 80px ${alpha('#000', isDark ? 0.5 : 0.15)}`,
        },
      },
    },
    MuiAlert: {
      styleOverrides: {
        root: {
          borderRadius: tokens.radius.md,
          border: '1px solid',
          backdropFilter: 'blur(8px)',
        },
      },
    },
    MuiTooltip: {
      styleOverrides: {
        tooltip: {
          borderRadius: tokens.radius.sm,
          fontSize: '0.75rem',
          fontWeight: 500,
          backgroundColor: isDark ? '#1e293b' : '#334155',
          border: `1px solid ${alpha('#fff', 0.1)}`,
          boxShadow: `0 4px 16px ${alpha('#000', 0.3)}`,
        },
      },
    },
    MuiLinearProgress: {
      styleOverrides: {
        root: {
          borderRadius: tokens.radius.full,
          height: 6,
          backgroundColor: alpha(tokens.primary.main, 0.12),
        },
        bar: {
          borderRadius: tokens.radius.full,
          background: `linear-gradient(90deg, ${tokens.primary.main}, ${tokens.accent.cyan})`,
        },
      },
    },
    MuiDivider: {
      styleOverrides: {
        root: {
          borderColor: alpha(surface.border, 0.5),
        },
      },
    },
    MuiListItemButton: {
      styleOverrides: {
        root: {
          borderRadius: tokens.radius.md,
          transition: 'all 0.2s ease',
          '&:hover': {
            backgroundColor: alpha(tokens.primary.main, 0.08),
          },
        },
      },
    },
    MuiSelect: {
      styleOverrides: {
        root: {
          borderRadius: tokens.radius.md,
        },
      },
    },
  };
};

// ─── Dark Theme ─────────────────────────────────────────────────────────────

export const darkTheme: Theme = createTheme({
  palette: {
    mode: 'dark',
    primary: tokens.primary,
    secondary: tokens.secondary,
    background: {
      default: tokens.dark.bg,
      paper: tokens.dark.surface,
    },
    divider: alpha(tokens.dark.border, 0.8),
    text: {
      primary: '#f1f5f9',
      secondary: '#94a3b8',
    },
    success: { main: tokens.accent.emerald },
    warning: { main: tokens.accent.amber },
    error: { main: tokens.accent.rose },
    info: { main: tokens.accent.cyan },
  },
  typography: {
    fontFamily: tokens.font.primary,
    h1: { fontWeight: 800, letterSpacing: '-0.025em', lineHeight: 1.1 },
    h2: { fontWeight: 800, letterSpacing: '-0.025em', lineHeight: 1.15 },
    h3: { fontWeight: 700, letterSpacing: '-0.02em', lineHeight: 1.2 },
    h4: { fontWeight: 700, letterSpacing: '-0.015em', lineHeight: 1.25 },
    h5: { fontWeight: 600, letterSpacing: '-0.01em', lineHeight: 1.3 },
    h6: { fontWeight: 600, letterSpacing: '-0.005em', lineHeight: 1.35 },
    subtitle1: { fontWeight: 500, letterSpacing: '0', lineHeight: 1.5 },
    subtitle2: { fontWeight: 600, letterSpacing: '0.01em', lineHeight: 1.5 },
    body1: { fontWeight: 400, letterSpacing: '0', lineHeight: 1.7 },
    body2: { fontWeight: 400, letterSpacing: '0.01em', lineHeight: 1.65 },
    caption: { fontWeight: 500, letterSpacing: '0.03em', lineHeight: 1.5 },
    overline: { fontWeight: 700, letterSpacing: '0.1em', lineHeight: 1.5, textTransform: 'uppercase' as const },
    button: { fontWeight: 600, letterSpacing: '0.025em' },
  },
  shape: { borderRadius: tokens.radius.md },
  components: getComponents('dark') as any,
});

// ─── Light Theme ────────────────────────────────────────────────────────────

export const lightTheme: Theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#4f46e5',
      light: '#6366f1',
      dark: '#4338ca',
      contrastText: '#ffffff',
    },
    secondary: {
      main: '#db2777',
      light: '#ec4899',
      dark: '#be185d',
      contrastText: '#ffffff',
    },
    background: {
      default: tokens.light.bg,
      paper: tokens.light.surface,
    },
    divider: alpha(tokens.light.border, 0.8),
    text: {
      primary: '#0f172a',
      secondary: '#475569',
    },
    success: { main: '#059669' },
    warning: { main: '#d97706' },
    error: { main: '#dc2626' },
    info: { main: '#0891b2' },
  },
  typography: {
    fontFamily: tokens.font.primary,
    h1: { fontWeight: 800, letterSpacing: '-0.025em', lineHeight: 1.1 },
    h2: { fontWeight: 800, letterSpacing: '-0.025em', lineHeight: 1.15 },
    h3: { fontWeight: 700, letterSpacing: '-0.02em', lineHeight: 1.2 },
    h4: { fontWeight: 700, letterSpacing: '-0.015em', lineHeight: 1.25 },
    h5: { fontWeight: 600, letterSpacing: '-0.01em', lineHeight: 1.3 },
    h6: { fontWeight: 600, letterSpacing: '-0.005em', lineHeight: 1.35 },
    subtitle1: { fontWeight: 500, letterSpacing: '0', lineHeight: 1.5 },
    subtitle2: { fontWeight: 600, letterSpacing: '0.01em', lineHeight: 1.5 },
    body1: { fontWeight: 400, letterSpacing: '0', lineHeight: 1.7 },
    body2: { fontWeight: 400, letterSpacing: '0.01em', lineHeight: 1.65 },
    caption: { fontWeight: 500, letterSpacing: '0.03em', lineHeight: 1.5 },
    overline: { fontWeight: 700, letterSpacing: '0.1em', lineHeight: 1.5, textTransform: 'uppercase' as const },
    button: { fontWeight: 600, letterSpacing: '0.025em' },
  },
  shape: { borderRadius: tokens.radius.md },
  components: getComponents('light') as any,
});

// ─── Backward Compat ────────────────────────────────────────────────────────

export const theme = darkTheme;

export function getTheme(mode: 'dark' | 'light'): Theme {
  return mode === 'dark' ? darkTheme : lightTheme;
}
