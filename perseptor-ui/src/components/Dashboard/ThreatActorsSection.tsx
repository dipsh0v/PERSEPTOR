import React from 'react';
import { Box, Typography, Chip, useTheme } from '@mui/material';
import { alpha } from '@mui/material/styles';
import SecurityIcon from '@mui/icons-material/Security';

const EASING = 'cubic-bezier(0.4, 0, 0.2, 1)';

interface Props {
  actors: string[];
  sectionHeader: (icon: React.ReactNode, label: string) => React.ReactNode;
  PRIMARY: string;
}

const ThreatActorsSection: React.FC<Props> = ({ actors, sectionHeader, PRIMARY }) => {
  const theme = useTheme();
  return (
    <Box sx={{ mb: 4 }}>
      {sectionHeader(<SecurityIcon sx={{ fontSize: 22, color: PRIMARY }} />, 'Threat Actors')}
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 2 }}>
        {actors.map((actor, index) => (
          <Chip
            key={index}
            label={actor}
            sx={{
              fontFamily: '"Inter", sans-serif',
              fontWeight: 700,
              fontSize: '0.85rem',
              borderRadius: '10px',
              backgroundColor: alpha(theme.palette.error.main, 0.1),
              color: theme.palette.error.main,
              border: `1px solid ${alpha(theme.palette.error.main, 0.25)}`,
              transition: `all 0.25s ${EASING}`,
              '&:hover': {
                backgroundColor: alpha(theme.palette.error.main, 0.18),
                boxShadow: `0 0 16px ${alpha(theme.palette.error.main, 0.2)}`,
              },
            }}
          />
        ))}
      </Box>
    </Box>
  );
};

export default ThreatActorsSection;
