import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { Provider } from 'react-redux';
import { store, useAppSelector, useAppDispatch } from './store';
import { hydrateSettings } from './store/slices/settingsSlice';
import { loadPersistedSettings } from './store/middleware/persistMiddleware';
import { getTheme } from './theme';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Reports from './pages/Reports';
import QA from './pages/QA';
import CreatedRules from './pages/CreatedRules';
import AboutPerseptor from './pages/AboutPerseptor';
import Settings from './pages/Settings';

/**
 * Inner app component that has access to Redux store.
 * Handles theme switching based on settings state.
 */
const AppContent: React.FC = () => {
  const dispatch = useAppDispatch();
  const themeMode = useAppSelector((state) => state.settings.themeMode);
  const currentTheme = getTheme(themeMode);

  // Hydrate settings from localStorage on mount
  useEffect(() => {
    const persisted = loadPersistedSettings();
    if (persisted) {
      dispatch(hydrateSettings(persisted));
    }
  }, [dispatch]);

  return (
    <ThemeProvider theme={currentTheme}>
      <CssBaseline />
      <Router>
        <Layout>
          <Routes>
            <Route path="/about" element={<AboutPerseptor />} />
            <Route path="/" element={<Dashboard />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/qa" element={<QA />} />
            <Route path="/rules" element={<CreatedRules />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </Layout>
      </Router>
    </ThemeProvider>
  );
};

function App() {
  return (
    <Provider store={store}>
      <AppContent />
    </Provider>
  );
}

export default App;
