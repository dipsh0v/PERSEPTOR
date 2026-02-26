/**
 * PERSEPTOR v2.0 - Reports Slice
 * Manages analysis reports state and async operations.
 */

import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { apiClient } from '../../services/api';
import type { AnalysisResult } from '../../services/api';

// ─── Types ──────────────────────────────────────────────────────────────────

export type ReportEntry = AnalysisResult & {
  id: string;
  url: string;
  timestamp: string;
};

export interface ReportsState {
  reports: ReportEntry[];
  loading: boolean;
  error: string | null;
  lastFetched: number | null;
}

const initialState: ReportsState = {
  reports: [],
  loading: false,
  error: null,
  lastFetched: null,
};

// ─── Async Thunks ───────────────────────────────────────────────────────────

export const fetchReports = createAsyncThunk(
  'reports/fetchReports',
  async (_, { getState, rejectWithValue }) => {
    try {
      const response = await apiClient.get('/api/reports');
      const reports = (response.data.reports || []).map((report: any) => ({
        ...report,
        yara_rules: Array.isArray(report.yara_rules) ? report.yara_rules : [],
      }));
      return reports as ReportEntry[];
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.error || 'Failed to fetch reports');
    }
  }
);

export const deleteReport = createAsyncThunk(
  'reports/deleteReport',
  async (reportId: string, { rejectWithValue }) => {
    try {
      await apiClient.delete(`/api/reports/${reportId}`);
      return reportId;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.error || 'Failed to delete report');
    }
  }
);

// ─── Slice ──────────────────────────────────────────────────────────────────

const reportsSlice = createSlice({
  name: 'reports',
  initialState,
  reducers: {
    clearReportsError(state) {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    // Fetch reports
    builder
      .addCase(fetchReports.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchReports.fulfilled, (state, action) => {
        state.loading = false;
        state.reports = action.payload;
        state.lastFetched = Date.now();
      })
      .addCase(fetchReports.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // Delete report
    builder
      .addCase(deleteReport.fulfilled, (state, action) => {
        state.reports = state.reports.filter((r) => r.id !== action.payload);
      })
      .addCase(deleteReport.rejected, (state, action) => {
        state.error = action.payload as string;
      });
  },
});

export const { clearReportsError } = reportsSlice.actions;
export default reportsSlice.reducer;
