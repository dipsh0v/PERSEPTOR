import React, { useState, useEffect } from 'react';
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
import SecurityIcon from '@mui/icons-material/Security';
import SearchIcon from '@mui/icons-material/Search';
import GitHubIcon from '@mui/icons-material/GitHub';
import TwitterIcon from '@mui/icons-material/Twitter';
import LinkedInIcon from '@mui/icons-material/LinkedIn';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import CodeIcon from '@mui/icons-material/Code';
import LockIcon from '@mui/icons-material/Lock';
import BugReportIcon from '@mui/icons-material/BugReport';
import ShieldIcon from '@mui/icons-material/Shield';
import { analyzeUrl, AnalysisResult } from '../services/api';

const cybersecurityFacts = [
  {
    fact: "The first computer virus was created in 1971 and was called 'Creeper'. It displayed the message 'I'm the creeper, catch me if you can!'",
    icon: <BugReportIcon />,
    category: "History"
  },
  {
    fact: "A strong password with 12 characters, including numbers, symbols, and mixed case letters, would take a supercomputer about 34,000 years to crack.",
    icon: <LockIcon />,
    category: "Security"
  },
  {
    fact: "The global cost of cybercrime is expected to reach $10.5 trillion annually by 2025, making it more profitable than the global trade of all major illegal drugs combined.",
    icon: <ShieldIcon />,
    category: "Impact"
  },
  {
    fact: "The first ransomware attack occurred in 1989, when a biologist distributed floppy disks containing malware that encrypted files and demanded payment.",
    icon: <CodeIcon />,
    category: "History"
  },
  {
    fact: "The average time to detect a data breach is 207 days, and the average time to contain it is 73 days.",
    icon: <BugReportIcon />,
    category: "Statistics"
  },
  {
    fact: "Quantum computers could potentially break current encryption methods, which is why post-quantum cryptography is being developed.",
    icon: <CodeIcon />,
    category: "Future"
  },
  {
    fact: "The first firewall was created in 1988 by Digital Equipment Corporation to protect their internal network.",
    icon: <ShieldIcon />,
    category: "History"
  },
  {
    fact: "Social engineering attacks account for 98% of all cyber attacks, making human error the biggest security vulnerability.",
    icon: <LockIcon />,
    category: "Security"
  },
  {
    fact: "The 'ILOVEYOU' virus, released in 2000, caused an estimated $10 billion in damages and infected over 50 million computers in just 10 days.",
    icon: <BugReportIcon />,
    category: "History"
  },
  {
    fact: "The first computer password was implemented at MIT in 1961 for their Compatible Time-Sharing System (CTSS).",
    icon: <LockIcon />,
    category: "History"
  },
  {
    fact: "The term 'bug' in computer science originated in 1947 when Grace Hopper found an actual moth causing problems in the Harvard Mark II computer.",
    icon: <BugReportIcon />,
    category: "Trivia"
  },
  {
    fact: "The first computer antivirus software was created in 1987 by Bernd Fix to combat the Vienna virus.",
    icon: <ShieldIcon />,
    category: "History"
  },
  {
    fact: "The largest DDoS attack ever recorded reached 2.3 terabits per second, targeting Amazon Web Services in 2020.",
    icon: <CodeIcon />,
    category: "Statistics"
  },
  {
    fact: "The first computer worm, the Morris Worm, was created by Robert Morris in 1988 and infected about 10% of all computers connected to the internet at that time.",
    icon: <BugReportIcon />,
    category: "History"
  },
  {
    fact: "The first known case of cyber espionage occurred in 1986 when a group of German hackers sold sensitive information to the KGB.",
    icon: <ShieldIcon />,
    category: "History"
  },
  {
    fact: "The first computer virus to target mobile phones, 'Cabir', was discovered in 2004 and spread via Bluetooth.",
    icon: <BugReportIcon />,
    category: "History"
  },
  {
    fact: "The first computer security conference, the National Computer Security Conference, was held in 1985.",
    icon: <ShieldIcon />,
    category: "History"
  },
  {
    fact: "The first computer virus to spread via email, 'Melissa', was created in 1999 and infected over 1 million computers.",
    icon: <BugReportIcon />,
    category: "History"
  },
  {
    fact: "The first computer virus to target industrial control systems, 'Stuxnet', was discovered in 2010 and was designed to sabotage Iran's nuclear program.",
    icon: <CodeIcon />,
    category: "History"
  },
  {
    fact: "The first computer virus to target Mac OS X, 'OSX/Leap-A', was discovered in 2006.",
    icon: <BugReportIcon />,
    category: "History"
  },
  {
    fact: "The first computer virus to target cloud computing, 'Cloudburst', was discovered in 2019.",
    icon: <CodeIcon />,
    category: "Future"
  },
  {
    fact: "The first computer virus to target IoT devices, 'Mirai', was discovered in 2016 and was used to launch massive DDoS attacks.",
    icon: <BugReportIcon />,
    category: "History"
  },
  {
    fact: "The first computer virus to target blockchain, 'Cryptojacking', was discovered in 2017 and was used to mine cryptocurrency without consent.",
    icon: <CodeIcon />,
    category: "Future"
  },
  {
    fact: "The first computer virus to target AI systems, 'DeepLocker', was discovered in 2018 and was designed to evade detection using AI.",
    icon: <CodeIcon />,
    category: "Future"
  },
  {
    fact: "The first computer virus to target quantum computers, 'Qubit', is expected to emerge in the next decade.",
    icon: <CodeIcon />,
    category: "Future"
  },
  {
    fact: "The first computer virus to target 5G networks, '5GStuxnet', is expected to emerge in the next few years.",
    icon: <CodeIcon />,
    category: "Future"
  },
  {
    fact: "The first computer virus to target autonomous vehicles, 'AutoHack', is expected to emerge in the next decade.",
    icon: <CodeIcon />,
    category: "Future"
  },
  {
    fact: "The first computer virus to target smart cities, 'CityHack', is expected to emerge in the next few years.",
    icon: <CodeIcon />,
    category: "Future"
  },
  {
    fact: "The first computer virus to target space systems, 'SpaceHack', is expected to emerge in the next decade.",
    icon: <CodeIcon />,
    category: "Future"
  },
  {
    fact: "The first computer virus to target brain-computer interfaces, 'BrainHack', is expected to emerge in the next few years.",
    icon: <CodeIcon />,
    category: "Future"
  },
  {
    fact: "The first computer virus to target quantum internet, 'QuantumHack', is expected to emerge in the next decade.",
    icon: <CodeIcon />,
    category: "Future"
  },
  {
    fact: "The first computer virus to target 6G networks, '6GStuxnet', is expected to emerge in the next few years.",
    icon: <CodeIcon />,
    category: "Future"
  },
  {
    fact: "The first computer virus to target artificial general intelligence, 'AGIHack', is expected to emerge in the next decade.",
    icon: <CodeIcon />,
    category: "Future"
  },
  {
    fact: "The first computer virus to target quantum internet, 'QuantumHack', is expected to emerge in the next decade.",
    icon: <CodeIcon />,
    category: "Future"
  },
  {
    fact: "The first computer virus to target brain-computer interfaces, 'BrainHack', is expected to emerge in the next few years.",
    icon: <CodeIcon />,
    category: "Future"
  },
  {
    fact: "The first computer virus to target space systems, 'SpaceHack', is expected to emerge in the next decade.",
    icon: <CodeIcon />,
    category: "Future"
  },
  {
    fact: "The first computer virus to target smart cities, 'CityHack', is expected to emerge in the next few years.",
    icon: <CodeIcon />,
    category: "Future"
  },
  {
    fact: "The first computer virus to target autonomous vehicles, 'AutoHack', is expected to emerge in the next decade.",
    icon: <CodeIcon />,
    category: "Future"
  },
  {
    fact: "The first computer virus to target 5G networks, '5GStuxnet', is expected to emerge in the next few years.",
    icon: <CodeIcon />,
    category: "Future"
  },
  {
    fact: "The first computer virus to target quantum computers, 'Qubit', is expected to emerge in the next decade.",
    icon: <CodeIcon />,
    category: "Future"
  },
  {
    fact: "The first computer virus to target AI systems, 'DeepLocker', was discovered in 2018 and was designed to evade detection using AI.",
    icon: <CodeIcon />,
    category: "Future"
  },
  {
    fact: "The first computer virus to target blockchain, 'Cryptojacking', was discovered in 2017 and was used to mine cryptocurrency without consent.",
    icon: <CodeIcon />,
    category: "Future"
  },
  {
    fact: "The first computer virus to target IoT devices, 'Mirai', was discovered in 2016 and was used to launch massive DDoS attacks.",
    icon: <BugReportIcon />,
    category: "History"
  },
  {
    fact: "The first computer virus to target cloud computing, 'Cloudburst', was discovered in 2019.",
    icon: <CodeIcon />,
    category: "Future"
  },
  {
    fact: "The first computer virus to target Mac OS X, 'OSX/Leap-A', was discovered in 2006.",
    icon: <BugReportIcon />,
    category: "History"
  },
  {
    fact: "The first computer virus to target industrial control systems, 'Stuxnet', was discovered in 2010 and was designed to sabotage Iran's nuclear program.",
    icon: <CodeIcon />,
    category: "History"
  },
  {
    fact: "The first computer virus to spread via email, 'Melissa', was created in 1999 and infected over 1 million computers.",
    icon: <BugReportIcon />,
    category: "History"
  },
  {
    fact: "The first computer security conference, the National Computer Security Conference, was held in 1985.",
    icon: <ShieldIcon />,
    category: "History"
  },
  {
    fact: "The first computer virus to target mobile phones, 'Cabir', was discovered in 2004 and spread via Bluetooth.",
    icon: <BugReportIcon />,
    category: "History"
  },
  {
    fact: "The first known case of cyber espionage occurred in 1986 when a group of German hackers sold sensitive information to the KGB.",
    icon: <ShieldIcon />,
    category: "History"
  },
  {
    fact: "The first computer worm, the Morris Worm, was created by Robert Morris in 1988 and infected about 10% of all computers connected to the internet at that time.",
    icon: <BugReportIcon />,
    category: "History"
  },
  {
    fact: "The largest DDoS attack ever recorded reached 2.3 terabits per second, targeting Amazon Web Services in 2020.",
    icon: <CodeIcon />,
    category: "Statistics"
  },
  {
    fact: "The first computer antivirus software was created in 1987 by Bernd Fix to combat the Vienna virus.",
    icon: <ShieldIcon />,
    category: "History"
  },
  {
    fact: "The term 'bug' in computer science originated in 1947 when Grace Hopper found an actual moth causing problems in the Harvard Mark II computer.",
    icon: <BugReportIcon />,
    category: "Trivia"
  },
  {
    fact: "The first computer password was implemented at MIT in 1961 for their Compatible Time-Sharing System (CTSS).",
    icon: <LockIcon />,
    category: "History"
  },
  {
    fact: "The 'ILOVEYOU' virus, released in 2000, caused an estimated $10 billion in damages and infected over 50 million computers in just 10 days.",
    icon: <BugReportIcon />,
    category: "History"
  }
];

