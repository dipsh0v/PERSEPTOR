import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  InputAdornment,
  Alert,
  Skeleton,
  Divider,
  Tooltip,
  LinearProgress,
} from '@mui/material';
import { alpha, useTheme } from '@mui/material/styles';
import {
  Search as SearchIcon,
  Visibility as ViewIcon,
  Download as DownloadIcon,
  Delete as DeleteIcon,
  Security as SecurityIcon,
  Close as CloseIcon,
  Shield as ShieldIcon,
  BugReport as BugReportIcon,
  Description as DescriptionIcon,
  CheckCircleOutline as CheckIcon,
  RecommendOutlined as RecIcon,
  LinkOutlined as RefIcon,
  PersonOutline as PersonIcon,
  CalendarToday as CalendarIcon,
} from '@mui/icons-material';
import SigmaIcon from '../components/SigmaIcon';
// @ts-ignore
import * as yaml from 'js-yaml';
import { useAppDispatch, useAppSelector } from '../store';
import {
  fetchRules,
  deleteRule,
  setSearchTerm,
  setSelectedRule,
} from '../store/slices/rulesSlice';
import type { Rule } from '../store/slices/rulesSlice';

/* ───────── keyframes ───────── */
const keyframes = `
@keyframes rulesFadeSlideUp {
  from { opacity: 0; transform: translateY(24px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes rulesCardEnter {
  from { opacity: 0; transform: translateY(16px) scale(0.97); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}
@keyframes rulesPulse {
  0%, 100% { opacity: 0.6; }
  50%      { opacity: 1; }
}
`;

