/**
 * PERSEPTOR v2.0 - Detection QA Page
 * Premium 2026 cybersecurity design with glassmorphic cards and smooth animations.
 */

import React, { useState } from 'react';
import {
  Typography,
  TextField,
  Button,
  Box,
  CircularProgress,
  Alert,
  Paper,
  Card,
  CardContent,
  Fade,
  Zoom,
  Divider,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  LinearProgress,
  useTheme,
} from '@mui/material';
import { alpha } from '@mui/material/styles';
import TrackChangesIcon from '@mui/icons-material/TrackChanges';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import CodeIcon from '@mui/icons-material/Code';
import { useAppDispatch, useAppSelector } from '../store';
import {
  setGenerationPrompt,
  generateRule,
  clearGenerationError,
} from '../store/slices/rulesSlice';
import ConfidenceGauge from '../components/ConfidenceGauge';

const QA: React.FC = () => {
  const dispatch = useAppDispatch();
  const { generationPrompt: prompt, generating: loading, generationError: error, generatedRule } =
    useAppSelector((state) => state.rules);
  const { isConnected, apiKey } = useAppSelector((state) => state.settings);
  const [showAnimation, setShowAnimation] = useState(false);
  const theme = useTheme();

  React.useEffect(() => {
    setShowAnimation(true);
  }, []);

  const handleGenerateRule = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt) return;
    if (!isConnected && !apiKey) return;
    dispatch(clearGenerationError());
    dispatch(generateRule(prompt));
  };

  const renderRuleContent = (rule: any) => {
    return Object.entries(rule).map(([key, value]) => {
      if (typeof value === 'object' && value !== null) {
        return (
          <Box key={key} sx={{ mb: 2 }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 700, color: theme.palette.primary.main, mb: 0.5, letterSpacing: '0.02em' }}>
              {key.replace(/_/g, ' ').toUpperCase()}
            </Typography>
            <Box
              component="pre"
              sx={{
                whiteSpace: 'pre-wrap',
                fontFamily: '"JetBrains Mono", monospace',
                fontSize: '0.8rem',
                lineHeight: 1.7,
                backgroundColor: alpha(theme.palette.background.default, 0.8),
                p: 2.5,
                borderRadius: '12px',
                border: `1px solid ${alpha(theme.palette.divider, 0.3)}`,
                color: theme.palette.text.secondary,
                overflow: 'auto',
              }}
            >
              {JSON.stringify(value, null, 2)}
            </Box>
          </Box>
        );
      }
      return (
        <Box key={key} sx={{ mb: 2 }}>
          <Typography variant="subtitle2" sx={{ fontWeight: 700, color: theme.palette.primary.main, mb: 0.5, letterSpacing: '0.02em' }}>
            {key.replace(/_/g, ' ').toUpperCase()}
          </Typography>
          <Typography variant="body2" sx={{ color: theme.palette.text.secondary, lineHeight: 1.7 }}>{String(value)}</Typography>
        </Box>
      );
    });
  };

  return (
    <Box sx={{ p: { xs: 2, md: 4 }, maxWidth: 1400, mx: 'auto', overflow: 'hidden' }}>
      {/* Loading Overlay */}
      {loading && (
        <Fade in timeout={500}>
          <Box
            sx={{
              position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
              background: `radial-gradient(ellipse at center, ${alpha('#0a0e1a', 0.95)} 0%, ${alpha('#000', 0.98)} 100%)`,
              backdropFilter: 'blur(12px)',
              zIndex: 9999, display: 'flex', flexDirection: 'column',
              alignItems: 'center', justifyContent: 'center', gap: 4,
            }}
          >
            <Box sx={{ position: 'relative', width: 180, height: 180, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <CircularProgress
                size={180}
                thickness={1.5}
                sx={{
                  color: theme.palette.primary.main,
                  position: 'absolute',
                  filter: `drop-shadow(0 0 12px ${theme.palette.primary.main})`,
                }}
              />
              <TrackChangesIcon
                sx={{
                  fontSize: 64,
                  color: theme.palette.primary.main,
                  animation: 'qaFloat 3s ease-in-out infinite',
                  '@keyframes qaFloat': {
                    '0%, 100%': { transform: 'translateY(0) rotate(0deg)' },
                    '50%': { transform: 'translateY(-15px) rotate(180deg)' },
                  },
                }}
              />
            </Box>
            <Typography
              variant="h4"
              sx={{
                color: 'white',
                fontWeight: 700,
                textShadow: `0 0 30px ${alpha(theme.palette.primary.main, 0.5)}`,
                letterSpacing: '-0.02em',
              }}
            >
              Generating Rule
            </Typography>
            <Box sx={{ width: '100%', maxWidth: 500 }}>
              <LinearProgress
                sx={{
                  height: 3,
                  borderRadius: 2,
                  backgroundColor: alpha('#fff', 0.06),
                  '& .MuiLinearProgress-bar': {
                    background: `linear-gradient(90deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
                  },
                }}
              />
            </Box>
            <Typography variant="body2" sx={{ color: alpha('#fff', 0.5), letterSpacing: '0.02em' }}>
              Analyzing rule quality, checking coverage, generating insights...
            </Typography>
          </Box>
        </Fade>
      )}

      {/* Page Header */}
      <Fade in={showAnimation} timeout={800}>
        <Box sx={{ mb: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
            <Box
              sx={{
                width: 52,
                height: 52,
                borderRadius: '14px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
                boxShadow: `0 4px 20px ${alpha(theme.palette.primary.main, 0.3)}`,
              }}
            >
              <TrackChangesIcon sx={{ color: '#fff', fontSize: 28 }} />
            </Box>
            <Box>
              <Typography
                variant="h3"
                sx={{
                  fontWeight: 800,
                  letterSpacing: '-0.02em',
                  background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                }}
              >
                Detection QA
              </Typography>
              <Typography variant="body2" sx={{ color: alpha(theme.palette.text.secondary, 0.7), letterSpacing: '0.02em' }}>
                AI-Powered Rule Quality Assurance
              </Typography>
            </Box>
          </Box>
        </Box>
      </Fade>

      {!isConnected && !apiKey && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          Please go to Settings to configure your AI provider and API key before generating rules.
        </Alert>
      )}

      <Box sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, gap: 3 }}>
        <Box sx={{ flex: { xs: '1 1 100%', md: '2 1 66%' } }}>
          {/* Rule Generation Card */}
          <Zoom in={showAnimation} timeout={800} style={{ transitionDelay: '200ms' }}>
            <Paper
              elevation={0}
              sx={{
                p: 3,
                mb: 3,
                position: 'relative',
                overflow: 'hidden',
                borderRadius: '16px',
                '&::before': {
                  content: '""',
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  right: 0,
                  height: 3,
                  background: `linear-gradient(90deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
                },
              }}
            >
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 700, display: 'flex', alignItems: 'center', gap: 1 }}>
                <AutoAwesomeIcon sx={{ color: theme.palette.primary.main }} />
                Rule Generation
              </Typography>
              <Box component="form" onSubmit={handleGenerateRule} sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <TextField
                  fullWidth
                  label="Describe the detection rule you need"
                  placeholder="Create a sigma rule to detect possible DNS Tunneling behavior"
                  value={prompt}
                  onChange={(e) => dispatch(setGenerationPrompt(e.target.value))}
                  error={!!error}
                  helperText={error}
                  multiline
                  rows={4}
                />
                <Button
                  type="submit"
                  variant="contained"
                  disabled={loading || (!isConnected && !apiKey)}
                  startIcon={loading ? <CircularProgress size={20} /> : <AutoAwesomeIcon />}
                  sx={{
                    height: 52,
                    fontSize: '0.9rem',
                    background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.primary.dark})`,
                    '&:hover': {
                      background: `linear-gradient(135deg, ${theme.palette.primary.light}, ${theme.palette.primary.main})`,
                      transform: 'translateY(-1px)',
                      boxShadow: `0 6px 20px ${alpha(theme.palette.primary.main, 0.4)}`,
                    },
                  }}
                >
                  {loading ? 'Generating...' : 'Generate Rule'}
                </Button>
              </Box>
            </Paper>
          </Zoom>

          {/* Generated Rule Results */}
          {generatedRule && (
            <Fade in={!!generatedRule} timeout={500}>
              <Box>
                <Card elevation={0} sx={{ mb: 3, borderRadius: '16px' }}>
                  <CardContent sx={{ p: 3 }}>
                    <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1, color: theme.palette.primary.main, fontWeight: 700 }}>
                      <CodeIcon /> Generated Rule
                    </Typography>
                    <Divider sx={{ mb: 2 }} />
                    {renderRuleContent(generatedRule.rule)}

                    {generatedRule.explanation && (
                      <Box sx={{ mt: 3 }}>
                        <Typography variant="subtitle1" sx={{ color: theme.palette.primary.main, fontWeight: 700, mb: 1 }}>Explanation</Typography>
                        <Typography variant="body2" sx={{ color: theme.palette.text.secondary, lineHeight: 1.8 }}>{generatedRule.explanation}</Typography>
                      </Box>
                    )}

                    {generatedRule.test_cases && generatedRule.test_cases.length > 0 && (
                      <Box sx={{ mt: 3 }}>
                        <Typography variant="subtitle1" sx={{ color: theme.palette.primary.main, fontWeight: 700, mb: 1 }}>Test Cases</Typography>
                        {generatedRule.test_cases.map((testCase, index) => (
                          <Accordion key={index} elevation={0} sx={{ mb: 1 }}>
                            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                              <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>{testCase.name}</Typography>
                            </AccordionSummary>
                            <AccordionDetails>
                              <Typography variant="body2" sx={{ color: theme.palette.text.secondary, mb: 1 }}>{testCase.description}</Typography>
                              <Chip label={`Expected: ${testCase.expected_result}`} size="small" color="primary" variant="outlined" />
                            </AccordionDetails>
                          </Accordion>
                        ))}
                      </Box>
                    )}

                    {generatedRule.mitre_techniques && generatedRule.mitre_techniques.length > 0 && (
                      <Box sx={{ mt: 3 }}>
                        <Typography variant="subtitle1" sx={{ color: theme.palette.primary.main, fontWeight: 700, mb: 1 }}>MITRE ATT&CK Techniques</Typography>
                        {generatedRule.mitre_techniques.map((technique, index) => (
                          <Accordion key={index} elevation={0} sx={{ mb: 1 }}>
                            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <Chip label={technique.id} size="small" sx={{ fontFamily: '"JetBrains Mono", monospace', fontWeight: 700, fontSize: '0.7rem' }} />
                                <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>{technique.name}</Typography>
                              </Box>
                            </AccordionSummary>
                            <AccordionDetails>
                              <Typography variant="body2" sx={{ color: theme.palette.text.secondary }}>{technique.description}</Typography>
                            </AccordionDetails>
                          </Accordion>
                        ))}
                      </Box>
                    )}

                    {generatedRule.confidence_score != null && (
                      <Box sx={{ mt: 3 }}>
                        <Typography variant="subtitle1" sx={{ color: theme.palette.primary.main, fontWeight: 700, mb: 1 }}>
                          Quality Assessment
                        </Typography>
                        <ConfidenceGauge
                          overallScore={generatedRule.confidence_score}
                          componentScores={generatedRule.component_scores}
                          maturity={generatedRule.maturity}
                          explanations={generatedRule.explanations}
                          weights={generatedRule.weights}
                        />
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Box>
            </Fade>
          )}
        </Box>

        {/* Side Panel */}
        <Box sx={{ flex: { xs: '1 1 100%', md: '1 1 33%' } }}>
          <Zoom in={showAnimation} timeout={800} style={{ transitionDelay: '400ms' }}>
            <Card elevation={0} sx={{ borderRadius: '16px' }}>
              <CardContent sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1, color: theme.palette.primary.main, fontWeight: 700 }}>
                  <TrackChangesIcon /> About Detection QA
                </Typography>
                <Divider sx={{ mb: 2 }} />
                <Typography variant="body2" paragraph sx={{ color: theme.palette.text.secondary, lineHeight: 1.8 }}>
                  Detection QA is an advanced tool that helps you generate and analyze security rules using AI.
                </Typography>
                <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1 }}>
                  Features
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  {[
                    'Multi-provider AI rule generation',
                    'Rule quality analysis',
                    'MITRE ATT&CK mapping',
                    'False positive detection',
                    'Confidence scoring with breakdown',
                  ].map((feat) => (
                    <Box key={feat} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Box sx={{ width: 5, height: 5, borderRadius: '50%', backgroundColor: theme.palette.primary.main, flexShrink: 0 }} />
                      <Typography variant="body2" sx={{ color: theme.palette.text.secondary, fontSize: '0.82rem' }}>
                        {feat}
                      </Typography>
                    </Box>
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Zoom>
        </Box>
      </Box>
    </Box>
  );
};

export default QA;
