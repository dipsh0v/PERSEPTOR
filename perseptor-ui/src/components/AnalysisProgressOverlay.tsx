/**
 * PERSEPTOR v2.0 - Analysis Progress Overlay
 * A stunning, animated full-screen progress overlay for threat analysis.
 * Connects to SSE stream and shows real-time stage-by-stage progress
 * with particle effects, glowing animations, and live result previews.
 */

import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import {
  Box,
  Typography,
  useTheme,
  Fade,
  Chip,
  Collapse,
  IconButton,
  Tooltip,
} from '@mui/material';
import SecurityIcon from '@mui/icons-material/Security';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';
import RadioButtonUncheckedIcon from '@mui/icons-material/RadioButtonUnchecked';
import LanguageIcon from '@mui/icons-material/Language';
import ImageSearchIcon from '@mui/icons-material/ImageSearch';
import PsychologyIcon from '@mui/icons-material/Psychology';
import FingerprintIcon from '@mui/icons-material/Fingerprint';
import BugReportIcon from '@mui/icons-material/BugReport';
import ShieldIcon from '@mui/icons-material/Shield';
import GavelIcon from '@mui/icons-material/Gavel';
import StorageIcon from '@mui/icons-material/Storage';
import DoneAllIcon from '@mui/icons-material/DoneAll';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';

// ─── Stage Configuration ──────────────────────────────────────────────────

interface StageConfig {
  id: string;
  label: string;
  icon: React.ReactNode;
  color: string;
  group: 'fetch' | 'ai' | 'rules' | 'siem' | 'final';
}

const STAGE_MAP: Record<string, StageConfig> = {
  fetching:          { id: 'fetching',      label: 'Fetching URL',            icon: <LanguageIcon />,      color: '#42a5f5', group: 'fetch' },
  fetched:           { id: 'fetched',       label: 'URL Fetched',             icon: <LanguageIcon />,      color: '#42a5f5', group: 'fetch' },
  ocr:               { id: 'ocr',           label: 'Image OCR Processing',    icon: <ImageSearchIcon />,   color: '#ab47bc', group: 'fetch' },
  ocr_done:          { id: 'ocr_done',      label: 'OCR Complete',            icon: <ImageSearchIcon />,   color: '#ab47bc', group: 'fetch' },
  ai_parallel:       { id: 'ai_parallel',   label: 'Parallel AI Analysis',    icon: <PsychologyIcon />,    color: '#ff7043', group: 'ai' },
  threat_summary:    { id: 'threat_summary', label: 'Threat Summary',         icon: <SecurityIcon />,      color: '#ef5350', group: 'ai' },
  ioc_extraction:    { id: 'ioc_extraction', label: 'IoC Extraction',         icon: <FingerprintIcon />,   color: '#ffa726', group: 'ai' },
  ai_sigma:          { id: 'ai_sigma',      label: 'AI Sigma Rules',          icon: <ShieldIcon />,        color: '#66bb6a', group: 'ai' },
  threat_summary_done: { id: 'threat_summary_done', label: 'Threat Summary', icon: <SecurityIcon />,      color: '#ef5350', group: 'ai' },
  ioc_done:          { id: 'ioc_done',      label: 'IoC Extraction',          icon: <FingerprintIcon />,   color: '#ffa726', group: 'ai' },
  rules:             { id: 'rules',         label: 'Detection Rules',         icon: <GavelIcon />,         color: '#26c6da', group: 'rules' },
  yara_done:         { id: 'yara_done',     label: 'YARA Rules',              icon: <BugReportIcon />,     color: '#8d6e63', group: 'rules' },
  mitre_done:        { id: 'mitre_done',    label: 'MITRE Mapping',           icon: <TrendingUpIcon />,    color: '#ec407a', group: 'rules' },
  sigma_done:        { id: 'sigma_done',    label: 'Sigma Rules',             icon: <ShieldIcon />,        color: '#66bb6a', group: 'rules' },
  sigma_match_done:  { id: 'sigma_match_done', label: 'Sigma Matching',      icon: <ShieldIcon />,        color: '#26a69a', group: 'rules' },
  siem:              { id: 'siem',          label: 'SIEM Queries',            icon: <StorageIcon />,       color: '#7e57c2', group: 'siem' },
  siem_structured_done: { id: 'siem_structured_done', label: 'IoC SIEM',    icon: <StorageIcon />,       color: '#7e57c2', group: 'siem' },
  siem_ai_done:      { id: 'siem_ai_done',  label: 'AI SIEM Refinement',     icon: <StorageIcon />,       color: '#7e57c2', group: 'siem' },
  atomic_tests:      { id: 'atomic_tests',  label: 'Atomic Red Team Tests',  icon: <SecurityIcon />,      color: '#f97316', group: 'siem' },
  atomic_tests_done: { id: 'atomic_tests_done', label: 'Atomic Tests Ready', icon: <SecurityIcon />,      color: '#f97316', group: 'siem' },
  finalizing:        { id: 'finalizing',    label: 'Compiling Report',        icon: <DoneAllIcon />,       color: '#4caf50', group: 'final' },
  complete:          { id: 'complete',      label: 'Analysis Complete!',      icon: <DoneAllIcon />,       color: '#4caf50', group: 'final' },
};