const CreatedRules: React.FC = () => {
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';
  const dispatch = useAppDispatch();
  const { rules, loading, error, searchTerm, selectedRule } = useAppSelector(
    (state) => state.rules
  );
  const [viewDialogOpen, setViewDialogOpen] = useState(false);

  useEffect(() => {
    dispatch(fetchRules());
  }, [dispatch]);

  const filteredRules = rules.filter(
    (rule) =>
      rule.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      rule.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      rule.product.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleViewRule = (rule: Rule) => {
    dispatch(setSelectedRule(rule));
    setViewDialogOpen(true);
  };

  const handleDownloadRule = async (rule: Rule) => {
    try {
      const response = await fetch(`/api/rules/${rule.id}/download`);
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${rule.title.replace(/\s+/g, '_')}.yaml`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (err) {
      console.error('Error downloading rule:', err);
    }
  };

  const handleDeleteRule = async (ruleId: string) => {
    if (window.confirm('Are you sure you want to delete this rule?')) {
      dispatch(deleteRule(ruleId));
    }
  };

  const getConfidenceColor = (score: number) => {
    if (score >= 0.8) return theme.palette.success.main;
    if (score >= 0.6) return theme.palette.warning.main;
    return theme.palette.error.main;
  };

  const getConfidenceLabel = (score: number) => {
    if (score >= 0.8) return 'High';
    if (score >= 0.6) return 'Medium';
    return 'Low';
  };

  /* ── code block style ── */
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
    maxHeight: 360,
  };

  /* ── Loading state ── */
  if (loading) {
    return (
      <>
        <style>{keyframes}</style>
        <Box sx={{ p: { xs: 2, md: 4 }, maxWidth: 1200, mx: 'auto', width: '100%', overflow: 'hidden' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2.5, mb: 4 }}>
            <Box sx={{
              width: 56, height: 56, borderRadius: '16px', display: 'flex', alignItems: 'center', justifyContent: 'center',
              background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
              boxShadow: `0 8px 32px ${alpha(theme.palette.primary.main, 0.35)}`,
            }}>
              <SigmaIcon color="#fff" width={28} height={28} />
            </Box>
            <Typography variant="h4" sx={{
              fontWeight: 800, letterSpacing: '-0.03em',
              background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
              backgroundClip: 'text', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
            }}>
              Created Rules
            </Typography>
          </Box>
          <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: 3 }}>
            {[1, 2, 3].map((item) => (
              <Skeleton key={item} variant="rectangular" height={220} sx={{ borderRadius: '16px' }} />
            ))}
          </Box>
        </Box>
      </>
    );
  }

  return (
    <>
      <style>{keyframes}</style>

      <Box sx={{ p: { xs: 2, md: 4 }, maxWidth: 1200, mx: 'auto', width: '100%', overflow: 'hidden' }}>
        {/* ── Page Header ── */}
        <Box sx={{
          display: 'flex', alignItems: 'center', gap: 2.5, mb: 1,
          animation: 'rulesFadeSlideUp 0.6s ease-out',
        }}>
          <Box sx={{
            width: 56, height: 56, borderRadius: '16px', display: 'flex', alignItems: 'center', justifyContent: 'center',
            background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
            boxShadow: `0 8px 32px ${alpha(theme.palette.primary.main, 0.35)}`,
          }}>
            <SigmaIcon color="#fff" width={28} height={28} />
          </Box>
          <Box>
            <Typography variant="h4" sx={{
              fontWeight: 800, letterSpacing: '-0.03em',
              background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.secondary.main} 100%)`,
              backgroundClip: 'text', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
            }}>
              Created Rules
            </Typography>
            <Typography variant="body2" sx={{ color: 'text.secondary', mt: 0.5 }}>
              Manage and export your detection rules library
            </Typography>
          </Box>
        </Box>

        {/* ── Stats bar ── */}
        <Box sx={{
          display: 'flex', gap: 3, mb: 3, mt: 3, flexWrap: 'wrap',
          animation: 'rulesFadeSlideUp 0.6s ease-out 0.08s both',
        }}>
          {[
            { label: 'Total Rules', value: rules.length, color: theme.palette.primary.main },
            { label: 'High Confidence', value: rules.filter(r => r.confidence_score >= 0.8).length, color: theme.palette.success.main },
            { label: 'Products', value: Array.from(new Set(rules.map(r => r.product))).length, color: theme.palette.secondary.main },
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
              <Typography variant="h6" sx={{ fontWeight: 700, color: s.color, fontFamily: '"JetBrains Mono", monospace', mt: 0.3 }}>
                {s.value}
              </Typography>
            </Box>
          ))}
        </Box>

        {/* ── Error ── */}
        {error && (
          <Alert severity="error" sx={{ mb: 3, borderRadius: '12px' }}>{error}</Alert>
        )}

        {/* ── Search ── */}
        <Box sx={{ animation: 'rulesFadeSlideUp 0.6s ease-out 0.15s both', mb: 4 }}>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Search rules by title, description, or product..."
            value={searchTerm}
            onChange={(e) => dispatch(setSearchTerm(e.target.value))}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon sx={{ color: 'text.secondary' }} />
                </InputAdornment>
              ),
            }}
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: '14px',
                backgroundColor: alpha(theme.palette.background.paper, isDark ? 0.4 : 0.8),
                backdropFilter: 'blur(12px)',
                transition: 'all 0.3s ease',
                '& fieldset': { borderColor: alpha(theme.palette.divider, 0.15) },
                '&:hover fieldset': { borderColor: alpha(theme.palette.primary.main, 0.3) },
                '&.Mui-focused fieldset': { borderColor: theme.palette.primary.main, borderWidth: 1 },
              },
            }}
          />
        </Box>

        {/* ── Empty state ── */}
        {filteredRules.length === 0 ? (
          <Box sx={{
            textAlign: 'center', py: 10, borderRadius: '20px',
            border: `1px dashed ${alpha(theme.palette.divider, 0.3)}`,
            backdropFilter: 'blur(12px)',
            backgroundColor: alpha(theme.palette.background.paper, isDark ? 0.2 : 0.5),
            animation: 'rulesFadeSlideUp 0.6s ease-out 0.2s both',
          }}>
            <SecurityIcon sx={{ fontSize: 72, color: alpha(theme.palette.primary.main, 0.25), mb: 2 }} />
            <Typography variant="h6" sx={{ fontWeight: 700, mb: 1 }}>No Rules Found</Typography>
            <Typography variant="body2" color="text.secondary">
              {searchTerm ? 'Try adjusting your search terms' : 'Create your first rule in the Detection QA section'}
            </Typography>
          </Box>
        ) : (
          /* ── Cards grid ── */
          <Box sx={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(min(340px, 100%), 1fr))',
            gap: 3,
          }}>
            {filteredRules.map((rule, idx) => {
              const confColor = getConfidenceColor(rule.confidence_score);
              const confPct = Math.round(rule.confidence_score * 100);

              return (
                <Box
                  key={rule.id}
                  sx={{ animation: `rulesCardEnter 0.5s ease-out ${idx * 0.05}s both` }}
                >
                  <Box sx={{
                    height: '100%', display: 'flex', flexDirection: 'column',
                    borderRadius: '16px', overflow: 'hidden',
                    border: `1px solid ${alpha(theme.palette.divider, 0.12)}`,
                    backgroundColor: alpha(theme.palette.background.paper, isDark ? 0.45 : 0.8),
                    backdropFilter: 'blur(16px)',
                    transition: 'all 0.35s cubic-bezier(0.4, 0, 0.2, 1)',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      borderColor: alpha(theme.palette.primary.main, 0.3),
                      boxShadow: `0 12px 40px ${alpha(theme.palette.primary.main, 0.12)}`,
                    },
                  }}>
                    {/* gradient top bar */}
                    <Box sx={{
                      height: 3,
                      background: `linear-gradient(90deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
                    }} />

                    <Box sx={{ p: 3, flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
                      {/* header row */}
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2, gap: 1 }}>
                        <Typography variant="subtitle1" sx={{
                          fontWeight: 700, letterSpacing: '-0.01em', lineHeight: 1.3, flex: 1,
                        }}>
                          {rule.title}
                        </Typography>
                        <Chip label={rule.product.toUpperCase()} size="small" sx={{
                          fontFamily: '"JetBrains Mono", monospace', fontSize: '0.65rem',
                          fontWeight: 700, borderRadius: '8px', height: 24, flexShrink: 0,
                          backgroundColor: alpha(theme.palette.primary.main, 0.1),
                          color: theme.palette.primary.main,
                          border: `1px solid ${alpha(theme.palette.primary.main, 0.2)}`,
                        }} />
                      </Box>

                      {/* description */}
                      <Typography variant="body2" sx={{
                        color: 'text.secondary', mb: 2.5, lineHeight: 1.7,
                        display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden',
                      }}>
                        {rule.description}
                      </Typography>

                      {/* meta */}
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2, flexWrap: 'wrap' }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          <PersonIcon sx={{ fontSize: 14, color: 'text.secondary' }} />
                          <Typography variant="caption" color="text.secondary">{rule.author}</Typography>
                        </Box>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          <CalendarIcon sx={{ fontSize: 14, color: 'text.secondary' }} />
                          <Typography variant="caption" color="text.secondary">
                            {new Date(rule.date).toLocaleDateString()}
                          </Typography>
                        </Box>
                      </Box>

                      {/* confidence bar */}
                      <Box sx={{ mb: 2 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                          <Typography variant="caption" sx={{ fontWeight: 600, fontSize: '0.7rem' }}>Confidence</Typography>
                          <Typography variant="caption" sx={{
                            fontFamily: '"JetBrains Mono", monospace', fontWeight: 700,
                            color: confColor, fontSize: '0.7rem',
                          }}>
                            {getConfidenceLabel(rule.confidence_score)} ({confPct}%)
                          </Typography>
                        </Box>
                        <LinearProgress
                          variant="determinate"
                          value={confPct}
                          sx={{
                            height: 5, borderRadius: 3,
                            backgroundColor: alpha(confColor, 0.12),
                            '& .MuiLinearProgress-bar': {
                              borderRadius: 3,
                              background: `linear-gradient(90deg, ${confColor}, ${alpha(confColor, 0.7)})`,
                            },
                          }}
                        />
                      </Box>

                      {/* mitre techniques */}
                      {rule.mitre_techniques.length > 0 && (
                        <Box sx={{ mb: 2 }}>
                          <Typography variant="caption" sx={{
                            fontWeight: 600, fontSize: '0.65rem', textTransform: 'uppercase',
                            letterSpacing: '0.06em', color: 'text.secondary', display: 'block', mb: 0.8,
                          }}>
                            MITRE Techniques
                          </Typography>
                          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.6 }}>
                            {rule.mitre_techniques.slice(0, 3).map((t) => (
                              <Chip key={t.id} label={t.id} size="small" sx={{
                                fontFamily: '"JetBrains Mono", monospace', fontSize: '0.65rem',
                                borderRadius: '6px', height: 22,
                                backgroundColor: alpha(theme.palette.warning.main, 0.08),
                                border: `1px solid ${alpha(theme.palette.warning.main, 0.2)}`,
                                color: theme.palette.warning.main,
                              }} />
                            ))}
                            {rule.mitre_techniques.length > 3 && (
                              <Chip label={`+${rule.mitre_techniques.length - 3}`} size="small" sx={{
                                fontSize: '0.65rem', borderRadius: '6px', height: 22,
                                backgroundColor: alpha(theme.palette.divider, 0.08),
                              }} />
                            )}
                          </Box>
                        </Box>
                      )}

                      {/* bottom stats & actions */}
                      <Box sx={{ mt: 'auto', pt: 2 }}>
                        <Divider sx={{ mb: 2, borderColor: alpha(theme.palette.divider, 0.1) }} />
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <Box sx={{ display: 'flex', gap: 2 }}>
                            <Typography variant="caption" sx={{ color: 'text.secondary', fontFamily: '"JetBrains Mono", monospace', fontSize: '0.7rem' }}>
                              {rule.test_cases.length} tests
                            </Typography>
                            <Typography variant="caption" sx={{ color: 'text.secondary', fontFamily: '"JetBrains Mono", monospace', fontSize: '0.7rem' }}>
                              {rule.recommendations.length} recs
                            </Typography>
                          </Box>
                          <Box sx={{ display: 'flex', gap: 0.3 }}>
                            <Tooltip title="View Details">
                              <IconButton size="small" onClick={() => handleViewRule(rule)} sx={{
                                color: theme.palette.primary.main, transition: 'all 0.2s',
                                '&:hover': { backgroundColor: alpha(theme.palette.primary.main, 0.1) },
                              }}>
                                <ViewIcon sx={{ fontSize: 18 }} />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Download YAML">
                              <IconButton size="small" onClick={() => handleDownloadRule(rule)} sx={{
                                color: theme.palette.success.main, transition: 'all 0.2s',
                                '&:hover': { backgroundColor: alpha(theme.palette.success.main, 0.1) },
                              }}>
                                <DownloadIcon sx={{ fontSize: 18 }} />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Delete Rule">
                              <IconButton size="small" onClick={() => handleDeleteRule(rule.id)} sx={{
                                color: 'text.secondary', transition: 'all 0.2s',
                                '&:hover': { backgroundColor: alpha(theme.palette.error.main, 0.1), color: theme.palette.error.main },
                              }}>
                                <DeleteIcon sx={{ fontSize: 18 }} />
                              </IconButton>
                            </Tooltip>
                          </Box>
                        </Box>
                      </Box>
                    </Box>
                  </Box>
                </Box>
              );
            })}
          </Box>
        )}

        {/* ═══════════════ Rule Detail Dialog ═══════════════ */}
        <Dialog
          open={viewDialogOpen}
          onClose={() => setViewDialogOpen(false)}
          maxWidth="md"
          fullWidth
          PaperProps={{
            sx: {
              borderRadius: '20px',
              backgroundColor: alpha(theme.palette.background.paper, isDark ? 0.92 : 0.98),
              backdropFilter: 'blur(24px)',
              border: `1px solid ${alpha(theme.palette.divider, 0.12)}`,
              overflow: 'visible',
            },
          }}
        >
          {selectedRule && (
            <>
              {/* gradient top */}
              <Box sx={{
                height: 4,
                background: `linear-gradient(90deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
              }} />

              <DialogTitle sx={{ px: 4, pt: 3, pb: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Box sx={{
                      width: 44, height: 44, borderRadius: '14px', display: 'flex', alignItems: 'center', justifyContent: 'center',
                      background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
                    }}>
                      <SecurityIcon sx={{ color: '#fff', fontSize: 22 }} />
                    </Box>
                    <Box>
                      <Typography variant="h6" sx={{ fontWeight: 700, letterSpacing: '-0.01em' }}>
                        {selectedRule.title}
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1, mt: 0.5 }}>
                        <Chip label={selectedRule.product.toUpperCase()} size="small" sx={{
                          fontFamily: '"JetBrains Mono", monospace', fontSize: '0.65rem',
                          fontWeight: 700, borderRadius: '8px', height: 22,
                          backgroundColor: alpha(theme.palette.primary.main, 0.1),
                          color: theme.palette.primary.main,
                        }} />
                        <Chip
                          label={`${getConfidenceLabel(selectedRule.confidence_score)} (${Math.round(selectedRule.confidence_score * 100)}%)`}
                          size="small"
                          sx={{
                            fontWeight: 700, fontSize: '0.65rem', borderRadius: '8px', height: 22,
                            backgroundColor: alpha(getConfidenceColor(selectedRule.confidence_score), 0.1),
                            color: getConfidenceColor(selectedRule.confidence_score),
                          }}
                        />
                      </Box>
                    </Box>
                  </Box>
                  <IconButton onClick={() => setViewDialogOpen(false)} sx={{ color: 'text.secondary' }}>
                    <CloseIcon />
                  </IconButton>
                </Box>
              </DialogTitle>

              <DialogContent sx={{ px: 4, pb: 4 }}>
                {/* description */}
                <Typography variant="body2" sx={{ color: 'text.secondary', lineHeight: 1.8, mb: 4 }}>
                  {selectedRule.description}
                </Typography>

                {/* ── MITRE ATT&CK ── */}
                {selectedRule.mitre_techniques.length > 0 && (
                  <Box sx={{ mb: 4 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
                      <Box sx={{
                        width: 32, height: 32, borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center',
                        background: `linear-gradient(135deg, ${theme.palette.warning.main}, ${theme.palette.error.main})`,
                        color: '#fff',
                      }}>
                        <ShieldIcon sx={{ fontSize: 18 }} />
                      </Box>
                      <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>MITRE ATT&CK Techniques</Typography>
                    </Box>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                      {selectedRule.mitre_techniques.map((t) => (
                        <Box key={t.id} sx={{
                          p: 2, borderRadius: '12px',
                          border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
                          backgroundColor: alpha(theme.palette.warning.main, 0.03),
                        }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                            <Chip label={t.id} size="small" sx={{
                              fontFamily: '"JetBrains Mono", monospace', fontSize: '0.7rem',
                              fontWeight: 700, borderRadius: '6px', height: 22,
                              backgroundColor: alpha(theme.palette.warning.main, 0.1),
                              color: theme.palette.warning.main,
                            }} />
                            <Typography variant="body2" sx={{ fontWeight: 600 }}>{t.name}</Typography>
                          </Box>
                          {t.description && (
                            <Typography variant="caption" sx={{ color: 'text.secondary', lineHeight: 1.6 }}>
                              {t.description}
                            </Typography>
                          )}
                        </Box>
                      ))}
                    </Box>
                  </Box>
                )}

                {/* ── Test Cases ── */}
                {selectedRule.test_cases.length > 0 && (
                  <Box sx={{ mb: 4 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
                      <Box sx={{
                        width: 32, height: 32, borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center',
                        background: `linear-gradient(135deg, ${theme.palette.success.main}, #10b981)`,
                        color: '#fff',
                      }}>
                        <CheckIcon sx={{ fontSize: 18 }} />
                      </Box>
                      <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>Test Cases</Typography>
                    </Box>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                      {selectedRule.test_cases.map((tc, i) => (
                        <Box key={i} sx={{
                          p: 2, borderRadius: '12px',
                          border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
                          backgroundColor: alpha(theme.palette.success.main, 0.03),
                        }}>
                          <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>{tc.name}</Typography>
                          <Typography variant="caption" sx={{ color: 'text.secondary', display: 'block', mb: 0.5 }}>
                            {tc.description}
                          </Typography>
                          <Typography variant="caption" sx={{
                            color: theme.palette.primary.main, fontWeight: 600,
                            fontFamily: '"JetBrains Mono", monospace', fontSize: '0.7rem',
                          }}>
                            Expected: {tc.expected_result}
                          </Typography>
                        </Box>
                      ))}
                    </Box>
                  </Box>
                )}

                {/* ── Recommendations ── */}
                {selectedRule.recommendations.length > 0 && (
                  <Box sx={{ mb: 4 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
                      <Box sx={{
                        width: 32, height: 32, borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center',
                        background: `linear-gradient(135deg, ${theme.palette.info.main}, #6366f1)`,
                        color: '#fff',
                      }}>
                        <RecIcon sx={{ fontSize: 18 }} />
                      </Box>
                      <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>Recommendations</Typography>
                    </Box>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                      {selectedRule.recommendations.map((rec, i) => (
                        <Box key={i} sx={{ display: 'flex', alignItems: 'flex-start', gap: 1.5, pl: 1 }}>
                          <Box sx={{
                            width: 6, height: 6, borderRadius: '50%', mt: 0.9, flexShrink: 0,
                            background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
                          }} />
                          <Typography variant="body2" sx={{ color: 'text.secondary', lineHeight: 1.7 }}>
                            {rec}
                          </Typography>
                        </Box>
                      ))}
                    </Box>
                  </Box>
                )}

                {/* ── References ── */}
                {selectedRule.references.length > 0 && (
                  <Box sx={{ mb: 4 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
                      <Box sx={{
                        width: 32, height: 32, borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center',
                        background: `linear-gradient(135deg, #6366f1, ${theme.palette.secondary.main})`,
                        color: '#fff',
                      }}>
                        <RefIcon sx={{ fontSize: 18 }} />
                      </Box>
                      <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>References</Typography>
                    </Box>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                      {selectedRule.references.map((ref, i) => (
                        <Box key={i} sx={{
                          p: 2, borderRadius: '12px',
                          border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
                          transition: 'border-color 0.2s',
                          '&:hover': { borderColor: alpha(theme.palette.primary.main, 0.3) },
                        }}>
                          <Typography
                            component="a"
                            href={ref.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            variant="body2"
                            sx={{
                              color: theme.palette.primary.main, fontWeight: 600,
                              textDecoration: 'none', '&:hover': { textDecoration: 'underline' },
                            }}
                          >
                            {ref.title}
                          </Typography>
                          {ref.description && (
                            <Typography variant="caption" sx={{ color: 'text.secondary', display: 'block', mt: 0.5 }}>
                              {ref.description}
                            </Typography>
                          )}
                        </Box>
                      ))}
                    </Box>
                  </Box>
                )}

                {/* ── Rule Content ── */}
                <Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
                    <Box sx={{
                      width: 32, height: 32, borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center',
                      background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
                      color: '#fff',
                    }}>
                      <DescriptionIcon sx={{ fontSize: 18 }} />
                    </Box>
                    <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>Rule Content</Typography>
                  </Box>
                  <Box component="pre" sx={codeBlockSx}>
                    {yaml.dump(selectedRule.rule_content)}
                  </Box>
                </Box>
              </DialogContent>

              <Divider sx={{ borderColor: alpha(theme.palette.divider, 0.1) }} />

              <DialogActions sx={{ px: 4, py: 2.5, gap: 1.5 }}>
                <Button
                  onClick={() => handleDownloadRule(selectedRule)}
                  startIcon={<DownloadIcon />}
                  variant="contained"
                  sx={{
                    borderRadius: '12px', textTransform: 'none', fontWeight: 600, px: 3,
                    background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
                    boxShadow: `0 4px 16px ${alpha(theme.palette.primary.main, 0.3)}`,
                    '&:hover': { boxShadow: `0 6px 24px ${alpha(theme.palette.primary.main, 0.45)}` },
                  }}
                >
                  Download YAML
                </Button>
                <Button
                  onClick={() => setViewDialogOpen(false)}
                  sx={{
                    borderRadius: '12px', textTransform: 'none', fontWeight: 600, px: 3,
                    color: 'text.secondary',
                    '&:hover': { backgroundColor: alpha(theme.palette.divider, 0.08) },
                  }}
                >
                  Close
                </Button>
              </DialogActions>
            </>
          )}
        </Dialog>
      </Box>
    </>
  );
};

export default CreatedRules;
