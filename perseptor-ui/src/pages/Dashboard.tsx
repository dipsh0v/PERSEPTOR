import React, { useState, useEffect } from 'react';
import {
  Typography, TextField, Button, Box, CircularProgress, Paper, Card, CardContent,
  Fade, Zoom, Divider, Chip, Accordion, AccordionSummary, AccordionDetails,
  Alert, IconButton, Tooltip, useTheme,
} from '@mui/material';
import { alpha } from '@mui/material/styles';
import SecurityIcon from '@mui/icons-material/Security';
import SearchIcon from '@mui/icons-material/Search';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import BugReportIcon from '@mui/icons-material/BugReport';
import CancelIcon from '@mui/icons-material/Cancel';
import FingerprintIcon from '@mui/icons-material/Fingerprint';
import ShieldIcon from '@mui/icons-material/Shield';
import StorageIcon from '@mui/icons-material/Storage';
import GpsFixedIcon from '@mui/icons-material/GpsFixed';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import ScienceIcon from '@mui/icons-material/Science';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import TerminalIcon from '@mui/icons-material/Terminal';
import { useAppDispatch, useAppSelector } from '../store';
import { setUrl, analyzeUrlStream, clearError, cancelAnalysis } from '../store/slices/analysisSlice';
import AnalysisProgressOverlay from '../components/AnalysisProgressOverlay';
import MitreNavigator from '../components/MitreNavigator';

// ─── Premium Design Tokens ──────────────────────────────────────────────────

const EASING = 'cubic-bezier(0.4, 0, 0.2, 1)';
const EASING_BOUNCE = 'cubic-bezier(0.34, 1.56, 0.64, 1)';
const CODE_FONT = '"JetBrains Mono", "Fira Code", "Cascadia Code", monospace';
const PRIMARY = '#6366f1';
const SECONDARY = '#ec4899';

