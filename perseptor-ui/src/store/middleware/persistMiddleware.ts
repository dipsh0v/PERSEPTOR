/**
 * PERSEPTOR v2.0 - Persist Middleware
 * Saves selected settings to localStorage for session persistence.
 */

import { Middleware } from '@reduxjs/toolkit';

const STORAGE_KEY = 'perseptor_settings';

// Keys from settings state that should be persisted
const PERSISTED_KEYS = [
  'sessionToken',
  'sessionId',
  'sessionExpiresAt',
  'aiProvider',
  'selectedModel',
  'themeMode',
  'isConnected',
] as const;

/**
 * Load persisted settings from localStorage.
 * Called once at app startup.
 */
export function loadPersistedSettings(): Record<string, any> | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;

    const parsed = JSON.parse(raw);

    // Check session expiry
    if (parsed.sessionExpiresAt) {
      const expiresAt = new Date(parsed.sessionExpiresAt);
      if (expiresAt <= new Date()) {
        // Session expired, clear it
        localStorage.removeItem(STORAGE_KEY);
        return {
          themeMode: parsed.themeMode || 'dark',
          aiProvider: parsed.aiProvider || 'openai',
          selectedModel: parsed.selectedModel || 'gpt-4.1-mini',
        };
      }
    }

    return parsed;
  } catch {
    return null;
  }
}

/**
 * Redux middleware that persists settings state changes to localStorage.
 */
export const persistMiddleware: Middleware = (store) => (next) => (action) => {
  const result = next(action);

  // Only persist on settings-related actions
  const actionType = (action as any)?.type;
  if (typeof actionType === 'string' && actionType.startsWith('settings/')) {
    try {
      const state = store.getState().settings;
      const toPersist: Record<string, any> = {};
      for (const key of PERSISTED_KEYS) {
        toPersist[key] = state[key];
      }
      localStorage.setItem(STORAGE_KEY, JSON.stringify(toPersist));
    } catch {
      // localStorage might be full or unavailable
    }
  }

  return result;
};
