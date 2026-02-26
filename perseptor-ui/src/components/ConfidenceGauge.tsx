import React from 'react';
import {
  Box,
  Typography,
  useTheme,
  Chip,
  LinearProgress,
  Paper,
  Tooltip,
  Divider,
} from '@mui/material';
import { alpha } from '@mui/material/styles';
import VerifiedIcon from '@mui/icons-material/Verified';
import WarningIcon from '@mui/icons-material/Warning';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import TipsAndUpdatesIcon from '@mui/icons-material/TipsAndUpdates';

interface ComponentScores {
  [key: string]: number;
}

interface Maturity {
  level: string;
  label: string;
  maturity_score: number;
  criteria_met: number;
  criteria_total: number;
  recommendations: string[];
}

interface ConfidenceGaugeProps {
  overallScore: number;
  componentScores?: ComponentScores;
  maturity?: Maturity;
  explanations?: Record<string, string>;
  weights?: Record<string, number>;
}

const COMPONENT_LABELS: Record<string, string> = {
  complexity: 'Complexity',
  coverage: 'Coverage',
  specificity: 'Specificity',
  mitre_alignment: 'MITRE Alignment',
  test_case_coverage: 'Test Coverage',
  rule_quality: 'Rule Quality',
  false_positive_risk: 'FP Risk',
};

const COMPONENT_ICONS: Record<string, string> = {
  complexity: '\u2699\ufe0f',
  coverage: '\ud83d\udee1\ufe0f',
  specificity: '\ud83c\udfaf',
  mitre_alignment: '\ud83d\udda7',
  test_case_coverage: '\ud83e\uddea',
  rule_quality: '\ud83d\udcdd',
  false_positive_risk: '\u26a0\ufe0f',
};