const LoadingScreen: React.FC = () => {
  const [currentFact, setCurrentFact] = useState(0);
  const [progress, setProgress] = useState(0);
  const theme = useTheme();

  useEffect(() => {
    const factInterval = setInterval(() => {
      setCurrentFact((prev) => (prev + 1) % cybersecurityFacts.length);
    }, 5000);

    const progressInterval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) return 0;
        return prev + 1;
      });
    }, 100);

    return () => {
      clearInterval(factInterval);
      clearInterval(progressInterval);
    };
  }, []);

  return (
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
          <SecurityIcon
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
          Analyzing Threat Report
        </Typography>

        <Box
          sx={{
            width: '100%',
            maxWidth: 600,
            backgroundColor: 'rgba(255, 255, 255, 0.1)',
            borderRadius: 2,
            p: 3,
            position: 'relative',
            overflow: 'hidden',
          }}
        >
          <Fade in key={currentFact} timeout={1000}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Box
                sx={{
                  color: theme.palette.primary.main,
                  animation: 'spin 4s linear infinite',
                  '@keyframes spin': {
                    '0%': { transform: 'rotate(0deg)' },
                    '100%': { transform: 'rotate(360deg)' },
                  },
                }}
              >
                {cybersecurityFacts[currentFact].icon}
              </Box>
              <Box>
                <Typography
                  variant="body1"
                  sx={{
                    color: 'white',
                    mb: 1,
                    fontWeight: 'bold',
                  }}
                >
                  {cybersecurityFacts[currentFact].category}
                </Typography>
                <Typography
                  variant="body2"
                  sx={{
                    color: 'rgba(255, 255, 255, 0.8)',
                    lineHeight: 1.6,
                  }}
                >
                  {cybersecurityFacts[currentFact].fact}
                </Typography>
              </Box>
            </Box>
          </Fade>
        </Box>

        <Box sx={{ width: '100%', maxWidth: 600 }}>
          <LinearProgress
            variant="determinate"
            value={progress}
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
          Scanning for threats, analyzing patterns, and generating security rules...
        </Typography>
      </Box>
    </Fade>
  );
};

