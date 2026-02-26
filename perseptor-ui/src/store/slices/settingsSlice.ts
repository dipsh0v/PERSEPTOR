/**
 * PERSEPTOR v2.0 - Settings Slice
 * Manages session token, AI provider, model selection, and theme.
 */

import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { apiClient } from '../../services/api';

// ─── Types ──────────────────────────────────────────────────────────────────

export interface ModelInfo {
  model_id: string;
  display_name: string;
  tier: string;
  max_tokens: number;
  cost_per_1k_input: number;
  cost_per_1k_output: number;
}

export interface ProviderInfo {
  provider: string;
  display_name: string;
  models: ModelInfo[];
  key_prefix: string;
}

export interface TokenUsage {
  total_prompt_tokens: number;
  total_completion_tokens: number;
  total_cost: number;
  request_count: number;
}

export type ThemeMode = 'dark' | 'light';

export interface SettingsState {
  // Session
  sessionToken: string | null;
  sessionId: string | null;
  sessionExpiresAt: string | null;

  // AI Provider
  aiProvider: string;
  selectedModel: string;
  apiKey: string;

  // Available providers & models (fetched from backend)
  availableProviders: ProviderInfo[];
  providersLoading: boolean;
  providersError: string | null;

  // Session management
  sessionLoading: boolean;
  sessionError: string | null;

  // Token usage
  tokenUsage: TokenUsage | null;
  usageLoading: boolean;

  // Theme
  themeMode: ThemeMode;

  // Connection status
  isConnected: boolean;
}

const initialState: SettingsState = {
  sessionToken: null,
  sessionId: null,
  sessionExpiresAt: null,

  aiProvider: 'openai',
  selectedModel: 'gpt-4.1-mini',
  apiKey: '',

  availableProviders: [],
  providersLoading: false,
  providersError: null,

  sessionLoading: false,
  sessionError: null,

  tokenUsage: null,
  usageLoading: false,

  themeMode: 'dark',

  isConnected: false,
};

// ─── Async Thunks ───────────────────────────────────────────────────────────

export const fetchProviders = createAsyncThunk(
  'settings/fetchProviders',
  async (_, { rejectWithValue }) => {
    try {
      const response = await apiClient.get('/api/models');
      return response.data.providers as ProviderInfo[];
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.error || 'Failed to fetch providers');
    }
  }
);

export const createSession = createAsyncThunk(
  'settings/createSession',
  async (
    payload: { apiKey: string; provider: string; model?: string },
    { rejectWithValue }
  ) => {
    try {
      const response = await apiClient.post('/api/session', {
        api_key: payload.apiKey,
        provider: payload.provider,
        model_preference: payload.model,
      });
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.error || 'Failed to create session');
    }
  }
);

export const destroySession = createAsyncThunk(
  'settings/destroySession',
  async (_, { getState, rejectWithValue }) => {
    try {
      const state = getState() as { settings: SettingsState };
      const token = state.settings.sessionToken;
      if (!token) return;
      await apiClient.delete('/api/session', {
        headers: { 'X-Session-Token': token },
      });
      return true;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.error || 'Failed to destroy session');
    }
  }
);

export const fetchTokenUsage = createAsyncThunk(
  'settings/fetchTokenUsage',
  async (_, { getState, rejectWithValue }) => {
    try {
      const state = getState() as { settings: SettingsState };
      const token = state.settings.sessionToken;
      if (!token) return null;
      const response = await apiClient.get('/api/session/usage', {
        headers: { 'X-Session-Token': token },
      });
      return response.data as TokenUsage;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.error || 'Failed to fetch usage');
    }
  }
);

// ─── Slice ──────────────────────────────────────────────────────────────────

const settingsSlice = createSlice({
  name: 'settings',
  initialState,
  reducers: {
    setApiKey(state, action: PayloadAction<string>) {
      state.apiKey = action.payload;
    },
    setProvider(state, action: PayloadAction<string>) {
      state.aiProvider = action.payload;
      // Auto-select first model for this provider
      const provider = state.availableProviders.find(
        (p) => p.provider === action.payload
      );
      if (provider && provider.models.length > 0) {
        state.selectedModel = provider.models[0].model_id;
      }
    },
    setModel(state, action: PayloadAction<string>) {
      state.selectedModel = action.payload;
    },
    setThemeMode(state, action: PayloadAction<ThemeMode>) {
      state.themeMode = action.payload;
    },
    toggleTheme(state) {
      state.themeMode = state.themeMode === 'dark' ? 'light' : 'dark';
    },
    clearSessionError(state) {
      state.sessionError = null;
    },
    // Hydrate from localStorage
    hydrateSettings(state, action: PayloadAction<Partial<SettingsState>>) {
      return { ...state, ...action.payload };
    },
  },
  extraReducers: (builder) => {
    // Fetch providers
    builder
      .addCase(fetchProviders.pending, (state) => {
        state.providersLoading = true;
        state.providersError = null;
      })
      .addCase(fetchProviders.fulfilled, (state, action) => {
        state.providersLoading = false;
        state.availableProviders = action.payload;
      })
      .addCase(fetchProviders.rejected, (state, action) => {
        state.providersLoading = false;
        state.providersError = action.payload as string;
      });

    // Create session
    builder
      .addCase(createSession.pending, (state) => {
        state.sessionLoading = true;
        state.sessionError = null;
      })
      .addCase(createSession.fulfilled, (state, action) => {
        state.sessionLoading = false;
        state.sessionToken = action.payload.session_token;
        state.sessionId = action.payload.session_id;
        state.sessionExpiresAt = action.payload.expires_at;
        state.aiProvider = action.payload.provider;
        if (action.payload.model_preference) {
          state.selectedModel = action.payload.model_preference;
        }
        state.isConnected = true;
      })
      .addCase(createSession.rejected, (state, action) => {
        state.sessionLoading = false;
        state.sessionError = action.payload as string;
        state.isConnected = false;
      });

    // Destroy session
    builder
      .addCase(destroySession.fulfilled, (state) => {
        state.sessionToken = null;
        state.sessionId = null;
        state.sessionExpiresAt = null;
        state.isConnected = false;
        state.apiKey = '';
        state.tokenUsage = null;
      });

    // Fetch token usage
    builder
      .addCase(fetchTokenUsage.pending, (state) => {
        state.usageLoading = true;
      })
      .addCase(fetchTokenUsage.fulfilled, (state, action) => {
        state.usageLoading = false;
        state.tokenUsage = action.payload;
      })
      .addCase(fetchTokenUsage.rejected, (state) => {
        state.usageLoading = false;
      });
  },
});

export const {
  setApiKey,
  setProvider,
  setModel,
  setThemeMode,
  toggleTheme,
  clearSessionError,
  hydrateSettings,
} = settingsSlice.actions;

export default settingsSlice.reducer;
