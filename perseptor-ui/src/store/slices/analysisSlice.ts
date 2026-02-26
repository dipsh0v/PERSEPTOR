/**
 * PERSEPTOR v2.0 - Analysis Slice
 * Manages threat analysis state with SSE streaming support.
 * Uses EventSource for real-time progress from /api/analyze/stream.
 */

import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import type { AnalysisResult } from '../../services/api';
import type { RootState } from '../index';
import type { SSEEvent } from '../../components/AnalysisProgressOverlay';

// ─── Types ──────────────────────────────────────────────────────────────────

export interface AnalysisState {
  url: string;
  loading: boolean;
  error: string | null;
  result: AnalysisResult | null;
  // SSE streaming state
  streaming: boolean;
  sseEvents: SSEEvent[];
  sseProgress: number;
  sseCurrentStage: string;
  sseStartTime: number | null;
  // History
  history: Array<{
    id: string;
    url: string;
    timestamp: string;
    summary: string;
  }>;
}

const initialState: AnalysisState = {
  url: '',
  loading: false,
  error: null,
  result: null,
  streaming: false,
  sseEvents: [],
  sseProgress: 0,
  sseCurrentStage: '',
  sseStartTime: null,
  history: [],
};

// ─── SSE Streaming Thunk ────────────────────────────────────────────────────

// We use a custom thunk that opens an EventSource-like connection via fetch
// (since EventSource doesn't support POST). This reads the SSE stream
// and dispatches stage updates in real-time.

let abortController: AbortController | null = null;