// ─── Particle System ──────────────────────────────────────────────────────

interface Particle {
  id: number;
  x: number;
  y: number;
  vx: number;
  vy: number;
  life: number;
  maxLife: number;
  size: number;
  color: string;
}

const ParticleCanvas: React.FC<{ color: string; active: boolean }> = ({ color, active }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const particlesRef = useRef<Particle[]>([]);
  const animFrameRef = useRef<number>(0);
  const nextIdRef = useRef(0);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const resize = () => {
      canvas.width = canvas.offsetWidth;
      canvas.height = canvas.offsetHeight;
    };
    resize();
    window.addEventListener('resize', resize);

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Spawn new particles
      if (active && Math.random() < 0.3) {
        const edge = Math.floor(Math.random() * 4);
        let x = 0, y = 0, vx = 0, vy = 0;
        switch (edge) {
          case 0: x = Math.random() * canvas.width; y = -5; vx = (Math.random() - 0.5) * 0.5; vy = Math.random() * 0.8 + 0.2; break;
          case 1: x = canvas.width + 5; y = Math.random() * canvas.height; vx = -(Math.random() * 0.8 + 0.2); vy = (Math.random() - 0.5) * 0.5; break;
          case 2: x = Math.random() * canvas.width; y = canvas.height + 5; vx = (Math.random() - 0.5) * 0.5; vy = -(Math.random() * 0.8 + 0.2); break;
          case 3: x = -5; y = Math.random() * canvas.height; vx = Math.random() * 0.8 + 0.2; vy = (Math.random() - 0.5) * 0.5; break;
        }
        particlesRef.current.push({
          id: nextIdRef.current++,
          x, y, vx, vy,
          life: 0,
          maxLife: 150 + Math.random() * 100,
          size: Math.random() * 2 + 1,
          color,
        });
      }

      // Update and draw
      particlesRef.current = particlesRef.current.filter(p => {
        p.x += p.vx;
        p.y += p.vy;
        p.life++;
        if (p.life >= p.maxLife) return false;
        const alpha = 1 - (p.life / p.maxLife);
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fillStyle = p.color + Math.floor(alpha * 255).toString(16).padStart(2, '0');
        ctx.fill();

        // Connection lines between nearby particles
        particlesRef.current.forEach(p2 => {
          if (p2.id === p.id) return;
          const dx = p.x - p2.x;
          const dy = p.y - p2.y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 100) {
            const lineAlpha = (1 - dist / 100) * alpha * 0.15;
            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(p2.x, p2.y);
            ctx.strokeStyle = p.color + Math.floor(lineAlpha * 255).toString(16).padStart(2, '0');
            ctx.lineWidth = 0.5;
            ctx.stroke();
          }
        });

        return true;
      });

      animFrameRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      window.removeEventListener('resize', resize);
      cancelAnimationFrame(animFrameRef.current);
    };
  }, [color, active]);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        pointerEvents: 'none',
      }}
    />
  );
};

// ─── Hex Grid Background ──────────────────────────────────────────────────

const HexGrid: React.FC<{ progress: number; color: string }> = ({ progress, color }) => {
  const cells = useMemo(() => {
    const items = [];
    const cols = 12;
    const rows = 8;
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        const idx = r * cols + c;
        const total = rows * cols;
        const threshold = (idx / total) * 100;
        items.push({
          key: `${r}-${c}`,
          x: c * 80 + (r % 2 ? 40 : 0),
          y: r * 70,
          active: progress > threshold,
          delay: idx * 20,
        });
      }
    }
    return items;
  }, [progress]);

  return (
    <Box
      sx={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        overflow: 'hidden',
        opacity: 0.06,
        pointerEvents: 'none',
      }}
    >
      <svg width="100%" height="100%" viewBox="0 0 960 560">
        {cells.map(cell => (
          <polygon
            key={cell.key}
            points="30,0 60,17 60,52 30,69 0,52 0,17"
            transform={`translate(${cell.x}, ${cell.y})`}
            fill={cell.active ? color : '#ffffff'}
            opacity={cell.active ? 0.8 : 0.2}
            style={{ transition: `all 0.6s ease ${cell.delay}ms` }}
          />
        ))}
      </svg>
    </Box>
  );
};

