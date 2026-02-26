import React from 'react';
import {
  Box,
  Typography,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  CircularProgress,
  useTheme,
  Chip,
  Paper,
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty';
import RadioButtonUncheckedIcon from '@mui/icons-material/RadioButtonUnchecked';

export interface AnalysisStep {
  label: string;
  description: string;
  status: 'pending' | 'running' | 'completed' | 'error';
  detail?: string;
  duration?: number;
}

interface ProgressTrackerProps {
  steps: AnalysisStep[];
  currentStep: number;
}

const ProgressTracker: React.FC<ProgressTrackerProps> = ({ steps, currentStep }) => {
  const theme = useTheme();

  const getStepIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon sx={{ color: theme.palette.success.main }} />;
      case 'running':
        return <CircularProgress size={20} thickness={4} />;
      case 'error':
        return <ErrorIcon sx={{ color: theme.palette.error.main }} />;
      default:
        return <RadioButtonUncheckedIcon sx={{ color: theme.palette.text.disabled }} />;
    }
  };

  const completedSteps = steps.filter((s) => s.status === 'completed').length;
  const overallProgress = steps.length > 0 ? (completedSteps / steps.length) * 100 : 0;

  return (
    <Paper
      sx={{
        p: 2,
        background: `linear-gradient(135deg, ${theme.palette.background.paper}, ${theme.palette.background.default})`,
        border: `1px solid ${theme.palette.divider}`,
        borderRadius: 2,
      }}
    >
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="subtitle1" fontWeight="bold">
          Analysis Progress
        </Typography>
        <Chip
          label={`${completedSteps}/${steps.length}`}
          size="small"
          color={completedSteps === steps.length ? 'success' : 'primary'}
        />
      </Box>

      {/* Overall progress bar */}
      <Box sx={{ mb: 2 }}>
        <Box
          sx={{
            width: '100%',
            height: 6,
            borderRadius: 3,
            backgroundColor: theme.palette.action.disabledBackground,
            overflow: 'hidden',
          }}
        >
          <Box
            sx={{
              width: `${overallProgress}%`,
              height: '100%',
              borderRadius: 3,
              background: `linear-gradient(90deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
              transition: 'width 0.5s ease',
            }}
          />
        </Box>
      </Box>

      <Stepper activeStep={currentStep} orientation="vertical" sx={{ '& .MuiStepConnector-line': { borderColor: theme.palette.divider } }}>
        {steps.map((step, index) => (
          <Step key={index} completed={step.status === 'completed'}>
            <StepLabel
              icon={getStepIcon(step.status)}
              sx={{
                '& .MuiStepLabel-label': {
                  color: step.status === 'running'
                    ? theme.palette.primary.main
                    : step.status === 'completed'
                    ? theme.palette.success.main
                    : step.status === 'error'
                    ? theme.palette.error.main
                    : theme.palette.text.secondary,
                  fontWeight: step.status === 'running' ? 'bold' : 'normal',
                },
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                {step.label}
                {step.duration && step.status === 'completed' && (
                  <Typography variant="caption" color="text.secondary">
                    ({(step.duration / 1000).toFixed(1)}s)
                  </Typography>
                )}
              </Box>
            </StepLabel>
            {step.status === 'running' && step.description && (
              <StepContent>
                <Typography variant="body2" color="text.secondary">
                  {step.description}
                </Typography>
              </StepContent>
            )}
            {step.status === 'error' && step.detail && (
              <StepContent>
                <Typography variant="body2" color="error">
                  {step.detail}
                </Typography>
              </StepContent>
            )}
          </Step>
        ))}
      </Stepper>
    </Paper>
  );
};

export default ProgressTracker;
