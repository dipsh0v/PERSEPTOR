import React, { useEffect, useState } from 'react';
import {
  Typography,
  Box,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip,
  IconButton,
  Tooltip,
  useTheme,
  Divider,
  CircularProgress,
  Alert,
  LinearProgress,
} from '@mui/material';
import { alpha } from '@mui/material/styles';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import SecurityIcon from '@mui/icons-material/Security';
import DeleteIcon from '@mui/icons-material/Delete';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import AssessmentIcon from '@mui/icons-material/Assessment';
import BugReportIcon from '@mui/icons-material/BugReport';
import ShieldIcon from '@mui/icons-material/Shield';
import LinkIcon from '@mui/icons-material/Link';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import CodeIcon from '@mui/icons-material/Code';
import StorageIcon from '@mui/icons-material/Storage';
import FingerprintIcon from '@mui/icons-material/Fingerprint';
import PublicIcon from '@mui/icons-material/Public';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import ScienceIcon from '@mui/icons-material/Science';
import TerminalIcon from '@mui/icons-material/Terminal';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import { useAppDispatch, useAppSelector } from '../store';
import { fetchReports, deleteReport, clearReportsError } from '../store/slices/reportsSlice';

/* ───────── keyframes ───────── */
const shimmerKf = `
@keyframes reportsShimmer {
  0% { background-position: -200% center; }
  100% { background-position: 200% center; }
}
@keyframes reportsFadeSlideUp {
  from { opacity: 0; transform: translateY(20px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes reportsPulseGlow {
  0%, 100% { box-shadow: 0 0 8px rgba(99,102,241,.25); }
  50%      { box-shadow: 0 0 20px rgba(99,102,241,.45); }
}
`;

