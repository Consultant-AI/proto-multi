import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { InstanceProvider } from './contexts/InstanceContext';
import { ThemeProvider, useTheme } from './contexts/ThemeContext';
import LandingPage from './components/Landing/LandingPage';
import ApiKeySetup from './components/Auth/ApiKeySetup';
import InstanceList from './components/Dashboard/InstanceList';
import CreateInstance from './components/Dashboard/CreateInstance';
import SplitView from './components/Desktop/SplitView';

// Theme toggle icons
const SunIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
  </svg>
);

const MoonIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
  </svg>
);

// Theme toggle button component
const ThemeToggle: React.FC = () => {
  const { theme, toggleTheme } = useTheme();
  return (
    <button
      type="button"
      onClick={toggleTheme}
      className="p-2 rounded-lg bg-theme-tertiary hover:bg-theme-hover text-theme-secondary hover:text-theme-primary transition-colors"
      title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
      aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
    >
      {theme === 'dark' ? <SunIcon className="w-5 h-5" /> : <MoonIcon className="w-5 h-5" />}
    </button>
  );
};

// Protected route wrapper
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-theme-primary">
        <div className="text-theme-primary text-xl">Loading...</div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};

// Home route wrapper
const HomeRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-theme-primary">
        <div className="text-theme-primary text-xl">Loading...</div>
      </div>
    );
  }

  return <>{children}</>;
};

// Dashboard layout with navigation
const DashboardLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-theme-primary">
      <nav className="bg-theme-nav border-b border-theme">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1
                className="text-xl font-bold text-theme-primary cursor-pointer"
                onClick={() => navigate('/')}
              >
                CloudBot Platform
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <ThemeToggle />
              <span className="text-theme-secondary">{user?.email}</span>
              <button
                type="button"
                onClick={handleLogout}
                className="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-md transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  );
};

// App routes
const AppRoutes: React.FC = () => {
  return (
    <Routes>
      {/* Home/Landing Page */}
      <Route
        path="/"
        element={
          <HomeRoute>
            <LandingPage />
          </HomeRoute>
        }
      />

      {/* Protected routes */}
      <Route
        path="/setup-api-keys"
        element={
          <ProtectedRoute>
            <ApiKeySetup />
          </ProtectedRoute>
        }
      />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <DashboardLayout>
              <InstanceList />
            </DashboardLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/create-instance"
        element={
          <ProtectedRoute>
            <DashboardLayout>
              <CreateInstance />
            </DashboardLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/instances/:instanceId"
        element={
          <ProtectedRoute>
            <SplitView />
          </ProtectedRoute>
        }
      />
      <Route
        path="/instances"
        element={
          <ProtectedRoute>
            <SplitView />
          </ProtectedRoute>
        }
      />

      {/* Redirect old routes */}
      <Route path="/login" element={<Navigate to="/" replace />} />
      <Route path="/signup" element={<Navigate to="/" replace />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

// Main App component
const App: React.FC = () => {
  return (
    <Router>
      <ThemeProvider>
        <AuthProvider>
          <InstanceProvider>
            <AppRoutes />
          </InstanceProvider>
        </AuthProvider>
      </ThemeProvider>
    </Router>
  );
};

export default App;
