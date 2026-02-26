/**
 * PERSEPTOR v2.0 - Settings Page
 * Premium 2026 cybersecurity design.
 * Provider selection, API key management, model selection, theme toggle, usage stats.
 */

import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Alert,
  CircularProgress,
  Divider,
  Switch,
  FormControlLabel,
  Tooltip,
  Fade,
  Zoom,
  Avatar,
  IconButton,
  Paper,
  LinearProgress,
  Tabs,
  Tab,
  keyframes,
} from '@mui/material';
import {
  Settings as SettingsIcon,
  Key as KeyIcon,
  SmartToy as AIIcon,
  Palette as PaletteIcon,
  Analytics as AnalyticsIcon,
  CheckCircle as ConnectedIcon,
  Cancel as DisconnectedIcon,
  Logout as LogoutIcon,
  Refresh as RefreshIcon,
  LightMode as LightModeIcon,
  DarkMode as DarkModeIcon,
  Lock as LockIcon,
  Check as CheckIcon,
  Star as StarIcon,
  Bolt as BoltIcon,
} from '@mui/icons-material';
import { useTheme } from '@mui/material/styles';
import { alpha } from '@mui/material/styles';
import { useAppDispatch, useAppSelector } from '../store';
import {
  setApiKey,
  setProvider,
  setModel,
  toggleTheme,
  createSession,
  destroySession,
  fetchProviders,
  fetchTokenUsage,
  clearSessionError,
} from '../store/slices/settingsSlice';

/* ── Keyframes ── */
const pulseGlow = keyframes`
  0%, 100% { box-shadow: 0 0 8px currentColor, 0 0 16px currentColor; }
  50% { box-shadow: 0 0 16px currentColor, 0 0 32px currentColor, 0 0 48px currentColor; }
`;

const shimmer = keyframes`
  0% { background-position: -200% center; }
  100% { background-position: 200% center; }
`;

const floatUp = keyframes`
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
`;

const rotateGlow = keyframes`
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
`;

