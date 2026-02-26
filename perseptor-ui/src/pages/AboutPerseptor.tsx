/**
 * PERSEPTOR v2.0 - About Page
 * Premium 2026 cybersecurity showcase — designed to impress.
 * Scroll-driven reveal animations, glassmorphic design, Atomic Red Team showcase.
 */

import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Chip,
  keyframes,
  styled,
} from '@mui/material';
import { useTheme } from '@mui/material/styles';
import { alpha } from '@mui/material/styles';
import {
  Security as SecurityIcon,
  Search as SearchIcon,
  TrackChanges as TrackChangesIcon,
  Code as CodeIcon,
  Speed as SpeedIcon,
  ArrowForward as ArrowForwardIcon,
  Psychology as PsychologyIcon,
  BugReport as BugReportIcon,
  Visibility as VisibilityIcon,
  Bolt as BoltIcon,
  CheckCircle as CheckCircleIcon,
  Hub as HubIcon,
  Science as ScienceIcon,
  Terminal as TerminalIcon,
  Gavel as GavelIcon,
  VerifiedUser as VerifiedUserIcon,
} from '@mui/icons-material';

/* ── Design Tokens ── */
const PRIMARY = '#6366f1';
const SECONDARY = '#ec4899';
const PURPLE = '#8b5cf6';
const CODE_FONT = '"JetBrains Mono", "Fira Code", monospace';
const EASING = 'cubic-bezier(0.4, 0, 0.2, 1)';
const ATOMIC_COLOR = '#f97316';

/* ── Keyframes ── */
const shimmer = keyframes`
  0% { background-position: -200% center; }
  100% { background-position: 200% center; }
`;

const glitch = keyframes`
  0%, 100% { transform: translate(0); }
  20% { transform: translate(-2px, 2px); }
  40% { transform: translate(-2px, -2px); }
  60% { transform: translate(2px, 2px); }
  80% { transform: translate(2px, -2px); }
`;

const pulseStep = keyframes`
  0%, 100% { transform: scale(1); opacity: 0.85; }
  50% { transform: scale(1.04); opacity: 1; }
`;

const connectorFlow = keyframes`
  0% { background-position: 0% 50%; }
  100% { background-position: 200% 50%; }
`;

const heroGlow = keyframes`
  0%, 100% { opacity: 0.4; }
  50% { opacity: 0.7; }
`;

const terminalBlink = keyframes`
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
`;

const scanline = keyframes`
  0% { transform: translateY(-100%); }
  100% { transform: translateY(100%); }
`;

const particleFloat = keyframes`
  0%, 100% { transform: translate(0, 0) rotate(0deg); opacity: 0.3; }
  25% { transform: translate(10px, -15px) rotate(90deg); opacity: 0.6; }
  50% { transform: translate(-5px, -25px) rotate(180deg); opacity: 0.4; }
  75% { transform: translate(-15px, -10px) rotate(270deg); opacity: 0.7; }
`;

/* ── Styled Components ── */
const GlitchText = styled(Typography)(() => ({
  position: 'relative',
  cursor: 'default',
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
    pointerEvents: 'none',
  },
  '&::before': {
    color: '#f43f5e',
    clipPath: 'polygon(0 0, 100% 0, 100% 45%, 0 45%)',
    opacity: 0,
  },
  '&::after': {
    color: '#3b82f6',
    clipPath: 'polygon(0 55%, 100% 55%, 100% 100%, 0 100%)',
    opacity: 0,
  },
  '&:hover::before, &:hover::after': {
    opacity: 0.7,
  },
}));

/* ── Scroll-driven reveal hook ── */
function useScrollReveal(threshold = 0.15): [React.RefObject<HTMLDivElement | null>, boolean] {
  const ref = useRef<HTMLDivElement | null>(null);
  const [isRevealed, setIsRevealed] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsRevealed(true);
          observer.unobserve(el);
        }
      },
      { threshold, rootMargin: '0px 0px -60px 0px' }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, [threshold]);

  return [ref, isRevealed];
}

/* ── Section wrapper with scroll reveal ── */
const RevealSection: React.FC<{
  children: React.ReactNode;
  delay?: number;
}> = ({ children, delay = 0 }) => {
  const [ref, isRevealed] = useScrollReveal(0.1);
  return (
    <Box
      ref={ref}
      sx={{
        opacity: isRevealed ? 1 : 0,
        transform: isRevealed ? 'translateY(0)' : 'translateY(50px)',
        transition: `opacity 0.8s ${EASING} ${delay}s, transform 0.8s ${EASING} ${delay}s`,
      }}
    >
      {children}
    </Box>
  );
};

