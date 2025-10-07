import React, { useState } from 'react';
import {
  Container,
  Typography,
  TextField,
  Button,
  Box,
  CircularProgress,
  Alert,
  Paper,
  useTheme,
  Card,
  CardContent,
  Fade,
  Zoom,
  Avatar,
  IconButton,
  Tooltip,
  Divider,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  LinearProgress,
} from '@mui/material';
import TrackChangesIcon from '@mui/icons-material/TrackChanges';
import SearchIcon from '@mui/icons-material/Search';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import CodeIcon from '@mui/icons-material/Code';
import { generateRule } from '../services/api';

interface RuleResponse {
  rule: {
    title: string;
    description: string;
    detection: any;
    fields: string[];
    level: string;
    [key: string]: any;
  };
  explanation: string;
  test_cases: Array<{
    name: string;
    description: string;
    expected_result: string;
  }>;
  mitre_techniques: Array<{
    id: string;
    name: string;
    description: string;
  }>;
  recommendations: string[];
  references: Array<{
    title: string;
    url: string;
    description: string;
  }>;
  confidence_score: number;
  component_scores: {
    [key: string]: number;
  };
}

const QA: React.FC = () => {
  const [prompt, setPrompt] = useState('');
  const [openaiApiKey, setOpenaiApiKey] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [generatedRule, setGeneratedRule] = useState<RuleResponse | null>(null);
  const [showAnimation, setShowAnimation] = useState(false);
  const theme = useTheme();

  React.useEffect(() => {
    setShowAnimation(true);
  }, []);

  const handleGenerateRule = async (e: React.FormEvent) => {
    e.preventDefault();
    
    console.log('handleGenerateRule called');
    console.log('Prompt:', prompt);
    console.log('API Key provided:', !!openaiApiKey);
    
    if (!prompt) {
      setError('Please enter a prompt');
      return;
    }

    if (!openaiApiKey) {
      setError('Please enter your OpenAI API Key');
      return;
    }

    setLoading(true);
    setError(null);
    setGeneratedRule(null);

    try {
      console.log('Calling generateRule API...');
      const response = await generateRule(prompt, openaiApiKey);
      console.log('API response received:', response);
      setGeneratedRule(response);
    } catch (err) {
      console.error('Error in handleGenerateRule:', err);
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const renderRuleContent = (rule: any) => {
    return Object.entries(rule).map(([key, value]) => {
      if (typeof value === 'object' && value !== null) {
        return (
          <Box key={key} sx={{ mb: 2 }}>
            <Typography variant="subtitle2" color="primary" sx={{ fontWeight: 'bold' }}>
              {key.replace(/_/g, ' ').toUpperCase()}:
            </Typography>
            <Box 
              component="pre" 
              sx={{ 
                whiteSpace: 'pre-wrap',
                fontFamily: 'monospace',
                fontSize: '0.875rem',
                backgroundColor: 'rgba(0, 0, 0, 0.04)',
                p: 2,
                borderRadius: 1,
                border: `1px solid ${theme.palette.divider}`,
              }}
            >
              {JSON.stringify(value, null, 2)}
            </Box>
          </Box>
        );
      }
      return (
        <Box key={key} sx={{ mb: 2 }}>
          <Typography variant="subtitle2" color="primary" sx={{ fontWeight: 'bold' }}>
            {key.replace(/_/g, ' ').toUpperCase()}:
          </Typography>
          <Typography variant="body2">{String(value)}</Typography>
        </Box>
      );
    });
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {loading && (
        <Fade in timeout={500}>
          <Box
            sx={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              backgroundColor: 'rgba(0, 0, 0, 0.8)',
              backdropFilter: 'blur(8px)',
              zIndex: 9999,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 4,
              p: 3,
            }}
          >
            <Box
              sx={{
                position: 'relative',
                width: 200,
                height: 200,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <CircularProgress
                size={200}
                thickness={2}
                sx={{
                  color: theme.palette.primary.main,
                  position: 'absolute',
                  animation: 'spin 4s linear infinite',
                  '@keyframes spin': {
                    '0%': { transform: 'rotate(0deg)' },
                    '100%': { transform: 'rotate(360deg)' },
                  },
                }}
              />
              <Box
                sx={{
                  position: 'absolute',
                  width: '100%',
                  height: '100%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  background: `radial-gradient(circle, ${theme.palette.primary.main}20 0%, transparent 70%)`,
                  animation: 'pulse 2s ease-in-out infinite',
                  '@keyframes pulse': {
                    '0%': { transform: 'scale(0.95)', opacity: 0.5 },
                    '50%': { transform: 'scale(1.05)', opacity: 0.8 },
                    '100%': { transform: 'scale(0.95)', opacity: 0.5 },
                  },
                }}
              />
              <TrackChangesIcon
                sx={{
                  fontSize: 80,
                  color: theme.palette.primary.main,
                  animation: 'float 3s ease-in-out infinite',
                  '@keyframes float': {
                    '0%': { transform: 'translateY(0px)' },
                    '50%': { transform: 'translateY(-20px)' },
                    '100%': { transform: 'translateY(0px)' },
                  },
                }}
              />
            </Box>

            <Typography
              variant="h4"
              sx={{
                color: 'white',
                textAlign: 'center',
                fontWeight: 'bold',
                textShadow: `0 0 10px ${theme.palette.primary.main}`,
              }}
            >
              Processing Rule
            </Typography>

            <Box sx={{ width: '100%', maxWidth: 600 }}>
              <LinearProgress
                sx={{
                  height: 4,
                  borderRadius: 2,
                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                  '& .MuiLinearProgress-bar': {
                    backgroundColor: theme.palette.primary.main,
                    boxShadow: `0 0 10px ${theme.palette.primary.main}`,
                  },
                }}
              />
            </Box>

            <Typography
              variant="body2"
              sx={{
                color: 'rgba(255, 255, 255, 0.6)',
                textAlign: 'center',
              }}
            >
              Analyzing rule, checking quality, and generating insights...
            </Typography>
          </Box>
        </Fade>
      )}

      <Fade in={showAnimation} timeout={1000}>
        <Box sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between',
          mb: 4,
          gap: 2
        }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Avatar 
              sx={{ 
                bgcolor: theme.palette.primary.main,
                width: 64,
                height: 64,
                boxShadow: `0 0 20px ${theme.palette.primary.main}40`,
                animation: 'pulse 2s infinite',
                '@keyframes pulse': {
                  '0%': { boxShadow: `0 0 0 0 ${theme.palette.primary.main}40` },
                  '70%': { boxShadow: `0 0 0 20px ${theme.palette.primary.main}00` },
                  '100%': { boxShadow: `0 0 0 0 ${theme.palette.primary.main}00` },
                },
              }}
            >
              <TrackChangesIcon fontSize="large" />
            </Avatar>
            <Box>
              <Typography 
                variant="h3" 
                gutterBottom 
                sx={{ 
                  fontWeight: 'bold',
                  background: `linear-gradient(45deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
                  backgroundClip: 'text',
                  textFillColor: 'transparent',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                }}
              >
                Detection QA
              </Typography>
              <Typography variant="subtitle1" color="text.secondary">
                AI-Powered Rule Quality Assurance
              </Typography>
            </Box>
          </Box>
        </Box>
      </Fade>

      <Box sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, gap: 3 }}>
        <Box sx={{ flex: { xs: '1 1 100%', md: '2 1 66%' } }}>
          <Zoom in={showAnimation} timeout={1000} style={{ transitionDelay: '200ms' }}>
            <Paper 
              sx={{ 
                p: 3, 
                mb: 3, 
                position: 'relative', 
                overflow: 'hidden',
                background: `linear-gradient(135deg, ${theme.palette.background.paper}, ${theme.palette.background.default})`,
                boxShadow: `0 8px 32px ${theme.palette.primary.main}10`,
                backdropFilter: 'blur(4px)',
                border: `1px solid ${theme.palette.divider}`,
              }}
            >
              <Box
                sx={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  right: 0,
                  height: '4px',
                  background: `linear-gradient(90deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
                  animation: 'gradient 3s ease infinite',
                  '@keyframes gradient': {
                    '0%': { backgroundPosition: '0% 50%' },
                    '50%': { backgroundPosition: '100% 50%' },
                    '100%': { backgroundPosition: '0% 50%' },
                  },
                }}
              />
              <Typography 
                variant="h5" 
                gutterBottom 
                sx={{ 
                  fontWeight: 'bold',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1,
                }}
              >
                <SearchIcon color="primary" />
                Rule Generation
              </Typography>
              <Box 
                component="form" 
                onSubmit={handleGenerateRule} 
                sx={{ 
                  display: 'flex', 
                  flexDirection: 'column', 
                  gap: 2,
                  '& .MuiTextField-root': {
                    '& .MuiOutlinedInput-root': {
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        transform: 'translateY(-2px)',
                        boxShadow: `0 4px 12px ${theme.palette.primary.main}20`,
                      },
                    },
                  },
                }}
              >
                <TextField
                  fullWidth
                  label="Enter Prompt"
                  placeholder="Create a sigma rule to detect possible DNS Tunneling behavior"
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  error={!!error}
                  helperText={error}
                  multiline
                  rows={4}
                  sx={{ mb: 2 }}
                />
                <TextField
                  fullWidth
                  label="OpenAI API Key"
                  type="password"
                  value={openaiApiKey}
                  onChange={(e) => setOpenaiApiKey(e.target.value)}
                  error={!!error}
                />
                <Button
                  type="submit"
                  variant="contained"
                  disabled={loading}
                  startIcon={loading ? <CircularProgress size={20} /> : <SearchIcon />}
                  sx={{ 
                    height: '56px',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-2px)',
                      boxShadow: `0 4px 12px ${theme.palette.primary.main}40`,
                    },
                  }}
                >
                  {loading ? 'Generating...' : 'Generate Rule'}
                </Button>
              </Box>
            </Paper>
          </Zoom>

          {generatedRule && (
            <Fade in={!!generatedRule} timeout={500}>
              <Box>
                <Card 
                  sx={{ 
                    mb: 3,
                    background: `linear-gradient(135deg, ${theme.palette.background.paper}, ${theme.palette.background.default})`,
                    boxShadow: `0 8px 32px ${theme.palette.primary.main}10`,
                    backdropFilter: 'blur(4px)',
                    border: `1px solid ${theme.palette.divider}`,
                  }}
                >
                  <CardContent>
                    <Typography 
                      variant="h6" 
                      gutterBottom
                      sx={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 1,
                        color: theme.palette.primary.main,
                      }}
                    >
                      <CodeIcon />
                      Generated Rule
                    </Typography>
                    
                    {/* Rule Content */}
                    {renderRuleContent(generatedRule.rule)}

                    {/* Explanation */}
                    {generatedRule.explanation && (
                      <Box sx={{ mt: 3 }}>
                        <Typography variant="subtitle1" color="primary" gutterBottom>
                          Explanation
                        </Typography>
                        <Typography variant="body2">
                          {generatedRule.explanation}
                        </Typography>
                      </Box>
                    )}

                    {/* Test Cases */}
                    {generatedRule.test_cases && generatedRule.test_cases.length > 0 && (
                      <Box sx={{ mt: 3 }}>
                        <Typography variant="subtitle1" color="primary" gutterBottom>
                          Test Cases
                        </Typography>
                        {generatedRule.test_cases.map((testCase, index) => (
                          <Accordion key={index} sx={{ mb: 1 }}>
                            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                              <Typography variant="subtitle2">{testCase.name}</Typography>
                            </AccordionSummary>
                            <AccordionDetails>
                              <Typography variant="body2" paragraph>
                                {testCase.description}
                              </Typography>
                              <Typography variant="body2" color="primary">
                                Expected Result: {testCase.expected_result}
                              </Typography>
                            </AccordionDetails>
                          </Accordion>
                        ))}
                      </Box>
                    )}

                    {/* MITRE Techniques */}
                    {generatedRule.mitre_techniques && generatedRule.mitre_techniques.length > 0 && (
                      <Box sx={{ mt: 3 }}>
                        <Typography variant="subtitle1" color="primary" gutterBottom>
                          MITRE ATT&CK Techniques
                        </Typography>
                        {generatedRule.mitre_techniques.map((technique, index) => (
                          <Accordion key={index} sx={{ mb: 1 }}>
                            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                              <Typography variant="subtitle2">
                                {technique.id}: {technique.name}
                              </Typography>
                            </AccordionSummary>
                            <AccordionDetails>
                              <Typography variant="body2">
                                {technique.description}
                              </Typography>
                            </AccordionDetails>
                          </Accordion>
                        ))}
                      </Box>
                    )}

                    {/* Confidence Score */}
                    {generatedRule.confidence_score && (
                      <Box sx={{ mt: 3 }}>
                        <Typography variant="subtitle1" color="primary" gutterBottom>
                          Confidence Score: {(generatedRule.confidence_score * 100).toFixed(1)}%
                        </Typography>
                        <LinearProgress 
                          variant="determinate" 
                          value={generatedRule.confidence_score * 100}
                          sx={{
                            height: 8,
                            borderRadius: 4,
                            backgroundColor: 'rgba(0, 0, 0, 0.1)',
                            '& .MuiLinearProgress-bar': {
                              borderRadius: 4,
                            },
                          }}
                        />
                      </Box>
                    )}

                    {/* Component Scores */}
                    {generatedRule.component_scores && (
                      <Box sx={{ mt: 3 }}>
                        <Typography variant="subtitle1" color="primary" gutterBottom>
                          Component Scores
                        </Typography>
                        {Object.entries(generatedRule.component_scores).map(([key, value]) => {
                          const score = Number(value) * 100;
                          const getScoreColor = (score: number) => {
                            if (score >= 80) return theme.palette.success.main;
                            if (score >= 60) return theme.palette.warning.main;
                            return theme.palette.error.main;
                          };

                          const getScoreDetails = (key: string, score: number) => {
                            const details: { [key: string]: { 
                              high: { description: string; factors: string[]; icon: string };
                              medium: { description: string; factors: string[]; icon: string };
                              low: { description: string; factors: string[]; icon: string };
                            }} = {
                              detection_quality: {
                                high: {
                                  description: "Excellent detection logic with comprehensive coverage",
                                  factors: [
                                    "Strong pattern matching",
                                    "Multiple detection conditions",
                                    "Comprehensive event correlation",
                                    "Robust filtering logic"
                                  ],
                                  icon: "🎯"
                                },
                                medium: {
                                  description: "Good detection logic but could be improved",
                                  factors: [
                                    "Basic pattern matching",
                                    "Limited event correlation",
                                    "Simple filtering logic",
                                    "Some detection gaps"
                                  ],
                                  icon: "⚡"
                                },
                                low: {
                                  description: "Basic detection logic that needs enhancement",
                                  factors: [
                                    "Weak pattern matching",
                                    "No event correlation",
                                    "Basic filtering",
                                    "Significant detection gaps"
                                  ],
                                  icon: "⚠️"
                                }
                              },
                              false_positive_risk: {
                                high: {
                                  description: "Low risk of false positives",
                                  factors: [
                                    "Strong context validation",
                                    "Multiple validation checks",
                                    "Comprehensive filtering",
                                    "Clear detection boundaries"
                                  ],
                                  icon: "🎯"
                                },
                                medium: {
                                  description: "Moderate risk of false positives",
                                  factors: [
                                    "Basic context validation",
                                    "Limited validation checks",
                                    "Simple filtering",
                                    "Some unclear boundaries"
                                  ],
                                  icon: "⚡"
                                },
                                low: {
                                  description: "High risk of false positives",
                                  factors: [
                                    "Weak context validation",
                                    "No validation checks",
                                    "Basic filtering",
                                    "Unclear detection boundaries"
                                  ],
                                  icon: "⚠️"
                                }
                              },
                              coverage: {
                                high: {
                                  description: "Extensive coverage of attack scenarios",
                                  factors: [
                                    "Multiple attack vectors covered",
                                    "Comprehensive MITRE mapping",
                                    "Edge cases considered",
                                    "Multiple detection stages"
                                  ],
                                  icon: "🎯"
                                },
                                medium: {
                                  description: "Good coverage but some gaps exist",
                                  factors: [
                                    "Basic attack vectors covered",
                                    "Limited MITRE mapping",
                                    "Some edge cases missed",
                                    "Single detection stage"
                                  ],
                                  icon: "⚡"
                                },
                                low: {
                                  description: "Limited coverage of attack scenarios",
                                  factors: [
                                    "Single attack vector",
                                    "No MITRE mapping",
                                    "Edge cases not considered",
                                    "Basic detection only"
                                  ],
                                  icon: "⚠️"
                                }
                              },
                              maintainability: {
                                high: {
                                  description: "Well-structured and easy to maintain",
                                  factors: [
                                    "Clear rule structure",
                                    "Well-documented logic",
                                    "Modular components",
                                    "Easy to update"
                                  ],
                                  icon: "🎯"
                                },
                                medium: {
                                  description: "Moderately maintainable",
                                  factors: [
                                    "Basic rule structure",
                                    "Limited documentation",
                                    "Some complex components",
                                    "Moderate update difficulty"
                                  ],
                                  icon: "⚡"
                                },
                                low: {
                                  description: "Complex and difficult to maintain",
                                  factors: [
                                    "Unclear structure",
                                    "Poor documentation",
                                    "Complex components",
                                    "Difficult to update"
                                  ],
                                  icon: "⚠️"
                                }
                              }
                            };

                            if (score >= 80) return details[key]?.high;
                            if (score >= 60) return details[key]?.medium;
                            return details[key]?.low;
                          };

                          const scoreDetails = getScoreDetails(key, score);

                          return (
                            <Box key={key} sx={{ mb: 3 }}>
                              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                                <Typography variant="body2" sx={{ fontWeight: 'bold', fontSize: '1rem' }}>
                                  {key.replace(/_/g, ' ').toUpperCase()}
                                </Typography>
                                <Typography 
                                  variant="body2" 
                                  sx={{ 
                                    color: getScoreColor(score),
                                    fontWeight: 'bold',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: 0.5,
                                    fontSize: '1rem'
                                  }}
                                >
                                  {score.toFixed(1)}% {scoreDetails?.icon}
                                </Typography>
                              </Box>
                              <Tooltip 
                                title={
                                  <Box sx={{ p: 1 }}>
                                    <Typography variant="subtitle2" sx={{ mb: 1 }}>Evaluation Factors:</Typography>
                                    {scoreDetails?.factors.map((factor, index) => (
                                      <Typography key={index} variant="body2" sx={{ mb: 0.5 }}>
                                        • {factor}
                                      </Typography>
                                    ))}
                                  </Box>
                                }
                                arrow
                                placement="top"
                              >
                                <LinearProgress 
                                  variant="determinate" 
                                  value={score}
                                  sx={{
                                    height: 8,
                                    borderRadius: 4,
                                    backgroundColor: 'rgba(0, 0, 0, 0.1)',
                                    '& .MuiLinearProgress-bar': {
                                      borderRadius: 4,
                                      backgroundColor: getScoreColor(score),
                                      transition: 'transform 0.4s ease-in-out',
                                      '&:hover': {
                                        transform: 'scaleX(1.02)',
                                      },
                                    },
                                  }}
                                />
                              </Tooltip>
                              <Typography 
                                variant="body2" 
                                sx={{ 
                                  mt: 1,
                                  color: 'text.secondary',
                                  fontStyle: 'italic',
                                  display: 'flex',
                                  alignItems: 'center',
                                  gap: 1
                                }}
                              >
                                {scoreDetails?.description}
                              </Typography>
                              <Box 
                                sx={{ 
                                  mt: 1,
                                  display: 'flex',
                                  flexWrap: 'wrap',
                                  gap: 1
                                }}
                              >
                                {scoreDetails?.factors.map((factor, index) => (
                                  <Chip
                                    key={index}
                                    label={factor}
                                    size="small"
                                    sx={{
                                      backgroundColor: `${getScoreColor(score)}20`,
                                      color: getScoreColor(score),
                                      border: `1px solid ${getScoreColor(score)}40`,
                                      '&:hover': {
                                        backgroundColor: `${getScoreColor(score)}30`,
                                      },
                                    }}
                                  />
                                ))}
                              </Box>
                            </Box>
                          );
                        })}
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Box>
            </Fade>
          )}
        </Box>

        <Box sx={{ flex: { xs: '1 1 100%', md: '1 1 33%' } }}>
          <Zoom in={showAnimation} timeout={1000} style={{ transitionDelay: '400ms' }}>
            <Card 
              sx={{ 
                height: '100%', 
                position: 'relative', 
                overflow: 'hidden',
                background: `linear-gradient(135deg, ${theme.palette.background.paper}, ${theme.palette.background.default})`,
                boxShadow: `0 8px 32px ${theme.palette.primary.main}10`,
                backdropFilter: 'blur(4px)',
                border: `1px solid ${theme.palette.divider}`,
              }}
            >
              <Box
                sx={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  right: 0,
                  bottom: 0,
                  background: `radial-gradient(circle at 50% 50%, ${theme.palette.primary.main}10, transparent 70%)`,
                  animation: 'pulse 4s ease-in-out infinite',
                  '@keyframes pulse': {
                    '0%': { opacity: 0.5 },
                    '50%': { opacity: 0.8 },
                    '100%': { opacity: 0.5 },
                  },
                }}
              />
              <CardContent>
                <Typography 
                  variant="h6" 
                  gutterBottom
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1,
                    color: theme.palette.primary.main,
                  }}
                >
                  <TrackChangesIcon color="primary" />
                  About Detection QA
                </Typography>
                <Divider sx={{ mb: 2 }} />
                <Typography 
                  variant="body2" 
                  paragraph
                  sx={{
                    color: theme.palette.text.secondary,
                    lineHeight: 1.8,
                  }}
                >
                  Detection QA is an advanced tool that helps you generate, and analyze security rules using AI.
                </Typography>
                <Typography 
                  variant="body2" 
                  paragraph
                  sx={{
                    color: theme.palette.text.secondary,
                    fontWeight: 'bold',
                  }}
                >
                  Features:
                </Typography>
                <Box 
                  component="ul" 
                  sx={{ 
                    paddingLeft: '20px', 
                    margin: 0,
                    '& li': {
                      color: theme.palette.text.secondary,
                      mb: 1,
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        color: theme.palette.primary.main,
                        transform: 'translateX(4px)',
                      },
                    },
                  }}
                >
                  <li>AI-powered rule generation</li>
                  <li>Rule quality analysis</li>
                  <li>MITRE ATT&CK mapping</li>
                  <li>False positive detection</li>
                </Box>
              </CardContent>
            </Card>
          </Zoom>
        </Box>
      </Box>
    </Container>
  );
};

export default QA; 