import React from 'react';
import {
  Box,
  Typography,
  Chip,
  Paper,
  useTheme,
  LinearProgress,
  Tooltip,
} from '@mui/material';
import GpsFixedIcon from '@mui/icons-material/GpsFixed';

interface MitreTechnique {
  technique_id: string;
  technique_name: string;
  tactic: string;
  confidence: number;
  source: string;
  keyword_hits?: number;
  description?: string;
}

interface TacticSummary {
  [tactic: string]: number;
}

interface MitreNavigatorProps {
  techniques: MitreTechnique[];
  tacticSummary: TacticSummary;
  tags: string[];
}

const TACTIC_ORDER = [
  'initial_access',
  'execution',
  'persistence',
  'privilege_escalation',
  'defense_evasion',
  'credential_access',
  'discovery',
  'lateral_movement',
  'collection',
  'command_and_control',
  'exfiltration',
  'impact',
];

const TACTIC_LABELS: Record<string, string> = {
  initial_access: 'Initial Access',
  execution: 'Execution',
  persistence: 'Persistence',
  privilege_escalation: 'Privilege Escalation',
  defense_evasion: 'Defense Evasion',
  credential_access: 'Credential Access',
  discovery: 'Discovery',
  lateral_movement: 'Lateral Movement',
  collection: 'Collection',
  command_and_control: 'Command & Control',
  exfiltration: 'Exfiltration',
  impact: 'Impact',
};

const TACTIC_COLORS: Record<string, string> = {
  initial_access: '#e74c3c',
  execution: '#e67e22',
  persistence: '#f1c40f',
  privilege_escalation: '#2ecc71',
  defense_evasion: '#1abc9c',
  credential_access: '#3498db',
  discovery: '#9b59b6',
  lateral_movement: '#e91e63',
  collection: '#ff9800',
  command_and_control: '#795548',
  exfiltration: '#607d8b',
  impact: '#f44336',
};

