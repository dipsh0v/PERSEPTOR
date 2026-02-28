import React from 'react';
import { Box, Typography, Chip, Accordion, AccordionSummary, AccordionDetails, useTheme } from '@mui/material';
import { alpha } from '@mui/material/styles';
import ShieldIcon from '@mui/icons-material/Shield';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

const CODE_FONT = '"JetBrains Mono", "Fira Code", "Cascadia Code", monospace';
const EASING = 'cubic-bezier(0.4, 0, 0.2, 1)';

interface Props {
  matches: any[];
  sectionHeader: (icon: React.ReactNode, label: string) => React.ReactNode;
  premiumAccordion: any;
  PRIMARY: string;
}

const GlobalSigmaMatchesViewer: React.FC<Props> = ({ matches, sectionHeader, premiumAccordion, PRIMARY }) => {
  const theme = useTheme();
  return (
    <Box sx={{ mb: 2, overflow: 'hidden', maxWidth: '100%' }}>
      {sectionHeader(<ShieldIcon sx={{ fontSize: 22, color: PRIMARY }} />, 'Global Sigma Matches')}
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2, overflow: 'hidden' }}>
        {matches.map((match, index) => {
          const score = match.match_ratio;
          const scoreColor = score >= 80 ? '#10b981' : score >= 60 ? '#f59e0b' : score >= 40 ? '#eab308' : theme.palette.error.main;
          const levelColor = match.level === 'critical' ? theme.palette.error.main : match.level === 'high' ? '#f59e0b' : '#3b82f6';
          const confidenceColor = match.confidence === 'Direct Hit' ? '#10b981' : match.confidence === 'Strong Match' ? '#f59e0b' : match.confidence === 'Relevant' ? '#eab308' : '#94a3b8';
          const breakdown = match.score_breakdown;
          return (
            <Accordion key={index} sx={premiumAccordion}>
              <AccordionSummary expandIcon={<ExpandMoreIcon sx={{ color: alpha(PRIMARY, 0.6) }} />} sx={{ overflow: 'hidden' }}>
                <Box sx={{ width: '100%', display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap', overflow: 'hidden', minWidth: 0 }}>
                  <Typography
                    component="a"
                    href={match.github_link}
                    target="_blank"
                    rel="noopener noreferrer"
                    onClick={(e: React.MouseEvent) => e.stopPropagation()}
                    variant="subtitle1"
                    sx={{
                      flex: '1 1 0', minWidth: 0, fontWeight: 600, fontFamily: '"Inter", sans-serif',
                      color: 'inherit', textDecoration: 'none',
                      overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
                      '&:hover': { color: PRIMARY, textDecoration: 'underline' },
                    }}
                  >
                    {match.title}
                  </Typography>
                  {match.confidence && (
                    <Chip label={match.confidence} size="small" sx={{
                      fontFamily: '"Inter", sans-serif', fontWeight: 700, fontSize: '0.68rem',
                      borderRadius: '6px', backgroundColor: alpha(confidenceColor, 0.12),
                      color: confidenceColor, border: `1px solid ${alpha(confidenceColor, 0.25)}`,
                    }} />
                  )}
                  <Chip label={`${score}%`} size="small" sx={{
                    fontFamily: CODE_FONT, fontWeight: 700, fontSize: '0.72rem',
                    borderRadius: '6px', backgroundColor: alpha(scoreColor, 0.12),
                    color: scoreColor, border: `1px solid ${alpha(scoreColor, 0.25)}`,
                  }} />
                  <Chip label={match.level} size="small" sx={{
                    fontFamily: '"Inter", sans-serif', fontWeight: 700, fontSize: '0.68rem',
                    borderRadius: '6px', textTransform: 'uppercase', letterSpacing: '0.05em',
                    backgroundColor: alpha(levelColor, 0.12), color: levelColor,
                    border: `1px solid ${alpha(levelColor, 0.25)}`,
                  }} />
                </Box>
              </AccordionSummary>
              <AccordionDetails sx={{ pt: 0 }}>
                <Typography variant="body2" sx={{ color: theme.palette.text.secondary, fontFamily: '"Inter", sans-serif', mb: 2, lineHeight: 1.7 }}>
                  {match.description}
                </Typography>

                {/* Score Breakdown Mini Bars */}
                {breakdown && (
                  <Box sx={{ mb: 2.5 }}>
                    <Typography variant="caption" sx={{ fontWeight: 600, display: 'block', mb: 1, color: alpha(theme.palette.text.primary, 0.6) }}>
                      Score Breakdown
                    </Typography>
                    <Box sx={{ display: 'grid', gridTemplateColumns: 'auto 1fr auto', gap: '4px 10px', alignItems: 'center' }}>
                      {[
                        { label: 'MITRE', value: breakdown.mitre, max: 40, color: '#8b5cf6' },
                        { label: 'IoC Field', value: breakdown.ioc_field, max: 25, color: '#10b981' },
                        { label: 'Logsource', value: breakdown.logsource, max: 15, color: '#3b82f6' },
                        { label: 'Keywords', value: breakdown.keyword, max: 20, color: '#f59e0b' },
                      ].map((bar) => (
                        <React.Fragment key={bar.label}>
                          <Typography variant="caption" sx={{ fontFamily: '"Inter", sans-serif', fontSize: '0.68rem', color: 'text.secondary', minWidth: 62 }}>
                            {bar.label}
                          </Typography>
                          <Box sx={{ height: 6, borderRadius: 3, backgroundColor: alpha(bar.color, 0.1), overflow: 'hidden' }}>
                            <Box sx={{ width: `${(bar.value / bar.max) * 100}%`, height: '100%', borderRadius: 3, background: `linear-gradient(90deg, ${bar.color}, ${alpha(bar.color, 0.6)})`, transition: 'width 0.5s ease' }} />
                          </Box>
                          <Typography variant="caption" sx={{ fontFamily: CODE_FONT, fontSize: '0.68rem', fontWeight: 600, color: bar.color, minWidth: 28, textAlign: 'right' }}>
                            {bar.value}
                          </Typography>
                        </React.Fragment>
                      ))}
                    </Box>
                  </Box>
                )}

                {/* MITRE Techniques Matched */}
                {match.mitre_matched && match.mitre_matched.length > 0 && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="caption" sx={{ fontWeight: 600, display: 'block', mb: 0.8, color: alpha(theme.palette.text.primary, 0.6) }}>
                      MITRE ATT&CK Matched
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.6 }}>
                      {match.mitre_matched.map((tid: string, idx: number) => (
                        <Chip key={idx} label={tid.toUpperCase()} size="small" sx={{
                          fontFamily: CODE_FONT, fontSize: '0.68rem', fontWeight: 700,
                          borderRadius: '6px', height: 22,
                          backgroundColor: alpha('#8b5cf6', 0.1), color: '#8b5cf6',
                          border: `1px solid ${alpha('#8b5cf6', 0.25)}`,
                        }} />
                      ))}
                    </Box>
                  </Box>
                )}

                {/* Matched Keywords */}
                {match.matched_keywords && match.matched_keywords.length > 0 && (
                  <Box>
                    <Typography variant="caption" sx={{ fontWeight: 600, display: 'block', mb: 0.8, color: alpha(theme.palette.text.primary, 0.6) }}>
                      Matched Keywords
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.6 }}>
                      {match.matched_keywords.map((keyword: string, idx: number) => (
                        <Chip key={idx} label={keyword} size="small" variant="outlined" sx={{
                          fontFamily: CODE_FONT, fontSize: '0.72rem', borderRadius: '6px',
                          borderColor: alpha(PRIMARY, 0.3), color: alpha(theme.palette.text.primary, 0.7),
                          transition: `all 0.25s ${EASING}`,
                          '&:hover': { borderColor: PRIMARY, backgroundColor: alpha(PRIMARY, 0.06) },
                        }} />
                      ))}
                    </Box>
                  </Box>
                )}

                {/* GitHub Link */}
                {match.github_link && (
                  <Box sx={{ mt: 2, pt: 1.5, borderTop: `1px solid ${alpha(theme.palette.divider, 0.08)}` }}>
                    <Typography
                      component="a"
                      href={match.github_link}
                      target="_blank"
                      rel="noopener noreferrer"
                      variant="caption"
                      sx={{
                        color: PRIMARY, fontFamily: CODE_FONT, fontSize: '0.72rem',
                        textDecoration: 'none', '&:hover': { textDecoration: 'underline' },
                      }}
                    >
                      View on SigmaHQ GitHub
                    </Typography>
                  </Box>
                )}
              </AccordionDetails>
            </Accordion>
          );
        })}
      </Box>
    </Box>
  );
};

export default GlobalSigmaMatchesViewer;
