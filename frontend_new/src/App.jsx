import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import AuthContext from './context/AuthContext';
import { apiCall } from './services/api';

import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import RecordsPage from './pages/RecordsPage';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
    const storedUser = localStorage.getItem('currentUser');
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch (e) {
        console.error('Invalid stored user:', e);
        localStorage.removeItem('currentUser');
      }
    }
    setLoading(false);
  }, []);

  const handleLogin = (userData) => {
    localStorage.setItem('currentUser', JSON.stringify(userData));
    setUser(userData);
  };

  const handleLogout = async () => {
    try {
      await apiCall('/logout', 'GET');
    } catch (e) {
      console.error('Logout error:', e);
    } finally {
      localStorage.removeItem('currentUser');
      localStorage.removeItem('API_URL');
      setUser(null);
    }
  };

  if (loading) {
    return <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh' }}>Loading...</div>;
  }

  return (
    <BrowserRouter>
      <AuthContext.Provider value={{ user, setUser, handleLogout }}>
        <Routes>
          {/* Login Page - No navbar */}
          <Route path="/" element={user ? <Navigate to="/dashboard" /> : <LoginPage onLogin={handleLogin} />} />
          
          {/* Protected Pages - With Navbar */}
          <Route path="/dashboard" element={user ? <DashboardPage user={user} onLogout={handleLogout} /> : <Navigate to="/" />} />
          <Route path="/records" element={user ? <RecordsPage user={user} onLogout={handleLogout} /> : <Navigate to="/" />} />
          
          {/* Catch all - redirect to home */}
          <Route path="*" element={<Navigate to={user ? "/dashboard" : "/"} />} />
        </Routes>
      </AuthContext.Provider>
    </BrowserRouter>
  );
}

export default App;
