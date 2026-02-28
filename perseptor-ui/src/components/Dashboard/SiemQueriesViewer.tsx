import React from 'react';
import { Box, Typography, Chip, Accordion, AccordionSummary, AccordionDetails, useTheme } from '@mui/material';
import { alpha } from '@mui/material/styles';
import StorageIcon from '@mui/icons-material/Storage';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

interface Props {
  queries: Record<string, any>;
  sectionHeader: (icon: React.ReactNode, label: string) => React.ReactNode;
  premiumAccordion: any;
  codeBlock: any;
  PRIMARY: string;
  SECONDARY: string;
}

const SiemQueriesViewer: React.FC<Props> = ({ queries, sectionHeader, premiumAccordion, codeBlock, PRIMARY, SECONDARY }) => {
  const theme = useTheme();
  return (
    <Box sx={{ mb: 4 }}>
      {sectionHeader(<StorageIcon sx={{ fontSize: 22, color: PRIMARY }} />, 'Generated SIEM Queries')}
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
        {Object.entries(queries).map(([platform, query]) => {
          const platformColors: Record<string, string> = {
            splunk: PRIMARY,
            qradar: SECONDARY,
            elastic: '#10b981',
            sentinel: '#f59e0b',
          };
          const pColor = platformColors[platform] || '#6b7280';
          return (
            <Accordion key={platform} sx={premiumAccordion}>
              <AccordionSummary expandIcon={<ExpandMoreIcon sx={{ color: alpha(PRIMARY, 0.6) }} />}>
                <Box sx={{ width: '100%', display: 'flex', alignItems: 'center', gap: 1.5 }}>
                  <Typography
                    variant="subtitle1"
                    sx={{
                      flexGrow: 1,
                      textTransform: 'capitalize',
                      fontWeight: 600,
                      fontFamily: '"Inter", sans-serif',
                    }}
                  >
                    {platform} Query
                  </Typography>
                  <Chip
                    label={platform}
                    size="small"
                    sx={{
                      fontFamily: '"Inter", sans-serif',
                      fontWeight: 700,
                      fontSize: '0.72rem',
                      borderRadius: '6px',
                      textTransform: 'uppercase',
                      letterSpacing: '0.05em',
                      backgroundColor: alpha(pColor, 0.12),
                      color: pColor,
                      border: `1px solid ${alpha(pColor, 0.25)}`,
                    }}
                  />
                </Box>
              </AccordionSummary>
              <AccordionDetails sx={{ pt: 0 }}>
                <Typography
                  variant="body2"
                  sx={{
                    color: theme.palette.text.secondary,
                    fontFamily: '"Inter", sans-serif',
                    mb: 2,
                    lineHeight: 1.7,
                  }}
                >
                  {query.description}
                </Typography>
                <Box component="pre" sx={codeBlock}>
                  {query.query}
                </Box>
                {query.notes && (
                  <Typography
                    variant="caption"
                    sx={{
                      display: 'block',
                      mt: 1.5,
                      color: alpha(theme.palette.text.secondary, 0.7),
                      fontFamily: '"Inter", sans-serif',
                      fontStyle: 'italic',
                    }}
                  >
                    Notes: {query.notes}
                  </Typography>
                )}
              </AccordionDetails>
            </Accordion>
          );
        })}
      </Box>
    </Box>
  );
};

export default SiemQueriesViewer;
