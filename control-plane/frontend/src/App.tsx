import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { InstanceProvider } from './contexts/InstanceContext';
import LandingPage from './components/Landing/LandingPage';
import ApiKeySetup from './components/Auth/ApiKeySetup';
import InstanceList from './components/Dashboard/InstanceList';
import CreateInstance from './components/Dashboard/CreateInstance';
import SplitView from './components/Desktop/SplitView';

// Protected route wrapper
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-900">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};

// Home route wrapper (show landing page, but user can be logged in or out)
const HomeRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-900">
        <div className="text-white text-xl">Loading...</div>
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
    <div className="min-h-screen bg-gray-900">
      <nav className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-white cursor-pointer" onClick={() => navigate('/')}>
                CloudBot Platform
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-gray-300">{user?.email}</span>
              <button
                onClick={handleLogout}
                className="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-md"
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
      <AuthProvider>
        <InstanceProvider>
          <AppRoutes />
        </InstanceProvider>
      </AuthProvider>
    </Router>
  );
};

export default App;
