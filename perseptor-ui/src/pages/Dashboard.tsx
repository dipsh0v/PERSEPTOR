import ThreatActorsSection from '../components/Dashboard/ThreatActorsSection';
import TTPsSection from '../components/Dashboard/TTPsSection';
import ToolsMalwareSection from '../components/Dashboard/ToolsMalwareSection';
import IndicatorsSection from '../components/Dashboard/IndicatorsSection';
import ThreatSummaryCard from '../components/Dashboard/ThreatSummaryCard';
import SiemQueriesViewer from '../components/Dashboard/SiemQueriesViewer';
import GeneratedSigmaRules from '../components/Dashboard/GeneratedSigmaRules';
import GeneratedYaraRules from '../components/Dashboard/GeneratedYaraRules';
import AtomicTestsAccordion from '../components/Dashboard/AtomicTestsAccordion';
import GlobalSigmaMatchesViewer from '../components/Dashboard/GlobalSigmaMatchesViewer';
import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Typography, TextField, Button, Box, CircularProgress, Paper, Card, CardContent,
  Fade, Zoom, Divider, Chip, Accordion, AccordionSummary, AccordionDetails,
  Alert, IconButton, Tooltip, useTheme, Tabs, Tab,
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
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
import CloseIcon from '@mui/icons-material/Close';
import { useAppDispatch, useAppSelector } from '../store';
import {
  setUrl, setInputMode, setPdfFileName,
  analyzeUrlStream, analyzePdfStream,
  clearError, cancelAnalysis,
} from '../store/slices/analysisSlice';
import type { InputMode } from '../store/slices/analysisSlice';
import AnalysisProgressOverlay from '../components/AnalysisProgressOverlay';
import MitreNavigator from '../components/MitreNavigator';

// ─── Premium Design Tokens ──────────────────────────────────────────────────

const EASING = 'cubic-bezier(0.4, 0, 0.2, 1)';
const EASING_BOUNCE = 'cubic-bezier(0.34, 1.56, 0.64, 1)';
const CODE_FONT = '"JetBrains Mono", "Fira Code", "Cascadia Code", monospace';



