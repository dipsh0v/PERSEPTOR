/**
 * PERSEPTOR v2.0 - Analysis Slice
 * Manages threat analysis state with SSE streaming support.
 * Supports both URL analysis and local PDF file upload.
 */

import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import type { AnalysisResult } from '../../services/api';
import type { RootState } from '../index';
import type { SSEEvent } from '../../components/AnalysisProgressOverlay';

// ─── Types ──────────────────────────────────────────────────────────────────

export type InputMode = 'url' | 'pdf';

export interface AnalysisState {
  url: string;
  inputMode: InputMode;
  pdfFileName: string | null;
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
  inputMode: 'url',
  pdfFileName: null,
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

// ─── SSE Stream Reader (shared) ─────────────────────────────────────────────

async function readSSEStream(
  response: Response,
  dispatch: any,
  signal: AbortSignal,
): Promise<AnalysisResult> {
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

    const lines = buffer.split('\n');
    buffer = lines.pop() || '';

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
            throw parseErr;
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
}

// ─── Helper: get session headers ────────────────────────────────────────────

function getSessionHeaders(state: RootState): Record<string, string> {
  const headers: Record<string, string> = {};
  const { sessionToken } = state.settings;

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

  return headers;
}

// ─── SSE Streaming Thunks ───────────────────────────────────────────────────

let abortController: AbortController | null = null;

export const analyzeUrlStream = createAsyncThunk(
  'analysis/analyzeUrlStream',
  async (url: string, { getState, dispatch, rejectWithValue }) => {
    if (abortController) {
      abortController.abort();
    }
    abortController = new AbortController();

    try {
      const state = getState() as RootState;
      const { aiProvider, selectedModel, apiKey, sessionToken } = state.settings;

      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        ...getSessionHeaders(state),
      };

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

      return await readSSEStream(response, dispatch, abortController.signal);
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

export const analyzePdfStream = createAsyncThunk(
  'analysis/analyzePdfStream',
  async (file: File, { getState, dispatch, rejectWithValue }) => {
    if (abortController) {
      abortController.abort();
    }
    abortController = new AbortController();

    try {
      const state = getState() as RootState;
      const { aiProvider, selectedModel, apiKey, sessionToken } = state.settings;

      const headers: Record<string, string> = {
        ...getSessionHeaders(state),
        // Do NOT set Content-Type — browser sets multipart/form-data with boundary
      };

      const formData = new FormData();
      formData.append('pdf', file);
      formData.append('provider', aiProvider);
      formData.append('model', selectedModel);
      if (!sessionToken && apiKey) {
        formData.append('openai_api_key', apiKey);
      }

      dispatch(sseStreamStarted());

      const response = await fetch('/api/analyze/pdf/stream', {
        method: 'POST',
        headers,
        body: formData,
        signal: abortController.signal,
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({ error: 'PDF upload failed' }));
        throw new Error(errData.error || `HTTP ${response.status}`);
      }

      return await readSSEStream(response, dispatch, abortController.signal);
    } catch (error: any) {
      if (error.name === 'AbortError') {
        return rejectWithValue('Analysis cancelled');
      }
      const message = error.message || 'PDF analysis failed';
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
    setInputMode(state, action: PayloadAction<InputMode>) {
      state.inputMode = action.payload;
    },
    setPdfFileName(state, action: PayloadAction<string | null>) {
      state.pdfFileName = action.payload;
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
    // ── URL SSE Streaming ──
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

    // ── PDF SSE Streaming ──
    builder
      .addCase(analyzePdfStream.pending, (state) => {
        state.loading = true;
        state.error = null;
        state.result = null;
      })
      .addCase(analyzePdfStream.fulfilled, (state, action) => {
        state.loading = false;
        state.streaming = false;
        state.result = action.payload;
        state.sseProgress = 100;
        state.sseCurrentStage = 'complete';
        state.history.unshift({
          id: Date.now().toString(),
          url: `pdf://${state.pdfFileName || 'upload'}`,
          timestamp: new Date().toISOString(),
          summary: action.payload.threat_summary?.substring(0, 120) || '',
        });
        if (state.history.length > 50) {
          state.history = state.history.slice(0, 50);
        }
      })
      .addCase(analyzePdfStream.rejected, (state, action) => {
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
  setInputMode,
  setPdfFileName,
  clearAnalysis,
  clearError,
  sseStreamStarted,
  sseEventReceived,
} = analysisSlice.actions;

export default analysisSlice.reducer;
