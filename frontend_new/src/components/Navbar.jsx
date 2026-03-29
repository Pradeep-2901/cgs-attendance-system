import { useContext } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { FaHome, FaCalendarAlt, FaSignOutAlt, FaSun, FaMoon } from 'react-icons/fa';
import ThemeContext from '../context/ThemeContext';
import styles from './Navbar.module.css';

function Navbar({ user, onLogout }) {
  const navigate = useNavigate();
  const location = useLocation();
  const { isDark, toggleTheme } = useContext(ThemeContext);

  const handleHome = () => {
    // Ensure we navigate properly
    if (location.pathname !== '/dashboard') {
      navigate('/dashboard', { replace: true });
    }
  };

  const handleRecords = () => {
    // Ensure we navigate properly
    if (location.pathname !== '/records') {
      navigate('/records', { replace: true });
    }
  };

  const handleLogout = () => {
    onLogout();
    navigate('/', { replace: true });
  };

  return (
    <nav className={styles.navbar}>
      <div className={styles.navbar__content}>
        {/* Left Section: Logo & Navigation */}
        <div className={styles.navbar__left}>
          <div className={styles.navbar__logo}>📍 CGS Attendance</div>
          
          <div className={styles.navbar__buttons}>
            <button
              className={styles.navbar__btn}
              onClick={handleHome}
              title="Go to Home"
              aria-current={location.pathname === '/dashboard' ? 'page' : undefined}
            >
              <FaHome className={styles.navbar__icon} />
              <span className={styles.navbar__label}>Home</span>
            </button>

            <button
              className={styles.navbar__btn}
              onClick={handleRecords}
              title="View Attendance Records"
              aria-current={location.pathname === '/records' ? 'page' : undefined}
            >
              <FaCalendarAlt className={styles.navbar__icon} />
              <span className={styles.navbar__label}>Records</span>
            </button>
          </div>
        </div>

        {/* Right Section: Theme Toggle & Logout */}
        <div className={styles.navbar__right}>
          <button
            className={`${styles.navbar__btn} ${styles.navbar__theme}`}
            onClick={toggleTheme}
            title={isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          >
            {isDark ? <FaSun className={styles.navbar__icon} /> : <FaMoon className={styles.navbar__icon} />}
            <span className={styles.navbar__label}>{isDark ? 'Light' : 'Dark'}</span>
          </button>

          <button
            className={`${styles.navbar__btn} ${styles.navbar__logout}`}
            onClick={handleLogout}
            title="Logout"
          >
            <FaSignOutAlt className={styles.navbar__icon} />
            <span className={styles.navbar__label}>Logout</span>
          </button>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
