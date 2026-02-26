/**
 * PERSEPTOR v2.0 - Redux Store Configuration
 * Centralized store with all slices, persist middleware, and typed hooks.
 */

import { configureStore } from '@reduxjs/toolkit';
import { TypedUseSelectorHook, useDispatch, useSelector } from 'react-redux';
import settingsReducer from './slices/settingsSlice';
import analysisReducer from './slices/analysisSlice';
import rulesReducer from './slices/rulesSlice';
import reportsReducer from './slices/reportsSlice';
import { persistMiddleware } from './middleware/persistMiddleware';

export const store = configureStore({
  reducer: {
    settings: settingsReducer,
    analysis: analysisReducer,
    rules: rulesReducer,
    reports: reportsReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        // Ignore non-serializable values in certain paths
        ignoredPaths: ['analysis.result.raw_response'],
      },
    }).concat(persistMiddleware),
  devTools: process.env.NODE_ENV !== 'production',
});

// ─── Typed Hooks ────────────────────────────────────────────────────────────

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

export const useAppDispatch: () => AppDispatch = useDispatch;
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;
