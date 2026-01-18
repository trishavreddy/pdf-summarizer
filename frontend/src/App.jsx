import { useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import useAuthStore from './services/authStore';
import Layout from './components/Layout';
import Login from './pages/Login';
import Register from './pages/Register';
import Upload from './pages/Upload';
import Dashboard from './pages/Dashboard';
import SummaryDetail from './pages/SummaryDetail';

function ProtectedRoute({ children }) {
  const { token, user, isLoading } = useAuthStore();

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return children;
}

function App() {
  const { token, fetchUser } = useAuthStore();

  useEffect(() => {
    if (token) {
      fetchUser();
    }
  }, [token, fetchUser]);

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/upload" replace />} />
        <Route path="upload" element={<Upload />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="summary/:id" element={<SummaryDetail />} />
      </Route>
    </Routes>
  );
}

export default App;