const AboutPerseptor: React.FC = () => {
  const theme = useTheme();
  const [isVisible, setIsVisible] = useState(false);
  const [countStarted, setCountStarted] = useState(false);
  const [statsRef, statsRevealed] = useScrollReveal(0.3);

  useEffect(() => {
    setIsVisible(true);
  }, []);

  useEffect(() => {
    if (statsRevealed) setCountStarted(true);
  }, [statsRevealed]);

  /* ── Animated counter ── */
  const AnimatedNumber: React.FC<{ target: string; started: boolean; color: string }> = ({ target, started, color }) => {
    const [display, setDisplay] = useState('0');
    const numericPart = target.replace(/[^0-9]/g, '');
    const suffix = target.replace(/[0-9]/g, '');

    useEffect(() => {
      if (!started) return;
      const end = parseInt(numericPart, 10);
      if (isNaN(end)) { setDisplay(target); return; }
      const duration = 1500;
      const startTime = Date.now();
      const step = () => {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        const current = Math.round(eased * end);
        setDisplay(current.toLocaleString() + suffix);
        if (progress < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    }, [started, numericPart, suffix, target]);

    return (
      <Typography
        sx={{
          fontFamily: CODE_FONT,
          fontWeight: 900,
          fontSize: { xs: '1.8rem', md: '2.4rem' },
          color,
          lineHeight: 1,
          mb: 0.3,
          filter: `drop-shadow(0 0 10px ${alpha(color, 0.35)})`,
          transition: 'all 0.3s ease',
        }}
      >
        {started ? display : '0'}
      </Typography>
    );
  };

  /* ── Problem-Solution pairs ── */
  const problemSolutions = [
    {
      problem: 'Threat intelligence reports take hours to analyze manually',
      solution: 'AI-powered analysis extracts IoCs, TTPs, and threat context in seconds',
      icon: <PsychologyIcon />, accent: PRIMARY, stat: '60x', statLabel: 'Faster',
    },
    {
      problem: 'Writing Sigma rules requires deep expertise and is error-prone',
      solution: 'Automated Sigma rule generation with 7-component quality scoring',
      icon: <SecurityIcon />, accent: PURPLE, stat: '7', statLabel: 'QA Metrics',
    },
    {
      problem: 'No way to validate if generated rules match known threat patterns',
      solution: 'Global Sigma Match engine scores rules against 2,750+ SigmaHQ rules',
      icon: <HubIcon />, accent: '#3b82f6', stat: '2,750+', statLabel: 'Rules',
    },
    {
      problem: 'Converting detections across SIEM platforms is tedious and inconsistent',
      solution: 'One-click conversion to Splunk SPL, QRadar AQL, Elastic KQL, Sentinel KQL',
      icon: <BoltIcon />, accent: '#f59e0b', stat: '4', statLabel: 'SIEMs',
    },
    {
      problem: 'No way to test if detection rules actually catch the threats they target',
      solution: 'AI generates Atomic Red Team test scenarios with copy-pasteable commands, expected detection output, and cleanup',
      icon: <ScienceIcon />, accent: ATOMIC_COLOR, stat: '1:1', statLabel: 'Rule→Test',
    },
    {
      problem: 'False positives in IoC extraction waste analyst time and erode trust',
      solution: 'Expert-level filtering removes contact emails, vendor domains, and noise',
      icon: <BugReportIcon />, accent: '#ef4444', stat: '95%', statLabel: 'Precision',
    },
    {
      problem: 'Understanding MITRE ATT&CK coverage gaps across detections is complex',
      solution: 'Automatic MITRE mapping with kill chain visualization and evidence',
      icon: <VisibilityIcon />, accent: '#10b981', stat: '14', statLabel: 'Tactics',
    },
  ];

  /* ── Core architecture modules ── */
  const modules = [
    {
      icon: <PsychologyIcon />,
      title: 'AI Analysis Engine',
      desc: 'Multi-provider AI backbone (OpenAI, Anthropic, Google) with chain-of-thought prompting.',
      accent: PRIMARY,
      tech: ['GPT-4o', 'Claude', 'Gemini'],
    },
    {
      icon: <SearchIcon />,
      title: 'Smart URL Fetcher',
      desc: 'Multi-strategy extraction with Playwright JS rendering fallback. Handles bot protection.',
      accent: '#14b8a6',
      tech: ['Playwright', 'BeautifulSoup', 'OCR'],
    },
    {
      icon: <SecurityIcon />,
      title: 'Sigma Rule Engine',
      desc: 'Production-quality Sigma rules following SigmaHQ conventions with selection+filter patterns.',
      accent: PURPLE,
      tech: ['YAML', 'SigmaHQ', 'Detection'],
    },
    {
      icon: <ScienceIcon />,
      title: 'Atomic Test Engine',
      desc: 'AI-generated Atomic Red Team scenarios per Sigma rule with execution steps, expected output, and cleanup.',
      accent: ATOMIC_COLOR,
      tech: ['Red Team', 'Validation', 'Safe Tests'],
    },
    {
      icon: <TrackChangesIcon />,
      title: 'Detection QA',
      desc: '7-component confidence scoring: complexity, coverage, specificity, MITRE alignment, quality.',
      accent: SECONDARY,
      tech: ['7 Algorithms', 'Explanations', 'Weights'],
    },
    {
      icon: <HubIcon />,
      title: 'Global Sigma Match',
      desc: 'Multi-signal scoring: MITRE match, IoC fields, logsource routing, TF-IDF keyword analysis.',
      accent: '#3b82f6',
      tech: ['TF-IDF', '2,750 Rules', '4 Signals'],
    },
    {
      icon: <BoltIcon />,
      title: 'SIEM Converter',
      desc: 'Platform-optimized queries for Splunk SPL, QRadar AQL, Elasticsearch, Sentinel KQL.',
      accent: '#f59e0b',
      tech: ['Splunk', 'QRadar', 'Elastic', 'Sentinel'],
    },
    {
      icon: <CodeIcon />,
      title: 'YARA Engine',
      desc: 'Pattern-based malware detection rules with hex patterns, string matching, and conditions.',
      accent: '#22c55e',
      tech: ['Hex Patterns', 'Strings', 'Conditions'],
    },
    {
      icon: <SpeedIcon />,
      title: 'SSE Streaming',
      desc: 'Real-time Server-Sent Events with parallel AI execution and live progress tracking.',
      accent: '#f43f5e',
      tech: ['SSE', 'Parallel', 'Real-time'],
    },
  ];

  const pipelineSteps = [
    { label: 'URL / Text Input', icon: '01' },
    { label: 'Smart Extraction', icon: '02' },
    { label: 'AI Analysis', icon: '03' },
    { label: 'Rule Generation', icon: '04' },
    { label: 'Atomic Testing', icon: '05' },
    { label: 'QA & Matching', icon: '06' },
    { label: 'SIEM Export', icon: '07' },
  ];

  /* ── Stats ── */
  const stats = [
    { value: '2750+', label: 'Sigma Rules in Database', color: PRIMARY },
    { value: '4', label: 'SIEM Platforms', color: '#f59e0b' },
    { value: '7', label: 'QA Scoring Algorithms', color: SECONDARY },
    { value: '3', label: 'AI Providers Supported', color: PURPLE },
    { value: '14', label: 'MITRE ATT&CK Tactics', color: '#10b981' },
    { value: '9', label: 'Analysis Modules', color: '#3b82f6' },
  ];

  /* ── Atomic Red Team showcase data ── */
  const atomicFeatures = [
    {
      icon: <TerminalIcon />,
      title: 'Copy-Pasteable Commands',
      desc: 'Every test includes an exact command you can paste into PowerShell, CMD, or Bash. No guessing, no scripting — just execute.',
      color: '#10b981',
    },
    {
      icon: <VerifiedUserIcon />,
      title: 'Expected Detection Output',
      desc: 'Know exactly which Event IDs, log sources, and field values your SIEM should capture when the test triggers.',
      color: PRIMARY,
    },
    {
      icon: <ScienceIcon />,
      title: 'Safe & Reversible',
      desc: 'Uses harmless payloads (calc.exe, notepad.exe) with cleanup commands. Every test is designed for controlled lab environments.',
      color: '#f59e0b',
    },
    {
      icon: <GavelIcon />,
      title: 'Real-World References',
      desc: 'Maps to APT groups, malware families, and official Atomic Red Team test IDs. Backed by MITRE ATT&CK intelligence.',
      color: ATOMIC_COLOR,
    },
  ];

  /* ── Terminal animation for Atomic showcase ── */
  const terminalLines = [
    { prefix: '$', text: 'invoke-atomictest T1059.001 -TestNumbers 1', color: '#10b981' },
    { prefix: '>', text: 'Executing: PowerShell Download Cradle...', color: '#94a3b8' },
    { prefix: '>', text: 'Process Created: powershell.exe -NoProfile', color: '#e6edf3' },
    { prefix: '[+]', text: 'Sysmon Event ID 1 triggered', color: '#f59e0b' },
    { prefix: '[+]', text: 'Security Event 4688 logged', color: '#f59e0b' },
    { prefix: '[✓]', text: 'Sigma rule "Suspicious PowerShell Download" MATCHED', color: '#10b981' },
    { prefix: '$', text: 'cleanup -RemoveArtifacts', color: '#94a3b8' },
    { prefix: '[✓]', text: 'All artifacts cleaned. Test complete.', color: '#10b981' },
  ];

  const [visibleLines, setVisibleLines] = useState(0);
  const [termRef, termRevealed] = useScrollReveal(0.3);

  useEffect(() => {
    if (!termRevealed) return;
    let i = 0;
    const interval = setInterval(() => {
      i++;
      setVisibleLines(i);
      if (i >= terminalLines.length) clearInterval(interval);
    }, 400);
    return () => clearInterval(interval);
  }, [termRevealed]);

  return (
    <Box
      sx={{
        minHeight: '100vh',
        position: 'relative',
        overflow: 'hidden',
        p: { xs: 2, md: 4 },
      }}
    >
      {/* ── Ambient background glows ── */}
      {[
        { top: '-20%', right: '-10%', size: 600, color: PRIMARY, dur: 6, delay: 0 },
        { bottom: '-15%', left: '-5%', size: 500, color: SECONDARY, dur: 8, delay: 3 },
        { top: '40%', left: '50%', size: 800, color: PURPLE, dur: 10, delay: 5, transform: 'translateX(-50%)' },
      ].map((g, i) => (
        <Box
          key={i}
          sx={{
            position: 'fixed',
            ...(g.top !== undefined ? { top: g.top } : {}),
            ...(g.bottom !== undefined ? { bottom: g.bottom } : {}),
            ...(g.left !== undefined ? { left: g.left } : {}),
            ...(g.right !== undefined ? { right: g.right } : {}),
            ...(g.transform ? { transform: g.transform } : {}),
            width: g.size, height: g.size,
            borderRadius: '50%',
            background: `radial-gradient(circle, ${alpha(g.color, 0.06)} 0%, transparent 70%)`,
            animation: `${heroGlow} ${g.dur}s ease-in-out infinite`,
            animationDelay: `${g.delay}s`,
            pointerEvents: 'none',
            zIndex: 0,
          }}
        />
      ))}

      <Box sx={{ position: 'relative', zIndex: 1, maxWidth: 1200, mx: 'auto' }}>
        {/* ════════════════════ HERO SECTION ════════════════════ */}
        <Box
          sx={{
            textAlign: 'center',
            pt: { xs: 4, md: 6 },
            pb: { xs: 4, md: 5 },
            mb: 2,
            opacity: isVisible ? 1 : 0,
            transform: isVisible ? 'translateY(0)' : 'translateY(30px)',
            transition: `all 1s ${EASING}`,
          }}
        >
          <GlitchText
            variant="h1"
            data-text="PERSEPTOR"
            sx={{
              fontFamily: '"Inter", sans-serif',
              fontWeight: 900,
              fontSize: { xs: '3rem', sm: '4rem', md: '5.5rem' },
              letterSpacing: '-0.04em',
              lineHeight: 1.1,
              background: `linear-gradient(135deg, ${PRIMARY} 0%, ${PURPLE} 25%, ${SECONDARY} 50%, ${PURPLE} 75%, ${PRIMARY} 100%)`,
              backgroundSize: '200% auto',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              animation: `${shimmer} 5s linear infinite`,
              mb: 2,
              filter: `drop-shadow(0 0 40px ${alpha(PRIMARY, 0.2)})`,
            }}
          >
            PERSEPTOR
          </GlitchText>

          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 1, mb: 2.5 }}>
            <Chip
              label="v2.0"
              size="small"
              sx={{
                fontFamily: CODE_FONT, fontWeight: 800, fontSize: '0.7rem',
                background: `linear-gradient(135deg, ${PRIMARY}, ${PURPLE})`,
                color: '#fff', letterSpacing: '0.05em',
              }}
            />
            <Chip
              label="AI-Powered"
              size="small"
              sx={{
                fontFamily: '"Inter", sans-serif', fontWeight: 600, fontSize: '0.68rem',
                backgroundColor: alpha(SECONDARY, 0.1), color: SECONDARY,
                border: `1px solid ${alpha(SECONDARY, 0.2)}`,
              }}
            />
            <Chip
              label="Atomic Red Team"
              size="small"
              sx={{
                fontFamily: '"Inter", sans-serif', fontWeight: 600, fontSize: '0.68rem',
                backgroundColor: alpha(ATOMIC_COLOR, 0.1), color: ATOMIC_COLOR,
                border: `1px solid ${alpha(ATOMIC_COLOR, 0.2)}`,
              }}
            />
          </Box>

          <Typography
            variant="body2"
            sx={{
              fontFamily: '"Inter", sans-serif', fontStyle: 'italic', fontSize: '1rem',
              color: alpha(theme.palette.text.secondary, 0.5), mb: 3,
            }}
          >
            Crafted with passion by <strong>Aytek AYTEMUR</strong>
          </Typography>

          <Typography
            variant="h6"
            sx={{
              fontFamily: '"Inter", sans-serif', fontWeight: 400,
              color: alpha(theme.palette.text.secondary, 0.75),
              maxWidth: 850, mx: 'auto', lineHeight: 1.8,
              fontSize: { xs: '0.95rem', md: '1.1rem' },
            }}
          >
            The Detection Engineering Platform that transforms raw threat intelligence into
            production-ready detection rules &mdash; then validates them with AI-generated
            Atomic Red Team test scenarios. From URL to tested SIEM query, powered by
            multi-provider AI, validated by 2,750+ Sigma rules, and scored by 7 quality algorithms.
          </Typography>
        </Box>

        {/* ════════════════════ ANIMATED STATS BAR ════════════════════ */}
        <RevealSection>
          <Box
            ref={statsRef}
            sx={{
              display: 'flex', flexWrap: 'wrap', justifyContent: 'center',
              gap: { xs: 2, md: 3 }, mb: 8, px: 2,
            }}
          >
            {stats.map((stat) => (
              <Box key={stat.label} sx={{ textAlign: 'center' }}>
                <AnimatedNumber target={stat.value} started={countStarted} color={stat.color} />
                <Typography
                  sx={{
                    fontFamily: '"Inter", sans-serif', fontSize: '0.68rem', fontWeight: 500,
                    color: alpha(theme.palette.text.secondary, 0.6),
                    letterSpacing: '0.05em', textTransform: 'uppercase', maxWidth: 100,
                  }}
                >
                  {stat.label}
                </Typography>
              </Box>
            ))}
          </Box>
        </RevealSection>

        {/* ════════════════════ PIPELINE (7 steps now) ════════════════════ */}
        <RevealSection>
          <Box sx={{ mb: 10 }}>
            <Box sx={{ textAlign: 'center', mb: 5 }}>
              <Typography
                variant="h4"
                sx={{
                  fontFamily: '"Inter", sans-serif', fontWeight: 800,
                  background: `linear-gradient(135deg, ${PRIMARY}, ${SECONDARY})`,
                  backgroundClip: 'text', WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  fontSize: { xs: '1.5rem', md: '2rem' }, mb: 1,
                }}
              >
                How It Works
              </Typography>
              <Typography variant="body2" sx={{ color: alpha(theme.palette.text.secondary, 0.6), maxWidth: 550, mx: 'auto' }}>
                From raw threat intelligence to tested, production-ready detections in 7 automated stages
              </Typography>
            </Box>

            <Box
              sx={{
                display: 'flex', justifyContent: 'center', alignItems: 'center',
                flexWrap: 'wrap', gap: { xs: 1, md: 0 },
              }}
            >
              {pipelineSteps.map((step, index) => {
                const isAtomic = step.label === 'Atomic Testing';
                const stepColor = isAtomic ? ATOMIC_COLOR : PRIMARY;
                return (
                  <Box
                    key={step.label}
                    sx={{ display: 'flex', alignItems: 'center' }}
                  >
                    <Box
                      sx={{
                        px: { xs: 1.5, md: 2.5 },
                        py: { xs: 1, md: 1.3 },
                        borderRadius: '14px',
                        background: alpha(theme.palette.background.paper, 0.7),
                        backdropFilter: 'blur(16px)',
                        border: `1px solid ${alpha(stepColor, isAtomic ? 0.3 : 0.15)}`,
                        position: 'relative', overflow: 'hidden',
                        animation: `${pulseStep} 4s ease-in-out infinite`,
                        animationDelay: `${index * 0.5}s`,
                        transition: `all 0.3s ${EASING}`,
                        cursor: 'default',
                        ...(isAtomic ? {
                          boxShadow: `0 0 20px ${alpha(ATOMIC_COLOR, 0.1)}, inset 0 1px 0 ${alpha(ATOMIC_COLOR, 0.05)}`,
                        } : {}),
                        '&:hover': {
                          borderColor: alpha(stepColor, 0.5),
                          boxShadow: `0 4px 20px ${alpha(stepColor, 0.15)}`,
                          transform: 'translateY(-2px) !important',
                          '& .step-number': {
                            background: `linear-gradient(135deg, ${stepColor}, ${alpha(stepColor, 0.7)})`,
                            color: '#fff',
                          },
                        },
                      }}
                    >
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.2 }}>
                        <Box
                          className="step-number"
                          sx={{
                            width: 24, height: 24, borderRadius: '7px',
                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                            background: alpha(stepColor, 0.1), color: stepColor,
                            fontFamily: CODE_FONT, fontWeight: 800, fontSize: '0.68rem',
                            transition: `all 0.3s ${EASING}`,
                          }}
                        >
                          {step.icon}
                        </Box>
                        <Typography
                          variant="body2"
                          sx={{
                            fontFamily: '"Inter", sans-serif', fontWeight: 700,
                            fontSize: { xs: '0.7rem', md: '0.78rem' },
                            color: isAtomic ? ATOMIC_COLOR : theme.palette.text.primary,
                            letterSpacing: '0.01em', whiteSpace: 'nowrap',
                          }}
                        >
                          {step.label}
                        </Typography>
                      </Box>
                    </Box>

                    {index < pipelineSteps.length - 1 && (
                      <Box sx={{ display: { xs: 'none', md: 'flex' }, alignItems: 'center', mx: 0.3 }}>
                        <Box
                          sx={{
                            width: 20, height: 2, borderRadius: 1,
                            background: `linear-gradient(90deg, ${alpha(PRIMARY, 0.6)}, ${alpha(SECONDARY, 0.6)}, ${alpha(PRIMARY, 0.6)})`,
                            backgroundSize: '200% 100%',
                            animation: `${connectorFlow} 2s linear infinite`,
                            animationDelay: `${index * 0.3}s`,
                          }}
                        />
                        <ArrowForwardIcon sx={{ fontSize: 12, color: alpha(PRIMARY, 0.4), ml: -0.5 }} />
                      </Box>
                    )}
                  </Box>
                );
              })}
            </Box>
          </Box>
        </RevealSection>

        {/* ════════════════════ ATOMIC RED TEAM SHOWCASE ════════════════════ */}
        <RevealSection>
          <Box sx={{ mb: 10 }}>
            <Box sx={{ textAlign: 'center', mb: 5 }}>
              <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 1.5, mb: 1.5 }}>
                <ScienceIcon sx={{ fontSize: 32, color: ATOMIC_COLOR }} />
                <Typography
                  variant="h4"
                  sx={{
                    fontFamily: '"Inter", sans-serif', fontWeight: 800,
                    background: `linear-gradient(135deg, ${ATOMIC_COLOR}, #ef4444)`,
                    backgroundClip: 'text', WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    fontSize: { xs: '1.5rem', md: '2rem' },
                  }}
                >
                  Atomic Red Team Integration
                </Typography>
              </Box>
              <Typography variant="body2" sx={{ color: alpha(theme.palette.text.secondary, 0.6), maxWidth: 600, mx: 'auto' }}>
                Every generated Sigma rule comes with a tailored atomic test scenario &mdash;
                so you can validate your detections before deploying to production
              </Typography>
            </Box>

            <Box sx={{ display: 'flex', flexDirection: { xs: 'column', lg: 'row' }, gap: 4, alignItems: 'stretch' }}>
              {/* Left: Terminal simulation */}
              <Box
                ref={termRef}
                sx={{
                  flex: { lg: '1 1 55%' },
                  borderRadius: '16px',
                  overflow: 'hidden',
                  border: `1px solid ${alpha(ATOMIC_COLOR, 0.15)}`,
                  background: alpha('#0d1117', 0.97),
                  position: 'relative',
                }}
              >
                {/* Terminal header */}
                <Box sx={{
                  px: 2, py: 1.2, display: 'flex', alignItems: 'center', gap: 1,
                  background: alpha('#161b22', 0.95),
                  borderBottom: `1px solid ${alpha('#30363d', 0.5)}`,
                }}>
                  <Box sx={{ display: 'flex', gap: 0.8 }}>
                    {['#ff5f57', '#febc2e', '#28c840'].map((c) => (
                      <Box key={c} sx={{ width: 10, height: 10, borderRadius: '50%', backgroundColor: c }} />
                    ))}
                  </Box>
                  <Typography sx={{ fontFamily: CODE_FONT, fontSize: '0.68rem', color: alpha('#e6edf3', 0.5), ml: 1 }}>
                    atomic-red-team — validation
                  </Typography>
                </Box>

                {/* Scanline effect */}
                <Box sx={{
                  position: 'absolute', top: 0, left: 0, right: 0, bottom: 0,
                  pointerEvents: 'none', zIndex: 1, overflow: 'hidden',
                  '&::after': {
                    content: '""', position: 'absolute', left: 0, right: 0,
                    height: '2px', background: `linear-gradient(90deg, transparent, ${alpha(ATOMIC_COLOR, 0.1)}, transparent)`,
                    animation: `${scanline} 4s linear infinite`,
                  },
                }} />

                {/* Terminal content */}
                <Box sx={{ p: 2.5, minHeight: 280, position: 'relative', zIndex: 2 }}>
                  {terminalLines.map((line, i) => (
                    <Box
                      key={i}
                      sx={{
                        display: 'flex', gap: 1, mb: 0.8,
                        opacity: i < visibleLines ? 1 : 0,
                        transform: i < visibleLines ? 'translateX(0)' : 'translateX(-10px)',
                        transition: `all 0.3s ${EASING} ${i * 0.05}s`,
                      }}
                    >
                      <Typography sx={{
                        fontFamily: CODE_FONT, fontSize: '0.75rem', color: alpha(ATOMIC_COLOR, 0.7),
                        fontWeight: 700, minWidth: 24, userSelect: 'none',
                      }}>
                        {line.prefix}
                      </Typography>
                      <Typography sx={{
                        fontFamily: CODE_FONT, fontSize: '0.75rem', color: line.color, lineHeight: 1.6,
                      }}>
                        {line.text}
                      </Typography>
                    </Box>
                  ))}
                  {/* Blinking cursor */}
                  {visibleLines >= terminalLines.length && (
                    <Box sx={{ display: 'flex', gap: 1, mt: 0.5 }}>
                      <Typography sx={{ fontFamily: CODE_FONT, fontSize: '0.75rem', color: alpha(ATOMIC_COLOR, 0.7), fontWeight: 700, minWidth: 24 }}>
                        $
                      </Typography>
                      <Box sx={{
                        width: 8, height: 16, backgroundColor: ATOMIC_COLOR,
                        animation: `${terminalBlink} 1s step-end infinite`,
                      }} />
                    </Box>
                  )}
                </Box>
              </Box>

              {/* Right: Feature cards */}
              <Box sx={{ flex: { lg: '1 1 45%' }, display: 'flex', flexDirection: 'column', gap: 2 }}>
                {atomicFeatures.map((feat, i) => (
                  <RevealSection key={feat.title} delay={i * 0.12}>
                    <Card
                      elevation={0}
                      sx={{
                        borderRadius: '14px',
                        background: alpha(theme.palette.background.paper, 0.5),
                        backdropFilter: 'blur(20px)',
                        border: `1px solid ${alpha(feat.color, 0.1)}`,
                        transition: `all 0.35s ${EASING}`,
                        cursor: 'default',
                        '&:hover': {
                          borderColor: alpha(feat.color, 0.35),
                          boxShadow: `0 8px 32px ${alpha(feat.color, 0.12)}`,
                          transform: 'translateX(6px)',
                          '& .feat-icon': {
                            background: `linear-gradient(135deg, ${feat.color}, ${alpha(feat.color, 0.7)})`,
                            '& .MuiSvgIcon-root': { color: '#fff !important' },
                          },
                        },
                      }}
                    >
                      <CardContent sx={{ p: 2.5, display: 'flex', gap: 2, alignItems: 'flex-start' }}>
                        <Box
                          className="feat-icon"
                          sx={{
                            width: 44, height: 44, borderRadius: '12px',
                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                            background: alpha(feat.color, 0.08),
                            border: `1px solid ${alpha(feat.color, 0.12)}`,
                            transition: `all 0.35s ${EASING}`, flexShrink: 0,
                            '& .MuiSvgIcon-root': { fontSize: '1.3rem', color: feat.color, transition: 'all 0.3s ease' },
                          }}
                        >
                          {feat.icon}
                        </Box>
                        <Box>
                          <Typography variant="subtitle2" sx={{
                            fontFamily: '"Inter", sans-serif', fontWeight: 700,
                            fontSize: '0.88rem', mb: 0.5, color: theme.palette.text.primary,
                          }}>
                            {feat.title}
                          </Typography>
                          <Typography variant="body2" sx={{
                            fontFamily: '"Inter", sans-serif', fontSize: '0.78rem',
                            color: alpha(theme.palette.text.secondary, 0.7), lineHeight: 1.65,
                          }}>
                            {feat.desc}
                          </Typography>
                        </Box>
                      </CardContent>
                    </Card>
                  </RevealSection>
                ))}
              </Box>
            </Box>
          </Box>
        </RevealSection>

        {/* ════════════════════ PROBLEM → SOLUTION SECTION ════════════════════ */}
        <RevealSection>
          <Box sx={{ mb: 10 }}>
            <Box sx={{ textAlign: 'center', mb: 5 }}>
              <Typography
                variant="h4"
                sx={{
                  fontFamily: '"Inter", sans-serif', fontWeight: 800,
                  background: `linear-gradient(135deg, ${PRIMARY}, ${SECONDARY})`,
                  backgroundClip: 'text', WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  fontSize: { xs: '1.5rem', md: '2rem' }, mb: 1,
                }}
              >
                Problems We Solve
              </Typography>
              <Typography variant="body2" sx={{ color: alpha(theme.palette.text.secondary, 0.6), maxWidth: 550, mx: 'auto' }}>
                Every feature exists because a real detection engineering pain point demanded a solution
              </Typography>
            </Box>

            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2.5 }}>
              {problemSolutions.map((item, index) => (
                <RevealSection key={index} delay={index * 0.06}>
                  <Card
                    elevation={0}
                    sx={{
                      borderRadius: '16px',
                      background: alpha(theme.palette.background.paper, 0.5),
                      backdropFilter: 'blur(20px)',
                      border: `1px solid ${alpha(item.accent, 0.08)}`,
                      overflow: 'hidden', transition: `all 0.35s ${EASING}`, cursor: 'default',
                      '&:hover': {
                        borderColor: alpha(item.accent, 0.25),
                        boxShadow: `0 8px 32px ${alpha(item.accent, 0.1)}`,
                        transform: 'translateX(4px)',
                        '& .solution-indicator': {
                          background: `linear-gradient(135deg, ${item.accent}, ${alpha(item.accent, 0.7)})`,
                          color: '#fff',
                          '& .MuiSvgIcon-root': { color: '#fff !important' },
                        },
                      },
                    }}
                  >
                    <CardContent sx={{ p: { xs: 2.5, md: 3 } }}>
                      <Box sx={{ display: 'flex', gap: { xs: 2, md: 3 }, alignItems: 'flex-start' }}>
                        <Box
                          className="solution-indicator"
                          sx={{
                            minWidth: 64, height: 64, borderRadius: '16px',
                            display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
                            background: alpha(item.accent, 0.08), border: `1px solid ${alpha(item.accent, 0.12)}`,
                            transition: `all 0.35s ${EASING}`, flexShrink: 0,
                            '& .MuiSvgIcon-root': { fontSize: '1.5rem', color: item.accent, transition: `all 0.3s ${EASING}` },
                          }}
                        >
                          {item.icon}
                        </Box>
                        <Box sx={{ flex: 1, minWidth: 0 }}>
                          <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2, mb: 0.8 }}>
                            <Box sx={{ flex: 1 }}>
                              <Typography
                                variant="body2"
                                sx={{
                                  fontFamily: '"Inter", sans-serif',
                                  color: alpha(theme.palette.text.secondary, 0.5),
                                  fontSize: '0.78rem', lineHeight: 1.5, mb: 0.5,
                                  textDecoration: 'line-through',
                                  textDecorationColor: alpha(theme.palette.error.main, 0.3),
                                }}
                              >
                                {item.problem}
                              </Typography>
                              <Typography
                                variant="body2"
                                sx={{
                                  fontFamily: '"Inter", sans-serif', color: theme.palette.text.primary,
                                  fontSize: '0.88rem', fontWeight: 500, lineHeight: 1.6,
                                  display: 'flex', alignItems: 'flex-start', gap: 0.8,
                                }}
                              >
                                <CheckCircleIcon sx={{ fontSize: 16, color: item.accent, mt: 0.3, flexShrink: 0 }} />
                                {item.solution}
                              </Typography>
                            </Box>
                            <Box sx={{ textAlign: 'center', flexShrink: 0, display: { xs: 'none', sm: 'block' } }}>
                              <Typography sx={{
                                fontFamily: CODE_FONT, fontWeight: 900, fontSize: '1.5rem',
                                color: item.accent, lineHeight: 1,
                              }}>
                                {item.stat}
                              </Typography>
                              <Typography sx={{
                                fontFamily: '"Inter", sans-serif', fontSize: '0.6rem', fontWeight: 600,
                                color: alpha(theme.palette.text.secondary, 0.5),
                                textTransform: 'uppercase', letterSpacing: '0.08em',
                              }}>
                                {item.statLabel}
                              </Typography>
                            </Box>
                          </Box>
                        </Box>
                      </Box>
                    </CardContent>
                  </Card>
                </RevealSection>
              ))}
            </Box>
          </Box>
        </RevealSection>

        {/* ════════════════════ ARCHITECTURE MODULES ════════════════════ */}
        <RevealSection>
          <Box sx={{ mb: 10 }}>
            <Box sx={{ textAlign: 'center', mb: 5 }}>
              <Typography
                variant="h4"
                sx={{
                  fontFamily: '"Inter", sans-serif', fontWeight: 800,
                  background: `linear-gradient(135deg, ${PRIMARY}, ${SECONDARY})`,
                  backgroundClip: 'text', WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  fontSize: { xs: '1.5rem', md: '2rem' }, mb: 1,
                }}
              >
                Architecture
              </Typography>
              <Typography variant="body2" sx={{ color: alpha(theme.palette.text.secondary, 0.6), maxWidth: 500, mx: 'auto' }}>
                9 specialized modules working in concert to deliver end-to-end detection engineering
              </Typography>
            </Box>

            <Box
              sx={{
                display: 'grid',
                gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(3, 1fr)' },
                gap: 2.5,
              }}
            >
              {modules.map((module, index) => (
                <RevealSection key={module.title} delay={index * 0.05}>
                  <Card
                    elevation={0}
                    sx={{
                      height: '100%', borderRadius: '20px',
                      background: alpha(theme.palette.background.paper, 0.5),
                      backdropFilter: 'blur(20px)',
                      border: `1px solid ${alpha(module.accent, 0.1)}`,
                      position: 'relative', overflow: 'hidden', cursor: 'default',
                      transition: `all 0.4s ${EASING}`,
                      '&::before': {
                        content: '""', position: 'absolute', top: 0, left: 0, right: 0,
                        height: 3, background: `linear-gradient(90deg, ${module.accent}, ${alpha(module.accent, 0.3)})`,
                        opacity: 0, transition: 'opacity 0.3s ease',
                      },
                      '&:hover': {
                        transform: 'translateY(-6px)',
                        borderColor: alpha(module.accent, 0.3),
                        boxShadow: `0 12px 40px ${alpha(module.accent, 0.15)}`,
                        '&::before': { opacity: 1 },
                        '& .module-icon-container': {
                          background: `linear-gradient(135deg, ${module.accent}, ${alpha(module.accent, 0.7)})`,
                          transform: 'scale(1.1)',
                          '& .MuiSvgIcon-root': { color: '#fff !important' },
                        },
                      },
                    }}
                  >
                    <CardContent sx={{ p: 2.5, textAlign: 'center', display: 'flex', flexDirection: 'column', height: '100%' }}>
                      <Box
                        className="module-icon-container"
                        sx={{
                          width: 52, height: 52, borderRadius: '14px',
                          display: 'flex', alignItems: 'center', justifyContent: 'center',
                          mx: 'auto', mb: 2,
                          background: alpha(module.accent, 0.1),
                          border: `1px solid ${alpha(module.accent, 0.15)}`,
                          transition: `all 0.35s ${EASING}`,
                          '& .MuiSvgIcon-root': { fontSize: '1.5rem', color: module.accent, transition: 'all 0.35s ease' },
                        }}
                      >
                        {module.icon}
                      </Box>
                      <Typography variant="h6" sx={{
                        fontFamily: '"Inter", sans-serif', fontWeight: 700,
                        fontSize: '0.92rem', mb: 1, color: theme.palette.text.primary,
                      }}>
                        {module.title}
                      </Typography>
                      <Typography variant="body2" sx={{
                        fontFamily: '"Inter", sans-serif', color: alpha(theme.palette.text.secondary, 0.65),
                        lineHeight: 1.65, fontSize: '0.78rem', mb: 1.5, flex: 1,
                      }}>
                        {module.desc}
                      </Typography>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, justifyContent: 'center' }}>
                        {module.tech.map((t) => (
                          <Chip
                            key={t}
                            label={t}
                            size="small"
                            sx={{
                              fontFamily: CODE_FONT, fontSize: '0.6rem', height: 20, fontWeight: 600,
                              backgroundColor: alpha(module.accent, 0.06),
                              color: alpha(module.accent, 0.8),
                              border: `1px solid ${alpha(module.accent, 0.1)}`,
                            }}
                          />
                        ))}
                      </Box>
                    </CardContent>
                  </Card>
                </RevealSection>
              ))}
            </Box>
          </Box>
        </RevealSection>

        {/* ════════════════════ TECH STACK ════════════════════ */}
        <RevealSection>
          <Box sx={{ mb: 8 }}>
            <Box sx={{ textAlign: 'center', mb: 4 }}>
              <Typography
                variant="h4"
                sx={{
                  fontFamily: '"Inter", sans-serif', fontWeight: 800,
                  background: `linear-gradient(135deg, ${PRIMARY}, ${SECONDARY})`,
                  backgroundClip: 'text', WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  fontSize: { xs: '1.5rem', md: '2rem' }, mb: 1,
                }}
              >
                Tech Stack
              </Typography>
            </Box>

            <Box
              sx={{
                display: 'flex', flexWrap: 'wrap', gap: 1.5,
                justifyContent: 'center', maxWidth: 900, mx: 'auto',
              }}
            >
              {[
                { label: 'React 18', color: '#61dafb' },
                { label: 'TypeScript', color: '#3178c6' },
                { label: 'Material UI 5', color: '#007fff' },
                { label: 'Python / Flask', color: '#3776ab' },
                { label: 'OpenAI API', color: '#412991' },
                { label: 'Anthropic API', color: '#d4a27f' },
                { label: 'Google AI', color: '#4285f4' },
                { label: 'Playwright', color: '#2ead33' },
                { label: 'BeautifulSoup', color: '#43b02a' },
                { label: 'SigmaHQ', color: '#e74c3c' },
                { label: 'YARA', color: '#ff6b35' },
                { label: 'MITRE ATT&CK', color: '#fa4616' },
                { label: 'Atomic Red Team', color: ATOMIC_COLOR },
                { label: 'SSE Streaming', color: '#f59e0b' },
                { label: 'SQLite', color: '#003b57' },
                { label: 'TF-IDF / NLP', color: '#9b59b6' },
              ].map((tech) => (
                <Chip
                  key={tech.label}
                  label={tech.label}
                  sx={{
                    fontFamily: CODE_FONT, fontWeight: 600, fontSize: '0.75rem',
                    backgroundColor: alpha(tech.color, 0.08), color: tech.color,
                    border: `1px solid ${alpha(tech.color, 0.15)}`,
                    transition: `all 0.25s ${EASING}`,
                    '&:hover': {
                      backgroundColor: alpha(tech.color, 0.15),
                      transform: 'translateY(-2px)',
                      boxShadow: `0 4px 12px ${alpha(tech.color, 0.2)}`,
                    },
                  }}
                />
              ))}
            </Box>
          </Box>
        </RevealSection>

        {/* ── Footer ── */}
        <RevealSection>
          <Box sx={{ textAlign: 'center', mt: 6, mb: 4, py: 3 }}>
            <Box
              sx={{
                width: 80, height: 2, mx: 'auto', mb: 3, borderRadius: 1,
                background: `linear-gradient(90deg, transparent, ${alpha(PRIMARY, 0.4)}, ${alpha(SECONDARY, 0.4)}, transparent)`,
              }}
            />
            <Typography
              variant="caption"
              sx={{
                fontFamily: CODE_FONT, fontSize: '0.75rem',
                color: alpha(theme.palette.text.secondary, 0.35), letterSpacing: '0.1em',
              }}
            >
              PERSEPTOR v2.0 &mdash; Next-Generation Detection Engineering Platform
            </Typography>
          </Box>
        </RevealSection>
      </Box>
    </Box>
  );
};

export default AboutPerseptor;