// ─── Circular Progress Ring ───────────────────────────────────────────────

const ProgressRing: React.FC<{ progress: number; color: string; stage: string }> = ({ progress, color, stage }) => {
  const radius = 85;
  const stroke = 6;
  const normalizedRadius = radius - stroke * 2;
  const circumference = normalizedRadius * 2 * Math.PI;
  const strokeDashoffset = circumference - (progress / 100) * circumference;

  return (
    <Box sx={{ position: 'relative', width: radius * 2, height: radius * 2 }}>
      <svg width={radius * 2} height={radius * 2} style={{ transform: 'rotate(-90deg)' }}>
        {/* Background track */}
        <circle
          stroke="rgba(255,255,255,0.08)"
          fill="transparent"
          strokeWidth={stroke}
          r={normalizedRadius}
          cx={radius}
          cy={radius}
        />
        {/* Animated progress */}
        <circle
          stroke={color}
          fill="transparent"
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={`${circumference} ${circumference}`}
          style={{
            strokeDashoffset,
            transition: 'stroke-dashoffset 0.8s cubic-bezier(0.4, 0, 0.2, 1), stroke 0.3s ease',
            filter: `drop-shadow(0 0 8px ${color})`,
          }}
          r={normalizedRadius}
          cx={radius}
          cy={radius}
        />
        {/* Glow pulse ring */}
        <circle
          stroke={color}
          fill="transparent"
          strokeWidth={2}
          r={normalizedRadius + 8}
          cx={radius}
          cy={radius}
          opacity={0.3}
          style={{
            animation: 'pulseRing 2s ease-in-out infinite',
          }}
        />
      </svg>
      {/* Center content */}
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <Typography
          variant="h3"
          sx={{
            color: 'white',
            fontWeight: 'bold',
            fontFamily: 'monospace',
            textShadow: `0 0 20px ${color}`,
          }}
        >
          {Math.round(progress)}%
        </Typography>
        <Typography
          variant="caption"
          sx={{
            color: 'rgba(255,255,255,0.6)',
            textTransform: 'uppercase',
            letterSpacing: 2,
            fontSize: '0.65rem',
          }}
        >
          {stage === 'complete' ? 'DONE' : 'ANALYZING'}
        </Typography>
      </Box>
    </Box>
  );
};

// ─── Stage Timeline Item ──────────────────────────────────────────────────

interface StageEvent {
  stage: string;
  progress: number;
  message: string;
  timestamp: number;
  status: 'active' | 'done' | 'error';
}

const StageItem: React.FC<{ event: StageEvent; isLatest: boolean }> = ({ event, isLatest }) => {
  const config = STAGE_MAP[event.stage];
  const color = config?.color || '#90caf9';
  const icon = config?.icon || <SecurityIcon />;
  const label = config?.label || event.stage;

  return (
    <Fade in timeout={400}>
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 1.5,
          py: 0.6,
          px: 1.5,
          borderRadius: 1,
          backgroundColor: isLatest ? 'rgba(255,255,255,0.06)' : 'transparent',
          transition: 'all 0.3s ease',
        }}
      >
        <Box
          sx={{
            color: event.status === 'done' ? '#4caf50'
              : event.status === 'error' ? '#f44336'
              : color,
            display: 'flex',
            alignItems: 'center',
            fontSize: 18,
            animation: event.status === 'active' ? 'pulse 1.5s ease-in-out infinite' : 'none',
            '& .MuiSvgIcon-root': { fontSize: 18 },
          }}
        >
          {event.status === 'done' ? <CheckCircleIcon /> : event.status === 'error' ? <ErrorOutlineIcon /> : icon}
        </Box>
        <Typography
          variant="body2"
          sx={{
            color: isLatest ? 'white' : 'rgba(255,255,255,0.55)',
            fontWeight: isLatest ? 600 : 400,
            fontSize: '0.8rem',
            flex: 1,
          }}
        >
          {event.message || label}
        </Typography>
        <Typography
          variant="caption"
          sx={{
            color: 'rgba(255,255,255,0.3)',
            fontFamily: 'monospace',
            fontSize: '0.65rem',
          }}
        >
          {event.progress}%
        </Typography>
      </Box>
    </Fade>
  );
};

// ─── Main Component ───────────────────────────────────────────────────────