const Reports: React.FC = () => {
  const dispatch = useAppDispatch();
  const { reports, loading, error } = useAppSelector((state) => state.reports);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';

  useEffect(() => {
    dispatch(fetchReports());
  }, [dispatch]);

  const handleDelete = async (id: string) => {
    if (!window.confirm('Are you sure you want to delete this report?')) return;
    dispatch(deleteReport(id));
  };

  const handleCopy = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const formatDate = (dateString: string) =>
    new Date(dateString).toLocaleString('en-US', {
      year: 'numeric', month: 'short', day: 'numeric',
      hour: '2-digit', minute: '2-digit',
    });

  /* ---- section icon helper ---- */
  const sectionIcon = (label: string) => {
    const map: Record<string, React.ReactNode> = {
      threat: <ShieldIcon sx={{ fontSize: 20 }} />,
      ioc: <FingerprintIcon sx={{ fontSize: 20 }} />,
      actors: <BugReportIcon sx={{ fontSize: 20 }} />,
      ttps: <WarningAmberIcon sx={{ fontSize: 20 }} />,
      tools: <CodeIcon sx={{ fontSize: 20 }} />,
      sigma: <SecurityIcon sx={{ fontSize: 20 }} />,
      atomic: <ScienceIcon sx={{ fontSize: 20 }} />,
      yara: <SecurityIcon sx={{ fontSize: 20 }} />,
      siem: <StorageIcon sx={{ fontSize: 20 }} />,
      global: <PublicIcon sx={{ fontSize: 20 }} />,
    };
    return map[label] || <SecurityIcon sx={{ fontSize: 20 }} />;
  };

  /* ---- reusable section header ---- */
  const SectionHeader = ({ icon, label }: { icon: string; label: string }) => (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
      <Box sx={{
        width: 32, height: 32, borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center',
        background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
        color: '#fff',
      }}>
        {sectionIcon(icon)}
      </Box>
      <Typography variant="subtitle1" sx={{ fontWeight: 700, letterSpacing: '-0.01em' }}>
        {label}
      </Typography>
    </Box>
  );

  /* ---- code block style ---- */
  const codeBlockSx = {
    whiteSpace: 'pre-wrap' as const,
    fontFamily: '"JetBrains Mono", monospace',
    fontSize: '0.8rem',
    lineHeight: 1.7,
    p: 2.5,
    borderRadius: '12px',
    border: `1px solid ${alpha(theme.palette.divider, 0.15)}`,
    backgroundColor: isDark ? alpha('#000', 0.4) : alpha('#0f172a', 0.04),
    color: isDark ? '#e2e8f0' : '#334155',
    overflow: 'auto',
  };

  /* ---- inner accordion style ---- */
  const innerAccordionSx = {
    background: alpha(theme.palette.primary.main, 0.03),
    boxShadow: 'none',
    '&:before': { display: 'none' },
    border: `1px solid ${alpha(theme.palette.divider, 0.12)}`,
    borderRadius: '12px !important',
    overflow: 'hidden',
    transition: 'border-color 0.3s ease',
    '&:hover': { borderColor: alpha(theme.palette.primary.main, 0.3) },
  };

  return (
    <>
      <style>{shimmerKf}</style>

      <Box sx={{ p: { xs: 2, md: 4 }, maxWidth: 960, mx: 'auto', width: '100%', overflow: 'hidden' }}>
        {/* ── Page Header ── */}
        <Box sx={{
          display: 'flex', alignItems: 'center', gap: 2.5, mb: 1,
          animation: 'reportsFadeSlideUp 0.6s ease-out',
        }}>
          <Box sx={{
            width: 56, height: 56, borderRadius: '16px', display: 'flex', alignItems: 'center', justifyContent: 'center',
            background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
            boxShadow: `0 8px 32px ${alpha(theme.palette.primary.main, 0.35)}`,
          }}>
            <AssessmentIcon sx={{ fontSize: 30, color: '#fff' }} />
          </Box>
          <Box>
            <Typography variant="h4" sx={{
              fontWeight: 800, letterSpacing: '-0.03em',
              background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.secondary.main} 100%)`,
              backgroundClip: 'text', WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}>
              Analyzed Reports
            </Typography>
            <Typography variant="body2" sx={{ color: 'text.secondary', mt: 0.5 }}>
              View and manage your threat analysis history
            </Typography>
          </Box>
        </Box>

        {/* ── Stats bar ── */}
        <Box sx={{
          display: 'flex', gap: 3, mb: 4, mt: 3, flexWrap: 'wrap',
          animation: 'reportsFadeSlideUp 0.6s ease-out 0.1s both',
        }}>
          {[
            { label: 'Total Reports', value: reports.length, color: theme.palette.primary.main },
            { label: 'Latest', value: reports.length > 0 ? formatDate(reports[0]?.timestamp) : '—', color: theme.palette.secondary.main },
          ].map((s) => (
            <Box key={s.label} sx={{
              px: 2.5, py: 1.5, borderRadius: '12px',
              border: `1px solid ${alpha(theme.palette.divider, 0.12)}`,
              backdropFilter: 'blur(12px)',
              backgroundColor: alpha(theme.palette.background.paper, isDark ? 0.4 : 0.7),
            }}>
              <Typography variant="caption" sx={{ color: 'text.secondary', textTransform: 'uppercase', letterSpacing: '0.08em', fontSize: '0.65rem' }}>
                {s.label}
              </Typography>
              <Typography variant="body1" sx={{ fontWeight: 700, color: s.color, fontFamily: '"JetBrains Mono", monospace', mt: 0.3 }}>
                {s.value}
              </Typography>
            </Box>
          ))}
        </Box>

        {/* ── Error alert ── */}
        {error && (
          <Alert severity="error" sx={{ mb: 3, borderRadius: '12px' }} onClose={() => dispatch(clearReportsError())}>
            {error}
          </Alert>
        )}

        {/* ── Loading ── */}
        {loading ? (
          <Box sx={{
            display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
            py: 12, gap: 3,
          }}>
            <Box sx={{ position: 'relative', display: 'inline-flex' }}>
              <CircularProgress size={64} thickness={2} sx={{ color: theme.palette.primary.main }} />
              <Box sx={{
                position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                <AssessmentIcon sx={{ fontSize: 24, color: theme.palette.primary.main, animation: 'reportsPulseGlow 2s ease-in-out infinite' }} />
              </Box>
            </Box>
            <Typography variant="body2" sx={{ color: 'text.secondary' }}>Loading reports...</Typography>
          </Box>
        ) : reports.length === 0 ? (
          /* ── Empty state ── */
          <Box sx={{
            textAlign: 'center', py: 10,
            borderRadius: '20px',
            border: `1px dashed ${alpha(theme.palette.divider, 0.3)}`,
            backdropFilter: 'blur(12px)',
            backgroundColor: alpha(theme.palette.background.paper, isDark ? 0.2 : 0.5),
          }}>
            <AssessmentIcon sx={{ fontSize: 72, color: alpha(theme.palette.primary.main, 0.25), mb: 2 }} />
            <Typography variant="h6" sx={{ fontWeight: 700, mb: 1 }}>No Reports Found</Typography>
            <Typography variant="body2" color="text.secondary">
              Start analyzing URLs from the Dashboard to see your reports here
            </Typography>
          </Box>
        ) : (
          /* ── Report list ── */
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2.5 }}>
            {reports.map((report, idx) => (
              <Box
                key={report.id}
                sx={{ animation: `reportsFadeSlideUp 0.5s ease-out ${idx * 0.06}s both` }}
              >
                <Accordion
                  sx={{
                    background: alpha(theme.palette.background.paper, isDark ? 0.45 : 0.8),
                    backdropFilter: 'blur(16px)',
                    boxShadow: 'none',
                    '&:before': { display: 'none' },
                    border: `1px solid ${alpha(theme.palette.divider, 0.12)}`,
                    borderRadius: '16px !important',
                    overflow: 'hidden',
                    transition: 'all 0.35s cubic-bezier(0.4, 0, 0.2, 1)',
                    '&:hover': {
                      transform: 'translateY(-2px)',
                      borderColor: alpha(theme.palette.primary.main, 0.3),
                      boxShadow: `0 8px 32px ${alpha(theme.palette.primary.main, 0.1)}`,
                    },
                  }}
                >
                  <AccordionSummary
                    expandIcon={<ExpandMoreIcon sx={{ color: theme.palette.primary.main }} />}
                    sx={{ px: 3, py: 1 }}
                  >
                    <Box sx={{ width: '100%', display: 'flex', alignItems: 'center', gap: 2 }}>
                      {/* link icon */}
                      <Box sx={{
                        width: 40, height: 40, borderRadius: '12px', flexShrink: 0,
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        background: alpha(theme.palette.primary.main, 0.1),
                        color: theme.palette.primary.main,
                      }}>
                        <LinkIcon sx={{ fontSize: 20 }} />
                      </Box>

                      <Box sx={{ flex: 1, minWidth: 0 }}>
                        <Typography variant="subtitle1" sx={{
                          fontWeight: 700, color: theme.palette.primary.main,
                          whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
                          fontFamily: '"JetBrains Mono", monospace', fontSize: '0.85rem',
                        }}>
                          {report.url}
                        </Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                          <AccessTimeIcon sx={{ fontSize: 14, color: 'text.secondary' }} />
                          <Typography variant="caption" color="text.secondary">
                            {formatDate(report.timestamp)}
                          </Typography>
                        </Box>
                      </Box>

                      <Box sx={{ display: 'flex', gap: 0.5, flexShrink: 0 }}>
                        <Tooltip title={copiedId === report.id ? 'Copied!' : 'Copy URL'}>
                          <IconButton
                            size="small"
                            onClick={(e) => { e.stopPropagation(); handleCopy(report.url, report.id); }}
                            sx={{
                              color: copiedId === report.id ? theme.palette.success.main : 'text.secondary',
                              transition: 'all 0.2s',
                              '&:hover': { backgroundColor: alpha(theme.palette.primary.main, 0.1) },
                            }}
                          >
                            <ContentCopyIcon sx={{ fontSize: 18 }} />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Delete Report">
                          <IconButton
                            size="small"
                            onClick={(e) => { e.stopPropagation(); handleDelete(report.id); }}
                            sx={{
                              color: 'text.secondary',
                              transition: 'all 0.2s',
                              '&:hover': { backgroundColor: alpha(theme.palette.error.main, 0.1), color: theme.palette.error.main },
                            }}
                          >
                            <DeleteIcon sx={{ fontSize: 18 }} />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </Box>
                  </AccordionSummary>

                  <AccordionDetails sx={{ px: 3, pb: 3 }}>
                    <Divider sx={{ mb: 3, borderColor: alpha(theme.palette.divider, 0.1) }} />

                    {/* ── Threat Summary ── */}
                    <SectionHeader icon="threat" label="Threat Summary" />
                    <Typography variant="body2" sx={{
                      whiteSpace: 'pre-wrap', lineHeight: 1.9,
                      color: 'text.secondary', mb: 4, pl: 1,
                    }}>
                      {report.threat_summary}
                    </Typography>

                    {/* ── Indicators of Compromise ── */}
                    {report.analysis_data?.indicators_of_compromise && (
                      <Box sx={{ mb: 4 }}>
                        <SectionHeader icon="ioc" label="Indicators of Compromise" />
                        {Object.entries(report.analysis_data.indicators_of_compromise).map(([key, value]) =>
                          Array.isArray(value) && value.length > 0 && (
                            <Box key={key} sx={{ mb: 2, pl: 1 }}>
                              <Typography variant="caption" sx={{
                                color: 'text.secondary', textTransform: 'uppercase',
                                letterSpacing: '0.08em', fontSize: '0.65rem', fontWeight: 600,
                              }}>
                                {key.replace(/_/g, ' ')}
                              </Typography>
                              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.8, mt: 0.8 }}>
                                {value.map((item, i) => (
                                  <Tooltip key={i} title={item} arrow>
                                    <Chip label={item} size="small" sx={{
                                      fontFamily: '"JetBrains Mono", monospace', fontSize: '0.7rem',
                                      borderRadius: '8px', height: 26, maxWidth: '340px',
                                      backgroundColor: alpha(theme.palette.primary.main, 0.08),
                                      border: `1px solid ${alpha(theme.palette.primary.main, 0.15)}`,
                                      '& .MuiChip-label': {
                                        overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
                                      },
                                      '&:hover': { backgroundColor: alpha(theme.palette.primary.main, 0.15) },
                                    }} />
                                  </Tooltip>
                                ))}
                              </Box>
                            </Box>
                          )
                        )}
                      </Box>
                    )}

                    {/* ── Threat Actors ── */}
                    {report.analysis_data?.threat_actors && report.analysis_data.threat_actors.length > 0 && (
                      <Box sx={{ mb: 4 }}>
                        <SectionHeader icon="actors" label="Threat Actors" />
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, pl: 1 }}>
                          {report.analysis_data.threat_actors.map((actor, i) => (
                            <Chip key={i} label={actor} sx={{
                              fontWeight: 600, borderRadius: '10px',
                              backgroundColor: alpha(theme.palette.error.main, 0.1),
                              color: theme.palette.error.main,
                              border: `1px solid ${alpha(theme.palette.error.main, 0.25)}`,
                            }} />
                          ))}
                        </Box>
                      </Box>
                    )}

                    {/* ── MITRE ATT&CK TTPs ── */}
                    {report.analysis_data?.ttps && report.analysis_data.ttps.length > 0 && (
                      <Box sx={{ mb: 4 }}>
                        <SectionHeader icon="ttps" label="MITRE ATT&CK TTPs" />
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, pl: 1 }}>
                          {report.analysis_data.ttps.map((ttp, i) => (
                            <Chip key={i}
                              label={typeof ttp === 'string' ? ttp : ttp.technique_name}
                              sx={{
                                borderRadius: '10px', fontWeight: 600,
                                backgroundColor: alpha(theme.palette.warning.main, 0.1),
                                color: theme.palette.warning.main,
                                border: `1px solid ${alpha(theme.palette.warning.main, 0.25)}`,
                              }}
                            />
                          ))}
                        </Box>
                      </Box>
                    )}

                    {/* ── Tools & Malware ── */}
                    {report.analysis_data?.tools_or_malware && report.analysis_data.tools_or_malware.length > 0 && (
                      <Box sx={{ mb: 4 }}>
                        <SectionHeader icon="tools" label="Tools & Malware" />
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, pl: 1 }}>
                          {report.analysis_data.tools_or_malware.map((item, i) => {
                            const isMalware = ['malware', 'trojan', 'ransomware', 'worm', 'virus'].some(k => item.toLowerCase().includes(k));
                            const clr = isMalware ? theme.palette.error.main : theme.palette.info.main;
                            return (
                              <Chip key={i} label={item} sx={{
                                borderRadius: '10px', fontWeight: 600,
                                backgroundColor: alpha(clr, 0.1), color: clr,
                                border: `1px solid ${alpha(clr, 0.25)}`,
                              }} />
                            );
                          })}
                        </Box>
                      </Box>
                    )}

                    {/* ── Generated Sigma Rules ── */}
                    {report.generated_sigma_rules && (
                      <Box sx={{ mb: 4 }}>
                        <SectionHeader icon="sigma" label="Generated Sigma Rules" />
                        <Accordion sx={innerAccordionSx}>
                          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                            <Typography variant="body2" sx={{ fontWeight: 600 }}>View Generated Sigma Rules</Typography>
                          </AccordionSummary>
                          <AccordionDetails>
                            <Box component="pre" sx={codeBlockSx}>
                              {report.generated_sigma_rules}
                            </Box>
                          </AccordionDetails>
                        </Accordion>
                      </Box>
                    )}

                    {/* ── Atomic Red Team Test Scenarios ── */}
                    {report.atomic_tests && report.atomic_tests.length > 0 && (
                      <Box sx={{ mb: 4 }}>
                        <SectionHeader icon="atomic" label="Atomic Red Team Test Scenarios" />
                        <Alert
                          severity="warning"
                          icon={<WarningAmberIcon />}
                          sx={{
                            mb: 2, borderRadius: '12px',
                            border: `1px solid ${alpha('#f59e0b', 0.25)}`,
                            fontSize: '0.8rem',
                          }}
                        >
                          Lab environment only. Ensure proper authorization before executing any commands.
                        </Alert>
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                          {report.atomic_tests.map((test, i) => {
                            const privColor = test.privilege_required === 'SYSTEM' ? theme.palette.error.main
                              : test.privilege_required === 'admin' ? '#f59e0b' : '#10b981';
                            return (
                              <Accordion key={i} sx={innerAccordionSx}>
                                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                                  <Box sx={{ width: '100%', display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap', overflow: 'hidden', minWidth: 0 }}>
                                    <ScienceIcon sx={{ fontSize: 16, color: '#f97316', flexShrink: 0 }} />
                                    <Typography variant="body2" sx={{
                                      flex: '1 1 0', minWidth: 0, fontWeight: 700,
                                      overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
                                    }}>
                                      {test.test_name}
                                    </Typography>
                                    <Chip
                                      label={test.mitre_technique} size="small"
                                      component="a"
                                      href={test.real_world_reference?.mitre_url || `https://attack.mitre.org/techniques/${test.mitre_technique.replace('.', '/')}/`}
                                      target="_blank" rel="noopener noreferrer" clickable
                                      onClick={(e: React.MouseEvent) => e.stopPropagation()}
                                      sx={{
                                        fontFamily: '"JetBrains Mono", monospace', fontWeight: 700, fontSize: '0.65rem',
                                        borderRadius: '6px', height: 22,
                                        backgroundColor: alpha('#8b5cf6', 0.1), color: '#8b5cf6',
                                        border: `1px solid ${alpha('#8b5cf6', 0.25)}`, textDecoration: 'none',
                                      }}
                                    />
                                    <Chip label={test.privilege_required} size="small" sx={{
                                      fontWeight: 700, fontSize: '0.6rem', borderRadius: '6px', height: 22,
                                      textTransform: 'uppercase', letterSpacing: '0.05em',
                                      backgroundColor: alpha(privColor, 0.1), color: privColor,
                                      border: `1px solid ${alpha(privColor, 0.25)}`,
                                    }} />
                                    {test.platforms?.map((p, pi) => (
                                      <Chip key={pi} label={p} size="small" sx={{
                                        fontWeight: 600, fontSize: '0.6rem', borderRadius: '6px', height: 22,
                                        backgroundColor: alpha('#3b82f6', 0.08), color: '#3b82f6',
                                        border: `1px solid ${alpha('#3b82f6', 0.2)}`,
                                      }} />
                                    ))}
                                  </Box>
                                </AccordionSummary>
                                <AccordionDetails>
                                  {/* Description */}
                                  <Typography variant="body2" sx={{ color: 'text.secondary', mb: 2, lineHeight: 1.8 }}>
                                    {test.description}
                                  </Typography>

                                  {/* Sigma Rule Reference */}
                                  {test.sigma_rule_title && (
                                    <Box sx={{
                                      mb: 2, p: 1.5, borderRadius: '10px',
                                      background: alpha(theme.palette.primary.main, 0.04),
                                      border: `1px solid ${alpha(theme.palette.primary.main, 0.12)}`,
                                    }}>
                                      <Typography variant="caption" sx={{
                                        fontWeight: 700, color: alpha(theme.palette.text.primary, 0.5),
                                        fontSize: '0.65rem', letterSpacing: '0.08em', textTransform: 'uppercase',
                                      }}>
                                        Validates Sigma Rule
                                      </Typography>
                                      <Typography variant="body2" sx={{
                                        fontWeight: 600, color: theme.palette.primary.main, mt: 0.3,
                                      }}>
                                        {test.sigma_rule_title}
                                      </Typography>
                                    </Box>
                                  )}

                                  {/* Prerequisites */}
                                  {test.prerequisites && test.prerequisites.length > 0 && (
                                    <Box sx={{ mb: 2 }}>
                                      <Typography variant="caption" sx={{
                                        fontWeight: 700, display: 'block', mb: 0.5,
                                        color: alpha(theme.palette.text.primary, 0.5),
                                        fontSize: '0.65rem', letterSpacing: '0.08em', textTransform: 'uppercase',
                                      }}>
                                        Prerequisites
                                      </Typography>
                                      {test.prerequisites.map((prereq, pi) => (
                                        <Typography key={pi} variant="body2" sx={{
                                          fontSize: '0.8rem', color: 'text.secondary',
                                          pl: 1.5, borderLeft: `2px solid ${alpha('#f59e0b', 0.3)}`, mb: 0.3, lineHeight: 1.6,
                                        }}>
                                          {prereq}
                                        </Typography>
                                      ))}
                                    </Box>
                                  )}

                                  {/* Execution Steps + Command */}
                                  {test.executor && (
                                    <Box sx={{ mb: 2 }}>
                                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                                        <TerminalIcon sx={{ fontSize: 16, color: '#10b981' }} />
                                        <Typography variant="caption" sx={{
                                          fontWeight: 700, color: alpha(theme.palette.text.primary, 0.5),
                                          fontSize: '0.65rem', letterSpacing: '0.08em', textTransform: 'uppercase',
                                        }}>
                                          Execution Steps ({test.executor.type})
                                        </Typography>
                                        {test.executor.elevation_required && (
                                          <Chip label="Elevation Required" size="small" sx={{
                                            fontSize: '0.6rem', fontWeight: 700, height: 20, borderRadius: '4px',
                                            backgroundColor: alpha(theme.palette.error.main, 0.1),
                                            color: theme.palette.error.main,
                                            border: `1px solid ${alpha(theme.palette.error.main, 0.25)}`,
                                          }} />
                                        )}
                                      </Box>
                                      {test.executor.steps?.map((step, si) => (
                                        <Typography key={si} variant="body2" sx={{
                                          fontSize: '0.8rem', color: 'text.secondary', lineHeight: 1.8,
                                          pl: 2, mb: 0.3, borderLeft: `2px solid ${alpha('#10b981', 0.2)}`,
                                        }}>
                                          {step}
                                        </Typography>
                                      ))}
                                      {test.executor.command && (
                                        <Box sx={{ mt: 1.5, position: 'relative' }}>
                                          <Tooltip title="Copy command">
                                            <IconButton
                                              size="small"
                                              onClick={() => navigator.clipboard.writeText(test.executor.command)}
                                              sx={{
                                                position: 'absolute', top: 6, right: 6, zIndex: 2,
                                                color: alpha('#e6edf3', 0.5), backgroundColor: alpha('#000', 0.3),
                                                '&:hover': { color: '#e6edf3', backgroundColor: alpha(theme.palette.primary.main, 0.3) },
                                              }}
                                            >
                                              <ContentCopyIcon sx={{ fontSize: 14 }} />
                                            </IconButton>
                                          </Tooltip>
                                          <Box component="pre" sx={{
                                            ...codeBlockSx,
                                            borderColor: alpha('#10b981', 0.25),
                                            position: 'relative', pt: 4,
                                            '&::before': {
                                              content: `"${test.executor.type?.toUpperCase() || 'COMMAND'}"`,
                                              position: 'absolute', top: 8, left: 12,
                                              fontSize: '0.6rem', fontWeight: 700, letterSpacing: '0.08em',
                                              color: alpha('#10b981', 0.6), fontFamily: '"JetBrains Mono", monospace',
                                            },
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
                                      mb: 2, p: 2, borderRadius: '10px',
                                      background: alpha('#10b981', 0.04),
                                      border: `1px solid ${alpha('#10b981', 0.15)}`,
                                    }}>
                                      <Typography variant="caption" sx={{
                                        fontWeight: 700, display: 'block', mb: 1, color: '#10b981',
                                        fontSize: '0.65rem', letterSpacing: '0.08em', textTransform: 'uppercase',
                                      }}>
                                        Expected Detection
                                      </Typography>
                                      <Box sx={{ display: 'grid', gridTemplateColumns: 'auto 1fr', gap: '4px 12px' }}>
                                        <Typography variant="caption" sx={{ fontWeight: 600, color: alpha(theme.palette.text.primary, 0.5) }}>
                                          Log Source
                                        </Typography>
                                        <Typography variant="caption" sx={{ fontFamily: '"JetBrains Mono", monospace', color: 'text.secondary' }}>
                                          {test.expected_detection.log_source}
                                        </Typography>
                                        <Typography variant="caption" sx={{ fontWeight: 600, color: alpha(theme.palette.text.primary, 0.5) }}>
                                          Event IDs
                                        </Typography>
                                        <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                                          {test.expected_detection.event_ids?.map((eid, ei) => (
                                            <Chip key={ei} label={eid} size="small" sx={{
                                              fontFamily: '"JetBrains Mono", monospace', fontSize: '0.65rem', fontWeight: 700,
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
                                              display: 'block', fontFamily: '"JetBrains Mono", monospace', fontSize: '0.7rem',
                                              color: 'text.secondary', lineHeight: 1.8,
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
                                          color: alpha('#10b981', 0.8), lineHeight: 1.6,
                                        }}>
                                          {test.expected_detection.sigma_condition_match}
                                        </Typography>
                                      )}
                                    </Box>
                                  )}

                                  {/* Cleanup */}
                                  {test.cleanup?.command && (
                                    <Box sx={{ mb: 2 }}>
                                      <Typography variant="caption" sx={{
                                        fontWeight: 700, display: 'block', mb: 0.5,
                                        color: alpha(theme.palette.text.primary, 0.5),
                                        fontSize: '0.65rem', letterSpacing: '0.08em', textTransform: 'uppercase',
                                      }}>
                                        Cleanup Command
                                      </Typography>
                                      <Typography variant="body2" sx={{ fontSize: '0.8rem', color: 'text.secondary', mb: 1, lineHeight: 1.6 }}>
                                        {test.cleanup.description}
                                      </Typography>
                                      <Box component="pre" sx={{
                                        ...codeBlockSx, py: 1.5, px: 2,
                                        borderColor: alpha('#f59e0b', 0.2), fontSize: '0.78rem',
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
                                        fontWeight: 700, display: 'block', mb: 1, color: '#8b5cf6',
                                        fontSize: '0.65rem', letterSpacing: '0.08em', textTransform: 'uppercase',
                                      }}>
                                        Real-World Reference
                                      </Typography>
                                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.6, mb: 1 }}>
                                        {test.real_world_reference.threat_actors?.map((actor, ai2) => (
                                          <Chip key={`a-${ai2}`} label={actor} size="small" sx={{
                                            fontSize: '0.65rem', fontWeight: 600, borderRadius: '6px',
                                            backgroundColor: alpha(theme.palette.error.main, 0.08),
                                            color: theme.palette.error.main,
                                            border: `1px solid ${alpha(theme.palette.error.main, 0.2)}`,
                                          }} />
                                        ))}
                                        {test.real_world_reference.malware_families?.map((mw, mi) => (
                                          <Chip key={`m-${mi}`} label={mw} size="small" sx={{
                                            fontSize: '0.65rem', fontWeight: 600, borderRadius: '6px',
                                            backgroundColor: alpha(theme.palette.secondary.main, 0.08),
                                            color: theme.palette.secondary.main,
                                            border: `1px solid ${alpha(theme.palette.secondary.main, 0.2)}`,
                                          }} />
                                        ))}
                                      </Box>
                                      <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                                        {test.real_world_reference.mitre_url && (
                                          <Typography component="a" href={test.real_world_reference.mitre_url}
                                            target="_blank" rel="noopener noreferrer" variant="caption" sx={{
                                              color: '#8b5cf6', fontFamily: '"JetBrains Mono", monospace', fontSize: '0.7rem',
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
                                              color: '#10b981', fontFamily: '"JetBrains Mono", monospace', fontSize: '0.7rem',
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
                                        color: alpha(theme.palette.text.secondary, 0.8),
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
                    )}

                    {/* ── YARA Rules ── */}
                    {report.yara_rules && report.yara_rules.length > 0 && (
                      <Box sx={{ mb: 4 }}>
                        <SectionHeader icon="yara" label="Generated YARA Rules" />
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                          {report.yara_rules.map((rule, i) => (
                            <Accordion key={i} sx={innerAccordionSx}>
                              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                                <Box>
                                  <Typography variant="body2" sx={{ fontWeight: 700 }}>{rule.name}</Typography>
                                  <Typography variant="caption" color="text.secondary">{rule.description}</Typography>
                                </Box>
                              </AccordionSummary>
                              <AccordionDetails>
                                <Box component="pre" sx={codeBlockSx}>{rule.rule}</Box>
                              </AccordionDetails>
                            </Accordion>
                          ))}
                        </Box>
                      </Box>
                    )}

                    {/* ── SIEM Queries ── */}
                    {report.siem_queries && (
                      <Box sx={{ mb: 4 }}>
                        <SectionHeader icon="siem" label="Generated SIEM Queries" />
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                          {Object.entries(report.siem_queries).map(([platform, query]) => {
                            const platformColors: Record<string, string> = {
                              splunk: '#65a637',
                              qradar: '#6366f1',
                              elastic: '#f59e0b',
                              sentinel: '#0ea5e9',
                            };
                            const clr = platformColors[platform] || theme.palette.primary.main;
                            return (
                              <Accordion key={platform} sx={innerAccordionSx}>
                                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                                  <Box sx={{ width: '100%', display: 'flex', alignItems: 'center', gap: 1.5 }}>
                                    <Typography variant="body2" sx={{ flexGrow: 1, fontWeight: 600, textTransform: 'capitalize' }}>
                                      {platform} Query
                                    </Typography>
                                    <Chip label={platform.toUpperCase()} size="small" sx={{
                                      fontFamily: '"JetBrains Mono", monospace', fontSize: '0.65rem',
                                      fontWeight: 700, borderRadius: '8px', height: 24,
                                      backgroundColor: alpha(clr, 0.12), color: clr,
                                      border: `1px solid ${alpha(clr, 0.3)}`,
                                    }} />
                                  </Box>
                                </AccordionSummary>
                                <AccordionDetails>
                                  {query.description && (
                                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                                      {query.description}
                                    </Typography>
                                  )}
                                  <Box component="pre" sx={codeBlockSx}>{query.query}</Box>
                                  {query.notes && (
                                    <Typography variant="caption" sx={{ mt: 1.5, display: 'block', fontStyle: 'italic', color: 'text.secondary' }}>
                                      Notes: {query.notes}
                                    </Typography>
                                  )}
                                </AccordionDetails>
                              </Accordion>
                            );
                          })}
                        </Box>
                      </Box>
                    )}

                    {/* ── Global Sigma Matches ── */}
                    {report.sigma_matches && report.sigma_matches.length > 0 && (
                      <Box sx={{ mb: 2 }}>
                        <SectionHeader icon="global" label="Global Sigma Matches" />
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                          {report.sigma_matches.map((match, i) => {
                            const score = match.match_ratio;
                            const scoreColor = score >= 80 ? theme.palette.success.main : score >= 60 ? theme.palette.warning.main : score >= 40 ? '#eab308' : theme.palette.error.main;
                            const levelColor = match.level === 'critical' ? theme.palette.error.main : match.level === 'high' ? theme.palette.warning.main : theme.palette.info.main;
                            const confidenceColor = match.confidence === 'Direct Hit' ? theme.palette.success.main : match.confidence === 'Strong Match' ? theme.palette.warning.main : match.confidence === 'Relevant' ? '#eab308' : '#94a3b8';
                            const breakdown = match.score_breakdown;

                            return (
                              <Accordion key={i} sx={innerAccordionSx}>
                                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                                  <Box sx={{ width: '100%', display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
                                    <Typography
                                      component="a"
                                      href={match.github_link}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      onClick={(e: React.MouseEvent) => e.stopPropagation()}
                                      variant="body2"
                                      sx={{
                                        flexGrow: 1, fontWeight: 600, color: 'inherit', textDecoration: 'none',
                                        '&:hover': { color: theme.palette.primary.main, textDecoration: 'underline' },
                                      }}
                                    >
                                      {match.title}
                                    </Typography>
                                    {match.confidence && (
                                      <Chip label={match.confidence} size="small" sx={{
                                        fontWeight: 700, fontSize: '0.6rem', borderRadius: '8px', height: 22,
                                        backgroundColor: alpha(confidenceColor, 0.12), color: confidenceColor,
                                        border: `1px solid ${alpha(confidenceColor, 0.25)}`,
                                      }} />
                                    )}
                                    <Chip label={`${score}%`} size="small" sx={{
                                      fontFamily: '"JetBrains Mono", monospace', fontWeight: 700,
                                      fontSize: '0.7rem', borderRadius: '8px', height: 24,
                                      backgroundColor: alpha(scoreColor, 0.12), color: scoreColor,
                                      border: `1px solid ${alpha(scoreColor, 0.3)}`,
                                    }} />
                                    <Chip label={match.level} size="small" sx={{
                                      fontWeight: 700, fontSize: '0.6rem', borderRadius: '8px', height: 22,
                                      textTransform: 'uppercase', letterSpacing: '0.05em',
                                      backgroundColor: alpha(levelColor, 0.12), color: levelColor,
                                    }} />
                                  </Box>
                                </AccordionSummary>
                                <AccordionDetails>
                                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                                    {match.description}
                                  </Typography>

                                  {/* Score Breakdown Mini Bars */}
                                  {breakdown && (
                                    <Box sx={{ mb: 2 }}>
                                      <Typography variant="caption" sx={{ fontWeight: 600, display: 'block', mb: 1 }}>Score Breakdown</Typography>
                                      <Box sx={{ display: 'grid', gridTemplateColumns: 'auto 1fr auto', gap: '4px 8px', alignItems: 'center' }}>
                                        {[
                                          { label: 'MITRE', value: breakdown.mitre, max: 40, color: '#8b5cf6' },
                                          { label: 'IoC', value: breakdown.ioc_field, max: 25, color: '#10b981' },
                                          { label: 'Logsrc', value: breakdown.logsource, max: 15, color: '#3b82f6' },
                                          { label: 'KW', value: breakdown.keyword, max: 20, color: '#f59e0b' },
                                        ].map((bar) => (
                                          <React.Fragment key={bar.label}>
                                            <Typography variant="caption" sx={{ fontSize: '0.62rem', color: 'text.secondary', minWidth: 42 }}>{bar.label}</Typography>
                                            <Box sx={{ height: 5, borderRadius: 3, backgroundColor: alpha(bar.color, 0.1), overflow: 'hidden' }}>
                                              <Box sx={{ width: `${(bar.value / bar.max) * 100}%`, height: '100%', borderRadius: 3, background: `linear-gradient(90deg, ${bar.color}, ${alpha(bar.color, 0.6)})` }} />
                                            </Box>
                                            <Typography variant="caption" sx={{ fontFamily: '"JetBrains Mono", monospace', fontSize: '0.62rem', fontWeight: 600, color: bar.color, textAlign: 'right' }}>{bar.value}</Typography>
                                          </React.Fragment>
                                        ))}
                                      </Box>
                                    </Box>
                                  )}

                                  {/* MITRE Techniques Matched */}
                                  {match.mitre_matched && match.mitre_matched.length > 0 && (
                                    <Box sx={{ mb: 2 }}>
                                      <Typography variant="caption" sx={{ fontWeight: 600, display: 'block', mb: 0.8 }}>MITRE Matched</Typography>
                                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.6 }}>
                                        {match.mitre_matched.map((tid, ki) => (
                                          <Chip key={ki} label={tid.toUpperCase()} size="small" sx={{
                                            fontFamily: '"JetBrains Mono", monospace', fontSize: '0.65rem', fontWeight: 700,
                                            borderRadius: '6px', height: 22, backgroundColor: alpha('#8b5cf6', 0.1),
                                            color: '#8b5cf6', border: `1px solid ${alpha('#8b5cf6', 0.25)}`,
                                          }} />
                                        ))}
                                      </Box>
                                    </Box>
                                  )}

                                  {/* Matched Keywords */}
                                  {match.matched_keywords && match.matched_keywords.length > 0 && (
                                    <Box sx={{ mb: 1 }}>
                                      <Typography variant="caption" sx={{ fontWeight: 600, display: 'block', mb: 0.8 }}>Matched Keywords</Typography>
                                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.6 }}>
                                        {match.matched_keywords.map((kw, ki) => (
                                          <Chip key={ki} label={kw} size="small" variant="outlined" sx={{
                                            fontFamily: '"JetBrains Mono", monospace', fontSize: '0.65rem', borderRadius: '6px', height: 22,
                                          }} />
                                        ))}
                                      </Box>
                                    </Box>
                                  )}

                                  {/* GitHub Link */}
                                  {match.github_link && (
                                    <Box sx={{ mt: 1.5, pt: 1, borderTop: `1px solid ${alpha(theme.palette.divider, 0.08)}` }}>
                                      <Typography
                                        component="a" href={match.github_link} target="_blank" rel="noopener noreferrer"
                                        variant="caption" sx={{ color: theme.palette.primary.main, fontFamily: '"JetBrains Mono", monospace', fontSize: '0.68rem', textDecoration: 'none', '&:hover': { textDecoration: 'underline' } }}
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
                    )}
                  </AccordionDetails>
                </Accordion>
              </Box>
            ))}
          </Box>
        )}
      </Box>
    </>
  );
};

export default Reports;
