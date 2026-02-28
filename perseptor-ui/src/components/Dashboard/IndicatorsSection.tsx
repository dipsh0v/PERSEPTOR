import React from 'react';
import { Box, Typography, Chip, Tooltip, useTheme } from '@mui/material';
import { alpha } from '@mui/material/styles';
import FingerprintIcon from '@mui/icons-material/Fingerprint';

const CODE_FONT = '"JetBrains Mono", "Fira Code", "Cascadia Code", monospace';
const EASING = 'cubic-bezier(0.4, 0, 0.2, 1)';

interface Props {
  iocs: Record<string, any>;
  sectionHeader: (icon: React.ReactNode, label: string) => React.ReactNode;
  PRIMARY: string;
  SECONDARY: string;
}

const IndicatorsSection: React.FC<Props> = ({ iocs, sectionHeader, PRIMARY, SECONDARY }) => {
  const theme = useTheme();
  return (
    <Box sx={{ mb: 4 }}>
      {sectionHeader(<FingerprintIcon sx={{ fontSize: 22, color: PRIMARY }} />, 'Indicators of Compromise')}
      <Box sx={{ mt: 2 }}>
        {Object.entries(iocs).map(([key, value]) => (
          Array.isArray(value) && value.length > 0 && (
            <Box key={key} sx={{ mb: 2.5 }}>
              <Typography
                variant="subtitle2"
                sx={{
                  color: alpha(theme.palette.text.primary, 0.6),
                  fontFamily: '"Inter", sans-serif',
                  fontWeight: 600,
                  fontSize: '0.75rem',
                  letterSpacing: '0.08em',
                  textTransform: 'uppercase',
                  mb: 1,
                }}
              >
                {key.replace(/_/g, ' ')}
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.8 }}>
                {value.map((item, index) => {
                  const isIp = key.includes('ip');
                  const isDomain = key.includes('domain');
                  const isHash = key.includes('hash') || key.includes('md5') || key.includes('sha');
                  const isUrl = key.includes('url');
                  const chipColor = isHash ? SECONDARY : isIp ? '#f59e0b' : isDomain ? '#10b981' : isUrl ? '#3b82f6' : PRIMARY;
                  return (
                    <Tooltip key={index} title={item} arrow>
                      <Chip
                        label={item}
                        size="small"
                        sx={{
                          fontFamily: CODE_FONT,
                          fontSize: '0.78rem',
                          fontWeight: 500,
                          borderRadius: '8px',
                          maxWidth: '340px',
                          backgroundColor: alpha(chipColor, 0.1),
                          color: chipColor,
                          border: `1px solid ${alpha(chipColor, 0.2)}`,
                          transition: `all 0.25s ${EASING}`,
                          '& .MuiChip-label': {
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap',
                          },
                          '&:hover': {
                            backgroundColor: alpha(chipColor, 0.18),
                            boxShadow: `0 0 12px ${alpha(chipColor, 0.2)}`,
                            transform: 'translateY(-1px)',
                          },
                        }}
                      />
                    </Tooltip>
                  );
                })}
              </Box>
            </Box>
          )
        ))}
      </Box>
    </Box>
  );
};

export default IndicatorsSection;
