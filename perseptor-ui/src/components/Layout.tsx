import React from 'react';
import { Box, useTheme } from '@mui/material';
import { alpha } from '@mui/material/styles';
import Sidebar from './Sidebar';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const theme = useTheme();

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <Sidebar />
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          ml: '260px',
          width: 'calc(100% - 260px)',
          minHeight: '100vh',
          background: theme.palette.background.default,
          position: 'relative',
          overflowX: 'hidden',
          overflowY: 'auto',
        }}
      >
        <Box sx={{ position: 'relative', zIndex: 1 }}>
          {children}
        </Box>
      </Box>
    </Box>
  );
};

export default Layout;
