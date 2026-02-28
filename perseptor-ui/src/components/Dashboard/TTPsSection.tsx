import React from 'react';
import { Box, Chip } from '@mui/material';
import { alpha } from '@mui/material/styles';
import GpsFixedIcon from '@mui/icons-material/GpsFixed';

const EASING = 'cubic-bezier(0.4, 0, 0.2, 1)';

interface Props {
  ttps: any[];
  sectionHeader: (icon: React.ReactNode, label: string) => React.ReactNode;
  PRIMARY: string;
}

const TTPsSection: React.FC<Props> = ({ ttps, sectionHeader, PRIMARY }) => {
  return (
    <Box sx={{ mb: 4 }}>
      {sectionHeader(<GpsFixedIcon sx={{ fontSize: 22, color: PRIMARY }} />, 'MITRE ATT&CK TTPs')}
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 2 }}>
        {ttps.map((ttp, index) => (
          <Chip
            key={index}
            label={typeof ttp === 'string' ? ttp : ttp.technique_name}
            sx={{
              fontFamily: '"Inter", sans-serif',
              fontWeight: 600,
              fontSize: '0.82rem',
              borderRadius: '10px',
              backgroundColor: alpha('#f59e0b', 0.1),
              color: '#f59e0b',
              border: `1px solid ${alpha('#f59e0b', 0.25)}`,
              transition: `all 0.25s ${EASING}`,
              '&:hover': {
                backgroundColor: alpha('#f59e0b', 0.18),
                boxShadow: `0 0 12px ${alpha('#f59e0b', 0.2)}`,
              },
            }}
          />
        ))}
      </Box>
    </Box>
  );
};

export default TTPsSection;
