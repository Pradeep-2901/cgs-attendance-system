import { useState } from 'react';
import { apiCall } from '../services/api';
import styles from './LoginPage.module.css';

function LoginPage({ onLogin }) {
  const [role, setRole] = useState('employee');
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
        role
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

  return (
    <div className={styles.container}>
      <div className={styles.wrapper}>
        {/* Left Panel - Design */}
        <div className={styles.leftPanel}>
          <div className={styles.content}>
            <div className={styles.logo}>📍</div>
            <h1>CGS Attendance</h1>
            <p>Employee Management System</p>
            <div className={styles.features}>
              <div className={styles.feature}>✓ Real-time Attendance</div>
              <div className={styles.feature}>✓ Location Tracking</div>
              <div className={styles.feature}>✓ Leave Management</div>
              <div className={styles.feature}>✓ Admin Dashboard</div>
            </div>
          </div>
        </div>

        {/* Right Panel - Login Form */}
        <div className={styles.rightPanel}>
          <div className={styles.form}>
            <h2>Welcome Back!</h2>
            <p>Sign in to your account</p>

            {error && (
              <div className={styles.error}>
                ❌ {error}
              </div>
            )}

            <form onSubmit={handleSubmit}>
              {/* Role Selection */}
              <div className={styles.roleSelector}>
                <label>
                  <input
                    type="radio"
                    name="role"
                    value="employee"
                    checked={role === 'employee'}
                    onChange={(e) => setRole(e.target.value)}
                  />
                  <span>👤 Employee</span>
                </label>
                <label>
                  <input
                    type="radio"
                    name="role"
                    value="admin"
                    checked={role === 'admin'}
                    onChange={(e) => setRole(e.target.value)}
                  />
                  <span>👨‍💼 Admin</span>
                </label>
              </div>

              {/* Username */}
              <div className={styles.formGroup}>
                <label>Username</label>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="Enter your username"
                  disabled={loading}
                  required
                />
              </div>

              {/* Password */}
              <div className={styles.formGroup}>
                <label>Password</label>
                <div className={styles.passwordInput}>
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter your password"
                    disabled={loading}
                    required
                  />
                  <button
                    type="button"
                    className={styles.togglePassword}
                    onClick={() => setShowPassword(!showPassword)}
                    disabled={loading}
                  >
                    {showPassword ? '🙈' : '👁️'}
                  </button>
                </div>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                className={styles.submitBtn}
                disabled={loading}
              >
                {loading ? 'Logging in...' : 'LOGIN'}
              </button>
            </form>

            <div className={styles.footer}>
              <p>Secure Employee Attendance & Leave Management</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;