const MitreNavigator: React.FC<MitreNavigatorProps> = ({
  techniques,
  tacticSummary,
  tags,
}) => {
  const theme = useTheme();

  const techniquesByTactic: Record<string, MitreTechnique[]> = {};
  techniques.forEach((t) => {
    if (!techniquesByTactic[t.tactic]) {
      techniquesByTactic[t.tactic] = [];
    }
    techniquesByTactic[t.tactic].push(t);
  });

  const activeTactics = TACTIC_ORDER.filter((t) => tacticSummary[t]);

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return theme.palette.success.main;
    if (confidence >= 0.5) return theme.palette.warning.main;
    return theme.palette.error.main;
  };

  const alpha = (color: string, opacity: number) => {
    // Simple alpha helper for hex colors
    const hex = Math.round(opacity * 255).toString(16).padStart(2, '0');
    return `${color}${hex}`;
  };

  return (
    <Paper
      sx={{
        p: 3,
        background: `linear-gradient(135deg, ${theme.palette.background.paper}, ${theme.palette.background.default})`,
        border: `1px solid ${theme.palette.divider}`,
        borderRadius: 2,
        overflow: 'hidden',
        maxWidth: '100%',
      }}
    >
      <Typography
        variant="h6"
        gutterBottom
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 1,
          color: theme.palette.primary.main,
          fontWeight: 'bold',
        }}
      >
        <GpsFixedIcon /> MITRE ATT&CK Mapping
      </Typography>

      {/* Kill Chain Overview */}
      <Box sx={{ mb: 3, overflowX: 'auto' }}>
        <Typography variant="subtitle2" color="text.secondary" gutterBottom>
          Kill Chain Coverage ({activeTactics.length}/{TACTIC_ORDER.length} tactics)
        </Typography>
        <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', minWidth: 0 }}>
          {TACTIC_ORDER.map((tactic) => {
            const isActive = !!tacticSummary[tactic];
            const count = tacticSummary[tactic] || 0;
            return (
              <Tooltip
                key={tactic}
                title={`${TACTIC_LABELS[tactic]}: ${count} technique${count !== 1 ? 's' : ''}`}
              >
                <Box
                  sx={{
                    flex: '1 1 auto',
                    minWidth: 55,
                    maxWidth: 100,
                    height: 32,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    borderRadius: 1,
                    backgroundColor: isActive
                      ? TACTIC_COLORS[tactic] + '30'
                      : theme.palette.action.disabledBackground,
                    border: `2px solid ${isActive ? TACTIC_COLORS[tactic] : 'transparent'}`,
                    cursor: 'default',
                    transition: 'all 0.2s',
                  }}
                >
                  <Typography
                    variant="caption"
                    sx={{
                      fontSize: '0.58rem',
                      fontWeight: isActive ? 'bold' : 'normal',
                      color: isActive ? TACTIC_COLORS[tactic] : theme.palette.text.disabled,
                      textAlign: 'center',
                      lineHeight: 1.1,
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap',
                      px: 0.3,
                    }}
                  >
                    {TACTIC_LABELS[tactic]}
                    {count > 0 && ` (${count})`}
                  </Typography>
                </Box>
              </Tooltip>
            );
          })}
        </Box>
      </Box>

      {/* Techniques by Tactic */}
      {activeTactics.map((tactic) => (
        <Box key={tactic} sx={{ mb: 2 }}>
          <Typography
            variant="subtitle2"
            sx={{
              color: TACTIC_COLORS[tactic],
              fontWeight: 'bold',
              mb: 1,
              borderLeft: `3px solid ${TACTIC_COLORS[tactic]}`,
              pl: 1,
            }}
          >
            {TACTIC_LABELS[tactic]}
          </Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            {(techniquesByTactic[tactic] || []).map((tech) => (
              <Box
                key={tech.technique_id}
                sx={{
                  p: 1.5,
                  borderRadius: 1.5,
                  border: `1px solid ${theme.palette.divider}`,
                  backgroundColor: theme.palette.background.paper,
                  transition: 'all 0.2s ease',
                  '&:hover': {
                    borderColor: TACTIC_COLORS[tactic] + '60',
                    boxShadow: `0 2px 8px ${TACTIC_COLORS[tactic]}15`,
                  },
                }}
              >
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5, flexWrap: 'wrap', gap: 0.5 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.8 }}>
                    <Chip
                      component="a"
                      href={`https://attack.mitre.org/techniques/${tech.technique_id.replace('.', '/')}/`}
                      target="_blank"
                      rel="noopener noreferrer"
                      label={tech.technique_id}
                      size="small"
                      clickable
                      sx={{
                        fontFamily: '"JetBrains Mono", monospace',
                        fontWeight: 'bold',
                        fontSize: '0.72rem',
                        backgroundColor: TACTIC_COLORS[tactic] + '20',
                        color: TACTIC_COLORS[tactic],
                        border: `1px solid ${TACTIC_COLORS[tactic]}40`,
                        textDecoration: 'none',
                        '&:hover': { backgroundColor: TACTIC_COLORS[tactic] + '35' },
                      }}
                    />
                    <Typography variant="body2" sx={{ fontWeight: 600, fontFamily: '"Inter", sans-serif' }}>
                      {tech.technique_name}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                    <Chip
                      label={tech.source === 'ai_extracted' ? 'AI' : 'Keyword'}
                      size="small"
                      variant="outlined"
                      sx={{
                        fontSize: '0.62rem',
                        height: 20,
                        borderColor: tech.source === 'ai_extracted' ? '#8b5cf6' : '#f59e0b',
                        color: tech.source === 'ai_extracted' ? '#8b5cf6' : '#f59e0b',
                      }}
                    />
                    <Typography
                      variant="caption"
                      sx={{
                        color: getConfidenceColor(tech.confidence),
                        fontWeight: 'bold',
                        fontFamily: '"JetBrains Mono", monospace',
                        fontSize: '0.72rem',
                      }}
                    >
                      {Math.round(tech.confidence * 100)}%
                    </Typography>
                  </Box>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: tech.description ? 0.8 : 0 }}>
                  <LinearProgress
                    variant="determinate"
                    value={tech.confidence * 100}
                    sx={{
                      flex: 1,
                      height: 3,
                      borderRadius: 2,
                      backgroundColor: theme.palette.action.disabledBackground,
                      '& .MuiLinearProgress-bar': {
                        backgroundColor: getConfidenceColor(tech.confidence),
                        borderRadius: 2,
                      },
                    }}
                  />
                </Box>
                {/* Technique Description / Explanation */}
                {tech.description && (
                  <Typography
                    variant="caption"
                    sx={{
                      display: 'block',
                      color: theme.palette.text.secondary,
                      fontFamily: '"Inter", sans-serif',
                      fontSize: '0.75rem',
                      lineHeight: 1.5,
                      mt: 0.5,
                      pl: 0.5,
                      borderLeft: `2px solid ${TACTIC_COLORS[tactic]}30`,
                      fontStyle: 'italic',
                    }}
                  >
                    {tech.description}
                  </Typography>
                )}
              </Box>
            ))}
          </Box>
        </Box>
      ))}

      {techniques.length === 0 && (
        <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 2 }}>
          No MITRE ATT&CK techniques identified.
        </Typography>
      )}
    </Paper>
  );
};

export default MitreNavigator;
