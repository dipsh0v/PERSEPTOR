import React from 'react';
import { Box, Typography, Accordion, AccordionSummary, AccordionDetails, useTheme } from '@mui/material';
import { alpha } from '@mui/material/styles';
import BugReportIcon from '@mui/icons-material/BugReport';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

interface Props {
  rules: any[];
  sectionHeader: (icon: React.ReactNode, label: string) => React.ReactNode;
  premiumAccordion: any;
  codeBlock: any;
  PRIMARY: string;
}

const GeneratedYaraRules: React.FC<Props> = ({ rules, sectionHeader, premiumAccordion, codeBlock, PRIMARY }) => {
  const theme = useTheme();
  return (
    <Box sx={{ mb: 4 }}>
      {sectionHeader(<BugReportIcon sx={{ fontSize: 22, color: PRIMARY }} />, 'Generated YARA Rules')}
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
        {rules.map((rule, index) => (
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
                  }}
                >
                  {rule.name}
                </Typography>
                <Typography
                  variant="body2"
                  sx={{
                    color: alpha(theme.palette.text.secondary, 0.7),
                    fontFamily: '"Inter", sans-serif',
                    mt: 0.5,
                  }}
                >
                  {rule.description}
                </Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails sx={{ pt: 0 }}>
              <Box component="pre" sx={codeBlock}>
                {rule.rule}
              </Box>
            </AccordionDetails>
          </Accordion>
        ))}
      </Box>
    </Box>
  );
};

export default GeneratedYaraRules;
