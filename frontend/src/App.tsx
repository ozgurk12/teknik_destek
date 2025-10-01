import React, { Suspense, lazy } from 'react';
import { HashRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import CssBaseline from '@mui/material/CssBaseline';
import { LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { tr } from 'date-fns/locale';
import { CircularProgress, Box } from '@mui/material';

// Auth
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import ErrorBoundary from './components/ErrorBoundary';

// Eagerly loaded components
import Login from './pages/Login';
import Layout from './components/Layout';

// Lazy loaded pages for code splitting
const Dashboard = lazy(() => import('./pages/Dashboard'));
const ActivityGenerator = lazy(() => import('./pages/ActivityGenerator'));
const ActivityList = lazy(() => import('./pages/ActivityList'));
const ActivityDetail = lazy(() => import('./pages/ActivityDetail'));
const KazanimList = lazy(() => import('./pages/KazanimList'));
const Statistics = lazy(() => import('./pages/Statistics'));
const DailyPlanList = lazy(() => import('./pages/DailyPlanList'));
const DailyPlanCreate = lazy(() => import('./pages/DailyPlanCreate'));
const DailyPlanDetail = lazy(() => import('./pages/DailyPlanDetail'));
const MonthlyPlanGenerator = lazy(() => import('./pages/MonthlyPlanGenerator'));
const MonthlyPlanList = lazy(() => import('./pages/MonthlyPlanList'));
const UserManagement = lazy(() => import('./pages/UserManagement'));
const Settings = lazy(() => import('./pages/Settings'));
const VideoGeneration = lazy(() => import('./pages/VideoGeneration'));
const VideoGenerationList = lazy(() => import('./pages/VideoGenerationList'));
const VideoScriptGenerator = lazy(() => import('./pages/VideoScriptGenerator'));
const VideoScriptList = lazy(() => import('./pages/VideoScriptList'));

// Loading component
const PageLoader = () => (
  <Box
    sx={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '60vh',
    }}
  >
    <CircularProgress />
  </Box>
);

// Create theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
      light: '#42a5f5',
      dark: '#1565c0',
    },
    secondary: {
      main: '#9c27b0',
      light: '#ba68c8',
      dark: '#7b1fa2',
    },
    success: {
      main: '#4caf50',
    },
    error: {
      main: '#f44336',
    },
    warning: {
      main: '#ff9800',
    },
    background: {
      default: '#f5f5f5',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 600,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 500,
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 500,
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 500,
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 500,
    },
    h6: {
      fontSize: '1rem',
      fontWeight: 500,
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
          padding: '8px 16px',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 12,
        },
      },
    },
  },
});

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={tr}>
          <CssBaseline />
          <Router>
            <AuthProvider>
              <Routes>
                {/* Public routes */}
                <Route path="/login" element={<Login />} />

                {/* Protected routes */}
                <Route path="/" element={
                  <ProtectedRoute>
                    <Layout />
                  </ProtectedRoute>
                }>
                  <Route index element={<Navigate to="/dashboard" replace />} />
                  <Route path="dashboard" element={
                    <Suspense fallback={<PageLoader />}>
                      <Dashboard />
                    </Suspense>
                  } />

                  {/* Activity Module */}
                  <Route path="activity-generator" element={
                    <ProtectedRoute requiredModule="etkinlik_olusturma">
                      <Suspense fallback={<PageLoader />}>
                        <ActivityGenerator />
                      </Suspense>
                    </ProtectedRoute>
                  } />
                  <Route path="activities" element={
                    <ProtectedRoute requiredModule="etkinlik_olusturma">
                      <Suspense fallback={<PageLoader />}>
                        <ActivityList />
                      </Suspense>
                    </ProtectedRoute>
                  } />
                  <Route path="activities/:id" element={
                    <ProtectedRoute requiredModule="etkinlik_olusturma">
                      <Suspense fallback={<PageLoader />}>
                        <ActivityDetail />
                      </Suspense>
                    </ProtectedRoute>
                  } />

                  {/* Kazanim Module */}
                  <Route path="kazanimlar" element={
                    <ProtectedRoute requiredModule="kazanim_yonetimi">
                      <Suspense fallback={<PageLoader />}>
                        <KazanimList />
                      </Suspense>
                    </ProtectedRoute>
                  } />

                  {/* Daily Plan Module */}
                  <Route path="daily-plans" element={
                    <ProtectedRoute requiredModule="gunluk_plan">
                      <Suspense fallback={<PageLoader />}>
                        <DailyPlanList />
                      </Suspense>
                    </ProtectedRoute>
                  } />
                  <Route path="daily-plans/new" element={
                    <ProtectedRoute requiredModule="gunluk_plan">
                      <Suspense fallback={<PageLoader />}>
                        <DailyPlanCreate />
                      </Suspense>
                    </ProtectedRoute>
                  } />
                  <Route path="daily-plans/:id" element={
                    <ProtectedRoute requiredModule="gunluk_plan">
                      <Suspense fallback={<PageLoader />}>
                        <DailyPlanDetail />
                      </Suspense>
                    </ProtectedRoute>
                  } />
                  <Route path="daily-plans/:id/edit" element={
                    <ProtectedRoute requiredModule="gunluk_plan">
                      <Suspense fallback={<PageLoader />}>
                        <DailyPlanCreate />
                      </Suspense>
                    </ProtectedRoute>
                  } />

                  {/* Monthly Plan Module */}
                  <Route path="monthly-plan-generator" element={
                    <ProtectedRoute requiredModule="aylik_plan">
                      <Suspense fallback={<PageLoader />}>
                        <MonthlyPlanGenerator />
                      </Suspense>
                    </ProtectedRoute>
                  } />
                  <Route path="monthly-plans" element={
                    <ProtectedRoute requiredModule="aylik_plan">
                      <Suspense fallback={<PageLoader />}>
                        <MonthlyPlanList />
                      </Suspense>
                    </ProtectedRoute>
                  } />

                  {/* Statistics Module */}
                  <Route path="statistics" element={
                    <ProtectedRoute requiredModule="raporlama">
                      <Suspense fallback={<PageLoader />}>
                        <Statistics />
                      </Suspense>
                    </ProtectedRoute>
                  } />

                  {/* User Management */}
                  <Route path="users" element={
                    <ProtectedRoute requiredRoles={['admin', 'yonetici']}>
                      <Suspense fallback={<PageLoader />}>
                        <UserManagement />
                      </Suspense>
                    </ProtectedRoute>
                  } />

                  {/* Settings */}
                  <Route path="settings" element={
                    <ProtectedRoute>
                      <ErrorBoundary>
                        <Suspense fallback={<PageLoader />}>
                          <Settings />
                        </Suspense>
                      </ErrorBoundary>
                    </ProtectedRoute>
                  } />

                  {/* Video Generation */}
                  <Route path="video-generation" element={
                    <ProtectedRoute requiredModule="video_generation">
                      <ErrorBoundary>
                        <Suspense fallback={<PageLoader />}>
                          <VideoGeneration />
                        </Suspense>
                      </ErrorBoundary>
                    </ProtectedRoute>
                  } />

                  {/* Video Script Generation */}
                  <Route path="video-script-generator" element={
                    <ProtectedRoute requiredModule="video_generation">
                      <ErrorBoundary>
                        <Suspense fallback={<PageLoader />}>
                          <VideoScriptGenerator />
                        </Suspense>
                      </ErrorBoundary>
                    </ProtectedRoute>
                  } />
                  <Route path="video-scripts" element={
                    <ProtectedRoute requiredModule="video_generation">
                      <ErrorBoundary>
                        <Suspense fallback={<PageLoader />}>
                          <VideoScriptList />
                        </Suspense>
                      </ErrorBoundary>
                    </ProtectedRoute>
                  } />
                </Route>

                {/* Public Video List - Outside of Layout */}
                <Route path="/video-list" element={
                  <ErrorBoundary>
                    <Suspense fallback={<PageLoader />}>
                      <VideoGenerationList />
                    </Suspense>
                  </ErrorBoundary>
                } />

                {/* Unauthorized */}
                <Route path="/unauthorized" element={
                  <div style={{ padding: '2rem', textAlign: 'center' }}>
                    <h2>Yetkisiz Erişim</h2>
                    <p>Bu sayfaya erişim yetkiniz bulunmamaktadır.</p>
                  </div>
                } />
              </Routes>
            </AuthProvider>
          </Router>
        </LocalizationProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;