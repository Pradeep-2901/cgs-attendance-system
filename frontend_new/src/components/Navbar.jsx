import { useNavigate } from 'react-router-dom';
import { FaHome, FaCalendarAlt, FaSignOutAlt } from 'react-icons/fa';
import styles from './Navbar.module.css';

function Navbar({ user, onLogout }) {
  const navigate = useNavigate();

  const handleNavigation = (path) => {
    navigate(path);
  };

  const handleLogout = () => {
    onLogout();
    navigate('/');
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
              onClick={() => handleNavigation('/dashboard')}
              title="Go to Dashboard"
            >
              <FaHome className={styles.navbar__icon} />
              <span className={styles.navbar__label}>Dashboard</span>
            </button>

            <button
              className={styles.navbar__btn}
              onClick={() => handleNavigation('/records')}
              title="View Attendance Records"
            >
              <FaCalendarAlt className={styles.navbar__icon} />
              <span className={styles.navbar__label}>Records</span>
            </button>
          </div>
        </div>

        {/* Right Section: User & Logout */}
        <div className={styles.navbar__right}>
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
