import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

export interface YaraRule {
  name: string;
  description: string;
  rule: string;
  severity: string;
  tags: string[];
  metadata: {
    author: string;
    version: string;
  };
}

export interface SigmaMatch {
  id: string;
  title: string;
  description: string;
  level: string;
  match_ratio: number;
  matched_keywords: string[];
  tags: string[];
  github_link: string;
}

export interface SIEMQuery {
  description: string;
  query: string;
  notes: string;
}

export interface SIEMQueries {
  splunk: SIEMQuery;
  qradar: SIEMQuery;
  elastic: SIEMQuery;
  sentinel: SIEMQuery;
}

export interface AnalysisData {
  threat_summary: string;
  iocs: string[];
  ttps: TTP[];
  threat_actors: string[];
  tools_or_malware: string[];
  yara_rules: YaraRule[];
  sigma_matches: SigmaMatch[];
  generated_sigma_rules: string[];
}

export interface TTP {
  mitre_id: string;
  technique_name: string;
  description: string;
}

export interface AnalysisResult {
  threat_summary: string;
  analysis_data: {
    indicators_of_compromise: {
      [key: string]: string[];
    };
    ttps: TTP[];
    threat_actors: string[];
    tools_or_malware: string[];
  };
  generated_sigma_rules: string;
  siem_queries: SIEMQueries;
  yara_rules: Array<{
    name: string;
    description: string;
    severity: string;
    rule: string;
    tags: string[];
    metadata: {
      author: string;
      version: string;
    };
  }>;
  sigma_matches: Array<{
    id: string;
    title: string;
    level: string;
    match_ratio: number;
    description: string;
    matched_keywords: string[];
    tags: string[];
  }>;
}

export interface RuleResponse {
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

export interface RuleAnalysis {
  quality: number;
  mitreMapping: string[];
  falsePositiveRisk: number;
  suggestions: string[];
  testResults: {
    passed: boolean;
    details: string;
  }[];
}

export const analyzeUrl = async (url: string, openaiApiKey: string): Promise<AnalysisResult> => {
  const response = await fetch(`${API_URL}/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ url, openai_api_key: openaiApiKey }),
  });

  if (!response.ok) {
    throw new Error('Failed to analyze URL');
  }

  return response.json();
};

export const generate_sigma_rule = async (threat_summary: string, openaiApiKey: string): Promise<string> => {
  try {
    const response = await fetch(`${API_URL}/generate_sigma_rule`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${openaiApiKey}`
      },
      body: JSON.stringify({
        threat_summary,
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to generate Sigma rules');
    }

    const data = await response.json();
    return data.rule;
  } catch (error) {
    console.error('Error generating Sigma rules:', error);
    throw error;
  }
};

export const generateRule = async (prompt: string, openaiApiKey: string): Promise<RuleResponse> => {
  try {
    const response = await fetch(`${API_URL}/generate_rule`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        prompt,
        openai_api_key: openaiApiKey,
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to generate rule');
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error generating rule:', error);
    throw error;
  }
}; 