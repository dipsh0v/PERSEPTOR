/**
 * PERSEPTOR v2.0 - Rules Slice
 * Manages created rules state and async operations.
 */

import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { apiClient } from '../../services/api';
import type { RuleResponse } from '../../services/api';
import type { RootState } from '../index';

// ─── Types ──────────────────────────────────────────────────────────────────

export interface Rule {
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

export interface RulesState {
  rules: Rule[];
  selectedRule: Rule | null;
  searchTerm: string;
  loading: boolean;
  error: string | null;

  // Rule generation
  generationPrompt: string;
  generatedRule: RuleResponse | null;
  generating: boolean;
  generationError: string | null;
}

const initialState: RulesState = {
  rules: [],
  selectedRule: null,
  searchTerm: '',
  loading: false,
  error: null,

  generationPrompt: '',
  generatedRule: null,
  generating: false,
  generationError: null,
};

// ─── Async Thunks ───────────────────────────────────────────────────────────

export const fetchRules = createAsyncThunk(
  'rules/fetchRules',
  async (_, { rejectWithValue }) => {
    try {
      const response = await apiClient.get('/api/rules');
      return (response.data.rules || []) as Rule[];
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.error || 'Failed to fetch rules');
    }
  }
);

export const deleteRule = createAsyncThunk(
  'rules/deleteRule',
  async (ruleId: string, { rejectWithValue }) => {
    try {
      await apiClient.delete(`/api/rules/${ruleId}`);
      return ruleId;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.error || 'Failed to delete rule');
    }
  }
);

export const generateRule = createAsyncThunk(
  'rules/generateRule',
  async (prompt: string, { getState, rejectWithValue }) => {
    try {
      const state = getState() as RootState;
      const { sessionToken, aiProvider, selectedModel, apiKey } = state.settings;

      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };
      if (sessionToken) {
        headers['X-Session-Token'] = sessionToken;
      }

      const body: Record<string, any> = {
        prompt,
        provider: aiProvider,
        model: selectedModel,
      };

      if (!sessionToken && apiKey) {
        body.openai_api_key = apiKey;
      }

      const response = await apiClient.post('/api/generate_rule', body, { headers });
      return response.data as RuleResponse;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.error || 'Failed to generate rule');
    }
  }
);

// ─── Slice ──────────────────────────────────────────────────────────────────

const rulesSlice = createSlice({
  name: 'rules',
  initialState,
  reducers: {
    setSearchTerm(state, action: PayloadAction<string>) {
      state.searchTerm = action.payload;
    },
    setSelectedRule(state, action: PayloadAction<Rule | null>) {
      state.selectedRule = action.payload;
    },
    setGenerationPrompt(state, action: PayloadAction<string>) {
      state.generationPrompt = action.payload;
    },
    clearGeneratedRule(state) {
      state.generatedRule = null;
      state.generationError = null;
    },
    clearRulesError(state) {
      state.error = null;
    },
    clearGenerationError(state) {
      state.generationError = null;
    },
  },
  extraReducers: (builder) => {
    // Fetch rules
    builder
      .addCase(fetchRules.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchRules.fulfilled, (state, action) => {
        state.loading = false;
        state.rules = action.payload;
      })
      .addCase(fetchRules.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // Delete rule
    builder
      .addCase(deleteRule.fulfilled, (state, action) => {
        state.rules = state.rules.filter((rule) => rule.id !== action.payload);
        if (state.selectedRule?.id === action.payload) {
          state.selectedRule = null;
        }
      })
      .addCase(deleteRule.rejected, (state, action) => {
        state.error = action.payload as string;
      });

    // Generate rule
    builder
      .addCase(generateRule.pending, (state) => {
        state.generating = true;
        state.generationError = null;
        state.generatedRule = null;
      })
      .addCase(generateRule.fulfilled, (state, action) => {
        state.generating = false;
        state.generatedRule = action.payload;
      })
      .addCase(generateRule.rejected, (state, action) => {
        state.generating = false;
        state.generationError = action.payload as string;
      });
  },
});

export const {
  setSearchTerm,
  setSelectedRule,
  setGenerationPrompt,
  clearGeneratedRule,
  clearRulesError,
  clearGenerationError,
} = rulesSlice.actions;

export default rulesSlice.reducer;
