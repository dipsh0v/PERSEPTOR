import React from 'react';
import { Box, Typography, Chip, Accordion, AccordionSummary, AccordionDetails, Alert, IconButton, Tooltip, useTheme } from '@mui/material';
import { alpha } from '@mui/material/styles';
import ScienceIcon from '@mui/icons-material/Science';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import TerminalIcon from '@mui/icons-material/Terminal';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';

const CODE_FONT = '"JetBrains Mono", "Fira Code", "Cascadia Code", monospace';

interface Props {
  tests: any[];
  sectionHeader: (icon: React.ReactNode, label: string) => React.ReactNode;
  premiumAccordion: any;
  codeBlock: any;
  PRIMARY: string;
  SECONDARY: string;
}

const AtomicTestsAccordion: React.FC<Props> = ({ tests, sectionHeader, premiumAccordion, codeBlock, PRIMARY, SECONDARY }) => {
  const theme = useTheme();
  return (
    <Box sx={{ mb: 4 }}>
      {sectionHeader(<ScienceIcon sx={{ fontSize: 22, color: PRIMARY }} />, 'Atomic Red Team Test Scenarios')}
      <Alert
        severity="warning"
        icon={<WarningAmberIcon />}
        sx={{
          mt: 2, mb: 2, borderRadius: '12px',
          border: `1px solid ${alpha('#f59e0b', 0.3)}`,
          backdropFilter: 'blur(8px)',
          fontFamily: '"Inter", sans-serif',
          fontSize: '0.82rem',
          '& .MuiAlert-message': { fontFamily: '"Inter", sans-serif' },
        }}
      >
        These test scenarios are designed for controlled lab environments only. Execute with caution and ensure proper authorization before running any commands.
      </Alert>
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        {tests.map((test, index) => {
          const privColor = test.privilege_required === 'SYSTEM' ? theme.palette.error.main
            : test.privilege_required === 'admin' ? '#f59e0b' : '#10b981';
          return (
            <Accordion key={index} sx={premiumAccordion}>
              <AccordionSummary expandIcon={<ExpandMoreIcon sx={{ color: alpha(PRIMARY, 0.6) }} />}>
                <Box sx={{ width: '100%', display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap', overflow: 'hidden', minWidth: 0 }}>
                  <ScienceIcon sx={{ fontSize: 18, color: alpha(PRIMARY, 0.7), flexShrink: 0 }} />
                  <Typography
                    variant="subtitle1"
                    sx={{
                      flex: '1 1 0', minWidth: 0, fontWeight: 700, fontFamily: '"Inter", sans-serif',
                      letterSpacing: '-0.01em', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
                    }}
                  >
                    {test.test_name}
                  </Typography>
                  <Chip label={test.mitre_technique || 'N/A'} size="small" component="a"
                    href={test.real_world_reference?.mitre_url || `https://attack.mitre.org/techniques/${(test.mitre_technique || '').replace('.', '/')}/`}
                    target="_blank" rel="noopener noreferrer" clickable
                    sx={{
                      fontFamily: CODE_FONT, fontWeight: 700, fontSize: '0.72rem', borderRadius: '6px',
                      backgroundColor: alpha('#8b5cf6', 0.1), color: '#8b5cf6',
                      border: `1px solid ${alpha('#8b5cf6', 0.25)}`,
                      textDecoration: 'none',
                    }}
                  />
                  <Chip label={test.privilege_required || 'user'} size="small" sx={{
                    fontFamily: '"Inter", sans-serif', fontWeight: 700, fontSize: '0.68rem', borderRadius: '6px',
                    textTransform: 'uppercase', letterSpacing: '0.05em',
                    backgroundColor: alpha(privColor, 0.1), color: privColor,
                    border: `1px solid ${alpha(privColor, 0.25)}`,
                  }} />
                  {test.platforms?.map((p: string, pi: number) => (
                    <Chip key={pi} label={p} size="small" sx={{
                      fontFamily: '"Inter", sans-serif', fontWeight: 600, fontSize: '0.68rem', borderRadius: '6px',
                      backgroundColor: alpha('#3b82f6', 0.08), color: '#3b82f6',
                      border: `1px solid ${alpha('#3b82f6', 0.2)}`,
                    }} />
                  ))}
                </Box>
              </AccordionSummary>
              <AccordionDetails sx={{ pt: 0 }}>
                {/* Description */}
                <Typography variant="body2" sx={{
                  color: theme.palette.text.secondary, fontFamily: '"Inter", sans-serif',
                  mb: 2.5, lineHeight: 1.8,
                }}>
                  {test.description}
                </Typography>

                {/* Sigma Rule Reference */}
                {test.sigma_rule_title && (
                  <Box sx={{
                    mb: 2.5, p: 1.5, borderRadius: '10px',
                    background: alpha(PRIMARY, 0.04), border: `1px solid ${alpha(PRIMARY, 0.12)}`,
                  }}>
                    <Typography variant="caption" sx={{
                      fontWeight: 700, color: alpha(theme.palette.text.primary, 0.5),
                      fontFamily: '"Inter", sans-serif', fontSize: '0.68rem',
                      letterSpacing: '0.08em', textTransform: 'uppercase',
                    }}>
                      Validates Sigma Rule
                    </Typography>
                    <Typography variant="body2" sx={{
                      fontWeight: 600, fontFamily: '"Inter", sans-serif', color: PRIMARY, mt: 0.3,
                    }}>
                      {test.sigma_rule_title}
                    </Typography>
                  </Box>
                )}

                {/* Prerequisites */}
                {test.prerequisites && test.prerequisites.length > 0 && (
                  <Box sx={{ mb: 2.5 }}>
                    <Typography variant="caption" sx={{
                      fontWeight: 700, display: 'block', mb: 0.8,
                      color: alpha(theme.palette.text.primary, 0.5), fontFamily: '"Inter", sans-serif',
                      fontSize: '0.68rem', letterSpacing: '0.08em', textTransform: 'uppercase',
                    }}>
                      Prerequisites
                    </Typography>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                      {test.prerequisites.map((prereq: string, pi: number) => (
                        <Typography key={pi} variant="body2" sx={{
                          fontFamily: '"Inter", sans-serif', fontSize: '0.82rem', color: theme.palette.text.secondary,
                          pl: 1.5, borderLeft: `2px solid ${alpha('#f59e0b', 0.3)}`, lineHeight: 1.6,
                        }}>
                          {prereq}
                        </Typography>
                      ))}
                    </Box>
                  </Box>
                )}

                {/* Execution Steps */}
                {test.executor && (
                  <Box sx={{ mb: 2.5 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <TerminalIcon sx={{ fontSize: 16, color: '#10b981' }} />
                      <Typography variant="caption" sx={{
                        fontWeight: 700, color: alpha(theme.palette.text.primary, 0.5),
                        fontFamily: '"Inter", sans-serif', fontSize: '0.68rem',
                        letterSpacing: '0.08em', textTransform: 'uppercase',
                      }}>
                        Execution Steps ({test.executor.type})
                      </Typography>
                      {test.executor.elevation_required && (
                        <Chip label="Elevation Required" size="small" sx={{
                          fontFamily: '"Inter", sans-serif', fontSize: '0.65rem', fontWeight: 700,
                          height: 20, borderRadius: '4px',
                          backgroundColor: alpha(theme.palette.error.main, 0.1),
                          color: theme.palette.error.main,
                          border: `1px solid ${alpha(theme.palette.error.main, 0.25)}`,
                        }} />
                      )}
                    </Box>
                    {test.executor.steps && test.executor.steps.map((step: string, si: number) => (
                      <Typography key={si} variant="body2" sx={{
                        fontFamily: '"Inter", sans-serif', fontSize: '0.82rem',
                        color: theme.palette.text.secondary, lineHeight: 1.8,
                        pl: 2, mb: 0.5,
                        borderLeft: `2px solid ${alpha('#10b981', 0.2)}`,
                      }}>
                        {step}
                      </Typography>
                    ))}

                    {/* Command Block */}
                    {test.executor.command && (
                      <Box sx={{ mt: 1.5, position: 'relative' }}>
                        <Tooltip title="Copy command" arrow>
                          <IconButton
                            size="small"
                            onClick={() => {
                              navigator.clipboard.writeText(test.executor.command);
                            }}
                            sx={{
                              position: 'absolute', top: 8, right: 8, zIndex: 2,
                              color: alpha('#e6edf3', 0.5), backgroundColor: alpha('#000', 0.3),
                              '&:hover': { color: '#e6edf3', backgroundColor: alpha(PRIMARY, 0.3) },
                            }}
                          >
                            <ContentCopyIcon sx={{ fontSize: 14 }} />
                          </IconButton>
                        </Tooltip>
                        <Box component="pre" sx={{
                          ...codeBlock,
                          borderColor: alpha('#10b981', 0.25),
                          '&::before': {
                            content: `"${test.executor.type?.toUpperCase() || 'COMMAND'}"`,
                            position: 'absolute', top: 8, left: 12,
                            fontSize: '0.62rem', fontWeight: 700, letterSpacing: '0.08em',
                            color: alpha('#10b981', 0.6), fontFamily: CODE_FONT,
                          },
                          pt: 4, position: 'relative',
                        }}>
                          {test.executor.command}
                        </Box>
                      </Box>
                    )}
                  </Box>
                )}

                {/* Expected Detection */}
                {test.expected_detection && (
                  <Box sx={{
                    mb: 2.5, p: 2, borderRadius: '10px',
                    background: alpha('#10b981', 0.04),
                    border: `1px solid ${alpha('#10b981', 0.15)}`,
                  }}>
                    <Typography variant="caption" sx={{
                      fontWeight: 700, display: 'block', mb: 1,
                      color: '#10b981', fontFamily: '"Inter", sans-serif',
                      fontSize: '0.68rem', letterSpacing: '0.08em', textTransform: 'uppercase',
                    }}>
                      Expected Detection
                    </Typography>
                    <Box sx={{ display: 'grid', gridTemplateColumns: 'auto 1fr', gap: '4px 12px' }}>
                      <Typography variant="caption" sx={{ fontWeight: 600, color: alpha(theme.palette.text.primary, 0.5), fontFamily: '"Inter", sans-serif' }}>
                        Log Source
                      </Typography>
                      <Typography variant="caption" sx={{ fontFamily: CODE_FONT, color: theme.palette.text.secondary }}>
                        {test.expected_detection.log_source}
                      </Typography>
                      <Typography variant="caption" sx={{ fontWeight: 600, color: alpha(theme.palette.text.primary, 0.5), fontFamily: '"Inter", sans-serif' }}>
                        Event IDs
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                        {test.expected_detection.event_ids?.map((eid: string, ei: number) => (
                          <Chip key={ei} label={eid} size="small" sx={{
                            fontFamily: CODE_FONT, fontSize: '0.68rem', fontWeight: 700,
                            height: 20, borderRadius: '4px',
                            backgroundColor: alpha('#10b981', 0.1), color: '#10b981',
                            border: `1px solid ${alpha('#10b981', 0.25)}`,
                          }} />
                        ))}
                      </Box>
                    </Box>
                    {test.expected_detection.key_fields && Object.keys(test.expected_detection.key_fields).length > 0 && (
                      <Box sx={{ mt: 1.5 }}>
                        <Typography variant="caption" sx={{ fontWeight: 600, display: 'block', mb: 0.5, color: alpha(theme.palette.text.primary, 0.5) }}>
                          Key Fields
                        </Typography>
                        {Object.entries(test.expected_detection.key_fields).map(([field, value]) => (
                          <Typography key={field} variant="caption" sx={{
                            display: 'block', fontFamily: CODE_FONT, fontSize: '0.72rem',
                            color: theme.palette.text.secondary, lineHeight: 1.8,
                          }}>
                            <Box component="span" sx={{ color: '#8b5cf6', fontWeight: 600 }}>{field}</Box>
                            {' = '}
                            <Box component="span" sx={{ color: '#f59e0b' }}>{String(value)}</Box>
                          </Typography>
                        ))}
                      </Box>
                    )}
                    {test.expected_detection.sigma_condition_match && (
                      <Typography variant="caption" sx={{
                        display: 'block', mt: 1, fontStyle: 'italic',
                        color: alpha('#10b981', 0.8), fontFamily: '"Inter", sans-serif', lineHeight: 1.6,
                      }}>
                        {test.expected_detection.sigma_condition_match}
                      </Typography>
                    )}
                  </Box>
                )}

                {/* Cleanup */}
                {test.cleanup && test.cleanup.command && (
                  <Box sx={{ mb: 2.5 }}>
                    <Typography variant="caption" sx={{
                      fontWeight: 700, display: 'block', mb: 0.8,
                      color: alpha(theme.palette.text.primary, 0.5), fontFamily: '"Inter", sans-serif',
                      fontSize: '0.68rem', letterSpacing: '0.08em', textTransform: 'uppercase',
                    }}>
                      Cleanup Command
                    </Typography>
                    <Typography variant="body2" sx={{
                      fontFamily: '"Inter", sans-serif', fontSize: '0.82rem',
                      color: theme.palette.text.secondary, mb: 1, lineHeight: 1.6,
                    }}>
                      {test.cleanup.description}
                    </Typography>
                    <Box component="pre" sx={{
                      ...codeBlock, py: 1.5, px: 2,
                      borderColor: alpha('#f59e0b', 0.2),
                      fontSize: '0.78rem',
                    }}>
                      {test.cleanup.command}
                    </Box>
                  </Box>
                )}

                {/* Real-World Reference */}
                {test.real_world_reference && (
                  <Box sx={{
                    p: 2, borderRadius: '10px',
                    background: alpha('#8b5cf6', 0.03),
                    border: `1px solid ${alpha('#8b5cf6', 0.12)}`,
                  }}>
                    <Typography variant="caption" sx={{
                      fontWeight: 700, display: 'block', mb: 1,
                      color: '#8b5cf6', fontFamily: '"Inter", sans-serif',
                      fontSize: '0.68rem', letterSpacing: '0.08em', textTransform: 'uppercase',
                    }}>
                      Real-World Reference
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.6, mb: 1 }}>
                      {test.real_world_reference.threat_actors?.map((actor: string, ai: number) => (
                        <Chip key={`actor-${ai}`} label={actor} size="small" sx={{
                          fontFamily: '"Inter", sans-serif', fontSize: '0.68rem', fontWeight: 600,
                          borderRadius: '6px', backgroundColor: alpha(theme.palette.error.main, 0.08),
                          color: theme.palette.error.main, border: `1px solid ${alpha(theme.palette.error.main, 0.2)}`,
                        }} />
                      ))}
                      {test.real_world_reference.malware_families?.map((mw: string, mi: number) => (
                        <Chip key={`mw-${mi}`} label={mw} size="small" sx={{
                          fontFamily: '"Inter", sans-serif', fontSize: '0.68rem', fontWeight: 600,
                          borderRadius: '6px', backgroundColor: alpha(SECONDARY, 0.08),
                          color: SECONDARY, border: `1px solid ${alpha(SECONDARY, 0.2)}`,
                        }} />
                      ))}
                    </Box>
                    <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                      {test.real_world_reference.mitre_url && (
                        <Typography component="a" href={test.real_world_reference.mitre_url}
                          target="_blank" rel="noopener noreferrer" variant="caption" sx={{
                            color: '#8b5cf6', fontFamily: CODE_FONT, fontSize: '0.72rem',
                            textDecoration: 'none', display: 'flex', alignItems: 'center', gap: 0.5,
                            '&:hover': { textDecoration: 'underline' },
                          }}>
                          <OpenInNewIcon sx={{ fontSize: 12 }} /> MITRE ATT&CK
                        </Typography>
                      )}
                      {test.real_world_reference.atomic_red_team_id && (
                        <Typography component="a"
                          href={`https://github.com/redcanaryco/atomic-red-team/blob/master/atomics/${test.mitre_technique}/${test.mitre_technique}.md`}
                          target="_blank" rel="noopener noreferrer" variant="caption" sx={{
                            color: '#10b981', fontFamily: CODE_FONT, fontSize: '0.72rem',
                            textDecoration: 'none', display: 'flex', alignItems: 'center', gap: 0.5,
                            '&:hover': { textDecoration: 'underline' },
                          }}>
                          <OpenInNewIcon sx={{ fontSize: 12 }} /> ART: {test.real_world_reference.atomic_red_team_id}
                        </Typography>
                      )}
                    </Box>
                  </Box>
                )}

                {/* Safety Notes */}
                {test.safety_notes && (
                  <Box sx={{
                    mt: 2, p: 1.5, borderRadius: '8px',
                    background: alpha('#f59e0b', 0.04),
                    border: `1px solid ${alpha('#f59e0b', 0.15)}`,
                    display: 'flex', alignItems: 'flex-start', gap: 1,
                  }}>
                    <WarningAmberIcon sx={{ fontSize: 16, color: '#f59e0b', mt: 0.2, flexShrink: 0 }} />
                    <Typography variant="caption" sx={{
                      fontFamily: '"Inter", sans-serif', color: alpha(theme.palette.text.secondary, 0.8),
                      lineHeight: 1.6, fontStyle: 'italic',
                    }}>
                      {test.safety_notes}
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

export default AtomicTestsAccordion;
