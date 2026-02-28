import React from 'react';
import { Box, Typography, Chip, Accordion, AccordionSummary, AccordionDetails, useTheme } from '@mui/material';
import { alpha } from '@mui/material/styles';
import ShieldIcon from '@mui/icons-material/Shield';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

interface Props {
  rules: string;
  sectionHeader: (icon: React.ReactNode, label: string) => React.ReactNode;
  premiumAccordion: any;
  codeBlock: any;
  PRIMARY: string;
}

const GeneratedSigmaRules: React.FC<Props> = ({ rules, sectionHeader, premiumAccordion, codeBlock, PRIMARY }) => {
  const theme = useTheme();

  return (
    <Box sx={{ mb: 4 }}>
      {sectionHeader(<ShieldIcon sx={{ fontSize: 22, color: PRIMARY }} />, 'Generated Sigma Rules')}
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
        {rules.split('---').filter((rule) => {
          if (!rule.trim()) return false;
          const t = rule.match(/title:\s*(.+)/);
          if (t && t[1].trim().startsWith('PERSEPTOR - Suspicious')) return false;
          return true;
        }).map((rule, index) => {
          const titleMatch = rule.match(/title:\s*(.+)/);
          const levelMatch = rule.match(/level:\s*(.+)/);
          const level = levelMatch ? levelMatch[1].trim() : '';
          const levelColor = level === 'critical' ? theme.palette.error.main : level === 'high' ? '#f59e0b' : '#3b82f6';
          return (
            <Accordion key={index} sx={premiumAccordion}>
              <AccordionSummary
                expandIcon={<ExpandMoreIcon sx={{ color: alpha(PRIMARY, 0.6) }} />}
              >
                <Box sx={{ width: '100%' }}>
                  <Typography
                    variant="subtitle1"
                    sx={{
                      fontWeight: 700,
                      fontFamily: '"Inter", sans-serif',
                      letterSpacing: '-0.01em',
                    }}
                  >
                    {titleMatch ? titleMatch[1].trim() : `Sigma Rule ${index + 1}`}
                  </Typography>
                  {levelMatch && (
                    <Chip
                      label={level}
                      size="small"
                      sx={{
                        mt: 1,
                        fontFamily: '"Inter", sans-serif',
                        fontWeight: 600,
                        fontSize: '0.72rem',
                        borderRadius: '6px',
                        textTransform: 'uppercase',
                        letterSpacing: '0.05em',
                        backgroundColor: alpha(levelColor, 0.1),
                        color: levelColor,
                        border: `1px solid ${alpha(levelColor, 0.25)}`,
                      }}
                    />
                  )}
                </Box>
              </AccordionSummary>
              <AccordionDetails sx={{ pt: 0 }}>
                <Box component="pre" sx={codeBlock}>
                  {rule.trim()}
                </Box>
              </AccordionDetails>
            </Accordion>
          );
        })}
      </Box>
    </Box>
  );
};

export default GeneratedSigmaRules;