const Dashboard: React.FC = () => {
  const dispatch = useAppDispatch();
  const {
    url,
    inputMode,
    pdfFileName,
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
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const theme = useTheme();
  const PRIMARY = theme.palette.primary.main;
  const SECONDARY = theme.palette.secondary.main;

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

  const handlePdfSelect = useCallback((file: File) => {
    if (file && file.type === 'application/pdf') {
      setPdfFile(file);
      dispatch(setPdfFileName(file.name));
    }
  }, [dispatch]);

  const handlePdfClear = useCallback(() => {
    setPdfFile(null);
    dispatch(setPdfFileName(null));
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }, [dispatch]);

  const handleFileInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handlePdfSelect(file);
  }, [handlePdfSelect]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handlePdfSelect(file);
  }, [handlePdfSelect]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setIsDragOver(false);
  }, []);

  const handleSubmitPdf = (e: React.FormEvent) => {
    e.preventDefault();
    if (!pdfFile) return;
    if (!isConnected && !apiKey) return;
    dispatch(analyzePdfStream(pdfFile));
  };

  const handleTabChange = (_: React.SyntheticEvent, newValue: number) => {
    dispatch(setInputMode(newValue === 0 ? 'url' : 'pdf'));
  };

  const handleCancel = () => {
    cancelAnalysis();
  };

  // ─── Shared Styles ──────────────────────────────────────────────────────────

  const glassCard = {
    background: theme.palette.background.paper,
    border: `1px solid ${theme.palette.divider}`,
    borderRadius: '12px',
    transition: `all 0.3s ${EASING}`,
  };

  const sectionHeader = (icon: React.ReactNode, label: string) => (
    <Typography
      variant="overline"
      sx={{
        display: 'flex',
        alignItems: 'center',
        gap: 1.2,
        fontWeight: 700,
        color: theme.palette.text.secondary,
        letterSpacing: '0.1em',
        mb: 2,
        pb: 1,
        borderBottom: `1px solid ${theme.palette.divider}`,
        '& .MuiSvgIcon-root': { fontSize: 18, color: theme.palette.primary.main }
      }}
    >
      {icon}
      {label}
    </Typography>
  );

  const premiumAccordion = {
    background: alpha(theme.palette.background.default, 0.5),
    boxShadow: 'none',
    '&:before': { display: 'none' },
    border: `1px solid ${theme.palette.divider}`,
    borderRadius: '8px !important',
    overflow: 'hidden',
    transition: `all 0.2s ${EASING}`,
    '&:hover': {
      borderColor: theme.palette.primary.main,
    },
    '& .MuiAccordionSummary-root': {
      minHeight: 48,
      '&.Mui-expanded': { minHeight: 48 },
    },
  };

  const codeBlock = {
    whiteSpace: 'pre-wrap' as const,
    fontFamily: CODE_FONT,
    fontSize: '0.82rem',
    lineHeight: 1.7,
    backgroundColor: theme.palette.mode === 'dark' ? '#09090b' : '#f4f4f5',
    color: theme.palette.text.primary,
    p: 2.5,
    borderRadius: '8px',
    border: `1px solid ${theme.palette.divider}`,
    overflow: 'auto',
    '&::-webkit-scrollbar': {
      width: 6,
      height: 6,
    },
    '&::-webkit-scrollbar-thumb': {
      background: alpha(theme.palette.primary.main, 0.2),
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
        px: 1,
        borderRadius: '8px',
        transition: `all 0.2s ${EASING}`,
        '&:hover': {
          background: alpha(theme.palette.primary.main, 0.04),
        },
      }}
    >
      <Box
        sx={{
          width: 28,
          height: 28,
          borderRadius: '6px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: alpha(theme.palette.primary.main, 0.08),
          color: theme.palette.primary.main,
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
          fontSize: '0.8125rem',
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
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2.5 }}>
            <Box>
              <Typography
                variant="h4"
                sx={{
                  fontWeight: 800,
                  fontFamily: '"Inter", sans-serif',
                  letterSpacing: '-0.02em',
                  color: theme.palette.text.primary,
                  mb: 0.5
                }}
              >
                Threat Intelligence Analysis
              </Typography>
              <Typography
                variant="body1"
                sx={{
                  color: theme.palette.text.secondary,
                  fontFamily: '"Inter", sans-serif',
                  fontWeight: 400,
                  maxWidth: 800
                }}
              >
                Ingest threat reports and technical articles to extract indicators, TTPs, and generate detection content.
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
                p: 3,
                mb: 3,
                position: 'relative',
                overflow: 'hidden',
                boxShadow: theme.palette.mode === 'dark' 
                  ? '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)' 
                  : '0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03)',
              }}
            >
              <Typography
                variant="subtitle2"
                sx={{
                  fontWeight: 700,
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em',
                  color: theme.palette.text.secondary,
                  mb: 2,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1
                }}
              >
                <SearchIcon sx={{ fontSize: 18 }} />
                New Analysis
              </Typography>

              <Tabs
                value={inputMode === 'url' ? 0 : 1}
                onChange={handleTabChange}
                sx={{
                  mb: 3,
                  minHeight: 40,
                  borderBottom: `1px solid ${theme.palette.divider}`,
                  '& .MuiTabs-indicator': {
                    height: 2,
                  },
                  '& .MuiTab-root': {
                    minHeight: 40,
                    fontSize: '0.875rem',
                    color: theme.palette.text.secondary,
                    '&.Mui-selected': { color: theme.palette.primary.main },
                  },
                }}
              >
                <Tab label="URL Analysis" />
                <Tab label="PDF Upload" />
              </Tabs>

              {/* ── URL Tab ── */}
              {inputMode === 'url' && (
                <Box
                  component="form"
                  onSubmit={handleSubmit}
                  sx={{
                    display: 'flex',
                    flexDirection: { xs: 'column', sm: 'row' },
                    gap: 2,
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
              )}

              {/* ── PDF Tab ── */}
              {inputMode === 'pdf' && (
                <Box component="form" onSubmit={handleSubmitPdf}>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".pdf"
                    style={{ display: 'none' }}
                    onChange={handleFileInputChange}
                  />

                  {!pdfFile ? (
                    <Box
                      onClick={() => fileInputRef.current?.click()}
                      onDrop={handleDrop}
                      onDragOver={handleDragOver}
                      onDragLeave={handleDragLeave}
                      sx={{
                        border: `2px dashed ${isDragOver ? PRIMARY : alpha(theme.palette.divider, 0.4)}`,
                        borderRadius: '12px',
                        p: 4,
                        textAlign: 'center',
                        cursor: 'pointer',
                        transition: `all 0.3s ${EASING}`,
                        background: isDragOver
                          ? alpha(PRIMARY, 0.06)
                          : alpha(theme.palette.background.default, 0.3),
                        '&:hover': {
                          borderColor: PRIMARY,
                          background: alpha(PRIMARY, 0.04),
                        },
                      }}
                    >
                      <CloudUploadIcon sx={{ fontSize: 48, color: alpha(PRIMARY, 0.6), mb: 1 }} />
                      <Typography
                        sx={{
                          fontFamily: '"Inter", sans-serif',
                          fontWeight: 600,
                          fontSize: '0.95rem',
                          color: alpha(theme.palette.text.primary, 0.7),
                        }}
                      >
                        Drop your PDF here or click to browse
                      </Typography>
                      <Typography
                        sx={{
                          fontFamily: '"Inter", sans-serif',
                          fontSize: '0.8rem',
                          color: alpha(theme.palette.text.primary, 0.4),
                          mt: 0.5,
                        }}
                      >
                        Maximum file size: 20MB
                      </Typography>
                    </Box>
                  ) : (
                    <Box
                      sx={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 2,
                        p: 2,
                        borderRadius: '12px',
                        border: `1px solid ${alpha(PRIMARY, 0.3)}`,
                        background: alpha(PRIMARY, 0.04),
                      }}
                    >
                      <PictureAsPdfIcon sx={{ fontSize: 36, color: '#ef4444' }} />
                      <Box sx={{ flex: 1, minWidth: 0 }}>
                        <Typography
                          sx={{
                            fontFamily: '"Inter", sans-serif',
                            fontWeight: 600,
                            fontSize: '0.9rem',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap',
                          }}
                        >
                          {pdfFile.name}
                        </Typography>
                        <Typography
                          sx={{
                            fontFamily: '"Inter", sans-serif',
                            fontSize: '0.75rem',
                            color: alpha(theme.palette.text.primary, 0.5),
                          }}
                        >
                          {(pdfFile.size / 1024 / 1024).toFixed(2)} MB
                        </Typography>
                      </Box>
                      <Tooltip title="Remove file" arrow>
                        <IconButton size="small" onClick={handlePdfClear}>
                          <CloseIcon sx={{ fontSize: 18 }} />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  )}

                  {error && (
                    <Alert severity="error" sx={{ mt: 1, borderRadius: '8px' }}>
                      {error}
                    </Alert>
                  )}

                  <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
                    <Button
                      type="submit"
                      variant="contained"
                      disabled={loading || !pdfFile || (!isConnected && !apiKey)}
                      startIcon={loading ? <CircularProgress size={20} sx={{ color: 'inherit' }} /> : <SearchIcon />}
                      sx={{
                        minWidth: '140px',
                        height: '48px',
                        borderRadius: '12px',
                        fontFamily: '"Inter", sans-serif',
                        fontWeight: 700,
                        fontSize: '0.95rem',
                        textTransform: 'none',
                        background: `linear-gradient(135deg, ${PRIMARY}, ${alpha(SECONDARY, 0.85)})`,
                        boxShadow: `0 4px 16px ${alpha(PRIMARY, 0.35)}`,
                        transition: `all 0.35s ${EASING_BOUNCE}`,
                        '&:hover': {
                          transform: 'translateY(-2px) scale(1.02)',
                          boxShadow: `0 8px 24px ${alpha(PRIMARY, 0.45)}`,
                          background: `linear-gradient(135deg, ${PRIMARY}, ${SECONDARY})`,
                        },
                        '&.Mui-disabled': {
                          background: alpha(PRIMARY, 0.25),
                          color: alpha('#fff', 0.5),
                        },
                      }}
                    >
                      {loading ? 'Analyzing...' : 'Analyze PDF'}
                    </Button>
                    {loading && (
                      <Tooltip title="Cancel analysis" arrow>
                        <IconButton
                          onClick={handleCancel}
                          sx={{
                            height: '48px',
                            width: '48px',
                            borderRadius: '12px',
                            color: theme.palette.error.main,
                            border: `1px solid ${alpha(theme.palette.error.main, 0.3)}`,
                            background: alpha(theme.palette.error.main, 0.06),
                            '&:hover': {
                              backgroundColor: alpha(theme.palette.error.main, 0.12),
                            },
                          }}
                        >
                          <CancelIcon />
                        </IconButton>
                      </Tooltip>
                    )}
                  </Box>
                </Box>
              )}
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
                    <ThreatSummaryCard summary={analysisResult.threat_summary} sectionHeader={sectionHeader} PRIMARY={PRIMARY} />

                    {/* ── Indicators of Compromise ─────────────────────────────── */}
                    {analysisResult.analysis_data?.indicators_of_compromise && (
                      <IndicatorsSection 
                        iocs={analysisResult.analysis_data.indicators_of_compromise} 
                        sectionHeader={sectionHeader} 
                        PRIMARY={PRIMARY} 
                        SECONDARY={SECONDARY} 
                      />
                    )}

                    {/* ── Threat Actors ─────────────────────────────────────────── */}
                    {analysisResult.analysis_data?.threat_actors && analysisResult.analysis_data.threat_actors.length > 0 && (
                      <ThreatActorsSection 
                        actors={analysisResult.analysis_data.threat_actors} 
                        sectionHeader={sectionHeader} 
                        PRIMARY={PRIMARY} 
                      />
                    )}

                    {/* ── MITRE ATT&CK TTPs ────────────────────────────────────── */}
                    {analysisResult.analysis_data?.ttps && analysisResult.analysis_data.ttps.length > 0 && (
                      <TTPsSection 
                        ttps={analysisResult.analysis_data.ttps} 
                        sectionHeader={sectionHeader} 
                        PRIMARY={PRIMARY} 
                      />
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
                      <ToolsMalwareSection 
                        tools={analysisResult.analysis_data.tools_or_malware} 
                        sectionHeader={sectionHeader} 
                        PRIMARY={PRIMARY} 
                      />
                    )}

                    {/* ── Generated Sigma Rules ────────────────────────────────── */}
                    {analysisResult.generated_sigma_rules && (
                      <GeneratedSigmaRules 
                        rules={analysisResult.generated_sigma_rules} 
                        sectionHeader={sectionHeader} 
                        premiumAccordion={premiumAccordion} 
                        codeBlock={codeBlock} 
                        PRIMARY={PRIMARY} 
                      />
                    )}

                    {/* ── Atomic Red Team Test Scenarios ──────────────────────── */}
                    {analysisResult.atomic_tests && analysisResult.atomic_tests.length > 0 && (
                      <AtomicTestsAccordion 
                        tests={analysisResult.atomic_tests} 
                        sectionHeader={sectionHeader} 
                        premiumAccordion={premiumAccordion} 
                        codeBlock={codeBlock} 
                        PRIMARY={PRIMARY} 
                        SECONDARY={SECONDARY} 
                      />
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

                    {/* ── Generated YARA Rules ────────────────────────────────── */}
                    {analysisResult.yara_rules && analysisResult.yara_rules.length > 0 && (
                      <GeneratedYaraRules 
                        rules={analysisResult.yara_rules} 
                        sectionHeader={sectionHeader} 
                        premiumAccordion={premiumAccordion} 
                        codeBlock={codeBlock} 
                        PRIMARY={PRIMARY} 
                      />
                    )}

                    {/* ── Global Sigma Matches ──────────────────────────────────── */}
                    {analysisResult.sigma_matches && analysisResult.sigma_matches.length > 0 && (
                      <GlobalSigmaMatchesViewer 
                        matches={analysisResult.sigma_matches} 
                        sectionHeader={sectionHeader} 
                        premiumAccordion={premiumAccordion} 
                        PRIMARY={PRIMARY} 
                      />
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
                boxShadow: theme.palette.mode === 'dark' 
                  ? '0 1px 3px rgba(0,0,0,0.2)' 
                  : '0 1px 3px rgba(0,0,0,0.05)',
              }}
            >
              <CardContent sx={{ p: 3 }}>
                <Typography
                  variant="subtitle2"
                  sx={{
                    fontWeight: 700,
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em',
                    color: theme.palette.text.secondary,
                    mb: 2,
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1
                  }}
                >
                  <AutoAwesomeIcon sx={{ fontSize: 18 }} />
                  Capabilities
                </Typography>

                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  {featureItem(
                    <AutoAwesomeIcon sx={{ fontSize: 14 }} />,
                    'Multi-provider AI analysis'
                  )}
                  {featureItem(
                    <SecurityIcon sx={{ fontSize: 14 }} />,
                    'Threat actor identification'
                  )}
                  {featureItem(
                    <GpsFixedIcon sx={{ fontSize: 14 }} />,
                    'MITRE ATT&CK mapping'
                  )}
                  {featureItem(
                    <ShieldIcon sx={{ fontSize: 14 }} />,
                    'Sigma & YARA generation'
                  )}
                  {featureItem(
                    <StorageIcon sx={{ fontSize: 14 }} />,
                    'SIEM Query conversion'
                  )}
                </Box>

                <Divider sx={{ my: 3 }} />

                <Box
                  sx={{
                    p: 2,
                    borderRadius: '8px',
                    background: alpha(theme.palette.success.main, 0.04),
                    border: `1px solid ${alpha(theme.palette.success.main, 0.1)}`,
                  }}
                >
                  <Typography
                    variant="caption"
                    sx={{
                      color: theme.palette.success.main,
                      fontWeight: 700,
                      textTransform: 'uppercase',
                      letterSpacing: '0.05em',
                      mb: 1,
                      display: 'flex',
                      alignItems: 'center',
                      gap: 1,
                    }}
                  >
                    <Box
                      sx={{
                        width: 6,
                        height: 6,
                        borderRadius: '50%',
                        backgroundColor: theme.palette.success.main,
                      }}
                    />
                    Engine Status: Ready
                  </Typography>
                  <Typography
                    variant="caption"
                    sx={{
                      color: theme.palette.text.secondary,
                      fontFamily: '"Inter", sans-serif',
                      lineHeight: 1.6,
                      display: 'block',
                    }}
                  >
                    Parallel processing enabled. Average analysis time: 15-30s.
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
