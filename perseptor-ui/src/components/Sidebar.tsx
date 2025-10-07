import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  useTheme,
  Typography,
  Avatar,
  Fade,
  Zoom,
} from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import AssessmentIcon from '@mui/icons-material/Assessment';
import SecurityIcon from '@mui/icons-material/Security';
import SearchIcon from '@mui/icons-material/Search';
import TrackChangesIcon from '@mui/icons-material/TrackChanges';
import SigmaIcon from './SigmaIcon';
import InfoIcon from '@mui/icons-material/Info';

const Sidebar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();

  const menuItems = [
    {
      text: 'About PERSEPTOR',
      icon: <InfoIcon />,
      path: '/about',
    },
    {
      text: 'Threat Report Analysis',
      icon: <SearchIcon />,
      path: '/',
    },
    {
      text: 'Analyzed Reports',
      icon: <AssessmentIcon />,
      path: '/reports',
    },
    {
      text: 'Detection QA',
      icon: <TrackChangesIcon />,
      path: '/qa',
    },
    {
      text: 'Created Rules',
      icon: <SigmaIcon color={theme.palette.mode === 'dark' ? '#fff' : '#222'} />,
      path: '/rules',
    },
  ];

  return (
    <Box
      sx={{
        width: 280,
        height: '100vh',
        backgroundColor: theme.palette.background.paper,
        borderRight: `1px solid ${theme.palette.divider}`,
        display: 'flex',
        flexDirection: 'column',
        position: 'fixed',
        left: 0,
        top: 0,
        background: `linear-gradient(135deg, ${theme.palette.background.paper}, ${theme.palette.background.default})`,
        boxShadow: `0 8px 32px ${theme.palette.primary.main}10`,
        backdropFilter: 'blur(4px)',
      }}
    >
      <Fade in timeout={1000}>
        <Box
          sx={{
            p: 3,
            display: 'flex',
            alignItems: 'center',
            gap: 2,
            borderBottom: `1px solid ${theme.palette.divider}`,
          }}
        >
          <Typography
            variant="h5"
            sx={{
              fontWeight: 'bold',
              background: `linear-gradient(45deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
              backgroundClip: 'text',
              textFillColor: 'transparent',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              position: 'relative',
              letterSpacing: 2,
              textShadow: '0 2px 8px rgba(0,0,0,0.10)',
              overflow: 'hidden',
              '&:after': {
                content: '""',
                position: 'absolute',
                top: 0,
                left: '-75%',
                width: '50%',
                height: '100%',
                background: 'linear-gradient(120deg, transparent, rgba(255,255,255,0.3), transparent)',
                transform: 'skewX(-20deg)',
                animation: 'shine 2.5s infinite',
              },
              '@keyframes shine': {
                '100%': { left: '125%' }
              }
            }}
          >
            PERSEPTOR
          </Typography>
        </Box>
      </Fade>

      <Zoom in timeout={1000} style={{ transitionDelay: '200ms' }}>
        <List sx={{ flex: 1, pt: 2 }}>
          {menuItems.map((item) => (
            <ListItem key={item.text} disablePadding>
              <ListItemButton
                onClick={() => navigate(item.path)}
                sx={{
                  mx: 2,
                  mb: 1,
                  borderRadius: 2,
                  transition: 'all 0.3s ease',
                  backgroundColor: location.pathname === item.path ? `${theme.palette.primary.main}15` : 'transparent',
                  '&:hover': {
                    backgroundColor: `${theme.palette.primary.main}25`,
                    transform: 'translateX(8px)',
                  },
                }}
              >
                <ListItemIcon
                  sx={{
                    color: location.pathname === item.path ? theme.palette.primary.main : theme.palette.text.secondary,
                    transition: 'all 0.3s ease',
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                <ListItemText
                  primary={item.text}
                  sx={{
                    '& .MuiTypography-root': {
                      fontWeight: location.pathname === item.path ? 'bold' : 'normal',
                      color: location.pathname === item.path ? theme.palette.primary.main : theme.palette.text.primary,
                      transition: 'all 0.3s ease',
                    },
                  }}
                />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
      </Zoom>
    </Box>
  );
};

export default Sidebar; 