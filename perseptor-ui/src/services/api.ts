/**
 * PERSEPTOR v2.0 - Unified API Service
 * Types, interfaces, HTTP client with session injection, retry logic, and API functions.
 */

import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';

// ─── Configuration ──────────────────────────────────────────────────────────

const API_URL = '/api';
const MAX_RETRIES = 2;
const RETRY_DELAY_MS = 1000;

// ─── HTTP Client ────────────────────────────────────────────────────────────

const client: AxiosInstance = axios.create({
  baseURL: '',
  timeout: 600000, // 10 minutes for long analysis (OCR + multiple AI calls)
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor — inject session token
client.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    try {
      const settings = localStorage.getItem('perseptor_settings');
      if (settings) {
        const parsed = JSON.parse(settings);
        if (parsed.sessionToken && !config.headers['X-Session-Token']) {
          config.headers['X-Session-Token'] = parsed.sessionToken;
        }
      }
    } catch {
      // Ignore localStorage errors
    }
    return config;
  },
  (error: AxiosError) => Promise.reject(error)
);

// Response Interceptor — retry logic + session expiry handling
client.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const config = error.config as InternalAxiosRequestConfig & {
      _retryCount?: number;
    };

    if (!config || !error.response) {
      return Promise.reject(error);
    }

    const status = error.response.status;

    // Session expired
    if (status === 401) {
      try {
        localStorage.removeItem('perseptor_settings');
      } catch {
        // Ignore
      }
      return Promise.reject(error);
    }

    // Rate limited — retry after delay
    if (status === 429) {
      const retryAfter = error.response.headers['retry-after'];
      const delay = retryAfter ? parseInt(retryAfter) * 1000 : RETRY_DELAY_MS * 2;

      config._retryCount = (config._retryCount || 0) + 1;
      if (config._retryCount <= MAX_RETRIES) {
        await new Promise((resolve) => setTimeout(resolve, delay));
        return client(config);
      }
    }

    // Server errors — retry with backoff
    if (status >= 500 && status < 600) {
      config._retryCount = (config._retryCount || 0) + 1;
      if (config._retryCount <= MAX_RETRIES) {
        const delay = RETRY_DELAY_MS * Math.pow(2, config._retryCount - 1);
        await new Promise((resolve) => setTimeout(resolve, delay));
        return client(config);
      }
    }

    return Promise.reject(error);
  }
);

export const apiClient = client;

// ─── Type Definitions ───────────────────────────────────────────────────────

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
  status?: string;
  match_ratio: number;
  combined_score?: number;
  confidence?: string;
  mitre_matched?: string[];
  logsource?: { category?: string; product?: string };
  matched_keywords: string[];
  phrase_matches?: string[];
  tags: string[];
  github_link: string;
  score_breakdown?: {
    mitre: number;
    ioc_field: number;
    logsource: number;
    keyword: number;
  };
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

export interface MitreTechnique {
  technique_id: string;
  technique_name: string;
  tactic: string;
  confidence: number;
  source: string;
  keyword_hits?: number;
}

export interface MitreMapping {
  techniques: MitreTechnique[];
  tactic_summary: { [tactic: string]: number };
  tags: string[];
}

export interface Maturity {
  level: string;
  label: string;
  maturity_score: number;
  criteria_met: number;
  criteria_total: number;
  criteria: { [key: string]: boolean };
  recommendations: string[];
}

export interface AtomicTestExecutor {
  type: string;
  steps: string[];
  command: string;
  elevation_required: boolean;
}

export interface AtomicTestDetection {
  log_source: string;
  event_ids: string[];
  key_fields: { [key: string]: string };
  sigma_condition_match: string;
}

export interface AtomicTestCleanup {
  command: string;
  description: string;
}

export interface AtomicTestReference {
  threat_actors: string[];
  malware_families: string[];
  mitre_url: string;
  atomic_red_team_id: string | null;
}

export interface AtomicTest {
  sigma_rule_title: string;
  test_name: string;
  description: string;
  mitre_technique: string;
  platforms: string[];
  privilege_required: string;
  prerequisites: string[];
  executor: AtomicTestExecutor;
  expected_detection: AtomicTestDetection;
  cleanup: AtomicTestCleanup;
  real_world_reference: AtomicTestReference;
  safety_notes: string;
}

export interface AnalysisResult {
  threat_summary: string;
  analysis_data: {
    indicators_of_compromise: {
      [key: string]: string[];
    };
    ttps: TTP[] | string[];
    threat_actors: string[];
    tools_or_malware: string[];
  };
  mitre_mapping?: MitreMapping;
  ioc_sigma_rules?: Array<{
    title: string;
    rule_yaml: string;
    category: string;
    level: string;
    tags: string[];
    ioc_type: string;
    ioc_count: number;
  }>;
  generated_sigma_rules: string;
  siem_queries: SIEMQueries;
  atomic_tests?: AtomicTest[];
  yara_rules: Array<{
    name: string;
    description: string;
    severity: string;
    rule: string;
    tags: string[];
    ioc_type?: string;
    ioc_count?: number;
  }>;
  sigma_matches: Array<{
    id: string;
    title: string;
    level: string;
    status?: string;
    match_ratio: number;
    combined_score?: number;
    confidence?: string;
    mitre_matched?: string[];
    logsource?: { category?: string; product?: string };
    description: string;
    matched_keywords: string[];
    phrase_matches?: string[];
    tags: string[];
    github_link?: string;
    score_breakdown?: {
      mitre: number;
      ioc_field: number;
      logsource: number;
      keyword: number;
    };
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
  explanations?: {
    [key: string]: string;
  };
  weights?: {
    [key: string]: number;
  };
  maturity?: Maturity;
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

// ─── API Functions ──────────────────────────────────────────────────────────

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
