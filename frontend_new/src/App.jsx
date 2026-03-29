import { useState, useEffect } from 'react';
import AuthContext from './context/AuthContext';
import { apiCall } from './services/api';

import LoginPage from './pages/LoginPage';
import EmployeeDashboard from './pages/EmployeeDashboard';
import AdminDashboard from './pages/AdminDashboard';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState('login');

  useEffect(() => {
    // Check if user is already logged in
    const storedUser = localStorage.getItem('currentUser');
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
        setCurrentPage(JSON.parse(storedUser).role === 'admin' ? 'admin-dashboard' : 'employee-dashboard');
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
    setCurrentPage(userData.role === 'admin' ? 'admin-dashboard' : 'employee-dashboard');
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
      setCurrentPage('login');
    }
  };

  if (loading) {
    return <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh' }}>Loading...</div>;
  }

  return (
    <AuthContext.Provider value={{ user, setUser, handleLogout }}>
      {currentPage === 'login' && <LoginPage onLogin={handleLogin} />}
      {currentPage === 'employee-dashboard' && (
        <EmployeeDashboard user={user} onLogout={handleLogout} setPage={setCurrentPage} />
      )}
      {currentPage === 'admin-dashboard' && (
        <AdminDashboard user={user} onLogout={handleLogout} setPage={setCurrentPage} />
      )}
    </AuthContext.Provider>
  );
}

export default App;
