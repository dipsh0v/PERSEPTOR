import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Container,
  Zoom,
  keyframes,
  styled,
  useTheme
} from '@mui/material';
import Grid from '@mui/material/Grid';
import {
  Security as SecurityIcon,
  Search as SearchIcon,
  Description as DescriptionIcon,
  TrackChanges as TrackChangesIcon,
  Storage as StorageIcon,
  Code as CodeIcon,
  BugReport as BugReportIcon,
  Assessment as AssessmentIcon,
  Speed as SpeedIcon,
  Shield as ShieldIcon
} from '@mui/icons-material';

// Parçacık animasyonu için keyframes
const float = keyframes`
  0%, 100% { transform: translateY(0px) rotate(0deg); opacity: 0.7; }
  50% { transform: translateY(-20px) rotate(180deg); opacity: 1; }
`;

const pulse = keyframes`
  0%, 100% { transform: scale(1); opacity: 0.8; }
  50% { transform: scale(1.1); opacity: 1; }
`;

const glitch = keyframes`
  0%, 100% { transform: translate(0); }
  20% { transform: translate(-2px, 2px); }
  40% { transform: translate(-2px, -2px); }
  60% { transform: translate(2px, 2px); }
  80% { transform: translate(2px, -2px); }
`;

const neonGlow = keyframes`
  0%, 100% { box-shadow: 0 0 5px currentColor, 0 0 10px currentColor, 0 0 15px currentColor; }
  50% { box-shadow: 0 0 10px currentColor, 0 0 20px currentColor, 0 0 30px currentColor; }
`;

// Styled components
const Particle = styled(Box)(({ theme }) => ({
  position: 'absolute',
  width: '4px',
  height: '4px',
  background: theme.palette.primary.main,
  borderRadius: '50%',
  animation: `${float} 6s ease-in-out infinite`,
  '&:nth-of-type(odd)': {
    animationDelay: '0s',
    animationDuration: '8s',
  },
  '&:nth-of-type(even)': {
    animationDelay: '2s',
    animationDuration: '10s',
  },
  '&:nth-of-type(3n)': {
    animationDelay: '4s',
    animationDuration: '12s',
  },
}));

const GlitchText = styled(Typography)(({ theme }) => ({
  position: 'relative',
  '&:hover': {
    animation: `${glitch} 0.3s ease-in-out`,
  },
  '&::before, &::after': {
    content: 'attr(data-text)',
    position: 'absolute',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
  },
  '&::before': {
    color: theme.palette.error.main,
    clipPath: 'polygon(0 0, 100% 0, 100% 45%, 0 45%)',
  },
  '&::after': {
    color: theme.palette.info.main,
    clipPath: 'polygon(0 55%, 100% 55%, 100% 100%, 0 100%)',
  },
}));

const NeonCard = styled(Card)(({ theme }) => ({
  position: 'relative',
  transition: 'all 0.3s ease-in-out',
  cursor: 'pointer',
  '&:hover': {
    transform: 'translateY(-4px) scale(1.01)',
    '& .card-icon': {
      transform: 'scale(1.1)',
    },
  },
  '& .card-icon': {
    transition: 'all 0.3s ease-in-out',
  },
}));

const MouseFollower = styled(Box)(({ theme }) => ({
  position: 'fixed',
  width: '20px',
  height: '20px',
  background: `radial-gradient(circle, ${theme.palette.primary.main}40, transparent)`,
  borderRadius: '50%',
  pointerEvents: 'none',
  zIndex: 9999,
  transition: 'all 0.1s ease-out',
  filter: 'blur(1px)',
}));

