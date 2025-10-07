import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  InputAdornment,
  Alert,
  Skeleton,
  Paper,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Fade,
  Zoom,
} from '@mui/material';
import {
  Search as SearchIcon,
  Visibility as ViewIcon,
  Download as DownloadIcon,
  Delete as DeleteIcon,
  Security as SecurityIcon,
  Code as CodeIcon,
  Description as DescriptionIcon,
} from '@mui/icons-material';
import { useTheme } from '@mui/material/styles';
import SigmaIcon from '../components/SigmaIcon';
// @ts-ignore
import * as yaml from 'js-yaml';

interface Rule {
  id: string;
  title: string;
  description: string;
  author: string;
  date: string;
  product: string;
  confidence_score: number;
  mitre_techniques: Array<{
    id: string;
    name: string;
    description: string;
  }>;
  test_cases: Array<{
    name: string;
    description: string;
    expected_result: string;
  }>;
  recommendations: string[];
  references: Array<{
    title: string;
    url: string;
    description: string;
  }>;
  rule_content: any;
}

const CreatedRules: React.FC = () => {
  const theme = useTheme();
  const [rules, setRules] = useState<Rule[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRule, setSelectedRule] = useState<Rule | null>(null);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showAnimation, setShowAnimation] = useState(false);

  useEffect(() => {
    setShowAnimation(true);
    fetchRules();
  }, []);

  const fetchRules = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:5000/api/rules');
      if (response.ok) {
        const data = await response.json();
        setRules(data.rules || []);
      } else {
        setError('Failed to fetch rules');
      }
    } catch (err) {
      setError('Error fetching rules');
      console.error('Error fetching rules:', err);
    } finally {
      setLoading(false);
    }
  };

  const filteredRules = rules.filter(rule =>
    rule.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    rule.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
    rule.product.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleViewRule = (rule: Rule) => {
    setSelectedRule(rule);
    setViewDialogOpen(true);
  };

  const handleDownloadRule = async (rule: Rule) => {
    try {
      const response = await fetch(`http://localhost:5000/api/rules/${rule.id}/download`);
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${rule.title.replace(/\s+/g, '_')}.yaml`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (err) {
      console.error('Error downloading rule:', err);
    }
  };

  const handleDeleteRule = async (ruleId: string) => {
    if (window.confirm('Are you sure you want to delete this rule?')) {
      try {
        const response = await fetch(`http://localhost:5000/api/rules/${ruleId}`, {
          method: 'DELETE',
        });
        if (response.ok) {
          setRules(rules.filter(rule => rule.id !== ruleId));
        }
      } catch (err) {
        console.error('Error deleting rule:', err);
      }
    }
  };

  const getConfidenceColor = (score: number) => {
    if (score >= 0.8) return 'success';
    if (score >= 0.6) return 'warning';
    return 'error';
  };

  const getConfidenceLabel = (score: number) => {
    if (score >= 0.8) return 'High';
    if (score >= 0.6) return 'Medium';
    return 'Low';
  };

  if (loading) {
    return (
      <Box sx={{ p: 3, ml: '280px' }}>
        <Typography variant="h4" gutterBottom>
          Created Rules
        </Typography>
        <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 3 }}>
          {[1, 2, 3].map((item) => (
            <Skeleton key={item} variant="rectangular" height={200} />
          ))}
        </Box>
      </Box>
    );
  }

  return (
    <Zoom in={showAnimation} timeout={1000} style={{ transitionDelay: '200ms' }}>
      <Box sx={{ p: 3, ml: '280px' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
          <SigmaIcon color={theme.palette.primary.main} width={48} height={48} />
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
            Created Rules
          </Typography>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        <TextField
          fullWidth
          variant="outlined"
          placeholder="Search rules by title, description, or product..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
          sx={{ mb: 3 }}
        />

        {filteredRules.length === 0 ? (
          <Paper
            sx={{
              p: 4,
              textAlign: 'center',
              background: `linear-gradient(135deg, ${theme.palette.background.paper}, ${theme.palette.background.default})`,
            }}
          >
            <SecurityIcon sx={{ fontSize: 64, color: theme.palette.text.secondary, mb: 2 }} />
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No rules found
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {searchTerm ? 'Try adjusting your search terms' : 'Create your first rule in the Detection QA section'}
            </Typography>
          </Paper>
        ) : (
          <Box
            sx={{
              display: 'flex',
              flexWrap: 'wrap',
              justifyContent: 'center',
              alignItems: 'flex-start',
              gap: 3,
              minHeight: '60vh',
              mt: 2,
            }}
          >
            {filteredRules.map((rule) => (
              <Box key={rule.id} sx={{ minWidth: 350, maxWidth: 420, flex: '1 1 350px' }}>
                <Card
                  sx={{
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: `0 8px 32px ${theme.palette.primary.main}20`,
                    },
                  }}
                >
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                      <Typography variant="h6" component="h2" gutterBottom sx={{ fontWeight: 'bold' }}>
                        {rule.title}
                      </Typography>
                      <Chip
                        label={rule.product.toUpperCase()}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                    </Box>

                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {rule.description}
                    </Typography>

                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                      <Typography variant="caption" color="text.secondary">
                        By {rule.author} • {new Date(rule.date).toLocaleDateString()}
                      </Typography>
                      <Chip
                        label={`${getConfidenceLabel(rule.confidence_score)} (${(rule.confidence_score * 100).toFixed(0)}%)`}
                        size="small"
                        color={getConfidenceColor(rule.confidence_score) as any}
                      />
                    </Box>

                    {rule.mitre_techniques.length > 0 && (
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
                          MITRE Techniques:
                        </Typography>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                          {rule.mitre_techniques.slice(0, 3).map((technique) => (
                            <Chip
                              key={technique.id}
                              label={technique.id}
                              size="small"
                              variant="outlined"
                              sx={{ fontSize: '0.7rem' }}
                            />
                          ))}
                          {rule.mitre_techniques.length > 3 && (
                            <Chip
                              label={`+${rule.mitre_techniques.length - 3}`}
                              size="small"
                              variant="outlined"
                              sx={{ fontSize: '0.7rem' }}
                            />
                          )}
                        </Box>
                      </Box>
                    )}

                    <Divider sx={{ my: 2 }} />

                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Box>
                        <Typography variant="caption" color="text.secondary" display="block">
                          {rule.test_cases.length} test cases
                        </Typography>
                        <Typography variant="caption" color="text.secondary" display="block">
                          {rule.recommendations.length} recommendations
                        </Typography>
                      </Box>
                      <Box>
                        <IconButton
                          size="small"
                          onClick={() => handleViewRule(rule)}
                          sx={{ color: theme.palette.primary.main }}
                        >
                          <ViewIcon />
                        </IconButton>
                        <IconButton
                          size="small"
                          onClick={() => handleDownloadRule(rule)}
                          sx={{ color: theme.palette.success.main }}
                        >
                          <DownloadIcon />
                        </IconButton>
                        <IconButton
                          size="small"
                          onClick={() => handleDeleteRule(rule.id)}
                          sx={{ color: theme.palette.error.main }}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Box>
            ))}
          </Box>
        )}

        {/* Rule Detail Dialog */}
        <Dialog
          open={viewDialogOpen}
          onClose={() => setViewDialogOpen(false)}
          maxWidth="md"
          fullWidth
        >
          {selectedRule && (
            <>
              <DialogTitle>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <SecurityIcon color="primary" />
                  <Typography variant="h6">{selectedRule.title}</Typography>
                </Box>
              </DialogTitle>
              <DialogContent>
                <Box sx={{ mb: 3 }}>
                  <Typography variant="body1" gutterBottom>
                    {selectedRule.description}
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
                    <Chip label={selectedRule.product.toUpperCase()} color="primary" />
                    <Chip
                      label={`Confidence: ${(selectedRule.confidence_score * 100).toFixed(0)}%`}
                      color={getConfidenceColor(selectedRule.confidence_score) as any}
                    />
                  </Box>
                </Box>

                {selectedRule.mitre_techniques.length > 0 && (
                  <Box sx={{ mb: 3 }}>
                    <Typography variant="h6" gutterBottom>
                      MITRE ATT&CK Techniques
                    </Typography>
                    <List dense>
                      {selectedRule.mitre_techniques.map((technique) => (
                        <ListItem key={technique.id}>
                          <ListItemText
                            primary={`${technique.id}: ${technique.name}`}
                            secondary={technique.description}
                          />
                        </ListItem>
                      ))}
                    </List>
                  </Box>
                )}

                {selectedRule.test_cases.length > 0 && (
                  <Box sx={{ mb: 3 }}>
                    <Typography variant="h6" gutterBottom>
                      Test Cases
                    </Typography>
                    <List dense>
                      {selectedRule.test_cases.map((testCase, index) => (
                        <ListItem key={index}>
                          <ListItemText
                            primary={testCase.name}
                            secondary={
                              <>
                                <Typography variant="body2" color="text.secondary">
                                  {testCase.description}
                                </Typography>
                                <Typography variant="body2" color="primary">
                                  Expected: {testCase.expected_result}
                                </Typography>
                              </>
                            }
                          />
                        </ListItem>
                      ))}
                    </List>
                  </Box>
                )}

                {selectedRule.recommendations.length > 0 && (
                  <Box sx={{ mb: 3 }}>
                    <Typography variant="h6" gutterBottom>
                      Recommendations
                    </Typography>
                    <List dense>
                      {selectedRule.recommendations.map((rec, index) => (
                        <ListItem key={index}>
                          <ListItemText primary={rec} />
                        </ListItem>
                      ))}
                    </List>
                  </Box>
                )}

                {selectedRule.references.length > 0 && (
                  <Box sx={{ mb: 3 }}>
                    <Typography variant="h6" gutterBottom>
                      References
                    </Typography>
                    <List dense>
                      {selectedRule.references.map((ref, index) => (
                        <ListItem key={index}>
                          <ListItemText
                            primary={
                              <a href={ref.url} target="_blank" rel="noopener noreferrer" style={{ color: theme.palette.primary.main }}>
                                {ref.title}
                              </a>
                            }
                            secondary={ref.description}
                          />
                        </ListItem>
                      ))}
                    </List>
                  </Box>
                )}

                <Box>
                  <Typography variant="h6" gutterBottom>
                    Rule Content
                  </Typography>
                  <Paper
                    sx={{
                      p: 2,
                      backgroundColor: theme.palette.mode === 'dark' ? '#222' : '#f5f5f5',
                      fontFamily: 'monospace',
                      fontSize: '0.95rem',
                      overflow: 'auto',
                      maxHeight: 300,
                      border: `1px solid ${theme.palette.divider}`,
                    }}
                  >
                    <pre style={{
                      margin: 0,
                      whiteSpace: 'pre-wrap',
                      wordBreak: 'break-word',
                      color: theme.palette.mode === 'dark' ? '#fff' : '#222',
                    }}>
                      {yaml.dump(selectedRule.rule_content)}
                    </pre>
                  </Paper>
                </Box>
              </DialogContent>
              <DialogActions>
                <Button onClick={() => handleDownloadRule(selectedRule)} startIcon={<DownloadIcon />}>
                  Download
                </Button>
                <Button onClick={() => setViewDialogOpen(false)}>Close</Button>
              </DialogActions>
            </>
          )}
        </Dialog>
      </Box>
    </Zoom>
  );
};

export default CreatedRules; 