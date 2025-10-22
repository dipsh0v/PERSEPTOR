import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip,
  IconButton,
  Tooltip,
  useTheme,
  Fade,
  Zoom,
  Divider,
  Avatar,
  CircularProgress,
  Alert,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import SecurityIcon from '@mui/icons-material/Security';
import DeleteIcon from '@mui/icons-material/Delete';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import AssessmentIcon from '@mui/icons-material/Assessment';
import { AnalysisResult } from '../services/api';

const Reports: React.FC = () => {
  const [reports, setReports] = useState<Array<AnalysisResult & { id: string; url: string; timestamp: string }>>([]);
  const [showAnimation, setShowAnimation] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const theme = useTheme();

  useEffect(() => {
    setShowAnimation(true);
    fetchReports();
  }, []);

  const fetchReports = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch('/api/reports');
      if (response.ok) {
        const data = await response.json();
        // Ensure yara_rules is always an array
        const formattedReports = (data.reports || []).map((report: any) => ({
          ...report,
          yara_rules: Array.isArray(report.yara_rules) ? report.yara_rules : []
        }));
        setReports(formattedReports);
      } else {
        setError('Failed to fetch reports');
      }
    } catch (err) {
      setError('Error fetching reports');
      console.error('Error fetching reports:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('Are you sure you want to delete this report?')) {
      return;
    }
    
    try {
      const response = await fetch(`/api/reports/${id}`, {
        method: 'DELETE',
      });
      
      if (response.ok) {
        setReports(reports.filter(report => report.id !== id));
      } else {
        setError('Failed to delete report');
      }
    } catch (err) {
      setError('Error deleting report');
      console.error('Error deleting report:', err);
    }
  };

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <Box sx={{
      p: 3,
      ml: { xs: 0, md: '280px' },
      maxWidth: 900,
      mx: 'auto',
      width: '100%',
    }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
        <AssessmentIcon sx={{ fontSize: 48, color: theme.palette.primary.main }} />
        <Typography
          variant="h3"
          fontWeight="bold"
          sx={{
            background: `linear-gradient(45deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
            backgroundClip: 'text',
            textFillColor: 'transparent',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}
        >
          Analyzed Reports
        </Typography>
      </Box>
      <Typography variant="subtitle1" color="text.secondary" sx={{ mb: 3, ml: 8 }}>
        View and manage your threat analysis history
      </Typography>

      <Zoom in={showAnimation} timeout={1000} style={{ transitionDelay: '200ms' }}>
        <Card 
          sx={{ 
            background: `linear-gradient(135deg, ${theme.palette.background.paper}, ${theme.palette.background.default})`,
            boxShadow: `0 8px 32px ${theme.palette.primary.main}10`,
            backdropFilter: 'blur(4px)',
            border: `1px solid ${theme.palette.divider}`,
          }}
        >
          <CardContent>
            {error && (
              <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
                {error}
              </Alert>
            )}
            
            {loading ? (
              <Box 
                sx={{ 
                  display: 'flex', 
                  justifyContent: 'center', 
                  alignItems: 'center',
                  py: 8 
                }}
              >
                <CircularProgress />
              </Box>
            ) : reports.length === 0 ? (
              <Box 
                sx={{ 
                  textAlign: 'center', 
                  py: 4,
                  color: theme.palette.text.secondary,
                }}
              >
                <Typography variant="h6" gutterBottom>
                  No Reports Found
                </Typography>
                <Typography variant="body2">
                  Start analyzing URLs to see your reports here
                </Typography>
              </Box>
            ) : (
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                {reports.map((report) => (
                  <Accordion
                    key={report.id}
                    sx={{
                      background: 'transparent',
                      boxShadow: 'none',
                      '&:before': { display: 'none' },
                      border: `1px solid ${theme.palette.divider}`,
                      borderRadius: '8px !important',
                      overflow: 'hidden',
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        transform: 'translateY(-2px)',
                        boxShadow: `0 4px 12px ${theme.palette.primary.main}20`,
                      },
                    }}
                  >
                    <AccordionSummary
                      expandIcon={<ExpandMoreIcon />}
                      sx={{
                        '& .MuiAccordionSummary-content': {
                          margin: '12px 0',
                        },
                      }}
                    >
                      <Box sx={{ width: '100%', display: 'flex', alignItems: 'center', gap: 2 }}>
                        <Box sx={{ flex: 1 }}>
                          <Typography 
                            variant="subtitle1" 
                            sx={{ 
                              fontWeight: 'bold',
                              color: theme.palette.primary.main,
                            }}
                          >
                            {report.url}
                          </Typography>
                          <Typography 
                            variant="body2" 
                            color="text.secondary"
                            sx={{ mt: 0.5 }}
                          >
                            Analyzed on {formatDate(report.timestamp)}
                          </Typography>
                        </Box>
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <Tooltip title="Copy URL">
                            <IconButton 
                              size="small"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleCopy(report.url);
                              }}
                            >
                              <ContentCopyIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Delete Report">
                            <IconButton 
                              size="small"
                              color="error"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleDelete(report.id);
                              }}
                            >
                              <DeleteIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </Box>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Divider sx={{ mb: 2 }} />
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
                        <SecurityIcon />
                        Threat Summary
                      </Typography>
                      <Typography 
                        variant="body1" 
                        sx={{ 
                          whiteSpace: 'pre-wrap',
                          lineHeight: 1.8,
                          color: theme.palette.text.secondary,
                          mb: 3,
                        }}
                      >
                        {report.threat_summary}
                      </Typography>

                      {report.analysis_data?.indicators_of_compromise && (
                        <>
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
                            <SecurityIcon />
                            Indicators of Compromise
                          </Typography>
                          <Box sx={{ mb: 3 }}>
                            {Object.entries(report.analysis_data.indicators_of_compromise).map(([key, value]) => (
                              Array.isArray(value) && value.length > 0 && (
                                <Box key={key} sx={{ mb: 2 }}>
                                  <Typography 
                                    variant="subtitle2" 
                                    sx={{ 
                                      color: theme.palette.text.secondary,
                                      mb: 1,
                                    }}
                                  >
                                    {key.replace(/_/g, ' ').toUpperCase()}
                                  </Typography>
                                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                                    {value.map((item, index) => (
                                      <Chip
                                        key={index}
                                        label={item}
                                        size="small"
                                        sx={{
                                          fontFamily: 'monospace',
                                          transition: 'all 0.3s ease',
                                          '&:hover': {
                                            transform: 'translateY(-2px)',
                                            boxShadow: `0 2px 8px ${theme.palette.primary.main}20`,
                                          },
                                        }}
                                      />
                                    ))}
                                  </Box>
                                </Box>
                              )
                            ))}
                          </Box>
                        </>
                      )}

                      {report.analysis_data?.threat_actors && report.analysis_data.threat_actors.length > 0 && (
                        <>
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
                            <SecurityIcon />
                            Threat Actors
                          </Typography>
                          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 3 }}>
                            {report.analysis_data.threat_actors.map((actor, index) => (
                              <Chip
                                key={index}
                                label={actor}
                                color="error"
                                sx={{
                                  transition: 'all 0.3s ease',
                                  '&:hover': {
                                    transform: 'translateY(-2px)',
                                    boxShadow: `0 2px 8px ${theme.palette.error.main}20`,
                                  },
                                }}
                              />
                            ))}
                          </Box>
                        </>
                      )}

                      {report.analysis_data?.ttps && report.analysis_data.ttps.length > 0 && (
                        <>
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
                            <SecurityIcon />
                            MITRE ATT&CK TTPs
                          </Typography>
                          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 3 }}>
                            {report.analysis_data.ttps.map((ttp, index) => (
                              <Chip
                                key={index}
                                label={typeof ttp === 'string' ? ttp : ttp.technique_name}
                                color="warning"
                                sx={{
                                  transition: 'all 0.3s ease',
                                  '&:hover': {
                                    transform: 'translateY(-2px)',
                                    boxShadow: `0 2px 8px ${theme.palette.warning.main}20`,
                                  },
                                }}
                              />
                            ))}
                          </Box>
                        </>
                      )}

                      {report.analysis_data?.tools_or_malware && report.analysis_data.tools_or_malware.length > 0 && (
                        <>
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
                            <SecurityIcon />
                            Tools & Malware
                          </Typography>
                          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 3 }}>
                            {report.analysis_data.tools_or_malware.map((item, index) => {
                              const isMalware = item.toLowerCase().includes('malware') || 
                                              item.toLowerCase().includes('trojan') || 
                                              item.toLowerCase().includes('ransomware') ||
                                              item.toLowerCase().includes('worm') ||
                                              item.toLowerCase().includes('virus');
                              
                              return (
                                <Chip
                                  key={index}
                                  label={item}
                                  color={isMalware ? "error" : "info"}
                                  sx={{
                                    transition: 'all 0.3s ease',
                                    '&:hover': {
                                      transform: 'translateY(-2px)',
                                      boxShadow: `0 2px 8px ${isMalware ? theme.palette.error.main : theme.palette.info.main}20`,
                                    },
                                  }}
                                />
                              );
                            })}
                          </Box>
                        </>
                      )}

                      {report.generated_sigma_rules && (
                        <>
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
                            <SecurityIcon />
                            Generated Sigma Rules
                          </Typography>
                          <Accordion
                            sx={{
                              background: 'transparent',
                              boxShadow: 'none',
                              '&:before': { display: 'none' },
                              border: `1px solid ${theme.palette.divider}`,
                              borderRadius: '8px !important',
                              overflow: 'hidden',
                              transition: 'all 0.3s ease',
                              '&:hover': {
                                transform: 'translateY(-2px)',
                                boxShadow: `0 4px 12px ${theme.palette.primary.main}20`,
                              },
                            }}
                          >
                            <AccordionSummary
                              expandIcon={<ExpandMoreIcon />}
                              sx={{
                                '& .MuiAccordionSummary-content': {
                                  margin: '12px 0',
                                },
                              }}
                            >
                              <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                                View Generated Sigma Rules
                              </Typography>
                            </AccordionSummary>
                            <AccordionDetails>
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
                                {report.generated_sigma_rules}
                              </Box>
                            </AccordionDetails>
                          </Accordion>
                        </>
                      )}

                      {report.yara_rules && report.yara_rules.length > 0 && (
                        <>
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
                            <SecurityIcon />
                            Generated YARA Rules
                          </Typography>
                          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mb: 3 }}>
                            {report.yara_rules.map((rule, index) => (
                              <Accordion
                                key={index}
                                sx={{
                                  background: 'transparent',
                                  boxShadow: 'none',
                                  '&:before': { display: 'none' },
                                  border: `1px solid ${theme.palette.divider}`,
                                  borderRadius: '8px !important',
                                  overflow: 'hidden',
                                  transition: 'all 0.3s ease',
                                  '&:hover': {
                                    transform: 'translateY(-2px)',
                                    boxShadow: `0 4px 12px ${theme.palette.primary.main}20`,
                                  },
                                }}
                              >
                                <AccordionSummary
                                  expandIcon={<ExpandMoreIcon />}
                                  sx={{
                                    '& .MuiAccordionSummary-content': {
                                      margin: '12px 0',
                                    },
                                  }}
                                >
                                  <Box sx={{ width: '100%' }}>
                                    <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                                      {rule.name}
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary">
                                      {rule.description}
                                    </Typography>
                                  </Box>
                                </AccordionSummary>
                                <AccordionDetails>
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
                                    {rule.rule}
                                  </Box>
                                </AccordionDetails>
                              </Accordion>
                            ))}
                          </Box>
                        </>
                      )}

                      {report.siem_queries && (
                        <>
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
                            <SecurityIcon />
                            Generated SIEM Queries
                          </Typography>
                          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mb: 3 }}>
                            {Object.entries(report.siem_queries).map(([platform, query]) => (
                              <Accordion
                                key={platform}
                                sx={{
                                  background: 'transparent',
                                  boxShadow: 'none',
                                  '&:before': { display: 'none' },
                                  border: `1px solid ${theme.palette.divider}`,
                                  borderRadius: '8px !important',
                                  overflow: 'hidden',
                                  transition: 'all 0.3s ease',
                                  '&:hover': {
                                    transform: 'translateY(-2px)',
                                    boxShadow: `0 4px 12px ${theme.palette.primary.main}20`,
                                  },
                                }}
                              >
                                <AccordionSummary
                                  expandIcon={<ExpandMoreIcon />}
                                  sx={{
                                    '& .MuiAccordionSummary-content': {
                                      margin: '12px 0',
                                    },
                                  }}
                                >
                                  <Box sx={{ width: '100%', display: 'flex', alignItems: 'center', gap: 1 }}>
                                    <Typography variant="subtitle1" sx={{ flexGrow: 1, textTransform: 'capitalize' }}>
                                      {platform} Query
                                    </Typography>
                                    <Chip
                                      label={platform}
                                      color={
                                        platform === "splunk" ? "primary" :
                                        platform === "qradar" ? "secondary" :
                                        platform === "elastic" ? "success" : "warning"
                                      }
                                      size="small"
                                    />
                                  </Box>
                                </AccordionSummary>
                                <AccordionDetails>
                                  <Typography variant="body2" color="text.secondary" paragraph>
                                    {query.description}
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
                                      mb: 2,
                                    }}
                                  >
                                    {query.query}
                                  </Box>
                                  {query.notes && (
                                    <Typography variant="caption" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                                      Notes: {query.notes}
                                    </Typography>
                                  )}
                                </AccordionDetails>
                              </Accordion>
                            ))}
                          </Box>
                        </>
                      )}

                      {report.sigma_matches && report.sigma_matches.length > 0 && (
                        <>
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
                            <SecurityIcon />
                            Possible Global Sigma Matches
                          </Typography>
                          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mb: 3 }}>
                            {report.sigma_matches.map((match, index) => (
                              <Accordion
                                key={index}
                                sx={{
                                  background: 'transparent',
                                  boxShadow: 'none',
                                  '&:before': { display: 'none' },
                                  border: `1px solid ${theme.palette.divider}`,
                                  borderRadius: '8px !important',
                                  overflow: 'hidden',
                                  transition: 'all 0.3s ease',
                                  '&:hover': {
                                    transform: 'translateY(-2px)',
                                    boxShadow: `0 4px 12px ${theme.palette.primary.main}20`,
                                  },
                                }}
                              >
                                <AccordionSummary
                                  expandIcon={<ExpandMoreIcon />}
                                  sx={{
                                    '& .MuiAccordionSummary-content': {
                                      margin: '12px 0',
                                    },
                                  }}
                                >
                                  <Box sx={{ width: '100%', display: 'flex', alignItems: 'center', gap: 1 }}>
                                    <Typography variant="subtitle1" sx={{ flexGrow: 1 }}>
                                      {match.title}
                                    </Typography>
                                    <Chip
                                      label={`${match.match_ratio}% Match`}
                                      color={match.match_ratio > 70 ? "success" : match.match_ratio > 40 ? "warning" : "error"}
                                      size="small"
                                    />
                                    <Chip
                                      label={match.level}
                                      color={
                                        match.level === "critical" ? "error" :
                                        match.level === "high" ? "warning" :
                                        match.level === "medium" ? "info" : "success"
                                      }
                                      size="small"
                                    />
                                  </Box>
                                </AccordionSummary>
                                <AccordionDetails>
                                  <Typography variant="body2" color="text.secondary" paragraph>
                                    {match.description}
                                  </Typography>
                                  {match.matched_keywords && match.matched_keywords.length > 0 && (
                                    <Box>
                                      <Typography variant="subtitle2" gutterBottom>
                                        Matched Keywords:
                                      </Typography>
                                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                                        {match.matched_keywords.map((keyword, idx) => (
                                          <Chip
                                            key={idx}
                                            label={keyword}
                                            size="small"
                                            variant="outlined"
                                            sx={{
                                              transition: 'all 0.3s ease',
                                              '&:hover': {
                                                transform: 'translateY(-2px)',
                                                boxShadow: `0 2px 8px ${theme.palette.primary.main}20`,
                                              },
                                            }}
                                          />
                                        ))}
                                      </Box>
                                    </Box>
                                  )}
                                </AccordionDetails>
                              </Accordion>
                            ))}
                          </Box>
                        </>
                      )}
                    </AccordionDetails>
                  </Accordion>
                ))}
              </Box>
            )}
          </CardContent>
        </Card>
      </Zoom>
    </Box>
  );
};

export default Reports; 