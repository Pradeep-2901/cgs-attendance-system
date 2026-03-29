import { useState } from 'react';
import { apiCall } from '../services/api';
import styles from './LoginPage.module.css';

function LoginPage({ onLogin }) {
  const [isAdmin, setIsAdmin] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await apiCall('/login', 'POST', {
        username,
        password,
        role: isAdmin ? 'admin' : 'employee'
      });

      if (response.authenticated) {
        onLogin({
          user_id: response.user_id,
          username: response.username,
          name: response.name,
          role: response.role
        });
      } else {
        setError(response.message || 'Login failed');
      }
    } catch (err) {
      setError(err.message || 'Connection error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  const toggleRole = () => {
    setIsAdmin(!isAdmin);
    setUsername('');
    setPassword('');
    setError('');
  };

  return (
    <div className={styles.pageContainer}>
      <div className={styles.container}>
        {/* Employee Form */}
        <div className={`${styles.formWrapper} ${isAdmin ? styles.hidden : ''}`}>
          <form className={styles.form} onSubmit={handleSubmit}>
            <h2>Employee</h2>
            {error && <div className={styles.errorMessage}>{error}</div>}
            <input
              type="text"
              placeholder="User name"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              disabled={loading}
            />
            <div className={styles.passwordWrapper}>
              <input
                type={showPassword ? 'text' : 'password'}
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                disabled={loading}
              />
              <button
                type="button"
                className={styles.toggleEye}
                onClick={togglePasswordVisibility}
                disabled={loading}
              >
                {showPassword ? '🙈' : '👁️'}
              </button>
            </div>
            <button type="submit" disabled={loading}>
              {loading ? 'Logging in...' : 'Login'}
            </button>
          </form>
        </div>

        {/* Admin Form */}
        <div className={`${styles.formWrapper} ${!isAdmin ? styles.hidden : ''}`}>
          <form className={styles.form} onSubmit={handleSubmit}>
            <h2>Admin</h2>
            {error && <div className={styles.errorMessage}>{error}</div>}
            <input
              type="text"
              placeholder="User name"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              disabled={loading}
            />
            <div className={styles.passwordWrapper}>
              <input
                type={showPassword ? 'text' : 'password'}
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                disabled={loading}
              />
              <button
                type="button"
                className={styles.toggleEye}
                onClick={togglePasswordVisibility}
                disabled={loading}
              >
                {showPassword ? '🙈' : '👁️'}
              </button>
            </div>
            <button type="submit" disabled={loading}>
              {loading ? 'Logging in...' : 'Login'}
            </button>
          </form>
        </div>

        {/* Admin Toggle Button */}
        <button
          type="button"
          className={styles.adminTab}
          onClick={toggleRole}
          disabled={loading}
        >
          {isAdmin ? 'Employee' : 'Admin'}
        </button>
      </div>
    </div>
  );
}

export default LoginPage;