const Settings: React.FC = () => {
  const theme = useTheme();
  const dispatch = useAppDispatch();
  const settings = useAppSelector((state) => state.settings);
  const [showAnimation, setShowAnimation] = useState(false);
  const [activeTab, setActiveTab] = useState(0);

  useEffect(() => {
    setShowAnimation(true);
    dispatch(fetchProviders());
    if (settings.sessionToken) {
      dispatch(fetchTokenUsage());
    }
  }, [dispatch, settings.sessionToken]);

  const handleConnect = async () => {
    if (!settings.apiKey) return;
    dispatch(clearSessionError());
    dispatch(
      createSession({
        apiKey: settings.apiKey,
        provider: settings.aiProvider,
        model: settings.selectedModel,
      })
    );
  };

  const handleDisconnect = () => {
    dispatch(destroySession());
  };

  const currentProvider = settings.availableProviders.find(
    (p) => p.provider === settings.aiProvider
  );

  const currentModel = currentProvider?.models.find(
    (m) => m.model_id === settings.selectedModel
  );

  /* ── Shared glassmorphic card style ── */
  const glassCard = {
    background: alpha(theme.palette.background.paper, 0.6),
    backdropFilter: 'blur(24px)',
    WebkitBackdropFilter: 'blur(24px)',
    border: `1px solid ${alpha(theme.palette.primary.main, 0.12)}`,
    borderRadius: '20px',
    boxShadow: `0 8px 32px ${alpha(theme.palette.primary.main, 0.08)}, inset 0 1px 0 ${alpha('#fff', 0.05)}`,
    overflow: 'hidden',
    position: 'relative' as const,
  };

  return (
    <Box sx={{ p: { xs: 2, md: 4 }, minHeight: '100vh' }}>
      {/* ── Page Header ── */}
      <Fade in={showAnimation} timeout={800}>
        <Box sx={{ mb: 5 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2.5, mb: 1 }}>
            {/* Animated icon container */}
            <Box
              sx={{
                width: 64,
                height: 64,
                borderRadius: '18px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                background: `linear-gradient(135deg, ${alpha('#6366f1', 0.15)}, ${alpha('#ec4899', 0.15)})`,
                border: `1px solid ${alpha('#6366f1', 0.2)}`,
                position: 'relative',
                '&::before': {
                  content: '""',
                  position: 'absolute',
                  inset: -1,
                  borderRadius: '19px',
                  padding: '1px',
                  background: `linear-gradient(135deg, ${alpha('#6366f1', 0.5)}, ${alpha('#ec4899', 0.5)})`,
                  WebkitMask: 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)',
                  WebkitMaskComposite: 'xor',
                  maskComposite: 'exclude',
                },
              }}
            >
              <SettingsIcon sx={{ fontSize: 32, color: '#6366f1' }} />
            </Box>
            <Box>
              <Typography
                variant="h3"
                sx={{
                  fontFamily: '"Inter", sans-serif',
                  fontWeight: 800,
                  fontSize: { xs: '2rem', md: '2.5rem' },
                  background: 'linear-gradient(135deg, #6366f1 0%, #ec4899 50%, #6366f1 100%)',
                  backgroundSize: '200% auto',
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  animation: `${shimmer} 4s linear infinite`,
                  letterSpacing: '-0.02em',
                }}
              >
                Settings
              </Typography>
              <Typography
                variant="subtitle1"
                sx={{
                  color: alpha(theme.palette.text.secondary, 0.7),
                  fontFamily: '"Inter", sans-serif',
                  fontWeight: 400,
                  fontSize: '0.95rem',
                  letterSpacing: '0.01em',
                }}
              >
                Configure AI provider, manage sessions, and customize your experience.
              </Typography>
            </Box>
          </Box>
        </Box>
      </Fade>

      {/* ── Tab Bar ── */}
      <Box sx={{ mb: 4 }}>
        <Tabs
          value={activeTab}
          onChange={(_, v) => setActiveTab(v)}
          sx={{
            minHeight: 56,
            '& .MuiTabs-indicator': {
              height: 3,
              borderRadius: '3px 3px 0 0',
              background: 'linear-gradient(90deg, #6366f1, #ec4899)',
              boxShadow: `0 0 12px ${alpha('#6366f1', 0.5)}`,
            },
            '& .MuiTabs-flexContainer': {
              gap: 1,
            },
            '& .MuiTab-root': {
              fontFamily: '"Inter", sans-serif',
              fontWeight: 600,
              fontSize: '0.85rem',
              textTransform: 'none',
              minHeight: 56,
              borderRadius: '12px 12px 0 0',
              color: alpha(theme.palette.text.primary, 0.5),
              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
              '&:hover': {
                color: theme.palette.text.primary,
                background: alpha('#6366f1', 0.06),
              },
              '&.Mui-selected': {
                color: '#6366f1',
              },
            },
          }}
        >
          <Tab icon={<KeyIcon sx={{ fontSize: 20 }} />} iconPosition="start" label="Connection" />
          <Tab icon={<AIIcon sx={{ fontSize: 20 }} />} iconPosition="start" label="AI Models" />
          <Tab icon={<PaletteIcon sx={{ fontSize: 20 }} />} iconPosition="start" label="Appearance" />
          <Tab icon={<AnalyticsIcon sx={{ fontSize: 20 }} />} iconPosition="start" label="Usage" />
        </Tabs>
        <Box sx={{ height: '1px', background: `linear-gradient(90deg, ${alpha('#6366f1', 0.2)}, ${alpha('#ec4899', 0.2)}, transparent)` }} />
      </Box>

      {/* ─────────────── Connection Tab ─────────────── */}
      {activeTab === 0 && (
        <Fade in timeout={500}>
          <Card sx={{ ...glassCard }}>
            {/* Decorative top gradient line */}
            <Box sx={{ height: 3, background: 'linear-gradient(90deg, #6366f1, #ec4899, #6366f1)', backgroundSize: '200% 100%', animation: `${shimmer} 3s linear infinite` }} />
            <CardContent sx={{ p: { xs: 3, md: 5 } }}>
              {/* Connection Status */}
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 2.5,
                  mb: 4,
                  p: 2.5,
                  borderRadius: '16px',
                  background: settings.isConnected
                    ? alpha('#22c55e', 0.06)
                    : alpha(theme.palette.error.main, 0.06),
                  border: `1px solid ${settings.isConnected ? alpha('#22c55e', 0.15) : alpha(theme.palette.error.main, 0.15)}`,
                }}
              >
                {settings.isConnected ? (
                  <Box
                    sx={{
                      width: 48,
                      height: 48,
                      borderRadius: '14px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      background: alpha('#22c55e', 0.12),
                      color: '#22c55e',
                      animation: `${pulseGlow} 2.5s ease-in-out infinite`,
                    }}
                  >
                    <ConnectedIcon sx={{ fontSize: 28 }} />
                  </Box>
                ) : (
                  <Box
                    sx={{
                      width: 48,
                      height: 48,
                      borderRadius: '14px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      background: alpha(theme.palette.error.main, 0.12),
                    }}
                  >
                    <DisconnectedIcon sx={{ color: theme.palette.error.main, fontSize: 28 }} />
                  </Box>
                )}
                <Box sx={{ flex: 1 }}>
                  <Typography
                    variant="h6"
                    sx={{
                      fontFamily: '"Inter", sans-serif',
                      fontWeight: 700,
                      color: settings.isConnected ? '#22c55e' : theme.palette.error.main,
                    }}
                  >
                    {settings.isConnected ? 'Connected' : 'Not Connected'}
                  </Typography>
                  {settings.isConnected && settings.sessionExpiresAt && (
                    <Typography
                      variant="caption"
                      sx={{
                        color: alpha(theme.palette.text.secondary, 0.7),
                        fontFamily: '"JetBrains Mono", monospace',
                        fontSize: '0.75rem',
                      }}
                    >
                      Session expires: {new Date(settings.sessionExpiresAt).toLocaleString()}
                    </Typography>
                  )}
                </Box>
                {settings.isConnected && (
                  <Button
                    variant="outlined"
                    color="error"
                    size="small"
                    startIcon={<LogoutIcon />}
                    onClick={handleDisconnect}
                    sx={{
                      borderRadius: '12px',
                      textTransform: 'none',
                      fontFamily: '"Inter", sans-serif',
                      fontWeight: 600,
                      borderColor: alpha(theme.palette.error.main, 0.3),
                      '&:hover': {
                        borderColor: theme.palette.error.main,
                        background: alpha(theme.palette.error.main, 0.08),
                      },
                    }}
                  >
                    Disconnect
                  </Button>
                )}
              </Box>

              <Divider sx={{ mb: 4, borderColor: alpha(theme.palette.divider, 0.08) }} />

              {/* Provider Selection */}
              <Typography
                variant="overline"
                sx={{
                  fontFamily: '"Inter", sans-serif',
                  fontWeight: 700,
                  fontSize: '0.7rem',
                  letterSpacing: '0.12em',
                  color: '#6366f1',
                  mb: 1.5,
                  display: 'block',
                }}
              >
                AI Provider
              </Typography>
              <FormControl
                fullWidth
                sx={{
                  mb: 4,
                  '& .MuiOutlinedInput-root': {
                    borderRadius: '14px',
                    fontFamily: '"Inter", sans-serif',
                    background: alpha(theme.palette.background.default, 0.5),
                    '& fieldset': {
                      borderColor: alpha('#6366f1', 0.15),
                      transition: 'all 0.3s ease',
                    },
                    '&:hover fieldset': {
                      borderColor: alpha('#6366f1', 0.3),
                    },
                    '&.Mui-focused fieldset': {
                      borderColor: '#6366f1',
                      borderWidth: 2,
                      boxShadow: `0 0 0 3px ${alpha('#6366f1', 0.1)}`,
                    },
                  },
                }}
              >
                <InputLabel sx={{ fontFamily: '"Inter", sans-serif' }}>AI Provider</InputLabel>
                <Select
                  value={settings.aiProvider}
                  label="AI Provider"
                  onChange={(e) => dispatch(setProvider(e.target.value))}
                  disabled={settings.isConnected}
                >
                  {settings.availableProviders.map((provider) => (
                    <MenuItem key={provider.provider} value={provider.provider}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                        <Typography sx={{ fontFamily: '"Inter", sans-serif', fontWeight: 600 }}>
                          {provider.display_name}
                        </Typography>
                        <Chip
                          label={`${provider.models.length} models`}
                          size="small"
                          sx={{
                            fontFamily: '"JetBrains Mono", monospace',
                            fontSize: '0.7rem',
                            height: 22,
                            background: alpha('#6366f1', 0.1),
                            color: '#6366f1',
                            border: `1px solid ${alpha('#6366f1', 0.2)}`,
                          }}
                        />
                      </Box>
                    </MenuItem>
                  ))}
                  {settings.availableProviders.length === 0 && (
                    <>
                      <MenuItem value="openai">OpenAI</MenuItem>
                      <MenuItem value="anthropic">Anthropic</MenuItem>
                      <MenuItem value="google">Google</MenuItem>
                    </>
                  )}
                </Select>
              </FormControl>

              {/* API Key */}
              <Typography
                variant="overline"
                sx={{
                  fontFamily: '"Inter", sans-serif',
                  fontWeight: 700,
                  fontSize: '0.7rem',
                  letterSpacing: '0.12em',
                  color: '#6366f1',
                  mb: 1.5,
                  display: 'block',
                }}
              >
                API Key
              </Typography>
              <TextField
                fullWidth
                label={`${settings.aiProvider === 'openai' ? 'OpenAI' : settings.aiProvider === 'anthropic' ? 'Anthropic' : 'Google'} API Key`}
                type="password"
                value={settings.apiKey}
                onChange={(e) => dispatch(setApiKey(e.target.value))}
                disabled={settings.isConnected}
                placeholder={
                  settings.aiProvider === 'openai'
                    ? 'sk-...'
                    : settings.aiProvider === 'anthropic'
                    ? 'sk-ant-...'
                    : 'AIza...'
                }
                sx={{
                  mb: 1,
                  '& .MuiOutlinedInput-root': {
                    borderRadius: '14px',
                    fontFamily: '"JetBrains Mono", monospace',
                    background: alpha(theme.palette.background.default, 0.5),
                    '& fieldset': {
                      borderColor: alpha('#6366f1', 0.15),
                      transition: 'all 0.3s ease',
                    },
                    '&:hover fieldset': {
                      borderColor: alpha('#6366f1', 0.3),
                    },
                    '&.Mui-focused fieldset': {
                      borderColor: '#6366f1',
                      borderWidth: 2,
                      boxShadow: `0 0 0 3px ${alpha('#6366f1', 0.1)}`,
                    },
                  },
                }}
                InputProps={{
                  startAdornment: (
                    <LockIcon sx={{ mr: 1.5, fontSize: 20, color: alpha('#6366f1', 0.5) }} />
                  ),
                }}
                helperText={
                  <Typography
                    component="span"
                    variant="caption"
                    sx={{
                      fontFamily: '"Inter", sans-serif',
                      color: alpha(theme.palette.text.secondary, 0.6),
                    }}
                  >
                    Your API key is encrypted and stored securely in your session.
                  </Typography>
                }
              />

              {/* Session Error */}
              {settings.sessionError && (
                <Alert
                  severity="error"
                  sx={{
                    mt: 2,
                    mb: 3,
                    borderRadius: '14px',
                    fontFamily: '"Inter", sans-serif',
                    border: `1px solid ${alpha(theme.palette.error.main, 0.2)}`,
                    '& .MuiAlert-icon': { alignItems: 'center' },
                  }}
                  onClose={() => dispatch(clearSessionError())}
                >
                  {settings.sessionError}
                </Alert>
              )}

              {/* Connect Button */}
              {!settings.isConnected && (
                <Button
                  variant="contained"
                  fullWidth
                  size="large"
                  onClick={handleConnect}
                  disabled={!settings.apiKey || settings.sessionLoading}
                  startIcon={
                    settings.sessionLoading ? (
                      <CircularProgress size={20} sx={{ color: 'inherit' }} />
                    ) : (
                      <KeyIcon />
                    )
                  }
                  sx={{
                    mt: 3,
                    height: 58,
                    borderRadius: '16px',
                    fontFamily: '"Inter", sans-serif',
                    fontWeight: 700,
                    fontSize: '1rem',
                    textTransform: 'none',
                    background: 'linear-gradient(135deg, #6366f1, #8b5cf6, #ec4899)',
                    backgroundSize: '200% 200%',
                    boxShadow: `0 4px 16px ${alpha('#6366f1', 0.35)}`,
                    transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                    '&:hover': {
                      transform: 'translateY(-2px)',
                      boxShadow: `0 8px 32px ${alpha('#6366f1', 0.5)}, 0 0 0 1px ${alpha('#6366f1', 0.2)}`,
                      backgroundPosition: 'right center',
                    },
                    '&:active': {
                      transform: 'translateY(0)',
                    },
                    '&.Mui-disabled': {
                      background: alpha(theme.palette.action.disabled, 0.12),
                    },
                  }}
                >
                  {settings.sessionLoading ? 'Connecting...' : 'Connect & Create Session'}
                </Button>
              )}
            </CardContent>
          </Card>
        </Fade>
      )}

      {/* ─────────────── AI Models Tab ─────────────── */}
      {activeTab === 1 && (
        <Fade in timeout={500}>
          <Box>
            <Card sx={{ ...glassCard, mb: 4 }}>
              <Box sx={{ height: 3, background: 'linear-gradient(90deg, #6366f1, #ec4899, #6366f1)', backgroundSize: '200% 100%', animation: `${shimmer} 3s linear infinite` }} />
              <CardContent sx={{ p: { xs: 3, md: 5 } }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
                  <AIIcon sx={{ fontSize: 28, color: '#6366f1' }} />
                  <Typography
                    variant="h5"
                    sx={{
                      fontFamily: '"Inter", sans-serif',
                      fontWeight: 800,
                      background: 'linear-gradient(135deg, #6366f1, #ec4899)',
                      backgroundClip: 'text',
                      WebkitBackgroundClip: 'text',
                      WebkitTextFillColor: 'transparent',
                    }}
                  >
                    Select AI Model
                  </Typography>
                </Box>
                <Typography
                  variant="body2"
                  sx={{
                    color: alpha(theme.palette.text.secondary, 0.7),
                    fontFamily: '"Inter", sans-serif',
                    mb: 4,
                    maxWidth: 600,
                  }}
                >
                  Choose the model that best fits your needs. Higher-tier models provide better results but cost more.
                </Typography>

                {settings.providersLoading ? (
                  <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
                    <CircularProgress sx={{ color: '#6366f1' }} />
                  </Box>
                ) : (
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    {currentProvider?.models.map((model) => {
                      const isSelected = settings.selectedModel === model.model_id;
                      const isFlagship = model.tier === 'flagship';
                      const isEfficient = model.tier === 'efficient';

                      return (
                        <Paper
                          key={model.model_id}
                          onClick={() => dispatch(setModel(model.model_id))}
                          elevation={0}
                          sx={{
                            p: 2.5,
                            cursor: 'pointer',
                            borderRadius: '16px',
                            background: isSelected
                              ? alpha('#6366f1', 0.06)
                              : alpha(theme.palette.background.default, 0.4),
                            border: `2px solid ${
                              isSelected
                                ? '#6366f1'
                                : alpha(theme.palette.divider, 0.08)
                            }`,
                            transition: 'all 0.35s cubic-bezier(0.4, 0, 0.2, 1)',
                            position: 'relative',
                            overflow: 'hidden',
                            ...(isSelected && {
                              boxShadow: `0 0 0 1px ${alpha('#6366f1', 0.2)}, 0 4px 24px ${alpha('#6366f1', 0.15)}`,
                            }),
                            '&:hover': {
                              borderColor: isSelected ? '#6366f1' : alpha('#6366f1', 0.4),
                              transform: 'translateY(-2px)',
                              boxShadow: `0 8px 24px ${alpha('#6366f1', 0.12)}`,
                              background: alpha('#6366f1', 0.04),
                            },
                          }}
                        >
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                              {/* Model icon */}
                              <Box
                                sx={{
                                  width: 42,
                                  height: 42,
                                  borderRadius: '12px',
                                  display: 'flex',
                                  alignItems: 'center',
                                  justifyContent: 'center',
                                  background: isFlagship
                                    ? 'linear-gradient(135deg, #6366f1, #ec4899)'
                                    : isEfficient
                                    ? alpha('#22c55e', 0.12)
                                    : alpha(theme.palette.text.secondary, 0.08),
                                }}
                              >
                                {isFlagship ? (
                                  <StarIcon sx={{ fontSize: 22, color: '#fff' }} />
                                ) : (
                                  <BoltIcon sx={{ fontSize: 22, color: isEfficient ? '#22c55e' : theme.palette.text.secondary }} />
                                )}
                              </Box>
                              <Box>
                                <Typography
                                  variant="subtitle1"
                                  sx={{
                                    fontFamily: '"Inter", sans-serif',
                                    fontWeight: 700,
                                    lineHeight: 1.3,
                                  }}
                                >
                                  {model.display_name}
                                </Typography>
                                <Typography
                                  variant="caption"
                                  sx={{
                                    fontFamily: '"JetBrains Mono", monospace',
                                    color: alpha(theme.palette.text.secondary, 0.6),
                                    fontSize: '0.72rem',
                                  }}
                                >
                                  Max {(model.max_tokens / 1000).toFixed(0)}K tokens
                                </Typography>
                              </Box>
                            </Box>
                            <Box sx={{ display: 'flex', gap: 1.5, alignItems: 'center' }}>
                              {/* Tier badge */}
                              <Chip
                                label={model.tier}
                                size="small"
                                sx={{
                                  fontFamily: '"Inter", sans-serif',
                                  fontWeight: 700,
                                  fontSize: '0.7rem',
                                  height: 26,
                                  borderRadius: '8px',
                                  textTransform: 'uppercase',
                                  letterSpacing: '0.05em',
                                  ...(isFlagship
                                    ? {
                                        background: 'linear-gradient(135deg, #6366f1, #ec4899)',
                                        color: '#fff',
                                        border: 'none',
                                      }
                                    : isEfficient
                                    ? {
                                        background: alpha('#22c55e', 0.12),
                                        color: '#22c55e',
                                        border: `1px solid ${alpha('#22c55e', 0.25)}`,
                                      }
                                    : {
                                        background: alpha(theme.palette.text.secondary, 0.08),
                                        color: theme.palette.text.secondary,
                                        border: `1px solid ${alpha(theme.palette.text.secondary, 0.15)}`,
                                      }),
                                }}
                              />
                              {isSelected && (
                                <Box
                                  sx={{
                                    width: 28,
                                    height: 28,
                                    borderRadius: '50%',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    background: 'linear-gradient(135deg, #6366f1, #ec4899)',
                                    boxShadow: `0 0 12px ${alpha('#6366f1', 0.4)}`,
                                  }}
                                >
                                  <CheckIcon sx={{ fontSize: 16, color: '#fff' }} />
                                </Box>
                              )}
                            </Box>
                          </Box>
                          {/* Cost info */}
                          <Box sx={{ display: 'flex', gap: 3, mt: 1.5, ml: 7.5 }}>
                            <Typography
                              variant="caption"
                              sx={{
                                fontFamily: '"JetBrains Mono", monospace',
                                color: alpha(theme.palette.text.secondary, 0.5),
                                fontSize: '0.72rem',
                              }}
                            >
                              Input: ${model.cost_per_1k_input}/1K tokens
                            </Typography>
                            <Typography
                              variant="caption"
                              sx={{
                                fontFamily: '"JetBrains Mono", monospace',
                                color: alpha(theme.palette.text.secondary, 0.5),
                                fontSize: '0.72rem',
                              }}
                            >
                              Output: ${model.cost_per_1k_output}/1K tokens
                            </Typography>
                          </Box>
                        </Paper>
                      );
                    }) || (
                      <Typography
                        variant="body2"
                        sx={{
                          fontFamily: '"Inter", sans-serif',
                          color: alpha(theme.palette.text.secondary, 0.6),
                          textAlign: 'center',
                          py: 4,
                        }}
                      >
                        Select a provider to view available models.
                      </Typography>
                    )}
                  </Box>
                )}
              </CardContent>
            </Card>
          </Box>
        </Fade>
      )}

      {/* ─────────────── Appearance Tab ─────────────── */}
      {activeTab === 2 && (
        <Fade in timeout={500}>
          <Card sx={{ ...glassCard }}>
            <Box sx={{ height: 3, background: 'linear-gradient(90deg, #6366f1, #ec4899, #6366f1)', backgroundSize: '200% 100%', animation: `${shimmer} 3s linear infinite` }} />
            <CardContent sx={{ p: { xs: 3, md: 5 } }}>
              <Typography
                variant="h5"
                sx={{
                  fontFamily: '"Inter", sans-serif',
                  fontWeight: 800,
                  mb: 1,
                  background: 'linear-gradient(135deg, #6366f1, #ec4899)',
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                }}
              >
                Theme
              </Typography>
              <Typography
                variant="body2"
                sx={{
                  fontFamily: '"Inter", sans-serif',
                  color: alpha(theme.palette.text.secondary, 0.6),
                  mb: 4,
                }}
              >
                Switch between light and dark mode to suit your preference.
              </Typography>

              {/* Beautiful theme toggle */}
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: 4,
                  py: 5,
                }}
              >
                {/* Light mode side */}
                <Box
                  sx={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    gap: 1.5,
                    opacity: settings.themeMode === 'light' ? 1 : 0.35,
                    transition: 'all 0.5s ease',
                  }}
                >
                  <Box
                    sx={{
                      width: 72,
                      height: 72,
                      borderRadius: '50%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      background: settings.themeMode === 'light'
                        ? 'linear-gradient(135deg, #f59e0b, #f97316)'
                        : alpha(theme.palette.text.secondary, 0.06),
                      boxShadow: settings.themeMode === 'light'
                        ? `0 0 32px ${alpha('#f59e0b', 0.35)}, 0 0 64px ${alpha('#f59e0b', 0.15)}`
                        : 'none',
                      transition: 'all 0.5s ease',
                    }}
                  >
                    <LightModeIcon
                      sx={{
                        fontSize: 36,
                        color: settings.themeMode === 'light' ? '#fff' : theme.palette.text.secondary,
                        transition: 'all 0.5s ease',
                      }}
                    />
                  </Box>
                  <Typography
                    variant="caption"
                    sx={{
                      fontFamily: '"Inter", sans-serif',
                      fontWeight: 700,
                      fontSize: '0.8rem',
                      color: settings.themeMode === 'light' ? '#f59e0b' : theme.palette.text.secondary,
                      transition: 'all 0.5s ease',
                    }}
                  >
                    Light
                  </Typography>
                </Box>

                {/* Toggle switch */}
                <Box
                  onClick={() => dispatch(toggleTheme())}
                  sx={{
                    width: 72,
                    height: 38,
                    borderRadius: '19px',
                    cursor: 'pointer',
                    position: 'relative',
                    background: settings.themeMode === 'dark'
                      ? 'linear-gradient(135deg, #6366f1, #8b5cf6)'
                      : 'linear-gradient(135deg, #f59e0b, #f97316)',
                    boxShadow: `0 2px 12px ${alpha(settings.themeMode === 'dark' ? '#6366f1' : '#f59e0b', 0.35)}`,
                    transition: 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)',
                    '&:hover': {
                      transform: 'scale(1.05)',
                    },
                  }}
                >
                  <Box
                    sx={{
                      position: 'absolute',
                      top: 3,
                      left: settings.themeMode === 'dark' ? 37 : 3,
                      width: 32,
                      height: 32,
                      borderRadius: '50%',
                      background: '#fff',
                      boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
                      transition: 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    {settings.themeMode === 'dark' ? (
                      <DarkModeIcon sx={{ fontSize: 18, color: '#6366f1' }} />
                    ) : (
                      <LightModeIcon sx={{ fontSize: 18, color: '#f59e0b' }} />
                    )}
                  </Box>
                </Box>

                {/* Dark mode side */}
                <Box
                  sx={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    gap: 1.5,
                    opacity: settings.themeMode === 'dark' ? 1 : 0.35,
                    transition: 'all 0.5s ease',
                  }}
                >
                  <Box
                    sx={{
                      width: 72,
                      height: 72,
                      borderRadius: '50%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      background: settings.themeMode === 'dark'
                        ? 'linear-gradient(135deg, #6366f1, #8b5cf6)'
                        : alpha(theme.palette.text.secondary, 0.06),
                      boxShadow: settings.themeMode === 'dark'
                        ? `0 0 32px ${alpha('#6366f1', 0.35)}, 0 0 64px ${alpha('#6366f1', 0.15)}`
                        : 'none',
                      transition: 'all 0.5s ease',
                    }}
                  >
                    <DarkModeIcon
                      sx={{
                        fontSize: 36,
                        color: settings.themeMode === 'dark' ? '#fff' : theme.palette.text.secondary,
                        transition: 'all 0.5s ease',
                      }}
                    />
                  </Box>
                  <Typography
                    variant="caption"
                    sx={{
                      fontFamily: '"Inter", sans-serif',
                      fontWeight: 700,
                      fontSize: '0.8rem',
                      color: settings.themeMode === 'dark' ? '#6366f1' : theme.palette.text.secondary,
                      transition: 'all 0.5s ease',
                    }}
                  >
                    Dark
                  </Typography>
                </Box>
              </Box>

              {/* Current mode label */}
              <Box sx={{ textAlign: 'center', mt: 2 }}>
                <Chip
                  label={settings.themeMode === 'dark' ? 'Dark Mode Active' : 'Light Mode Active'}
                  sx={{
                    fontFamily: '"Inter", sans-serif',
                    fontWeight: 600,
                    fontSize: '0.8rem',
                    height: 32,
                    borderRadius: '10px',
                    background: alpha('#6366f1', 0.1),
                    color: '#6366f1',
                    border: `1px solid ${alpha('#6366f1', 0.2)}`,
                  }}
                />
              </Box>
            </CardContent>
          </Card>
        </Fade>
      )}

      {/* ─────────────── Usage Tab ─────────────── */}
      {activeTab === 3 && (
        <Fade in timeout={500}>
          <Card sx={{ ...glassCard }}>
            <Box sx={{ height: 3, background: 'linear-gradient(90deg, #6366f1, #ec4899, #6366f1)', backgroundSize: '200% 100%', animation: `${shimmer} 3s linear infinite` }} />
            <CardContent sx={{ p: { xs: 3, md: 5 } }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
                <Box>
                  <Typography
                    variant="h5"
                    sx={{
                      fontFamily: '"Inter", sans-serif',
                      fontWeight: 800,
                      background: 'linear-gradient(135deg, #6366f1, #ec4899)',
                      backgroundClip: 'text',
                      WebkitBackgroundClip: 'text',
                      WebkitTextFillColor: 'transparent',
                    }}
                  >
                    Token Usage
                  </Typography>
                  <Typography
                    variant="body2"
                    sx={{
                      fontFamily: '"Inter", sans-serif',
                      color: alpha(theme.palette.text.secondary, 0.6),
                      mt: 0.5,
                    }}
                  >
                    Monitor your API consumption and costs.
                  </Typography>
                </Box>
                <IconButton
                  onClick={() => dispatch(fetchTokenUsage())}
                  disabled={!settings.sessionToken || settings.usageLoading}
                  sx={{
                    width: 44,
                    height: 44,
                    borderRadius: '12px',
                    background: alpha('#6366f1', 0.08),
                    border: `1px solid ${alpha('#6366f1', 0.15)}`,
                    color: '#6366f1',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      background: alpha('#6366f1', 0.15),
                      transform: 'rotate(180deg)',
                    },
                  }}
                >
                  <RefreshIcon />
                </IconButton>
              </Box>

              {!settings.isConnected ? (
                <Alert
                  severity="info"
                  sx={{
                    borderRadius: '14px',
                    fontFamily: '"Inter", sans-serif',
                    border: `1px solid ${alpha(theme.palette.info.main, 0.15)}`,
                  }}
                >
                  Connect to a provider to view token usage statistics.
                </Alert>
              ) : settings.usageLoading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
                  <CircularProgress sx={{ color: '#6366f1' }} />
                </Box>
              ) : settings.tokenUsage ? (
                <Box
                  sx={{
                    display: 'grid',
                    gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)' },
                    gap: 3,
                  }}
                >
                  {/* Stat Card: Total Requests */}
                  <Paper
                    elevation={0}
                    sx={{
                      p: 3,
                      textAlign: 'center',
                      borderRadius: '18px',
                      background: alpha(theme.palette.background.default, 0.5),
                      border: `1px solid ${alpha('#6366f1', 0.1)}`,
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        transform: 'translateY(-4px)',
                        boxShadow: `0 8px 24px ${alpha('#6366f1', 0.12)}`,
                        borderColor: alpha('#6366f1', 0.25),
                      },
                    }}
                  >
                    <Typography
                      variant="h3"
                      sx={{
                        fontFamily: '"JetBrains Mono", monospace',
                        fontWeight: 800,
                        background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                        backgroundClip: 'text',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                        mb: 0.5,
                        fontSize: { xs: '2rem', md: '2.2rem' },
                      }}
                    >
                      {settings.tokenUsage.request_count}
                    </Typography>
                    <Typography
                      variant="body2"
                      sx={{
                        fontFamily: '"Inter", sans-serif',
                        color: alpha(theme.palette.text.secondary, 0.6),
                        fontWeight: 500,
                        fontSize: '0.8rem',
                      }}
                    >
                      Total Requests
                    </Typography>
                  </Paper>

                  {/* Stat Card: Prompt Tokens */}
                  <Paper
                    elevation={0}
                    sx={{
                      p: 3,
                      textAlign: 'center',
                      borderRadius: '18px',
                      background: alpha(theme.palette.background.default, 0.5),
                      border: `1px solid ${alpha('#6366f1', 0.1)}`,
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        transform: 'translateY(-4px)',
                        boxShadow: `0 8px 24px ${alpha('#6366f1', 0.12)}`,
                        borderColor: alpha('#6366f1', 0.25),
                      },
                    }}
                  >
                    <Typography
                      variant="h3"
                      sx={{
                        fontFamily: '"JetBrains Mono", monospace',
                        fontWeight: 800,
                        background: 'linear-gradient(135deg, #6366f1, #a78bfa)',
                        backgroundClip: 'text',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                        mb: 0.5,
                        fontSize: { xs: '2rem', md: '2.2rem' },
                      }}
                    >
                      {settings.tokenUsage.total_prompt_tokens.toLocaleString()}
                    </Typography>
                    <Typography
                      variant="body2"
                      sx={{
                        fontFamily: '"Inter", sans-serif',
                        color: alpha(theme.palette.text.secondary, 0.6),
                        fontWeight: 500,
                        fontSize: '0.8rem',
                      }}
                    >
                      Prompt Tokens
                    </Typography>
                  </Paper>

                  {/* Stat Card: Completion Tokens */}
                  <Paper
                    elevation={0}
                    sx={{
                      p: 3,
                      textAlign: 'center',
                      borderRadius: '18px',
                      background: alpha(theme.palette.background.default, 0.5),
                      border: `1px solid ${alpha('#6366f1', 0.1)}`,
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        transform: 'translateY(-4px)',
                        boxShadow: `0 8px 24px ${alpha('#ec4899', 0.12)}`,
                        borderColor: alpha('#ec4899', 0.25),
                      },
                    }}
                  >
                    <Typography
                      variant="h3"
                      sx={{
                        fontFamily: '"JetBrains Mono", monospace',
                        fontWeight: 800,
                        background: 'linear-gradient(135deg, #ec4899, #f472b6)',
                        backgroundClip: 'text',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                        mb: 0.5,
                        fontSize: { xs: '2rem', md: '2.2rem' },
                      }}
                    >
                      {settings.tokenUsage.total_completion_tokens.toLocaleString()}
                    </Typography>
                    <Typography
                      variant="body2"
                      sx={{
                        fontFamily: '"Inter", sans-serif',
                        color: alpha(theme.palette.text.secondary, 0.6),
                        fontWeight: 500,
                        fontSize: '0.8rem',
                      }}
                    >
                      Completion Tokens
                    </Typography>
                  </Paper>

                  {/* Stat Card: Estimated Cost */}
                  <Paper
                    elevation={0}
                    sx={{
                      p: 3,
                      textAlign: 'center',
                      borderRadius: '18px',
                      background: alpha(theme.palette.background.default, 0.5),
                      border: `1px solid ${alpha('#ec4899', 0.1)}`,
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        transform: 'translateY(-4px)',
                        boxShadow: `0 8px 24px ${alpha('#ec4899', 0.12)}`,
                        borderColor: alpha('#ec4899', 0.25),
                      },
                    }}
                  >
                    <Typography
                      variant="h3"
                      sx={{
                        fontFamily: '"JetBrains Mono", monospace',
                        fontWeight: 800,
                        background: 'linear-gradient(135deg, #ec4899, #f43f5e)',
                        backgroundClip: 'text',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                        mb: 0.5,
                        fontSize: { xs: '2rem', md: '2.2rem' },
                      }}
                    >
                      ${settings.tokenUsage.total_cost.toFixed(4)}
                    </Typography>
                    <Typography
                      variant="body2"
                      sx={{
                        fontFamily: '"Inter", sans-serif',
                        color: alpha(theme.palette.text.secondary, 0.6),
                        fontWeight: 500,
                        fontSize: '0.8rem',
                      }}
                    >
                      Estimated Cost
                    </Typography>
                  </Paper>
                </Box>
              ) : (
                <Alert
                  severity="info"
                  sx={{
                    borderRadius: '14px',
                    fontFamily: '"Inter", sans-serif',
                    border: `1px solid ${alpha(theme.palette.info.main, 0.15)}`,
                  }}
                >
                  No usage data available yet. Start analyzing to see your token usage.
                </Alert>
              )}
            </CardContent>
          </Card>
        </Fade>
      )}
    </Box>
  );
};

export default Settings;