const AboutPerseptor: React.FC = () => {
  const theme = useTheme();
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [isVisible, setIsVisible] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setIsVisible(true);
    
    let timeoutId: NodeJS.Timeout;
    const handleMouseMove = (e: MouseEvent) => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => {
        setMousePosition({ x: e.clientX, y: e.clientY });
      }, 16); // ~60fps throttling
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      clearTimeout(timeoutId);
    };
  }, []);

  const modules = [
    {
      icon: <SecurityIcon className="card-icon" color="primary" />, title: 'Sigma Rules',
      desc: 'Advanced threat detection using Sigma rules for comprehensive security monitoring.'
    },
    {
      icon: <SearchIcon className="card-icon" color="primary" />, title: 'YARA Rules',
      desc: 'Pattern-based malware detection and classification using YARA signatures.'
    },
    {
      icon: <TrackChangesIcon className="card-icon" color="primary" />, title: 'Detection QA',
      desc: 'Generate, and analyze Sigma rules with AI-powered quality assurance.'
    },
    {
      icon: <StorageIcon className="card-icon" color="primary" />, title: 'Cache Management',
      desc: 'Efficient caching system for optimized performance and data retrieval.'
    },
    {
      icon: <CodeIcon className="card-icon" color="primary" />, title: 'OCR Processing',
      desc: 'Optical Character Recognition for extracting text from images and documents.'
    },
    {
      icon: <AssessmentIcon className="card-icon" color="primary" />, title: 'Global Sigma Match',
      desc: 'Global pattern matching and correlation across multiple Sigma rules.'
    },
    {
      icon: <SpeedIcon className="card-icon" color="primary" />, title: 'Performance',
      desc: 'High-performance processing and real-time threat detection capabilities.'
    },
    {
      icon: <ShieldIcon className="card-icon" color="primary" />, title: 'Security',
      desc: 'Enterprise-grade security with advanced threat protection and monitoring.'
    }
  ];

  return (
    <Box
      ref={containerRef}
      sx={{
        minHeight: '100vh',
        background: `linear-gradient(135deg, ${theme.palette.background.default} 0%, ${theme.palette.background.paper} 100%)`,
        position: 'relative',
        overflow: 'hidden',
        opacity: isVisible ? 1 : 0,
        transition: 'opacity 0.5s ease-in-out',
      }}
    >
      {/* Mouse follower - Lightweight */}
      <MouseFollower
        sx={{
          left: mousePosition.x - 10,
          top: mousePosition.y - 10,
        }}
      />

      <Container maxWidth="lg" sx={{ py: 4, position: 'relative', zIndex: 1 }}>
        <Zoom in={isVisible} style={{ transitionDelay: '200ms' }}>
          <Box sx={{ textAlign: 'center', mb: 6 }}>
            <GlitchText
              variant="h2"
              data-text="About PERSEPTOR"
              sx={{
                background: `linear-gradient(45deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                fontWeight: 'bold',
                mb: 2,
                textShadow: `0 0 20px ${theme.palette.primary.main}40`,
              }}
            >
              About PERSEPTOR
            </GlitchText>
            <Typography
              variant="body2"
              sx={{
                textAlign: 'center',
                opacity: 0.5,
                fontStyle: 'italic',
                fontSize: '1rem',
                mb: 1,
              }}
            >
              (Crafted with passion by <b>Aytek AYTEMUR</b>)
            </Typography>
            <Typography
              variant="h5"
              color="text.secondary"
              sx={{
                mb: 4,
                maxWidth: '800px',
                mx: 'auto',
                lineHeight: 1.6,
                textShadow: `0 0 10px ${theme.palette.text.secondary}20`,
              }}
            >
              AI-driven detection engineering platform that revolutionizes threat intelligence 
              through advanced algorithms, automated detection rule generation, 
              and intelligent security orchestration for next-generation cyber defense.
            </Typography>
          </Box>
        </Zoom>

        <Zoom in={isVisible} style={{ transitionDelay: '400ms' }}>
          <Box sx={{ mb: 6 }}>
            <Typography
              variant="h4"
              component="h2"
              sx={{
                textAlign: 'center',
                mb: 4,
                background: `linear-gradient(45deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                fontWeight: 'bold',
                textShadow: `0 0 15px ${theme.palette.primary.main}30`,
              }}
            >
              Platform Flow
            </Typography>
            <Box
              sx={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                flexWrap: 'wrap',
                gap: 2,
                mb: 4,
              }}
            >
              {['Data Input', 'Processing', 'Analysis', 'Detection', 'Reporting'].map((step, index) => (
                <Box
                  key={step}
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1,
                    px: 3,
                    py: 1.5,
                    borderRadius: '25px',
                    background: `linear-gradient(45deg, ${theme.palette.primary.main}20, ${theme.palette.secondary.main}20)`,
                    border: `1px solid ${theme.palette.primary.main}40`,
                    color: theme.palette.primary.main,
                    fontWeight: 'bold',
                    position: 'relative',
                    overflow: 'hidden',
                    '&::before': {
                      content: '""',
                      position: 'absolute',
                      top: 0,
                      left: '-100%',
                      width: '100%',
                      height: '100%',
                      background: `linear-gradient(90deg, transparent, ${theme.palette.primary.main}20, transparent)`,
                      transition: 'left 0.5s ease-in-out',
                    },
                    '&:hover::before': {
                      left: '100%',
                    },
                                         animation: `${pulse} 4s ease-in-out infinite`,
                     animationDelay: `${index * 0.5}s`,
                  }}
                >
                  <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                    {step}
                  </Typography>
                                     {index < 5 && (
                    <Box
                      sx={{
                        width: '20px',
                        height: '2px',
                        background: `linear-gradient(90deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
                        mx: 1,
                                                 animation: `${pulse} 3s ease-in-out infinite`,
                         animationDelay: `${index * 0.4}s`,
                      }}
                    />
                  )}
                </Box>
              ))}
            </Box>
          </Box>
        </Zoom>

        <Zoom in={isVisible} style={{ transitionDelay: '600ms' }}>
          <Box>
            <Typography
              variant="h4"
              component="h2"
              sx={{
                textAlign: 'center',
                mb: 4,
                background: `linear-gradient(45deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                fontWeight: 'bold',
                textShadow: `0 0 15px ${theme.palette.primary.main}30`,
              }}
            >
              Core Modules
            </Typography>
            <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(3, 1fr)' }, gap: 3 }}>
              {modules.map((module, index) => (
                <Zoom in={isVisible} style={{ transitionDelay: `${800 + index * 100}ms` }} key={module.title}>
                                      <NeonCard
                      sx={{
                        height: '100%',
                        background: `linear-gradient(135deg, ${theme.palette.background.paper} 0%, ${theme.palette.background.default} 100%)`,
                        border: `1px solid ${theme.palette.primary.main}20`,
                        boxShadow: `0 4px 16px ${theme.palette.primary.main}10`,
                      }}
                    >
                      <CardContent
                      sx={{
                        textAlign: 'center',
                        p: 3,
                        position: 'relative',
                        zIndex: 1,
                      }}
                    >
                      <Box
                        sx={{
                          display: 'flex',
                          justifyContent: 'center',
                          mb: 2,
                          '& .MuiSvgIcon-root': {
                            fontSize: '3rem',
                            filter: `drop-shadow(0 0 10px ${theme.palette.primary.main}40)`,
                          },
                        }}
                      >
                        {module.icon}
                      </Box>
                      <Typography
                        variant="h6"
                        sx={{
                          mb: 1,
                          fontWeight: 'bold',
                          background: `linear-gradient(45deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
                          backgroundClip: 'text',
                          WebkitBackgroundClip: 'text',
                          WebkitTextFillColor: 'transparent',
                        }}
                      >
                        {module.title}
                      </Typography>
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{
                          lineHeight: 1.6,
                          textShadow: `0 0 5px ${theme.palette.text.secondary}10`,
                        }}
                      >
                        {module.desc}
                      </Typography>
                    </CardContent>
                  </NeonCard>
                </Zoom>
              ))}
            </Box>
          </Box>
        </Zoom>
      </Container>
    </Box>
  );
};

export default AboutPerseptor; 