export interface SSEEvent {
  stage: string;
  progress: number;
  message: string;
  data?: any;
}

interface AnalysisProgressOverlayProps {
  visible: boolean;
  events: SSEEvent[];
  progress: number;
  currentStage: string;
  elapsedSeconds: number;
}

const AnalysisProgressOverlay: React.FC<AnalysisProgressOverlayProps> = ({
  visible,
  events,
  progress,
  currentStage,
  elapsedSeconds,
}) => {
  const theme = useTheme();
  const [showTimeline, setShowTimeline] = useState(true);
  const timelineRef = useRef<HTMLDivElement>(null);

  const currentColor = useMemo(() => {
    return STAGE_MAP[currentStage]?.color || theme.palette.primary.main;
  }, [currentStage, theme]);

  // Auto-scroll timeline
  useEffect(() => {
    if (timelineRef.current) {
      timelineRef.current.scrollTop = timelineRef.current.scrollHeight;
    }
  }, [events]);

  // Build timeline events with status
  const stageEvents: StageEvent[] = useMemo(() => {
    const result: StageEvent[] = [];
    const seen = new Set<string>();

    events.forEach((ev, idx) => {
      const isLast = idx === events.length - 1;
      const isDone = ev.stage.endsWith('_done') || ev.stage === 'complete' || ev.stage === 'fetched';
      result.push({
        stage: ev.stage,
        progress: ev.progress,
        message: ev.message,
        timestamp: Date.now(),
        status: isDone ? 'done' : ev.stage === 'error' ? 'error' : isLast ? 'active' : 'done',
      });
    });

    return result;
  }, [events]);

  // Format elapsed time
  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return m > 0 ? `${m}m ${s}s` : `${s}s`;
  };

  // Group counts for quick stats
  const stats = useMemo(() => {
    const completed = stageEvents.filter(e => e.status === 'done').length;
    const errors = stageEvents.filter(e => e.status === 'error').length;
    return { completed, errors, total: stageEvents.length };
  }, [stageEvents]);

  if (!visible) return null;

  return (
    <Fade in={visible} timeout={600}>
      <Box
        sx={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          zIndex: 9999,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          background: `radial-gradient(ellipse at center, rgba(10,15,30,0.95) 0%, rgba(0,0,0,0.98) 100%)`,
          backdropFilter: 'blur(12px)',
          // Global keyframes
          '@keyframes pulse': {
            '0%, 100%': { opacity: 1 },
            '50%': { opacity: 0.5 },
          },
          '@keyframes pulseRing': {
            '0%, 100%': { opacity: 0.3, transform: 'scale(1)' },
            '50%': { opacity: 0.1, transform: 'scale(1.05)' },
          },
          '@keyframes slideIn': {
            from: { opacity: 0, transform: 'translateY(10px)' },
            to: { opacity: 1, transform: 'translateY(0)' },
          },
          '@keyframes scanline': {
            '0%': { top: '-2px' },
            '100%': { top: '100%' },
          },
          '@keyframes glowPulse': {
            '0%, 100%': { boxShadow: `0 0 20px ${currentColor}33` },
            '50%': { boxShadow: `0 0 40px ${currentColor}66` },
          },
        }}
      >
        {/* Particle background */}
        <ParticleCanvas color={currentColor} active={progress < 100} />

        {/* Hex grid */}
        <HexGrid progress={progress} color={currentColor} />

        {/* Scanline effect */}
        <Box
          sx={{
            position: 'absolute',
            left: 0,
            right: 0,
            height: '2px',
            background: `linear-gradient(90deg, transparent, ${currentColor}40, transparent)`,
            animation: 'scanline 3s linear infinite',
            pointerEvents: 'none',
          }}
        />

        {/* Main content */}
        <Box
          sx={{
            position: 'relative',
            zIndex: 1,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: 3,
            maxWidth: 700,
            width: '90%',
          }}
        >
          {/* Title */}
          <Typography
            variant="h5"
            sx={{
              color: 'white',
              fontWeight: 700,
              letterSpacing: 3,
              textTransform: 'uppercase',
              textShadow: `0 0 30px ${currentColor}80`,
              textAlign: 'center',
            }}
          >
            {progress >= 100 ? 'Analysis Complete' : 'Analyzing Threat Report'}
          </Typography>

          {/* Progress Ring */}
          <ProgressRing progress={progress} color={currentColor} stage={currentStage} />

          {/* Stats bar */}
          <Box
            sx={{
              display: 'flex',
              gap: 2,
              alignItems: 'center',
              justifyContent: 'center',
              flexWrap: 'wrap',
            }}
          >
            <Chip
              icon={<CheckCircleIcon sx={{ fontSize: 16 }} />}
              label={`${stats.completed} stages`}
              size="small"
              sx={{
                backgroundColor: 'rgba(76,175,80,0.15)',
                color: '#4caf50',
                border: '1px solid rgba(76,175,80,0.3)',
                fontFamily: 'monospace',
                fontSize: '0.7rem',
              }}
            />
            {stats.errors > 0 && (
              <Chip
                icon={<ErrorOutlineIcon sx={{ fontSize: 16 }} />}
                label={`${stats.errors} errors`}
                size="small"
                sx={{
                  backgroundColor: 'rgba(244,67,54,0.15)',
                  color: '#f44336',
                  border: '1px solid rgba(244,67,54,0.3)',
                  fontFamily: 'monospace',
                  fontSize: '0.7rem',
                }}
              />
            )}
            <Chip
              label={formatTime(elapsedSeconds)}
              size="small"
              sx={{
                backgroundColor: 'rgba(255,255,255,0.08)',
                color: 'rgba(255,255,255,0.7)',
                border: '1px solid rgba(255,255,255,0.12)',
                fontFamily: 'monospace',
                fontSize: '0.7rem',
              }}
            />
          </Box>

          {/* Current stage message */}
          <Box
            sx={{
              textAlign: 'center',
              animation: 'slideIn 0.4s ease',
            }}
          >
            <Typography
              variant="body1"
              sx={{
                color: currentColor,
                fontWeight: 600,
                textShadow: `0 0 10px ${currentColor}60`,
              }}
            >
              {events.length > 0 ? events[events.length - 1].message : 'Initializing...'}
            </Typography>
          </Box>

          {/* Stage Timeline (collapsible) */}
          <Box
            sx={{
              width: '100%',
              maxWidth: 550,
              backgroundColor: 'rgba(0,0,0,0.3)',
              border: `1px solid rgba(255,255,255,0.08)`,
              borderRadius: 2,
              overflow: 'hidden',
              animation: 'glowPulse 3s ease-in-out infinite',
            }}
          >
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                px: 2,
                py: 1,
                borderBottom: showTimeline ? '1px solid rgba(255,255,255,0.06)' : 'none',
                cursor: 'pointer',
              }}
              onClick={() => setShowTimeline(!showTimeline)}
            >
              <Typography
                variant="caption"
                sx={{
                  color: 'rgba(255,255,255,0.5)',
                  textTransform: 'uppercase',
                  letterSpacing: 2,
                  fontSize: '0.65rem',
                }}
              >
                Stage Timeline
              </Typography>
              <IconButton size="small" sx={{ color: 'rgba(255,255,255,0.4)' }}>
                {showTimeline ? <ExpandLessIcon fontSize="small" /> : <ExpandMoreIcon fontSize="small" />}
              </IconButton>
            </Box>

            <Collapse in={showTimeline}>
              <Box
                ref={timelineRef}
                sx={{
                  maxHeight: 250,
                  overflowY: 'auto',
                  py: 0.5,
                  '&::-webkit-scrollbar': { width: 4 },
                  '&::-webkit-scrollbar-track': { background: 'transparent' },
                  '&::-webkit-scrollbar-thumb': {
                    background: 'rgba(255,255,255,0.15)',
                    borderRadius: 2,
                  },
                }}
              >
                {stageEvents.map((event, idx) => (
                  <StageItem
                    key={`${event.stage}-${idx}`}
                    event={event}
                    isLatest={idx === stageEvents.length - 1}
                  />
                ))}
                {stageEvents.length === 0 && (
                  <Box sx={{ p: 2, textAlign: 'center' }}>
                    <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.3)' }}>
                      Waiting for analysis to begin...
                    </Typography>
                  </Box>
                )}
              </Box>
            </Collapse>
          </Box>

          {/* Progress bar (bottom) */}
          <Box
            sx={{
              width: '100%',
              maxWidth: 550,
              height: 3,
              borderRadius: 2,
              backgroundColor: 'rgba(255,255,255,0.06)',
              overflow: 'hidden',
            }}
          >
            <Box
              sx={{
                width: `${progress}%`,
                height: '100%',
                borderRadius: 2,
                background: `linear-gradient(90deg, ${currentColor}, ${currentColor}cc)`,
                transition: 'width 0.8s cubic-bezier(0.4, 0, 0.2, 1)',
                boxShadow: `0 0 12px ${currentColor}80`,
              }}
            />
          </Box>
        </Box>
      </Box>
    </Fade>
  );
};

export default AnalysisProgressOverlay;