const Dashboard: React.FC = () => {
  const [url, setUrl] = useState('');
  const [openaiApiKey, setOpenaiApiKey] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [showAnimation, setShowAnimation] = useState(false);
  const theme = useTheme();

  useEffect(() => {
    setShowAnimation(true);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      new URL(url);
    } catch (err) {
      setError('Please enter a valid URL');
      return;
    }

    if (!openaiApiKey) {
      setError('Please enter your OpenAI API Key');
      return;
    }

    setLoading(true);
    setError(null);
    setAnalysisResult(null);

    try {
      const analysisResult = await analyzeUrl(url, openaiApiKey);
      console.log('API Response:', analysisResult);
      setAnalysisResult(analysisResult);
      
      // Reports are now saved automatically on the backend
      // No need to store in localStorage
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 3, ml: '280px' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
        <SearchIcon sx={{ fontSize: 48, color: theme.palette.primary.main }} />
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
          Threat Report Analysis
        </Typography>
      </Box>
      <Typography variant="subtitle1" color="text.secondary" sx={{ mb: 3, ml: 8 }}>
        Analyze threat reports and extract actionable intelligence.
      </Typography>
      {loading && <LoadingScreen />}
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
                URL Analysis
              </Typography>
              <Box 
                component="form" 
                onSubmit={handleSubmit} 
                sx={{ 
                  display: 'flex', 
                  flexDirection: { xs: 'column', sm: 'row' }, 
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
                  label="Enter URL"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  error={!!error}
                  helperText={error}
                  placeholder="https://example.com"
                  sx={{ flexGrow: 1 }}
                />
                <TextField
                  fullWidth
                  label="OpenAI API Key"
                  type="password"
                  value={openaiApiKey}
                  onChange={(e) => setOpenaiApiKey(e.target.value)}
                  error={!!error}
                  sx={{ flexGrow: 1 }}
                />
                <Button
                  type="submit"
                  variant="contained"
                  disabled={loading}
                  startIcon={loading ? <CircularProgress size={20} /> : <SearchIcon />}
                  sx={{ 
                    minWidth: { xs: '100%', sm: '120px' },
                    height: '56px',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-2px)',
                      boxShadow: `0 4px 12px ${theme.palette.primary.main}40`,
                    },
                  }}
                >
                  {loading ? 'Analyzing...' : 'Analyze'}
                </Button>
              </Box>
            </Paper>
          </Zoom>

          {analysisResult && (
            <Fade in={!!analysisResult} timeout={500}>
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
                      {analysisResult.threat_summary}
                    </Typography>

                    {analysisResult.analysis_data?.indicators_of_compromise && (
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
                          {Object.entries(analysisResult.analysis_data.indicators_of_compromise).map(([key, value]) => (
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

                    {analysisResult.analysis_data?.threat_actors && analysisResult.analysis_data.threat_actors.length > 0 && (
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
                          {analysisResult.analysis_data.threat_actors.map((actor, index) => (
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

                    {analysisResult.analysis_data?.ttps && analysisResult.analysis_data.ttps.length > 0 && (
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
                          {analysisResult.analysis_data.ttps.map((ttp, index) => (
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

                    {analysisResult.analysis_data?.tools_or_malware && analysisResult.analysis_data.tools_or_malware.length > 0 && (
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
                          {analysisResult.analysis_data.tools_or_malware.map((item, index) => {
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

                    {analysisResult.generated_sigma_rules && (
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
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mb: 3 }}>
                          {analysisResult.generated_sigma_rules.split('---').map((rule, index) => {
                            if (!rule.trim()) return null;
                            
                            const titleMatch = rule.match(/title:\s*(.+)/);
                            const descriptionMatch = rule.match(/description:\s*>\s*([\s\S]+?)(?=\n\w|$)/);
                            const levelMatch = rule.match(/level:\s*(.+)/);
                            
                            return (
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
                                      {titleMatch ? titleMatch[1].trim() : `Sigma Rule ${index + 1}`}
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary">
                                      {descriptionMatch ? descriptionMatch[1].trim() : ''}
                                    </Typography>
                                    {levelMatch && (
                                      <Chip
                                        label={levelMatch[1].trim()}
                                        color={
                                          levelMatch[1].trim() === "critical" ? "error" :
                                          levelMatch[1].trim() === "high" ? "warning" :
                                          levelMatch[1].trim() === "medium" ? "info" : "success"
                                        }
                                        size="small"
                                        sx={{ mt: 1 }}
                                      />
                                    )}
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
                                    {rule.trim()}
                                  </Box>
                                </AccordionDetails>
                              </Accordion>
                            );
                          })}
                        </Box>
                      </>
                    )}

                    {analysisResult.siem_queries && (
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
                          {Object.entries(analysisResult.siem_queries).map(([platform, query]) => (
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

                    {analysisResult.yara_rules && analysisResult.yara_rules.length > 0 && (
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
                          {analysisResult.yara_rules.map((rule, index) => (
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

                    {analysisResult.sigma_matches && analysisResult.sigma_matches.length > 0 && (
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
                          Sigma Matches
                        </Typography>
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mb: 3 }}>
                          {analysisResult.sigma_matches.map((match, index) => (
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
                  <SecurityIcon />
                  About Threat Report Analysis
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
                  Advanced threat intelligence platform that leverages AI to analyze URLs and provide comprehensive security insights.
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
                  <li>AI-powered URL analysis</li>
                  <li>Threat actor identification</li>
                  <li>MITRE ATT&CK mapping</li>
                  <li>Sigma/YARA rule generation</li>
                  <li>Global Sigma rule matching</li>
                  <li>IoC/TTP extraction</li>
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