const Dashboard: React.FC = () => {
  const dispatch = useAppDispatch();
  const {
    url,
    loading,
    error,
    result: analysisResult,
    streaming,
    sseEvents,
    sseProgress,
    sseCurrentStage,
    sseStartTime,
  } = useAppSelector((state) => state.analysis);
  const { isConnected, apiKey } = useAppSelector((state) => state.settings);
  const [showAnimation, setShowAnimation] = useState(false);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const theme = useTheme();

  useEffect(() => {
    setShowAnimation(true);
  }, []);

  // Elapsed time counter
  useEffect(() => {
    if (!sseStartTime || !loading) {
      return;
    }
    const interval = setInterval(() => {
      setElapsedSeconds(Math.floor((Date.now() - sseStartTime) / 1000));
    }, 1000);
    return () => clearInterval(interval);
  }, [sseStartTime, loading]);

  // Reset elapsed when not loading
  useEffect(() => {
    if (!loading) {
      const timeout = setTimeout(() => {
        if (!loading) setElapsedSeconds(0);
      }, 3000);
      return () => clearTimeout(timeout);
    }
  }, [loading]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      new URL(url);
    } catch {
      return;
    }

    if (!isConnected && !apiKey) {
      return;
    }

    dispatch(analyzeUrlStream(url));
  };

  const handleCancel = () => {
    cancelAnalysis();
  };

  // ─── Shared Styles ──────────────────────────────────────────────────────────

  const glassCard = {
    backdropFilter: 'blur(20px)',
    background: alpha(theme.palette.background.paper, 0.6),
    border: `1px solid ${alpha(theme.palette.divider, 0.12)}`,
    borderRadius: '16px',
    transition: `all 0.4s ${EASING}`,
  };

  const sectionHeader = (icon: React.ReactNode, label: string) => (
    <Typography
      variant="h6"
      gutterBottom
      sx={{
        display: 'flex',
        alignItems: 'center',
        gap: 1.5,
        fontWeight: 700,
        fontFamily: '"Inter", sans-serif',
        color: PRIMARY,
        letterSpacing: '-0.01em',
        position: 'relative',
        '&::after': {
          content: '""',
          position: 'absolute',
          bottom: -4,
          left: 0,
          width: 40,
          height: 2,
          background: `linear-gradient(90deg, ${PRIMARY}, transparent)`,
          borderRadius: 1,
        },
      }}
    >
      {icon}
      {label}
    </Typography>
  );

  const premiumAccordion = {
    background: alpha(theme.palette.background.paper, 0.4),
    backdropFilter: 'blur(12px)',
    boxShadow: 'none',
    '&:before': { display: 'none' },
    border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
    borderRadius: '12px !important',
    overflow: 'hidden',
    transition: `all 0.35s ${EASING}`,
    '&:hover': {
      border: `1px solid ${alpha(PRIMARY, 0.3)}`,
      boxShadow: `0 0 20px ${alpha(PRIMARY, 0.08)}, 0 4px 16px ${alpha(PRIMARY, 0.06)}`,
      transform: 'translateY(-1px)',
    },
    '& .MuiAccordionSummary-root': {
      transition: `background 0.3s ${EASING}`,
      '&:hover': {
        background: alpha(PRIMARY, 0.04),
      },
    },
  };

  const codeBlock = {
    whiteSpace: 'pre-wrap' as const,
    fontFamily: CODE_FONT,
    fontSize: '0.82rem',
    lineHeight: 1.7,
    backgroundColor: alpha('#0d1117', 0.95),
    color: '#e6edf3',
    p: 2.5,
    borderRadius: '10px',
    border: `1px solid ${alpha(PRIMARY, 0.15)}`,
    boxShadow: `inset 0 1px 4px ${alpha('#000', 0.3)}`,
    overflow: 'auto',
    '&::-webkit-scrollbar': {
      width: 6,
      height: 6,
    },
    '&::-webkit-scrollbar-thumb': {
      background: alpha(PRIMARY, 0.3),
      borderRadius: 3,
    },
  };

  const featureItem = (icon: React.ReactNode, text: string) => (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        gap: 1.5,
        py: 1,
        px: 1.5,
        borderRadius: '10px',
        transition: `all 0.3s ${EASING}`,
        '&:hover': {
          background: alpha(PRIMARY, 0.06),
          transform: 'translateX(4px)',
        },
      }}
    >
      <Box
        sx={{
          width: 32,
          height: 32,
          borderRadius: '8px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: `linear-gradient(135deg, ${alpha(PRIMARY, 0.15)}, ${alpha(SECONDARY, 0.1)})`,
          flexShrink: 0,
        }}
      >
        {icon}
      </Box>
      <Typography
        variant="body2"
        sx={{
          color: theme.palette.text.secondary,
          fontFamily: '"Inter", sans-serif',
          fontWeight: 500,
          fontSize: '0.84rem',
        }}
      >
        {text}
      </Typography>
    </Box>
  );

  // ─── Render ─────────────────────────────────────────────────────────────────

  return (
    <Box sx={{ p: { xs: 2, md: 4 }, maxWidth: 1400, mx: 'auto', overflow: 'hidden' }}>
      {/* ── Page Header ──────────────────────────────────────────────────────── */}
      <Fade in={showAnimation} timeout={800}>
        <Box sx={{ mb: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1.5 }}>
            <Box
              sx={{
                width: 56,
                height: 56,
                borderRadius: '16px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                background: `linear-gradient(135deg, ${PRIMARY}, ${SECONDARY})`,
                boxShadow: `0 8px 24px ${alpha(PRIMARY, 0.35)}`,
                animation: 'pulse-glow 3s ease-in-out infinite',
                '@keyframes pulse-glow': {
                  '0%, 100%': { boxShadow: `0 8px 24px ${alpha(PRIMARY, 0.35)}` },
                  '50%': { boxShadow: `0 8px 32px ${alpha(PRIMARY, 0.55)}` },
                },
              }}
            >
              <SearchIcon sx={{ fontSize: 30, color: '#fff' }} />
            </Box>
            <Box>
              <Typography
                variant="h3"
                sx={{
                  fontWeight: 800,
                  fontFamily: '"Inter", sans-serif',
                  letterSpacing: '-0.03em',
                  lineHeight: 1.1,
                  background: `linear-gradient(135deg, ${PRIMARY} 0%, ${SECONDARY} 50%, ${PRIMARY} 100%)`,
                  backgroundSize: '200% auto',
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  animation: 'gradient-shift 4s ease infinite',
                  '@keyframes gradient-shift': {
                    '0%': { backgroundPosition: '0% center' },
                    '50%': { backgroundPosition: '100% center' },
                    '100%': { backgroundPosition: '0% center' },
                  },
                }}
              >
                Threat Report Analysis
              </Typography>
              <Typography
                variant="subtitle1"
                sx={{
                  color: alpha(theme.palette.text.secondary, 0.7),
                  fontFamily: '"Inter", sans-serif',
                  fontWeight: 500,
                  mt: 0.5,
                  letterSpacing: '0.02em',
                  animation: 'fade-slide-up 1s ease-out 0.3s both',
                  '@keyframes fade-slide-up': {
                    from: { opacity: 0, transform: 'translateY(8px)' },
                    to: { opacity: 1, transform: 'translateY(0)' },
                  },
                }}
              >
                Extract actionable intelligence from threat reports with AI-powered analysis
              </Typography>
            </Box>
          </Box>
        </Box>
      </Fade>

      {/* ── SSE Progress Overlay ──────────────────────────────────────────────── */}
      <AnalysisProgressOverlay
        visible={loading && streaming}
        events={sseEvents}
        progress={sseProgress}
        currentStage={sseCurrentStage}
        elapsedSeconds={elapsedSeconds}
      />

      {/* ── Connection Warning ────────────────────────────────────────────────── */}
      {!isConnected && !apiKey && (
        <Alert
          severity="warning"
          sx={{
            mb: 3,
            borderRadius: '12px',
            border: `1px solid ${alpha('#f59e0b', 0.3)}`,
            backdropFilter: 'blur(8px)',
            fontFamily: '"Inter", sans-serif',
          }}
        >
          Please go to Settings to configure your AI provider and API key before analyzing.
        </Alert>
      )}

      {/* ── Main Content Grid ─────────────────────────────────────────────────── */}
      <Box sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, gap: 3 }}>

        {/* ── Left Column (Search + Results) ────────────────────────────────── */}
        <Box sx={{ flex: { xs: '1 1 100%', md: '2 1 66%' } }}>

          {/* ── Search Card ─────────────────────────────────────────────────── */}
          <Zoom in={showAnimation} timeout={1000} style={{ transitionDelay: '200ms' }}>
            <Paper
              elevation={0}
              sx={{
                ...glassCard,
                p: 3.5,
                mb: 3,
                position: 'relative',
                overflow: 'hidden',
                boxShadow: `0 8px 40px ${alpha(PRIMARY, 0.08)}, 0 2px 8px ${alpha('#000', 0.06)}`,
                '&:hover': {
                  boxShadow: `0 12px 48px ${alpha(PRIMARY, 0.14)}, 0 4px 12px ${alpha('#000', 0.08)}`,
                },
              }}
            >
              {/* Gradient top border */}
              <Box
                sx={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  right: 0,
                  height: '3px',
                  background: `linear-gradient(90deg, ${PRIMARY}, ${SECONDARY}, ${PRIMARY})`,
                  backgroundSize: '200% 100%',
                  animation: 'shimmer-border 3s ease infinite',
                  '@keyframes shimmer-border': {
                    '0%': { backgroundPosition: '0% 0%' },
                    '100%': { backgroundPosition: '200% 0%' },
                  },
                }}
              />
              {/* Subtle corner glow */}
              <Box
                sx={{
                  position: 'absolute',
                  top: -60,
                  right: -60,
                  width: 160,
                  height: 160,
                  borderRadius: '50%',
                  background: `radial-gradient(circle, ${alpha(PRIMARY, 0.08)} 0%, transparent 70%)`,
                  pointerEvents: 'none',
                }}
              />

              <Typography
                variant="h5"
                gutterBottom
                sx={{
                  fontWeight: 700,
                  fontFamily: '"Inter", sans-serif',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1.5,
                  letterSpacing: '-0.01em',
                }}
              >
                <Box
                  sx={{
                    width: 36,
                    height: 36,
                    borderRadius: '10px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    background: `linear-gradient(135deg, ${alpha(PRIMARY, 0.15)}, ${alpha(SECONDARY, 0.1)})`,
                  }}
                >
                  <SearchIcon sx={{ color: PRIMARY, fontSize: 20 }} />
                </Box>
                URL Analysis
              </Typography>

              <Box
                component="form"
                onSubmit={handleSubmit}
                sx={{
                  display: 'flex',
                  flexDirection: { xs: 'column', sm: 'row' },
                  gap: 2,
                  mt: 2,
                }}
              >
                <TextField
                  fullWidth
                  label="Enter URL"
                  value={url}
                  onChange={(e) => dispatch(setUrl(e.target.value))}
                  error={!!error}
                  helperText={error}
                  placeholder="https://example.com/threat-report"
                  sx={{
                    flexGrow: 1,
                    '& .MuiOutlinedInput-root': {
                      borderRadius: '12px',
                      fontFamily: '"Inter", sans-serif',
                      transition: `all 0.3s ${EASING}`,
                      '&.Mui-focused': {
                        boxShadow: `0 0 0 3px ${alpha(PRIMARY, 0.15)}`,
                      },
                      '&:hover': {
                        boxShadow: `0 0 0 2px ${alpha(PRIMARY, 0.08)}`,
                      },
                    },
                    '& .MuiInputLabel-root': {
                      fontFamily: '"Inter", sans-serif',
                    },
                  }}
                />
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Button
                    type="submit"
                    variant="contained"
                    disabled={loading || (!isConnected && !apiKey)}
                    startIcon={loading ? <CircularProgress size={20} sx={{ color: 'inherit' }} /> : <SearchIcon />}
                    sx={{
                      minWidth: { xs: '100%', sm: '140px' },
                      height: '56px',
                      borderRadius: '12px',
                      fontFamily: '"Inter", sans-serif',
                      fontWeight: 700,
                      fontSize: '0.95rem',
                      letterSpacing: '0.02em',
                      textTransform: 'none',
                      background: `linear-gradient(135deg, ${PRIMARY}, ${alpha(SECONDARY, 0.85)})`,
                      boxShadow: `0 4px 16px ${alpha(PRIMARY, 0.35)}`,
                      transition: `all 0.35s ${EASING_BOUNCE}`,
                      '&:hover': {
                        transform: 'translateY(-2px) scale(1.02)',
                        boxShadow: `0 8px 24px ${alpha(PRIMARY, 0.45)}`,
                        background: `linear-gradient(135deg, ${PRIMARY}, ${SECONDARY})`,
                      },
                      '&:active': {
                        transform: 'translateY(0) scale(0.98)',
                      },
                      '&.Mui-disabled': {
                        background: alpha(PRIMARY, 0.25),
                        color: alpha('#fff', 0.5),
                      },
                    }}
                  >
                    {loading ? 'Analyzing...' : 'Analyze'}
                  </Button>
                  {loading && (
                    <Tooltip title="Cancel analysis" arrow>
                      <IconButton
                        onClick={handleCancel}
                        sx={{
                          height: '56px',
                          width: '56px',
                          borderRadius: '12px',
                          color: theme.palette.error.main,
                          border: `1px solid ${alpha(theme.palette.error.main, 0.3)}`,
                          background: alpha(theme.palette.error.main, 0.06),
                          transition: `all 0.3s ${EASING}`,
                          animation: 'cancel-pulse 2s ease-in-out infinite',
                          '@keyframes cancel-pulse': {
                            '0%, 100%': { boxShadow: `0 0 0 0 ${alpha(theme.palette.error.main, 0.2)}` },
                            '50%': { boxShadow: `0 0 16px 4px ${alpha(theme.palette.error.main, 0.15)}` },
                          },
                          '&:hover': {
                            backgroundColor: alpha(theme.palette.error.main, 0.12),
                            boxShadow: `0 0 20px ${alpha(theme.palette.error.main, 0.3)}`,
                            transform: 'scale(1.05)',
                          },
                        }}
                      >
                        <CancelIcon />
                      </IconButton>
                    </Tooltip>
                  )}
                </Box>
              </Box>
            </Paper>
          </Zoom>

          {/* ── Analysis Results ────────────────────────────────────────────── */}
          {analysisResult && (
            <Fade in={!!analysisResult} timeout={600}>
              <Box>
                <Card
                  elevation={0}
                  sx={{
                    ...glassCard,
                    mb: 3,
                    overflow: 'visible',
                    boxShadow: `0 4px 32px ${alpha(PRIMARY, 0.06)}`,
                  }}
                >
                  <CardContent sx={{ p: { xs: 2.5, md: 3.5 } }}>

                    {/* ── Threat Summary ───────────────────────────────────────── */}
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
                        {analysisResult.threat_summary}
                      </Typography>
                    </Box>

                    {/* ── Indicators of Compromise ─────────────────────────────── */}
                    {analysisResult.analysis_data?.indicators_of_compromise && (
                      <Box sx={{ mb: 4 }}>
                        {sectionHeader(<FingerprintIcon sx={{ fontSize: 22, color: PRIMARY }} />, 'Indicators of Compromise')}
                        <Box sx={{ mt: 2 }}>
                          {Object.entries(analysisResult.analysis_data.indicators_of_compromise).map(([key, value]) => (
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
                    )}

                    {/* ── Threat Actors ─────────────────────────────────────────── */}
                    {analysisResult.analysis_data?.threat_actors && analysisResult.analysis_data.threat_actors.length > 0 && (
                      <Box sx={{ mb: 4 }}>
                        {sectionHeader(<SecurityIcon sx={{ fontSize: 22, color: PRIMARY }} />, 'Threat Actors')}
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 2 }}>
                          {analysisResult.analysis_data.threat_actors.map((actor, index) => (
                            <Chip
                              key={index}
                              label={actor}
                              sx={{
                                fontFamily: '"Inter", sans-serif',
                                fontWeight: 600,
                                fontSize: '0.85rem',
                                borderRadius: '10px',
                                backgroundColor: alpha(theme.palette.error.main, 0.1),
                                color: theme.palette.error.main,
                                border: `1px solid ${alpha(theme.palette.error.main, 0.25)}`,
                                px: 1,
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
                    )}

                    {/* ── MITRE ATT&CK TTPs ────────────────────────────────────── */}
                    {analysisResult.analysis_data?.ttps && analysisResult.analysis_data.ttps.length > 0 && (
                      <Box sx={{ mb: 4 }}>
                        {sectionHeader(<GpsFixedIcon sx={{ fontSize: 22, color: PRIMARY }} />, 'MITRE ATT&CK TTPs')}
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 2 }}>
                          {analysisResult.analysis_data.ttps.map((ttp, index) => (
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
                    )}

                    {/* ── MITRE Navigator ───────────────────────────────────────── */}
                    {analysisResult.mitre_mapping?.techniques && analysisResult.mitre_mapping.techniques.length > 0 && (
                      <Box sx={{ mb: 4 }}>
                        <MitreNavigator
                          techniques={analysisResult.mitre_mapping.techniques}
                          tacticSummary={analysisResult.mitre_mapping.tactic_summary || {}}
                          tags={analysisResult.mitre_mapping.tags || []}
                        />
                      </Box>
                    )}

                    {/* ── Tools & Malware ───────────────────────────────────────── */}
                    {analysisResult.analysis_data?.tools_or_malware && analysisResult.analysis_data.tools_or_malware.length > 0 && (
                      <Box sx={{ mb: 4 }}>
                        {sectionHeader(<BugReportIcon sx={{ fontSize: 22, color: PRIMARY }} />, 'Tools & Malware')}
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 2 }}>
                          {analysisResult.analysis_data.tools_or_malware.map((item, index) => {
                            const isMalware = ['malware', 'trojan', 'ransomware', 'worm', 'virus'].some(k => item.toLowerCase().includes(k));
                            const chipColor = isMalware ? theme.palette.error.main : '#3b82f6';
                            return (
                              <Chip
                                key={index}
                                label={item}
                                sx={{
                                  fontFamily: '"Inter", sans-serif',
                                  fontWeight: 600,
                                  fontSize: '0.82rem',
                                  borderRadius: '10px',
                                  backgroundColor: alpha(chipColor, 0.1),
                                  color: chipColor,
                                  border: `1px solid ${alpha(chipColor, 0.25)}`,
                                  transition: `all 0.25s ${EASING}`,
                                  '&:hover': {
                                    backgroundColor: alpha(chipColor, 0.18),
                                    boxShadow: `0 0 12px ${alpha(chipColor, 0.2)}`,
                                  },
                                }}
                              />
                            );
                          })}
                        </Box>
                      </Box>
                    )}

                    {/* ── Generated Sigma Rules ────────────────────────────────── */}
                    {analysisResult.generated_sigma_rules && (
                      <Box sx={{ mb: 4 }}>
                        {sectionHeader(<ShieldIcon sx={{ fontSize: 22, color: PRIMARY }} />, 'Generated Sigma Rules')}
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
                          {analysisResult.generated_sigma_rules.split('---').filter((rule) => {
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
                    )}

                    {/* ── Atomic Red Team Test Scenarios ──────────────────────── */}
                    {analysisResult.atomic_tests && analysisResult.atomic_tests.length > 0 && (
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
                          {analysisResult.atomic_tests.map((test, index) => {
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
                                    <Chip label={test.mitre_technique} size="small" component="a"
                                      href={test.real_world_reference?.mitre_url || `https://attack.mitre.org/techniques/${test.mitre_technique.replace('.', '/')}/`}
                                      target="_blank" rel="noopener noreferrer" clickable
                                      sx={{
                                        fontFamily: CODE_FONT, fontWeight: 700, fontSize: '0.72rem', borderRadius: '6px',
                                        backgroundColor: alpha('#8b5cf6', 0.1), color: '#8b5cf6',
                                        border: `1px solid ${alpha('#8b5cf6', 0.25)}`,
                                        textDecoration: 'none',
                                      }}
                                    />
                                    <Chip label={test.privilege_required} size="small" sx={{
                                      fontFamily: '"Inter", sans-serif', fontWeight: 700, fontSize: '0.68rem', borderRadius: '6px',
                                      textTransform: 'uppercase', letterSpacing: '0.05em',
                                      backgroundColor: alpha(privColor, 0.1), color: privColor,
                                      border: `1px solid ${alpha(privColor, 0.25)}`,
                                    }} />
                                    {test.platforms?.map((p, pi) => (
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
                                        {test.prerequisites.map((prereq, pi) => (
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
                                      {test.executor.steps && test.executor.steps.map((step, si) => (
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
                                          {test.expected_detection.event_ids?.map((eid, ei) => (
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
                                        {test.real_world_reference.threat_actors?.map((actor, ai) => (
                                          <Chip key={`actor-${ai}`} label={actor} size="small" sx={{
                                            fontFamily: '"Inter", sans-serif', fontSize: '0.68rem', fontWeight: 600,
                                            borderRadius: '6px', backgroundColor: alpha(theme.palette.error.main, 0.08),
                                            color: theme.palette.error.main, border: `1px solid ${alpha(theme.palette.error.main, 0.2)}`,
                                          }} />
                                        ))}
                                        {test.real_world_reference.malware_families?.map((mw, mi) => (
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
                    )}

                    {/* ── SIEM Queries ──────────────────────────────────────────── */}
                    {analysisResult.siem_queries && (
                      <Box sx={{ mb: 4 }}>
                        {sectionHeader(<StorageIcon sx={{ fontSize: 22, color: PRIMARY }} />, 'Generated SIEM Queries')}
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
                          {Object.entries(analysisResult.siem_queries).map(([platform, query]) => {
                            const platformColors: Record<string, string> = {
                              splunk: PRIMARY,
                              qradar: SECONDARY,
                              elastic: '#10b981',
                              sentinel: '#f59e0b',
                            };
                            const pColor = platformColors[platform] || '#6b7280';
                            return (
                              <Accordion key={platform} sx={premiumAccordion}>
                                <AccordionSummary
                                  expandIcon={<ExpandMoreIcon sx={{ color: alpha(PRIMARY, 0.6) }} />}
                                >
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
                    )}

                    {/* ── YARA Rules ────────────────────────────────────────────── */}
                    {analysisResult.yara_rules && analysisResult.yara_rules.length > 0 && (
                      <Box sx={{ mb: 4 }}>
                        {sectionHeader(<BugReportIcon sx={{ fontSize: 22, color: PRIMARY }} />, 'Generated YARA Rules')}
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
                          {analysisResult.yara_rules.map((rule, index) => (
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
                    )}

                    {/* ── Global Sigma Matches ──────────────────────────────────── */}
                    {analysisResult.sigma_matches && analysisResult.sigma_matches.length > 0 && (
                      <Box sx={{ mb: 2, overflow: 'hidden', maxWidth: '100%' }}>
                        {sectionHeader(<ShieldIcon sx={{ fontSize: 22, color: PRIMARY }} />, 'Global Sigma Matches')}
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2, overflow: 'hidden' }}>
                          {analysisResult.sigma_matches.map((match, index) => {
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
                                        {match.mitre_matched.map((tid, idx) => (
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
                                        {match.matched_keywords.map((keyword, idx) => (
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
                    )}

                  </CardContent>
                </Card>
              </Box>
            </Fade>
          )}
        </Box>

        {/* ── Right Column (Info Panel) ─────────────────────────────────────── */}
        <Box sx={{ flex: { xs: '1 1 100%', md: '1 1 33%' } }}>
          <Zoom in={showAnimation} timeout={1000} style={{ transitionDelay: '400ms' }}>
            <Card
              elevation={0}
              sx={{
                ...glassCard,
                height: '100%',
                position: 'relative',
                overflow: 'hidden',
                boxShadow: `0 4px 32px ${alpha(PRIMARY, 0.06)}`,
              }}
            >
              {/* Decorative gradient orb */}
              <Box
                sx={{
                  position: 'absolute',
                  top: -40,
                  right: -40,
                  width: 120,
                  height: 120,
                  borderRadius: '50%',
                  background: `radial-gradient(circle, ${alpha(SECONDARY, 0.1)} 0%, transparent 70%)`,
                  pointerEvents: 'none',
                }}
              />
              <Box
                sx={{
                  position: 'absolute',
                  bottom: -30,
                  left: -30,
                  width: 100,
                  height: 100,
                  borderRadius: '50%',
                  background: `radial-gradient(circle, ${alpha(PRIMARY, 0.08)} 0%, transparent 70%)`,
                  pointerEvents: 'none',
                }}
              />

              <CardContent sx={{ p: 3, position: 'relative', zIndex: 1 }}>
                <Typography
                  variant="h6"
                  gutterBottom
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1.5,
                    fontWeight: 700,
                    fontFamily: '"Inter", sans-serif',
                    color: PRIMARY,
                    letterSpacing: '-0.01em',
                  }}
                >
                  <Box
                    sx={{
                      width: 34,
                      height: 34,
                      borderRadius: '10px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      background: `linear-gradient(135deg, ${alpha(PRIMARY, 0.15)}, ${alpha(SECONDARY, 0.1)})`,
                    }}
                  >
                    <AutoAwesomeIcon sx={{ color: PRIMARY, fontSize: 18 }} />
                  </Box>
                  About Threat Analysis
                </Typography>

                <Divider sx={{ mb: 2.5, borderColor: alpha(theme.palette.divider, 0.08) }} />

                <Typography
                  variant="body2"
                  sx={{
                    color: theme.palette.text.secondary,
                    fontFamily: '"Inter", sans-serif',
                    lineHeight: 1.9,
                    mb: 3,
                    fontSize: '0.85rem',
                  }}
                >
                  Advanced threat intelligence platform that leverages AI to analyze URLs and provide comprehensive security insights.
                </Typography>

                <Typography
                  variant="subtitle2"
                  sx={{
                    fontFamily: '"Inter", sans-serif',
                    fontWeight: 700,
                    fontSize: '0.75rem',
                    letterSpacing: '0.1em',
                    textTransform: 'uppercase',
                    color: alpha(theme.palette.text.primary, 0.5),
                    mb: 1.5,
                  }}
                >
                  Capabilities
                </Typography>

                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                  {featureItem(
                    <AutoAwesomeIcon sx={{ fontSize: 16, color: PRIMARY }} />,
                    'Multi-provider AI analysis (OpenAI, Anthropic, Google)'
                  )}
                  {featureItem(
                    <SecurityIcon sx={{ fontSize: 16, color: PRIMARY }} />,
                    'Threat actor identification'
                  )}
                  {featureItem(
                    <GpsFixedIcon sx={{ fontSize: 16, color: PRIMARY }} />,
                    'MITRE ATT&CK mapping'
                  )}
                  {featureItem(
                    <ShieldIcon sx={{ fontSize: 16, color: PRIMARY }} />,
                    'Sigma/YARA rule generation'
                  )}
                  {featureItem(
                    <ShieldIcon sx={{ fontSize: 16, color: SECONDARY }} />,
                    'Global Sigma rule matching'
                  )}
                  {featureItem(
                    <FingerprintIcon sx={{ fontSize: 16, color: PRIMARY }} />,
                    'IoC/TTP extraction'
                  )}
                  {featureItem(
                    <StorageIcon sx={{ fontSize: 16, color: PRIMARY }} />,
                    'Multi-platform SIEM queries'
                  )}
                </Box>

                {/* Performance info */}
                <Divider sx={{ my: 2.5, borderColor: alpha(theme.palette.divider, 0.08) }} />

                <Box
                  sx={{
                    p: 2,
                    borderRadius: '12px',
                    background: `linear-gradient(135deg, ${alpha('#10b981', 0.06)}, ${alpha(PRIMARY, 0.04)})`,
                    border: `1px solid ${alpha('#10b981', 0.15)}`,
                  }}
                >
                  <Typography
                    variant="body2"
                    sx={{
                      color: '#10b981',
                      fontWeight: 700,
                      fontFamily: '"Inter", sans-serif',
                      fontSize: '0.85rem',
                      mb: 0.75,
                      display: 'flex',
                      alignItems: 'center',
                      gap: 1,
                    }}
                  >
                    <Box
                      sx={{
                        width: 8,
                        height: 8,
                        borderRadius: '50%',
                        backgroundColor: '#10b981',
                        animation: 'status-pulse 2s ease-in-out infinite',
                        '@keyframes status-pulse': {
                          '0%, 100%': { opacity: 1 },
                          '50%': { opacity: 0.4 },
                        },
                      }}
                    />
                    Parallel Processing Engine
                  </Typography>
                  <Typography
                    variant="caption"
                    sx={{
                      color: alpha(theme.palette.text.secondary, 0.8),
                      fontFamily: '"Inter", sans-serif',
                      lineHeight: 1.8,
                      display: 'block',
                    }}
                  >
                    PERSEPTOR uses parallel AI calls and real-time SSE streaming to deliver results faster.
                    Multiple analysis stages run simultaneously, cutting total analysis time significantly.
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Zoom>
        </Box>
      </Box>
    </Box>
  );
};

export default Dashboard;