export const analyzeUrlStream = createAsyncThunk(
  'analysis/analyzeUrlStream',
  async (url: string, { getState, dispatch, rejectWithValue }) => {
    // Abort any previous stream
    if (abortController) {
      abortController.abort();
    }
    abortController = new AbortController();

    try {
      const state = getState() as RootState;
      const { sessionToken, aiProvider, selectedModel, apiKey } = state.settings;

      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };
      if (sessionToken) {
        headers['X-Session-Token'] = sessionToken;
      }

      // Also inject from localStorage as fallback
      try {
        const stored = localStorage.getItem('perseptor_settings');
        if (stored) {
          const parsed = JSON.parse(stored);
          if (parsed.sessionToken && !headers['X-Session-Token']) {
            headers['X-Session-Token'] = parsed.sessionToken;
          }
        }
      } catch {}

      const body: Record<string, any> = { url };
      if (!sessionToken && apiKey) {
        body.openai_api_key = apiKey;
      }
      body.provider = aiProvider;
      body.model = selectedModel;

      dispatch(sseStreamStarted());

      const response = await fetch('/api/analyze/stream', {
        method: 'POST',
        headers,
        body: JSON.stringify(body),
        signal: abortController.signal,
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({ error: 'Stream connection failed' }));
        throw new Error(errData.error || `HTTP ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('ReadableStream not supported');
      }

      const decoder = new TextDecoder();
      let buffer = '';
      let finalResult: AnalysisResult | null = null;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        // Parse SSE events from buffer
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // Keep incomplete line in buffer

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const eventData: SSEEvent = JSON.parse(line.slice(6));

              dispatch(sseEventReceived(eventData));

              if (eventData.stage === 'complete' && eventData.data) {
                finalResult = eventData.data as AnalysisResult;
              }

              if (eventData.stage === 'error') {
                throw new Error(eventData.message);
              }
            } catch (parseErr: any) {
              if (parseErr.message && !parseErr.message.includes('JSON')) {
                throw parseErr; // Re-throw non-parse errors
              }
              console.warn('SSE parse warning:', parseErr);
            }
          }
        }
      }

      if (finalResult) {
        return finalResult;
      }

      throw new Error('Stream ended without complete result');
    } catch (error: any) {
      if (error.name === 'AbortError') {
        return rejectWithValue('Analysis cancelled');
      }
      const message = error.message || 'Analysis failed';
      return rejectWithValue(message);
    } finally {
      abortController = null;
    }
  }
);

// Also keep the old non-streaming thunk as fallback
export const analyzeUrl = createAsyncThunk(
  'analysis/analyzeUrl',
  async (url: string, { getState, rejectWithValue }) => {
    try {
      const { apiClient } = await import('../../services/api');
      const state = getState() as RootState;
      const { sessionToken, aiProvider, selectedModel, apiKey } = state.settings;

      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };
      if (sessionToken) {
        headers['X-Session-Token'] = sessionToken;
      }

      const body: Record<string, any> = { url };
      if (!sessionToken && apiKey) {
        body.openai_api_key = apiKey;
      }
      body.provider = aiProvider;
      body.model = selectedModel;

      const response = await apiClient.post('/api/analyze', body, { headers });
      return response.data as AnalysisResult;
    } catch (error: any) {
      const message =
        error.response?.data?.error || error.message || 'Analysis failed';
      return rejectWithValue(message);
    }
  }
);

export const cancelAnalysis = () => {
  if (abortController) {
    abortController.abort();
    abortController = null;
  }
};

// ─── Slice ──────────────────────────────────────────────────────────────────

const analysisSlice = createSlice({
  name: 'analysis',
  initialState,
  reducers: {
    setUrl(state, action: PayloadAction<string>) {
      state.url = action.payload;
    },
    clearAnalysis(state) {
      state.result = null;
      state.error = null;
      state.sseEvents = [];
      state.sseProgress = 0;
      state.sseCurrentStage = '';
      state.sseStartTime = null;
    },
    clearError(state) {
      state.error = null;
    },
    sseStreamStarted(state) {
      state.streaming = true;
      state.loading = true;
      state.error = null;
      state.result = null;
      state.sseEvents = [];
      state.sseProgress = 0;
      state.sseCurrentStage = '';
      state.sseStartTime = Date.now();
    },
    sseEventReceived(state, action: PayloadAction<SSEEvent>) {
      const event = action.payload;
      state.sseEvents.push(event);
      state.sseProgress = event.progress;
      state.sseCurrentStage = event.stage;
    },
  },
  extraReducers: (builder) => {
    // ── SSE Streaming ──
    builder
      .addCase(analyzeUrlStream.pending, (state) => {
        state.loading = true;
        state.error = null;
        state.result = null;
      })
      .addCase(analyzeUrlStream.fulfilled, (state, action) => {
        state.loading = false;
        state.streaming = false;
        state.result = action.payload;
        state.sseProgress = 100;
        state.sseCurrentStage = 'complete';
        // Add to history
        state.history.unshift({
          id: Date.now().toString(),
          url: state.url,
          timestamp: new Date().toISOString(),
          summary: action.payload.threat_summary?.substring(0, 120) || '',
        });
        if (state.history.length > 50) {
          state.history = state.history.slice(0, 50);
        }
      })
      .addCase(analyzeUrlStream.rejected, (state, action) => {
        state.loading = false;
        state.streaming = false;
        state.error = action.payload as string;
        state.sseCurrentStage = 'error';
      });

    // ── Legacy (non-streaming) ──
    builder
      .addCase(analyzeUrl.pending, (state) => {
        state.loading = true;
        state.error = null;
        state.result = null;
      })
      .addCase(analyzeUrl.fulfilled, (state, action) => {
        state.loading = false;
        state.result = action.payload;
        state.history.unshift({
          id: Date.now().toString(),
          url: state.url,
          timestamp: new Date().toISOString(),
          summary: action.payload.threat_summary?.substring(0, 120) || '',
        });
        if (state.history.length > 50) {
          state.history = state.history.slice(0, 50);
        }
      })
      .addCase(analyzeUrl.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const {
  setUrl,
  clearAnalysis,
  clearError,
  sseStreamStarted,
  sseEventReceived,
} = analysisSlice.actions;

export default analysisSlice.reducer;