const ConfidenceGauge: React.FC<ConfidenceGaugeProps> = ({
  overallScore,
  componentScores,
  maturity,
  explanations,
  weights,
}) => {
  const theme = useTheme();

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return theme.palette.success.main;
    if (score >= 0.6) return theme.palette.warning.main;
    return theme.palette.error.main;
  };

  const getScoreIcon = (score: number) => {
    if (score >= 0.8) return <VerifiedIcon sx={{ color: theme.palette.success.main, fontSize: 28 }} />;
    if (score >= 0.6) return <WarningIcon sx={{ color: theme.palette.warning.main, fontSize: 28 }} />;
    return <ErrorOutlineIcon sx={{ color: theme.palette.error.main, fontSize: 28 }} />;
  };

  const getMaturityColor = (level: string) => {
    switch (level) {
      case 'production': return 'success';
      case 'testing': return 'info';
      case 'experimental': return 'warning';
      default: return 'error';
    }
  };

  const getInsight = (score: number) => {
    if (score >= 0.8) return {
      text: 'This rule is production-ready with strong detection logic',
      color: theme.palette.success.main,
      bg: alpha(theme.palette.success.main, 0.08),
      border: alpha(theme.palette.success.main, 0.2),
    };
    if (score >= 0.6) return {
      text: 'Good foundation but some areas need improvement',
      color: theme.palette.warning.main,
      bg: alpha(theme.palette.warning.main, 0.08),
      border: alpha(theme.palette.warning.main, 0.2),
    };
    return {
      text: 'Significant issues detected \u2014 review recommendations below',
      color: theme.palette.error.main,
      bg: alpha(theme.palette.error.main, 0.08),
      border: alpha(theme.palette.error.main, 0.2),
    };
  };

  // Parse explanation pipe-separated entries into individual points
  const parseExplanation = (raw: string): string[] => {
    if (!raw) return [];
    return raw.split(' | ').filter(Boolean);
  };

  const scorePercent = Math.round(overallScore * 100);
  const scoreColor = getScoreColor(overallScore);
  const insight = getInsight(overallScore);

  return (
    <Paper
      sx={{
        p: 2.5,
        background: `linear-gradient(135deg, ${alpha(theme.palette.background.paper, 0.95)}, ${alpha(theme.palette.background.default, 0.9)})`,
        border: `1px solid ${alpha(theme.palette.divider, 0.15)}`,
        borderRadius: '14px',
        backdropFilter: 'blur(12px)',
      }}
    >
      {/* ── Overall Score ── */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
        {getScoreIcon(overallScore)}
        <Box sx={{ flex: 1, minWidth: 0 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="subtitle2" fontWeight="bold">
              Confidence Score
            </Typography>
            <Typography
              variant="h5"
              fontWeight="bold"
              sx={{ color: scoreColor, fontFamily: '"JetBrains Mono", monospace' }}
            >
              {scorePercent}%
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={scorePercent}
            sx={{
              height: 8,
              borderRadius: 4,
              backgroundColor: alpha(theme.palette.action.disabledBackground, 0.5),
              '& .MuiLinearProgress-bar': {
                backgroundColor: scoreColor,
                borderRadius: 4,
                transition: 'transform 0.8s ease',
              },
            }}
          />
        </Box>
      </Box>

      {/* ── Insight Summary ── */}
      <Box
        sx={{
          p: 1.5,
          mb: 2,
          borderRadius: '10px',
          backgroundColor: insight.bg,
          border: `1px solid ${insight.border}`,
          display: 'flex',
          alignItems: 'center',
          gap: 1,
        }}
      >
        <CheckCircleOutlineIcon sx={{ color: insight.color, fontSize: 18, flexShrink: 0 }} />
        <Typography variant="body2" sx={{ color: insight.color, fontWeight: 600, fontSize: '0.8rem' }}>
          {insight.text}
        </Typography>
      </Box>

      {/* ── Maturity Level ── */}
      {maturity && (
        <Box sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
          <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600 }}>
            Maturity:
          </Typography>
          <Chip
            label={maturity.label}
            size="small"
            color={getMaturityColor(maturity.level) as any}
            sx={{ fontWeight: 'bold', fontSize: '0.72rem' }}
          />
          <Typography variant="caption" color="text.secondary">
            ({maturity.criteria_met}/{maturity.criteria_total} criteria)
          </Typography>
        </Box>
      )}

      <Divider sx={{ mb: 2, opacity: 0.5 }} />

      {/* ── Component Scores with Explanations ── */}
      {componentScores && (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
          <Typography variant="caption" sx={{ fontWeight: 700, color: 'text.secondary', textTransform: 'uppercase', letterSpacing: '0.05em', fontSize: '0.68rem' }}>
            Score Breakdown
          </Typography>

          {Object.entries(componentScores).map(([key, score]) => {
            const label = COMPONENT_LABELS[key] || key;
            const icon = COMPONENT_ICONS[key] || '\ud83d\udcca';
            const color = getScoreColor(score);
            const pct = Math.round(score * 100);
            const weight = weights?.[key];
            const rawExplanation = explanations?.[key] || '';
            const points = parseExplanation(rawExplanation);

            return (
              <Box key={key}>
                {/* Score bar row */}
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Typography sx={{ fontSize: '0.85rem', width: 20, textAlign: 'center', flexShrink: 0 }}>
                    {icon}
                  </Typography>
                  <Tooltip title={`${label}: ${pct}%${weight ? ` (weight: ${Math.round(weight * 100)}%)` : ''}`}>
                    <Typography
                      variant="caption"
                      sx={{
                        width: 95,
                        color: theme.palette.text.secondary,
                        fontSize: '0.72rem',
                        fontWeight: 600,
                        flexShrink: 0,
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                      }}
                    >
                      {label}
                    </Typography>
                  </Tooltip>
                  <LinearProgress
                    variant="determinate"
                    value={pct}
                    sx={{
                      flex: 1,
                      height: 6,
                      borderRadius: 3,
                      minWidth: 0,
                      backgroundColor: alpha(theme.palette.action.disabledBackground, 0.4),
                      '& .MuiLinearProgress-bar': {
                        backgroundColor: color,
                        borderRadius: 3,
                        transition: 'transform 0.6s ease',
                      },
                    }}
                  />
                  <Typography
                    variant="caption"
                    sx={{
                      width: 36,
                      textAlign: 'right',
                      color: color,
                      fontSize: '0.72rem',
                      fontWeight: 700,
                      fontFamily: '"JetBrains Mono", monospace',
                      flexShrink: 0,
                    }}
                  >
                    {pct}%
                  </Typography>
                  {weight != null && (
                    <Chip
                      label={`${Math.round(weight * 100)}%`}
                      size="small"
                      sx={{
                        height: 18,
                        fontSize: '0.6rem',
                        fontWeight: 700,
                        fontFamily: '"JetBrains Mono", monospace',
                        backgroundColor: alpha(theme.palette.primary.main, 0.08),
                        color: alpha(theme.palette.text.secondary, 0.7),
                        '& .MuiChip-label': { px: 0.6 },
                        flexShrink: 0,
                      }}
                    />
                  )}
                </Box>

                {/* Explanation points */}
                {points.length > 0 && (
                  <Box sx={{ pl: '28px', mt: 0.3 }}>
                    {points.map((point, idx) => (
                      <Typography
                        key={idx}
                        variant="caption"
                        sx={{
                          display: 'block',
                          color: alpha(theme.palette.text.secondary, 0.75),
                          fontSize: '0.68rem',
                          lineHeight: 1.5,
                          pl: 0.5,
                        }}
                      >
                        {point}
                      </Typography>
                    ))}
                  </Box>
                )}
              </Box>
            );
          })}
        </Box>
      )}

      {/* ── Improvement Recommendations ── */}
      {maturity?.recommendations && maturity.recommendations.length > 0 && (
        <Box sx={{ mt: 2, pt: 2, borderTop: `1px solid ${alpha(theme.palette.divider, 0.15)}` }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 1 }}>
            <TipsAndUpdatesIcon sx={{ fontSize: 16, color: theme.palette.warning.main }} />
            <Typography variant="caption" sx={{ fontWeight: 700, color: theme.palette.warning.main, fontSize: '0.72rem' }}>
              Recommendations
            </Typography>
          </Box>
          {maturity.recommendations.slice(0, 5).map((rec, idx) => (
            <Box key={idx} sx={{ display: 'flex', alignItems: 'flex-start', gap: 0.8, mb: 0.5, pl: 0.5 }}>
              <Box
                sx={{
                  width: 5,
                  height: 5,
                  borderRadius: '50%',
                  backgroundColor: theme.palette.warning.main,
                  mt: '6px',
                  flexShrink: 0,
                }}
              />
              <Typography variant="caption" sx={{ color: alpha(theme.palette.text.secondary, 0.85), fontSize: '0.72rem', lineHeight: 1.5 }}>
                {rec}
              </Typography>
            </Box>
          ))}
        </Box>
      )}
    </Paper>
  );
};

export default ConfidenceGauge;
