import React from 'react';
import { Box, Typography, useTheme } from '@mui/material';
import { alpha } from '@mui/material/styles';
import SecurityIcon from '@mui/icons-material/Security';

interface Props {
  summary: string;
  sectionHeader: (icon: React.ReactNode, label: string) => React.ReactNode;
  PRIMARY: string;
}

const ThreatSummaryCard: React.FC<Props> = ({ summary, sectionHeader, PRIMARY }) => {
  const theme = useTheme();
  return (
    <Box sx={{ mb: 4 }}>
      {sectionHeader(<SecurityIcon sx={{ fontSize: 22, color: PRIMARY }} />, 'Threat Summary')}
      <Typography
        variant="body1"
        sx={{
          whiteSpace: 'pre-wrap',
          lineHeight: 1.9,
          color: theme.palette.text.secondary,
          fontFamily: '"Inter", sans-serif',
          mt: 2,
          pl: 1,
          borderLeft: `3px solid ${alpha(PRIMARY, 0.2)}`,
          paddingLeft: 2,
        }}
      >
        {summary}
      </Typography>
    </Box>
  );
};

export default ThreatSummaryCard;
