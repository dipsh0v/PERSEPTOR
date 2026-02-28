import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Typography,
  Tooltip,
  useTheme,
} from '@mui/material';
import { alpha } from '@mui/material/styles';
import AssessmentIcon from '@mui/icons-material/Assessment';
import SearchIcon from '@mui/icons-material/Search';
import TrackChangesIcon from '@mui/icons-material/TrackChanges';
import SettingsIcon from '@mui/icons-material/Settings';
import InfoIcon from '@mui/icons-material/Info';
import FiberManualRecordIcon from '@mui/icons-material/FiberManualRecord';
import SigmaIcon from './SigmaIcon';
import { useAppSelector } from '../store';

const SIDEBAR_WIDTH = 260;

const Sidebar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const { isConnected, aiProvider, selectedModel } = useAppSelector(
    (state) => state.settings
  );

  const menuItems = [
    { text: 'About PERSEPTOR', icon: <InfoIcon />, path: '/about' },
    { text: 'Threat Analysis', icon: <SearchIcon />, path: '/' },
    { text: 'Reports', icon: <AssessmentIcon />, path: '/reports' },
    { text: 'Detection QA', icon: <TrackChangesIcon />, path: '/qa' },
    { text: 'Created Rules', icon: <SigmaIcon />, path: '/rules' },
    { text: 'Settings', icon: <SettingsIcon />, path: '/settings' },
  ];

  return (
    <Box
      sx={{
        width: SIDEBAR_WIDTH,
        height: '100vh',
        position: 'fixed',
        left: 0,
        top: 0,
        zIndex: 1200,
        display: 'flex',
        flexDirection: 'column',
        background: theme.palette.mode === 'dark'
          ? alpha(theme.palette.background.paper, 0.98)
          : alpha(theme.palette.background.paper, 0.98),
        backdropFilter: 'blur(16px)',
        borderRight: `1px solid ${theme.palette.divider}`,
        boxShadow: theme.palette.mode === 'dark'
          ? `4px 0 24px ${alpha('#000', 0.3)}`
          : `4px 0 24px ${alpha('#000', 0.05)}`,
      }}
    >
      {/* Logo Section */}
      <Box
        sx={{
          p: 3,
          pb: 2,
          borderBottom: `1px solid ${alpha(theme.palette.divider, 0.3)}`,
        }}
      >
        <Typography
          variant="h5"
          sx={{
            fontWeight: 800,
            letterSpacing: '0.08em',
            color: theme.palette.text.primary,
            position: 'relative',
            overflow: 'hidden',
            cursor: 'default',
            display: 'flex',
            alignItems: 'center',
            gap: 1,
            '&::before': {
              content: '""',
              display: 'inline-block',
              width: 12,
              height: 12,
              borderRadius: '50%',
              backgroundColor: theme.palette.primary.main,
            }
          }}
        >
          PERSEPTOR
        </Typography>
        <Typography
          variant="caption"
          sx={{
            color: alpha(theme.palette.text.secondary, 0.6),
            letterSpacing: '0.05em',
            display: 'block',
            mt: 0.5,
          }}
        >
          Detection Engineering Platform
        </Typography>
      </Box>

      {/* Navigation */}
      <List sx={{ flex: 1, py: 2, px: 1.5 }}>
        {menuItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <ListItem key={item.text} disablePadding sx={{ mb: 0.5 }}>
              <ListItemButton
                onClick={() => navigate(item.path)}
                sx={{
                  borderRadius: '10px',
                  py: 1.2,
                  px: 2,
                  position: 'relative',
                  overflow: 'hidden',
                  transition: 'all 0.25s cubic-bezier(0.4, 0, 0.2, 1)',
                  backgroundColor: isActive
                    ? alpha(theme.palette.primary.main, 0.12)
                    : 'transparent',
                  borderLeft: isActive
                    ? `3px solid ${theme.palette.primary.main}`
                    : '3px solid transparent',
                  '&:hover': {
                    backgroundColor: alpha(theme.palette.primary.main, isActive ? 0.15 : 0.06),
                    transform: 'translateX(4px)',
                    '& .MuiListItemIcon-root': {
                      color: theme.palette.primary.main,
                    },
                  },
                }}
              >
                <ListItemIcon
                  sx={{
                    minWidth: 36,
                    color: isActive
                      ? theme.palette.primary.main
                      : theme.palette.text.secondary,
                    transition: 'color 0.2s ease',
                    '& .MuiSvgIcon-root': { fontSize: 20 },
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                <ListItemText
                  primary={item.text}
                  primaryTypographyProps={{
                    fontSize: '0.835rem',
                    fontWeight: isActive ? 600 : 400,
                    color: isActive
                      ? theme.palette.text.primary
                      : theme.palette.text.secondary,
                    letterSpacing: '0.01em',
                  }}
                />
                {isActive && (
                  <Box
                    sx={{
                      position: 'absolute',
                      right: 12,
                      width: 6,
                      height: 6,
                      borderRadius: '50%',
                      backgroundColor: theme.palette.primary.main,
                      boxShadow: `0 0 8px ${theme.palette.primary.main}`,
                    }}
                  />
                )}
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>

      {/* Connection Status */}
      <Box
        sx={{
          p: 2,
          mx: 1.5,
          mb: 1,
          borderRadius: '10px',
          backgroundColor: alpha(theme.palette.divider, 0.08),
          border: `1px solid ${alpha(theme.palette.divider, 0.15)}`,
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <FiberManualRecordIcon
            sx={{
              fontSize: 10,
              color: isConnected ? theme.palette.success.main : theme.palette.error.main,
              animation: isConnected ? 'connPulse 2s ease-in-out infinite' : 'none',
              '@keyframes connPulse': {
                '0%, 100%': { opacity: 1, transform: 'scale(1)' },
                '50%': { opacity: 0.5, transform: 'scale(1.3)' },
              },
            }}
          />
          <Box sx={{ flex: 1, minWidth: 0 }}>
            <Typography
              variant="caption"
              sx={{
                fontWeight: 600,
                color: isConnected
                  ? theme.palette.success.main
                  : alpha(theme.palette.text.secondary, 0.6),
                display: 'block',
                fontSize: '0.7rem',
                letterSpacing: '0.03em',
              }}
            >
              {isConnected ? aiProvider.toUpperCase() : 'NOT CONNECTED'}
            </Typography>
            {isConnected && (
              <Typography
                variant="caption"
                sx={{
                  color: alpha(theme.palette.text.secondary, 0.5),
                  display: 'block',
                  fontSize: '0.65rem',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                }}
              >
                {selectedModel}
              </Typography>
            )}
          </Box>
        </Box>
      </Box>

      {/* Version */}
      <Box sx={{ p: 2, pt: 0, textAlign: 'center' }}>
        <Typography
          variant="caption"
          sx={{
            color: alpha(theme.palette.text.secondary, 0.3),
            fontSize: '0.6rem',
            letterSpacing: '0.1em',
          }}
        >
          v2.0.0
        </Typography>
      </Box>
    </Box>
  );
};

export default Sidebar;
